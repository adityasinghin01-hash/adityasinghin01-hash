#!/usr/bin/env bash
# Screenshot an animated SVG through headless Chrome. Static converters render
# these blank because every element starts at opacity 0 and only SMIL brings it
# in — Chrome is the only local renderer that actually runs the timeline.
set -euo pipefail

SVG="$1"; OUT="${2:-/tmp/preview.png}"; DELAY="${3:-3500}"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

W=$(python3 - "$SVG" <<'PY'
import re,sys
s=open(sys.argv[1]).read(500)
print(int(float(re.search(r'width="([\d.]+)"',s).group(1))))
PY
)
H=$(python3 - "$SVG" <<'PY'
import re,sys
s=open(sys.argv[1]).read(500)
print(int(float(re.search(r'height="([\d.]+)"',s).group(1))))
PY
)

"$CHROME" --headless --disable-gpu --hide-scrollbars \
  --virtual-time-budget="$DELAY" \
  --screenshot="$OUT" --window-size="${W},${H}" \
  --default-background-color=00000000 \
  "file://$(cd "$(dirname "$SVG")" && pwd)/$(basename "$SVG")" 2>/dev/null

echo "$OUT  (${W}x${H})"
