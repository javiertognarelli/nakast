#!/usr/bin/env bash
# Regenerate the PDF versions of the documentation.
#
# The manuals embed the workflow diagram as Mermaid, which GitHub renders natively
# but pandoc does not. This script renders the diagram to PNG first, substitutes it
# into a temporary copy of the Markdown, and then produces the PDF. Every
# intermediate file, the rendered PNG included, lives in a temporary directory that
# is removed on exit, so building leaves nothing behind but the PDFs.
#
# Requires: mermaid-cli (via npx), pandoc, weasyprint, and a Chrome binary for
# mermaid-cli. Set CHROME to override the autodetected path.
set -euo pipefail
cd "$(dirname "$0")"

CHROME="${CHROME:-$(ls -d "$HOME"/.cache/puppeteer/chrome/linux-*/chrome-linux64/chrome 2>/dev/null | tail -1)}"
[ -x "$CHROME" ] || { echo "Chrome not found; set CHROME=/path/to/chrome" >&2; exit 1; }

TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT

# Linked as an author stylesheet through pandoc rather than handed to WeasyPrint
# with -s: a user stylesheet loses every conflict with pandoc's built-in styles,
# whatever its specificity, which silently discarded the cover page spacing.
CSS="$(pwd)/pdf.css"
printf '{ "executablePath": "%s", "args": ["--no-sandbox","--disable-dev-shm-usage"] }\n' "$CHROME" > "$TMP/pc.json"

build() {  # $1=markdown  $2=pdf  $3=basename for the diagram  $4=title  $5=lang
    python3 - "$1" "$TMP/$3.png" "$TMP/$3.mmd" "$TMP/body.md" <<'PY'
import re, sys
src, png, mmd, out = sys.argv[1:5]
text = open(src).read()
diagram = re.search(r'```mermaid\n(.*?)```', text, re.S)
assert diagram, f'{src}: no mermaid block found'
open(mmd, 'w').write(diagram.group(1))
# height rather than width: the diagram is tall, and sizing it by width would
# overflow the page and make WeasyPrint drop it.
body, n = re.subn(r'```mermaid\n.*?```', f'![]({png}){{height=20cm}}', text, flags=re.S)
assert n == 1, f'{src}: expected one mermaid block, found {n}'
open(out, 'w').write(body)
PY
    npx -y @mermaid-js/mermaid-cli -i "$TMP/$3.mmd" -o "$TMP/$3.png" -p "$TMP/pc.json" \
        -b white -s 2 >/dev/null 2>&1
    # gfm_auto_identifiers makes pandoc build heading anchors the way GitHub does,
    # so the cross-references written for GitHub also resolve inside the PDF.
    # lang drives WeasyPrint's hyphenation, which justified text needs.
    pandoc "$TMP/body.md" -f markdown+gfm_auto_identifiers -t html5 --standalone \
        --metadata pagetitle="$4" --metadata lang="$5" --css "$CSS" -o "$TMP/body.html"
    weasyprint "$TMP/body.html" "$2"
    echo "  wrote $2"
}

build USER_MANUAL.md    USER_MANUAL.pdf    workflow_en "NAKAST — User Manual"       en
build MANUAL_USUARIO.md MANUAL_USUARIO.pdf workflow_es "NAKAST — Manual de usuario" es

# The services and licences compilation has no diagram, so it goes straight
# through pandoc.
pandoc THIRD_PARTY_LICENSES.md -f markdown+gfm_auto_identifiers -t html5 --standalone \
    --metadata pagetitle="NAKAST — Compilado de Servicios y Licencias" --metadata lang=es --css "$CSS" \
    -o "$TMP/lic.html"
weasyprint "$TMP/lic.html" THIRD_PARTY_LICENSES.pdf
echo "  wrote THIRD_PARTY_LICENSES.pdf"
