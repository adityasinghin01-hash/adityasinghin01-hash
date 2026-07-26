"""Render the ASCII portrait as a self-contained animated SVG.

Everything is SMIL + CSS-free presentation attributes: GitHub serves README
images through its camo proxy inside an <img>, so there is no JavaScript and
no pointer interaction. Row reveal, gradient drift, scanline and cursor blink
all have to live inside the file.
"""
import sys
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image
from asciiart import asciify

ROOT = Path(__file__).resolve().parent.parent
ADV, LH, FS = 8.4, 14.7, 14.0          # advance, line height, font size
PAD = 22
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace"

THEMES = {
    "dark":  dict(bg="#030712", panel="#0F172A", stroke="rgba(255,255,255,.08)",
                  g1="#7C3AED", g2="#22D3EE", g3="#10B981", glow=".55", scan=".07"),
    "light": dict(bg="#FFFFFF", panel="#F8FAFC", stroke="rgba(15,23,42,.08)",
                  g1="#2563EB", g2="#06B6D4", g3="#10B981", glow=".28", scan=".05"),
}


def build(lines, theme, reveal=0.030, dur=0.26):
    t = THEMES[theme]
    cols, rows = len(lines[0]), len(lines)
    w = round(cols * ADV + PAD * 2, 1)
    h = round(rows * LH + PAD * 2, 1)
    total = round(rows * reveal + dur, 2)

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" role="img" aria-label="ASCII portrait of Aditya Singh">',
        "<defs>",
        # drifting accent gradient
        f'<linearGradient id="g" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{w}" y2="{h}">',
        f'<stop offset="0" stop-color="{t["g1"]}"/>',
        f'<stop offset=".5" stop-color="{t["g2"]}"/>',
        f'<stop offset="1" stop-color="{t["g3"]}"/>',
        '<animateTransform attributeName="gradientTransform" type="translate" '
        f'values="0 0; {w*0.35:.0f} {h*0.2:.0f}; 0 0" dur="14s" repeatCount="indefinite"/>',
        "</linearGradient>",
        # soft bloom so the characters read as emitting light
        '<filter id="bloom" x="-20%" y="-20%" width="140%" height="140%">',
        f'<feGaussianBlur stdDeviation="2.2" result="b"/>',
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>',
        "</filter>",
        # scanline band
        '<linearGradient id="scan" x1="0" y1="0" x2="0" y2="1">',
        '<stop offset="0" stop-color="#fff" stop-opacity="0"/>',
        f'<stop offset=".5" stop-color="{t["g2"]}" stop-opacity="{t["scan"]}"/>',
        '<stop offset="1" stop-color="#fff" stop-opacity="0"/>',
        "</linearGradient>",
        "</defs>",
        f'<rect width="{w}" height="{h}" rx="14" fill="{t["bg"]}"/>',
        f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="13.5" fill="none" stroke="{t["stroke"]}"/>',
        # the whole portrait breathes slightly
        '<g><animateTransform attributeName="transform" type="translate" '
        'values="0 0; 0 -3.5; 0 0" dur="7s" repeatCount="indefinite" '
        'calcMode="spline" keyTimes="0;.5;1" keySplines=".4 0 .6 1;.4 0 .6 1"/>',
        f'<g font-family="{MONO}" font-size="{FS}" fill="url(#g)" '
        f'filter="url(#bloom)" opacity="{t["glow"]}" xml:space="preserve">',
    ]

    # base pass (blurred, low opacity) then crisp pass on top
    for layer, (op, filt) in enumerate([(t["glow"], True), ("1", False)]):
        if layer == 1:
            out.append("</g>")
            out.append(f'<g font-family="{MONO}" font-size="{FS}" fill="url(#g)" '
                       f'xml:space="preserve">')
        for i, ln in enumerate(lines):
            y = round(PAD + (i + 0.82) * LH, 1)
            begin = round(i * reveal, 3)
            # xml:space has to sit on the <text> itself — Chrome ignores it when
            # it is only inherited from the parent <g>, the leading/trailing
            # spaces collapse, and textLength then smears the surviving glyphs
            # across the whole row.
            out.append(
                f'<text xml:space="preserve" x="{PAD}" y="{y}" '
                f'textLength="{round(cols*ADV,1)}" '
                f'lengthAdjust="spacing" opacity="0">{escape(ln)}'
                f'<animate attributeName="opacity" from="0" to="1" begin="{begin}s" '
                f'dur="{dur}s" fill="freeze"/></text>')
    out.append("</g>")

    # scanline sweep, starts once the portrait has resolved
    out += [
        f'<rect x="0" y="0" width="{w}" height="46" fill="url(#scan)" opacity="0">',
        f'<animate attributeName="opacity" from="0" to="1" begin="{total}s" dur=".4s" fill="freeze"/>',
        f'<animate attributeName="y" values="-46;{h}" begin="{total}s" dur="4.5s" repeatCount="indefinite"/>',
        "</rect>",
        # terminal cursor parks under the last row
        f'<rect x="{PAD}" y="{round(PAD + rows * LH + 3, 1)}" width="{ADV}" height="{FS}" '
        f'fill="{THEMES[theme]["g2"]}" opacity="0">',
        f'<animate attributeName="opacity" values="0;1" begin="{total}s" dur=".01s" fill="freeze"/>',
        f'<animate attributeName="opacity" values="1;1;0;0;1" begin="{total}s" dur="1.06s" '
        'repeatCount="indefinite"/>',
        "</rect>",
        "</g></svg>",
    ]
    return "\n".join(out)


if __name__ == "__main__":
    src = ROOT / "assets" / "source-portrait.png"
    cols = int(sys.argv[1]) if len(sys.argv) > 1 else 78
    lines = asciify(Image.open(src), cols=cols)
    for theme in THEMES:
        path = ROOT / f"ascii-{theme}.svg"
        path.write_text(build(lines, theme))
        print(f"{path.name}  {len(lines[0])}x{len(lines)}  {path.stat().st_size/1024:.1f} KB")
