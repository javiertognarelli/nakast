#!/usr/bin/env bash
# Regenerate the PDF versions of the documentation.
#
# The manuals embed the workflow diagram as Mermaid, which GitHub renders natively
# but pandoc does not. This script renders the diagram to PNG first, substitutes it
# into a temporary copy of the Markdown, and then produces the PDF.
#
# Requires: mermaid-cli (via npx), pandoc, weasyprint, and a Chrome binary for
# mermaid-cli. Set CHROME to override the autodetected path.
set -euo pipefail
cd "$(dirname "$0")"

CHROME="${CHROME:-$(ls -d "$HOME"/.cache/puppeteer/chrome/linux-*/chrome-linux64/chrome 2>/dev/null | tail -1)}"
[ -x "$CHROME" ] || { echo "Chrome not found; set CHROME=/path/to/chrome" >&2; exit 1; }

TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
printf '{ "executablePath": "%s", "args": ["--no-sandbox","--disable-dev-shm-usage"] }\n' "$CHROME" > "$TMP/pc.json"

build() {  # $1=markdown  $2=pdf  $3=png  $4=title
    python3 - "$1" "$TMP/$3" "$TMP/body.md" <<'PY'
import re, sys
src, png, out = sys.argv[1:4]
text = open(src).read()
diagram = re.search(r'```mermaid\n(.*?)```', text, re.S)
open(png.replace('.png', '.mmd'), 'w').write(diagram.group(1))
body, n = re.subn(r'```mermaid\n.*?```', f'![]({png}){{height=20cm}}', text, flags=re.S)
assert n == 1, f'{src}: expected one mermaid block, found {n}'
open(out, 'w').write(body)
PY
    npx -y @mermaid-js/mermaid-cli -i "$TMP/${3%.png}.mmd" -o "$TMP/$3" -p "$TMP/pc.json" -b white -s 2 >/dev/null 2>&1
    # gfm_auto_identifiers makes pandoc build heading anchors the way GitHub does,
    # so the cross-references written for GitHub also resolve inside the PDF.
    pandoc "$TMP/body.md" -f markdown+gfm_auto_identifiers -t html5 --standalone \
        --metadata title="$4" -o "$TMP/body.html"
    weasyprint "$TMP/body.html" "$2"
    cp "$TMP/$3" "img/${3}"
    echo "  wrote $2"
}

build USER_MANUAL.md    USER_MANUAL.pdf    workflow_en.png "NAKAST — User Manual"
build MANUAL_USUARIO.md MANUAL_USUARIO.pdf workflow_es.png "NAKAST — Manual de usuario"
