"""Render the ASCII portrait as a self-contained animated SVG.

Everything is SMIL + presentation attributes: GitHub serves README images
through its camo proxy inside an <img>, so there is no JavaScript and no
pointer interaction. The reveal, gradient drift, scanline and cursor blink all
have to live inside the file.

The portrait is *printed* character by character. Each glyph gets its own
arrival time from a flow field — a diagonal drift warped by two out-of-phase
sine waves — so glyphs land individually but in travelling bands rather than
raster order. A mask wipe was tried first and reads as a wipe, not as drawing:
it uncovers regions of an image that is already there, so you never see a
character appear.
"""
import math
import sys
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image
from asciiart import asciify

ROOT = Path(__file__).resolve().parent.parent
ADV, LH, FS = 8.4, 14.7, 14.0          # advance, line height, font size
PAD = 22
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace"
BUCKETS = 190                          # distinct arrival times

THEMES = {
    "dark":  dict(bg="#030712", panel="#0F172A", stroke="rgba(255,255,255,.08)",
                  g1="#7C3AED", g2="#22D3EE", g3="#10B981", glow=".55", scan=".07"),
    "light": dict(bg="#FFFFFF", panel="#F8FAFC", stroke="rgba(15,23,42,.08)",
                  g1="#2563EB", g2="#06B6D4", g3="#10B981", glow=".28", scan=".05"),
}


def flow(u, v):
    """Arrival phase for a glyph at normalised position (u, v).

    Mostly top-down with a diagonal lean, warped by two sine waves at
    incommensurate frequencies so the advancing front is a wandering band
    instead of a straight line. Purely analytic — no noise texture to ship.
    """
    base = u * 0.26 + v * 0.74
    warp = (0.170 * math.sin(u * 5.9 + v * 2.7)
            + 0.105 * math.sin(u * 3.1 - v * 8.6 + 1.7)
            + 0.058 * math.sin(u * 13.7 + v * 5.3 + 0.4)
            + 0.032 * math.sin(u * 21.1 - v * 17.3 + 2.2))
    return base + warp


def build(lines, theme, sweep=4.0):
    t = THEMES[theme]
    cols, rows = len(lines[0]), len(lines)
    w = round(cols * ADV + PAD * 2, 1)
    h = round(rows * LH + PAD * 2, 1)

    # bucket every non-blank glyph by arrival phase
    glyphs = []
    for r, ln in enumerate(lines):
        for c, ch in enumerate(ln):
            if ch == " ":
                continue
            glyphs.append((flow(c / (cols - 1), r / (rows - 1)), c, r, ch))
    lo = min(g[0] for g in glyphs)
    hi = max(g[0] for g in glyphs)

    buckets = [[] for _ in range(BUCKETS)]
    for phase, c, r, ch in glyphs:
        k = int((phase - lo) / (hi - lo) * (BUCKETS - 1))
        buckets[k].append((c, r, ch))

    span = round(sweep + 0.6, 2)       # one shared timeline for every bucket
    art = [f'<g font-family="{MONO}" font-size="{FS}" fill="url(#g)" '
           f'filter="url(#bloom)">']
    for k, items in enumerate(buckets):
        if not items:
            continue
        begin = k / (BUCKETS - 1) * sweep
        # Every group's animation runs from t=0 and simply *holds* at zero
        # until its turn. Using begin="{n}s" instead would leave the group at
        # its base opacity until that moment — i.e. fully visible — so the
        # whole portrait appears at once and nothing staggers. Base opacity
        # stays 1 so a renderer that ignores SMIL still shows the artwork.
        p = round(begin / span, 4)
        q = round(min((begin + 0.42) / span, 1.0), 4)
        q2 = round(min((begin + 0.55) / span, 1.0), 4)
        art.append(f'<g opacity="1">'
                   f'<animate attributeName="opacity" values="0;0;1;1" '
                   f'keyTimes="0;{p};{q};1" dur="{span}s" fill="freeze" '
                   f'calcMode="spline" '
                   f'keySplines="0 0 1 1;.2 .7 .3 1;0 0 1 1"/>'
                   f'<animateTransform attributeName="transform" type="translate" '
                   f'values="0 3.2;0 3.2;0 0;0 0" keyTimes="0;{p};{q2};1" '
                   f'dur="{span}s" fill="freeze" calcMode="spline" '
                   f'keySplines="0 0 1 1;.15 .85 .25 1;0 0 1 1"/>')
        for c, r, ch in items:
            x = round(PAD + c * ADV, 1)
            y = round(PAD + (r + 0.82) * LH, 1)
            art.append(f'<text x="{x}" y="{y}">{escape(ch)}</text>')
        art.append("</g>")
    art.append("</g>")

    total = span
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" role="img" '
        f'aria-label="ASCII portrait of Aditya Singh">',
        "<defs>",
        # drifting accent gradient
        f'<linearGradient id="g" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{w}" y2="{h}">',
        f'<stop offset="0" stop-color="{t["g1"]}"/>',
        f'<stop offset=".5" stop-color="{t["g2"]}"/>',
        f'<stop offset="1" stop-color="{t["g3"]}"/>',
        '<animateTransform attributeName="gradientTransform" type="translate" '
        f'values="0 0; {w*0.35:.0f} {h*0.2:.0f}; 0 0" dur="14s" repeatCount="indefinite"/>',
        "</linearGradient>",
        # Bloom in a single pass: blurred copy dimmed, then the crisp source
        # merged over it. Doing this with a second <use> of the glyphs instead
        # would need the art to live in <defs>, and SMIL does not drive <use>
        # instances of a defs subtree in Chrome — the animations simply never
        # run and the base opacity shows the finished portrait from frame one.
        '<filter id="bloom" x="-20%" y="-20%" width="140%" height="140%">',
        '<feGaussianBlur stdDeviation="2.4" result="b"/>',
        f'<feComponentTransfer in="b" result="bd">'
        f'<feFuncA type="linear" slope="{t["glow"]}"/></feComponentTransfer>',
        '<feMerge><feMergeNode in="bd"/><feMergeNode in="SourceGraphic"/></feMerge>',
        "</filter>",
        # scanline band
        '<linearGradient id="scan" x1="0" y1="0" x2="0" y2="1">',
        '<stop offset="0" stop-color="#fff" stop-opacity="0"/>',
        f'<stop offset=".5" stop-color="{t["g2"]}" stop-opacity="{t["scan"]}"/>',
        '<stop offset="1" stop-color="#fff" stop-opacity="0"/>',
        "</linearGradient>",
        "</defs>",
        f'<rect width="{w}" height="{h}" rx="14" fill="{t["bg"]}"/>',
        f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="13.5" '
        f'fill="none" stroke="{t["stroke"]}"/>',
        # the whole portrait breathes slightly
        '<g><animateTransform attributeName="transform" type="translate" '
        'values="0 0; 0 -3.5; 0 0" dur="7s" repeatCount="indefinite" '
        'calcMode="spline" keyTimes="0;.5;1" keySplines=".4 0 .6 1;.4 0 .6 1"/>',
        # <use> instances the glyphs twice — blurred underneath, crisp on top —
        # so the bloom costs one extra element instead of a second full copy.
        *art,
        # scanline sweep, starts once the portrait has resolved
        f'<rect x="0" y="0" width="{w}" height="46" fill="url(#scan)" opacity="0">',
        f'<animate attributeName="opacity" from="0" to="1" begin="{total}s" dur=".4s" fill="freeze"/>',
        f'<animate attributeName="y" values="-46;{h}" begin="{total}s" dur="4.5s" repeatCount="indefinite"/>',
        "</rect>",
        # terminal cursor parks under the last row
        f'<rect x="{PAD}" y="{round(PAD + rows * LH + 3, 1)}" width="{ADV}" height="{FS}" '
        f'fill="{t["g2"]}" opacity="0">',
        f'<animate attributeName="opacity" values="1;1;0;0;1" begin="{total}s" dur="1.06s" '
        'repeatCount="indefinite" fill="freeze"/>',
        "</rect>",
        "</g></svg>",
    ])


if __name__ == "__main__":
    src = ROOT / "assets" / "source-portrait.png"
    cols = int(sys.argv[1]) if len(sys.argv) > 1 else 78
    lines = asciify(Image.open(src), cols=cols)
    for theme in THEMES:
        path = ROOT / f"ascii-{theme}.svg"
        path.write_text(build(lines, theme))
        print(f"{path.name}  {len(lines[0])}x{len(lines)}  {path.stat().st_size/1024:.1f} KB")
