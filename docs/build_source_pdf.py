#!/usr/bin/env python3
"""Build a PDF listing of the NAKAST source code, for software registration.

The listing covers the files that make up the work itself: the Nextflow pipeline,
its configuration and the Python scripts it runs. Documentation, the species
catalogue (data rather than code) and the documentation build scripts are left
out.

Each file is printed with line numbers and a SHA-256 fingerprint, so the deposited
listing can later be checked against the repository. The commit the listing was
built from is recorded on the contents page; a working tree with uncommitted
changes is flagged as such.

Requires: pygments, weasyprint. Usage: python3 docs/build_source_pdf.py
"""

import hashlib
import html
import os
import subprocess
import sys
import tempfile

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import GroovyLexer, PythonLexer

DOCS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(DOCS)
OUTPUT = os.path.join(DOCS, "CODIGO_FUENTE.pdf")

# (path, lexer, description), in the order a reader would follow the pipeline.
FILES = [
    ("nakast.nf", GroovyLexer, "Definición del flujo de trabajo y de sus procesos (Nextflow)"),
    ("nextflow.config", GroovyLexer, "Configuración de parámetros, recursos, ambientes y perfiles"),
    ("bin/validate_samplesheet.py", PythonLexer, "Validación de la tabla de muestras"),
    ("bin/pubmlst_api.py", PythonLexer, "Cliente de la API REST de PubMLST"),
    ("bin/download_pubmlst.py", PythonLexer, "Descarga del esquema MLST de cada especie"),
    ("bin/parse_kma.py", PythonLexer, "Llamado de alelos y asignación de ST y CC"),
    ("bin/list_pubmlst_species.py", PythonLexer, "Catálogo de especies compatibles"),
]

AUTHORS = [
    "JAVIER ALEJANDRO TOGNARELLI SANTIAGO",
    "DANIEL FERNANDO ESCOBAR ARAYA",
    "FERNANDO ANDRÉS AMAYA INZUNZA",
]
DATE = "SEPTIEMBRE 2026"

EXTRA_CSS = """
/* One row per source line: the number sits in its own column, so a long line
   wraps inside the code column and the numbering stays aligned. */
.listing { font-family: monospace; font-size: 7.6pt; line-height: 1.35; }
.line { display: flex; }
.lineno { flex: 0 0 2.8em; text-align: right; padding-right: 0.9em; color: #999; }
.code { flex: 1; white-space: pre-wrap; overflow-wrap: anywhere; text-align: left; }
.file-header { page-break-before: always; }
.file-header h2 { font-family: monospace; font-size: 13pt; margin-bottom: 0.2em; }
.file-meta { font-size: 8.5pt; color: #555; margin: 0 0 0.8em 0; text-align: left; }
.file-meta code { font-size: 8pt; }
table.files { font-size: 9pt; }
table.files td, table.files th { padding: 3px 6px; vertical-align: top; }
.hash { font-family: monospace; font-size: 7.5pt; word-break: break-all; }
"""


def git(*args):
    return subprocess.run(["git", "-C", ROOT, *args], capture_output=True,
                          text=True).stdout.strip()


def revision():
    commit = git("rev-parse", "--short", "HEAD") or "desconocido"
    dirty = bool(git("status", "--porcelain", "--", *[f for f, _, _ in FILES]))
    return commit, dirty


def render(text, lexer, formatter):
    """Highlight a file and lay it out as numbered rows."""
    marked = highlight(text, lexer(), formatter).split("\n")
    if marked and marked[-1] == "":
        marked.pop()
    return "".join(
        f"<div class='line'><span class='lineno'>{n}</span>"
        f"<span class='code'>{line or ' '}</span></div>"
        for n, line in enumerate(marked, 1))


def main():
    # nowrap emits bare markup with every line closing its own spans, so the output
    # can be split into lines safely even inside multi-line strings.
    formatter = HtmlFormatter(nowrap=True, style="default")
    commit, dirty = revision()

    rows, sections, total = [], [], 0
    for i, (path, lexer, description) in enumerate(FILES, 1):
        with open(os.path.join(ROOT, path), "rb") as fh:
            raw = fh.read()
        text = raw.decode("utf-8")
        lines = text.count("\n") + (0 if text.endswith("\n") else 1)
        digest = hashlib.sha256(raw).hexdigest()
        total += lines
        rows.append(
            f"<tr><td>{i}</td><td><code>{html.escape(path)}</code></td>"
            f"<td>{html.escape(description)}</td><td>{lines}</td>"
            f"<td class='hash'>{digest}</td></tr>")
        sections.append(
            f"<div class='file-header'><h2>{i}. {html.escape(path)}</h2>"
            f"<p class='file-meta'>{html.escape(description)} · {lines} líneas · "
            f"SHA-256 <code>{digest}</code></p></div>"
            f"<div class='listing highlight'>{render(text, lexer, formatter)}</div>")

    state = (f"commit <code>{commit}</code> con cambios sin registrar en el historial"
             if dirty else f"commit <code>{commit}</code>")

    body = f"""
<div class="cover" align="center">
<h1>NAKAST</h1>
<p class="cover-subtitle">Código Fuente</p>
<p class="cover-institution">UNIVERSIDAD DE VALPARAÍSO</p>
<p class="cover-authors">Autores:<br>{'<br>'.join(AUTHORS)}</p>
<p class="cover-date">{DATE}</p>
</div>
<div class="page-break"></div>

<h2>Contenido</h2>
<p>Este documento reproduce íntegramente el código fuente de NAKAST: el flujo de trabajo en
Nextflow, su configuración y los scripts en Python que ejecuta. Se omiten la documentación,
el catálogo de especies compatibles (<code>assets/pubmlst_species.tsv</code>, que contiene
datos y no código) y los scripts que generan la documentación en PDF.</p>
<p>Repositorio: <code>https://github.com/javiertognarelli/nakast</code>. Estado del código
listado: {state}.</p>
<p>La huella SHA-256 de cada archivo permite verificar que una copia del código coincide
exactamente con la aquí listada.</p>
<table class="files">
<thead><tr><th>#</th><th>Archivo</th><th>Descripción</th><th>Líneas</th><th>SHA-256</th></tr></thead>
<tbody>{''.join(rows)}</tbody>
</table>
<p>Total: {len(FILES)} archivos, {total} líneas.</p>
{''.join(sections)}
"""
    page = f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<title>NAKAST — Código Fuente</title>
<link rel="stylesheet" href="{os.path.join(DOCS, 'pdf.css')}">
<style>{formatter.get_style_defs('.highlight')}{EXTRA_CSS}</style>
</head><body>{body}</body></html>"""

    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "source.html")
        with open(src, "w") as fh:
            fh.write(page)
        subprocess.run(["weasyprint", src, OUTPUT], check=True,
                       stderr=subprocess.DEVNULL)
    print(f"  wrote {os.path.relpath(OUTPUT, ROOT)} ({len(FILES)} files, {total} lines, "
          f"{'dirty ' if dirty else ''}{commit})")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
