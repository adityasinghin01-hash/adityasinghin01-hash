"""The main profile card: ASCII portrait typed out beside a system-info panel,
both inside one glowing container.

Everything is SMIL. GitHub serves README images through its camo proxy inside
an <img>, so there is no JavaScript and no pointer interaction — the typing,
the cursor and the panel reveal all have to live in the file.

The portrait is typed row by row: each row carries a <clipPath> whose rect
widens left to right, so glyphs appear under a travelling print head rather
than the whole line switching on at once.
"""
import sys
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image

from asciiart import asciify
from profile import (USERNAME, HANDLE, IDENTITY, SECTIONS, LOCK, CHIPS, FOOTER)
from theme import THEMES, MONO, ADVANCE, LINE, ramp_color

ROOT = Path(__file__).resolve().parent.parent

W = 1800                      # viewBox units; scales to whatever GitHub gives it
PAD = 30
GAP = 22
BAR = 74                      # title bar + traffic lights
PANE_PAD = 24
INFO_W = 610
ART_W = W - PAD * 2 - INFO_W - GAP

INFO_FS = 17.0
HEAD_FS = 13.0
SWEEP = 8.2                   # seconds to type the whole portrait


def esc(t):
    return escape(str(t))


def leader_row(x, y, width, key, val, t, fs):
    """label ······· value, with the dots drawn between the two text runs."""
    adv = fs * ADVANCE
    kx = x + adv * 2                       # room for the bullet
    kw = len(key) * adv
    vw = len(val) * adv
    d0 = kx + kw + adv
    d1 = x + width - vw - adv
    out = [f'<text x="{x:.1f}" y="{y:.1f}" fill="{t["cyan"]}">•</text>',
           f'<text x="{kx:.1f}" y="{y:.1f}" fill="{t["emerald"]}">{esc(key)}</text>',
           f'<text x="{x + width:.1f}" y="{y:.1f}" text-anchor="end" '
           f'fill="{t["ink"]}">{esc(val)}</text>']
    if d1 > d0:
        out.append(f'<line x1="{d0:.1f}" y1="{y - fs * 0.28:.1f}" '
                   f'x2="{d1:.1f}" y2="{y - fs * 0.28:.1f}" '
                   f'stroke="{t["dim"]}" stroke-width="1" stroke-opacity=".55" '
                   f'stroke-dasharray="1 4" stroke-linecap="round"/>')
    return "".join(out)


def build(lines, theme):
    t = THEMES[theme]
    cols, rows = len(lines[0]), len(lines)

    art_inner = ART_W - PANE_PAD * 2
    fs = art_inner / cols / ADVANCE        # portrait font size
    lh = fs * LINE
    art_x = PAD + PANE_PAD
    art_y = BAR + PANE_PAD + 34            # below the pane header
    art_h = rows * lh

    pane_h = PANE_PAD * 2 + 34 + art_h + 26
    chips_y = BAR + pane_h + GAP + 34
    H = chips_y + 54

    row_t = SWEEP / rows
    o = []

    # ---------- defs -------------------------------------------------
    o.append('<defs>')
    o.append(f'<linearGradient id="edge" x1="0" y1="0" x2="{W}" y2="{H}" '
             f'gradientUnits="userSpaceOnUse">'
             f'<stop offset="0" stop-color="{t["violet"]}"/>'
             f'<stop offset=".5" stop-color="{t["cyan"]}"/>'
             f'<stop offset="1" stop-color="{t["emerald"]}"/>'
             f'<animateTransform attributeName="gradientTransform" type="translate" '
             f'values="0 0;{W*0.3:.0f} 0;0 0" dur="16s" repeatCount="indefinite"/>'
             '</linearGradient>')
    # One clipPath holding two rects — a clip path is the union of its shapes,
    # so the finished block and the row under the head can share a single clip
    # and the glyphs only have to exist once.
    done_h = ";".join(f"{i * lh:.2f}" for i in range(rows + 1))
    live_y = ";".join(f"{art_y + i * lh - fs * 0.85:.2f}" for i in range(rows))
    o.append(f'<clipPath id="type">'
             f'<rect x="{art_x:.1f}" y="{art_y - fs * 0.85:.2f}" '
             f'width="{art_inner:.1f}" height="0">'
             f'<animate attributeName="height" values="{done_h}" '
             f'calcMode="discrete" dur="{SWEEP:.2f}s" fill="freeze"/></rect>'
             f'<rect x="{art_x:.1f}" y="{art_y - fs * 0.85:.2f}" width="0" '
             f'height="{lh * 1.15:.2f}">'
             f'<animate attributeName="width" from="0" to="{art_inner:.1f}" '
             f'dur="{row_t:.4f}s" repeatCount="{rows}"/>'
             f'<animate attributeName="y" values="{live_y}" calcMode="discrete" '
             f'dur="{SWEEP:.2f}s" fill="freeze"/></rect>'
             '</clipPath>')
    o.append('</defs>')

    # ---------- shell ------------------------------------------------
    o.append(f'<rect width="{W}" height="{H:.0f}" rx="20" fill="{t["ground"]}"/>')
    o.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2:.0f}" rx="19" '
             f'fill="{t["panel"]}" stroke="url(#edge)" stroke-width="2" '
             'stroke-opacity=".55"/>')

    o.append(f'<g font-family="{MONO}" font-size="{HEAD_FS + 3:.0f}">')
    o.append(f'<text x="{PAD + 6}" y="{PAD + 20}" fill="{t["ink"]}">'
             f'{esc(USERNAME)}/README.md</text>')
    o.append(f'<text x="{W - PAD - 6}" y="{PAD + 20}" text-anchor="end" '
             f'fill="{t["dim"]}">{esc(HANDLE)}@github — '
             f'<tspan fill="{t["cyan"]}">$ ./profile --live</tspan></text>')
    o.append('</g>')
    for i, c in enumerate(("#FF5F57", "#FEBC2E", "#28C840")):
        o.append(f'<circle cx="{PAD + 12 + i * 22}" cy="{PAD + 42}" r="7" fill="{c}"/>')

    # ---------- portrait pane ---------------------------------------
    o.append(f'<rect x="{PAD}" y="{BAR}" width="{ART_W}" height="{pane_h:.1f}" '
             f'rx="14" fill="{t["sub"]}" stroke="{t["line"]}"/>')
    o.append(f'<g font-family="{MONO}" font-size="{HEAD_FS}" letter-spacing="2.4">')
    o.append(f'<text x="{art_x}" y="{BAR + PANE_PAD + 14}" fill="{t["cyan"]}">'
             f'VISUAL.MAP <tspan fill="{t["dim"]}">/ PORTRAIT.SIGNAL</tspan></text>')
    o.append('</g>')
    o.append(f'<line x1="{art_x}" y1="{BAR + PANE_PAD + 26}" '
             f'x2="{PAD + ART_W - PANE_PAD}" y2="{BAR + PANE_PAD + 26}" '
             f'stroke="{t["line"]}"/>')

    # reticle corners
    rl, rr = art_x - 8, PAD + ART_W - PANE_PAD + 8
    rt, rb = art_y - lh - 6, art_y + art_h + 6
    for x, y, dx, dy in ((rl, rt, 1, 1), (rr, rt, -1, 1), (rl, rb, 1, -1), (rr, rb, -1, -1)):
        o.append(f'<path d="M{x} {y + 18*dy} L{x} {y} L{x + 18*dx} {y}" fill="none" '
                 f'stroke="{t["cyan"]}" stroke-opacity=".5" stroke-width="1.5"/>')

    # Padding whitespace was 46% of the glyphs and cost exactly as much to lay
    # out as real ones. Trim it and shift x instead. textLength/lengthAdjust is
    # gone too: it forces a per-glyph spacing solve, which Safari redoes on
    # every frame the clip changes. Rows share one font and size, so they stay
    # aligned with each other without it.
    adv = fs * ADVANCE
    o.append(f'<g clip-path="url(#type)" font-family="{MONO}" '
             f'font-size="{fs:.3f}">')
    for i, ln in enumerate(lines):
        body = ln.rstrip()
        lead = len(body) - len(body.lstrip())
        body = body.lstrip()
        if not body:
            continue
        col = ramp_color(t["ramp"], i / max(rows - 1, 1))
        # xml:space still matters — the interior spaces carry the image
        o.append(f'<text xml:space="preserve" x="{art_x + lead * adv:.2f}" '
                 f'y="{art_y + i * lh:.2f}" fill="{col}">{esc(body)}</text>')
    o.append('</g>')

    # print cursor: x sweeps each row, y steps down one row at a time
    cw = fs * ADVANCE
    ys = ";".join(f"{art_y + i * lh - fs * 0.82:.2f}" for i in range(rows))
    o.append(f'<rect width="{cw:.2f}" height="{fs:.2f}" fill="{t["cyan"]}" '
             f'x="{art_x:.1f}" y="{art_y - fs * 0.82:.2f}">'
             f'<animate attributeName="x" from="{art_x:.1f}" '
             f'to="{art_x + art_inner:.1f}" dur="{row_t:.3f}s" repeatCount="{rows}"/>'
             f'<animate attributeName="y" values="{ys}" calcMode="discrete" '
             f'dur="{SWEEP:.2f}s" fill="freeze"/>'
             f'<animate attributeName="opacity" values="1;1;0" keyTimes="0;.995;1" '
             f'dur="{SWEEP:.2f}s" fill="freeze"/>'
             '</rect>')

    o.append(f'<text x="{art_x}" y="{BAR + pane_h - 14}" font-family="{MONO}" '
             f'font-size="{HEAD_FS - 1}" letter-spacing="2" fill="{t["dim"]}">'
             f'SCAN 01 — ASCII {cols} × {rows}</text>')

    # ---------- info pane --------------------------------------------
    ix = PAD + ART_W + GAP
    o.append(f'<rect x="{ix}" y="{BAR}" width="{INFO_W}" height="{pane_h:.1f}" '
             f'rx="14" fill="{t["sub"]}" stroke="{t["line"]}"/>')
    tx = ix + PANE_PAD
    tw = INFO_W - PANE_PAD * 2
    o.append(f'<g font-family="{MONO}" font-size="{HEAD_FS}" letter-spacing="2.4">')
    o.append(f'<text x="{tx}" y="{BAR + PANE_PAD + 14}" fill="{t["cyan"]}">'
             f'SYSTEM.INFO <tspan fill="{t["dim"]}">/ STUDENT.BUILDER</tspan></text>')
    o.append('</g>')
    o.append(f'<line x1="{tx}" y1="{BAR + PANE_PAD + 26}" x2="{tx + tw}" '
             f'y2="{BAR + PANE_PAD + 26}" stroke="{t["line"]}"/>')

    body, y, n = [], BAR + PANE_PAD + 58, 0
    step = INFO_FS * 1.62

    def reveal(markup):
        nonlocal n
        # Staggered to land alongside the typing rather than after it.
        b = 0.25 + n * (SWEEP * 0.78) / 26
        n += 1
        return (f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" '
                f'begin="{b:.2f}s" dur=".45s" fill="freeze"/>{markup}</g>')

    body.append(reveal(
        f'<text x="{tx}" y="{y:.0f}" fill="{t["violet"]}" font-weight="600">'
        f'{esc(HANDLE)}<tspan fill="{t["mute"]}">@</tspan>'
        f'<tspan fill="{t["cyan"]}">github</tspan></text>'))
    y += step * 1.5

    for k, v in IDENTITY:
        body.append(reveal(leader_row(tx, y, tw, k, v, t, INFO_FS)))
        y += step

    for title, entries in SECTIONS:
        y += step * 0.55
        lw = len(title) * HEAD_FS * ADVANCE + 10
        body.append(reveal(
            f'<text x="{tx}" y="{y:.0f}" fill="{t["emerald"]}" '
            f'font-size="{HEAD_FS}" letter-spacing="2.2">{esc(title)}</text>'
            f'<line x1="{tx + lw:.0f}" y1="{y - 5:.0f}" x2="{tx + tw}" '
            f'y2="{y - 5:.0f}" stroke="{t["line2"]}"/>'))
        y += step * 0.95
        for k, v in entries:
            body.append(reveal(leader_row(tx, y, tw, k, v, t, INFO_FS)))
            y += step

    y += step * 0.6
    body.append(reveal(
        f'<text x="{tx}" y="{y:.0f}" fill="{t["dim"]}">signal.locked &gt; '
        f'<tspan fill="{t["cyan"]}">{esc(LOCK)}</tspan></text>'))

    o.append(f'<g font-family="{MONO}" font-size="{INFO_FS}">')
    o.extend(body)
    o.append('</g>')

    # ---------- chips + footer ---------------------------------------
    cx = PAD
    o.append(f'<g font-family="{MONO}" font-size="{HEAD_FS}" letter-spacing="2">')
    for i, label in enumerate(CHIPS):
        cwid = len(label) * HEAD_FS * ADVANCE + 30
        solid = i == len(CHIPS) - 1
        o.append(f'<rect x="{cx:.0f}" y="{chips_y:.0f}" width="{cwid:.0f}" height="30" '
                 f'rx="7" fill="{t["cyan"] if solid else "none"}" '
                 f'stroke="{t["line2"]}"/>')
        o.append(f'<text x="{cx + cwid/2:.0f}" y="{chips_y + 20:.0f}" '
                 f'text-anchor="middle" fill="{t["ground"] if solid else t["mute"]}">'
                 f'{esc(label)}</text>')
        cx += cwid + 10
    o.append(f'<text x="{W/2:.0f}" y="{H - 16:.0f}" text-anchor="middle" '
             f'fill="{t["dim"]}" font-size="{HEAD_FS - 2}" letter-spacing="3">'
             f'{esc(FOOTER)}</text>')
    o.append('</g>')

    head = (f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H:.0f}" '
            f'width="{W}" height="{H:.0f}" role="img" '
            f'aria-label="Profile card for {esc(USERNAME)}">')
    return head + "".join(o) + "</svg>"


if __name__ == "__main__":
    cols = int(sys.argv[1]) if len(sys.argv) > 1 else 240
    lines = asciify(Image.open(ROOT / "assets" / "source-portrait.png").convert("RGB"),
                    cols=cols, trim_bottom=0.80)
    for theme in THEMES:
        p = ROOT / f"card-{theme}.svg"
        p.write_text(build(lines, theme))
        print(f"{p.name}  {len(lines[0])}x{len(lines)}  {p.stat().st_size/1024:.0f} KB")
