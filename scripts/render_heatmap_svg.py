"""Contribution calendar as an SVG.

The whole year is drawn immediately. A soft gust then crosses it once, and
ambient streaks keep blowing afterwards so the card does not sit dead.

Nothing may hide a column. Browsers discard an offscreen image and rebuild it
from scratch on scroll-back, restarting every timeline in the file, and an
<img>-hosted SVG cannot tell that rebuild apart from a genuine page load. A
reveal-from-blank therefore replays its empty state every time you scroll past.
Drawing first and animating over the top makes the rebuild invisible.

Stdlib only — this is the one generator the scheduled workflow runs, and the
runner installs nothing.
"""
import json
from datetime import date, timedelta
from pathlib import Path

from theme import THEMES, MONO

ROOT = Path(__file__).resolve().parent.parent

W = 1800
PAD, PANE_PAD, BAR = 30, 24, 74
CELL, GAP, R = 26, 6, 6
COL = CELL + GAP
HEAD_FS, FOOT_FS = 13.0, 15.0
SWEEP = 1.1                     # seconds for the gust to cross the year

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def level(count, peak):
    """Scale to the account's own busiest day. GitHub's absolute thresholds
    flatten a low-volume year into a single shade."""
    if count <= 0:
        return 0
    return min(4, 1 + int(count / max(peak, 1) * 3.999))


def build(data, theme):
    t = THEMES[theme]
    days, peak = data["days"], data["best_day"]["count"]

    start = date.fromisoformat(min(days))
    start -= timedelta(days=(start.weekday() + 1) % 7)      # back to a Sunday
    end = date.fromisoformat(max(days))
    weeks = ((end - start).days // 7) + 1

    gx = PAD + PANE_PAD
    gy = BAR + PANE_PAD + 34 + 26                           # header + months
    grid_w = weeks * COL - GAP
    grid_h = 7 * COL - GAP
    pane_h = PANE_PAD * 2 + 34 + 26 + grid_h + 44
    H = BAR + pane_h + PAD

    col_t = SWEEP / weeks
    o = ['<defs>']
    o.append(f'<linearGradient id="edge" x1="0" y1="0" x2="{W}" y2="0" '
             f'gradientUnits="userSpaceOnUse">'
             f'<stop offset="0" stop-color="{t["violet"]}"/>'
             f'<stop offset=".5" stop-color="{t["cyan"]}"/>'
             f'<stop offset="1" stop-color="{t["emerald"]}"/>'
             f'<animateTransform attributeName="gradientTransform" type="translate" '
             f'values="0 0;{W*0.3:.0f} 0;0 0" dur="16s" repeatCount="indefinite"/>'
             '</linearGradient>')
    o.append(f'<linearGradient id="gust" x1="0" y1="0" x2="1" y2="0">'
             f'<stop offset="0" stop-color="{t["wind"]}" stop-opacity="0"/>'
             f'<stop offset=".5" stop-color="{t["wind"]}" stop-opacity=".30"/>'
             f'<stop offset="1" stop-color="{t["wind"]}" stop-opacity="0"/>'
             '</linearGradient>')
    o.append(f'<linearGradient id="streak" x1="0" y1="0" x2="1" y2="0">'
             f'<stop offset="0" stop-color="{t["wind"]}" stop-opacity="0"/>'
             f'<stop offset=".5" stop-color="{t["wind"]}" stop-opacity=".55"/>'
             f'<stop offset="1" stop-color="{t["wind"]}" stop-opacity="0"/>'
             '</linearGradient>')
    o.append('</defs>')

    o.append(f'<rect width="{W}" height="{H:.0f}" rx="20" fill="{t["ground"]}"/>')
    o.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2:.0f}" rx="19" '
             f'fill="{t["panel"]}" stroke="url(#edge)" stroke-width="2" '
             'stroke-opacity=".55"/>')

    o.append(f'<g font-family="{MONO}" font-size="{HEAD_FS + 3:.0f}">')
    o.append(f'<text x="{PAD + 6}" y="{PAD + 20}" fill="{t["ink"]}">'
             f'signal.map / 12 months</text>')
    o.append(f'<text x="{W - PAD - 6}" y="{PAD + 20}" text-anchor="end" '
             f'fill="{t["dim"]}">{data["total"]} events — '
             f'<tspan fill="{t["cyan"]}">$ ./scan --wind</tspan></text>')
    o.append('</g>')

    o.append(f'<rect x="{PAD}" y="{BAR}" width="{W - PAD*2}" height="{pane_h:.0f}" '
             f'rx="14" fill="{t["sub"]}" stroke="{t["line"]}"/>')
    o.append(f'<text x="{gx}" y="{BAR + PANE_PAD + 14}" font-family="{MONO}" '
             f'font-size="{HEAD_FS}" letter-spacing="2.4" fill="{t["cyan"]}">'
             f'CONTRIBUTION.GRID <tspan fill="{t["dim"]}">/ ACTIVITY.SIGNAL</tspan></text>')
    o.append(f'<line x1="{gx}" y1="{BAR + PANE_PAD + 26}" x2="{W - PAD - PANE_PAD}" '
             f'y2="{BAR + PANE_PAD + 26}" stroke="{t["line"]}"/>')

    seen = set()
    o.append(f'<g font-family="{MONO}" font-size="{HEAD_FS}" fill="{t["dim"]}">')
    for wk in range(weeks):
        d = start + timedelta(days=wk * 7)
        if d.day <= 7 and d.month not in seen:
            seen.add(d.month)
            o.append(f'<text x="{gx + wk*COL}" y="{gy - 10}">{MONTHS[d.month-1]}</text>')
    o.append('</g>')

    # cells — the curtain
    # One pair of animations per column, not per cell. The curtain's unit is
    # the column anyway, and animating all 371 cells individually meant 742
    # concurrent SMIL timelines for the browser to evaluate every frame.
    for wk in range(weeks):
        begin = wk * col_t
        cells = []
        for dow in range(7):
            d = start + timedelta(days=wk * 7 + dow)
            key = d.isoformat()
            if key not in days:
                continue
            x = gx + wk * COL
            y = gy + dow * COL
            lv = level(days[key], peak)
            cells.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                         f'rx="{R}" fill="{t["levels"][lv]}">'
                         f'<title>{days[key]} on {key}</title></rect>')
        if not cells:
            continue
        o.append('<g>' + "".join(cells) + '</g>')

    # gust locked to the reveal front
    o.append(f'<rect y="{gy - 20}" width="90" height="{grid_h + 40}" '
             f'fill="url(#gust)" x="{gx - 90}">'
             f'<animate attributeName="x" from="{gx - 90}" to="{gx + grid_w}" '
             f'dur="{SWEEP:.2f}s" fill="freeze"/>'
             f'<animate attributeName="opacity" values="1;1;0" keyTimes="0;.94;1" '
             f'dur="{SWEEP:.2f}s" fill="freeze"/>'
             '</rect>')

    # ambient streaks — keep blowing after the graph lands
    for top, wide, dur, delay in [
            (0.10, 300, 4.1, 0.0), (0.28, 460, 5.6, -1.4), (0.44, 240, 3.4, -2.6),
            (0.62, 520, 6.2, -0.7), (0.80, 330, 4.6, -3.1), (0.93, 400, 5.1, -2.0)]:
        y = gy + grid_h * top
        o.append(f'<rect x="{-wide}" y="{y:.0f}" width="{wide}" height="2" '
                 f'fill="url(#streak)" opacity=".5">'
                 f'<animate attributeName="x" from="{-wide}" to="{W}" '
                 f'dur="{dur}s" begin="{delay}s" repeatCount="indefinite"/>'
                 '</rect>')

    stats = (f'{data["total"]} contributions   ·   {data["current_streak"]} day streak'
             f'   ·   best {data["longest_streak"]}   ·   peak {peak} '
             f'on {data["best_day"]["date"]}')
    fy = gy + grid_h + 34
    o.append(f'<text x="{gx}" y="{fy}" font-family="{MONO}" font-size="{FOOT_FS}" '
             f'fill="{t["ink"]}">{stats}</text>')

    lx = W - PAD - PANE_PAD - (5 * COL + 90)
    o.append(f'<g font-family="{MONO}" font-size="{HEAD_FS}" fill="{t["dim"]}">')
    o.append(f'<text x="{lx - 8}" y="{fy}" text-anchor="end">Less</text>')
    for i, c in enumerate(t["levels"]):
        o.append(f'<rect x="{lx + i*COL}" y="{fy - 14}" width="{CELL}" '
                 f'height="{CELL}" rx="{R}" fill="{c}"/>')
    o.append(f'<text x="{lx + 5*COL + 6}" y="{fy}">More</text>')
    o.append('</g>')

    head = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H:.0f}" '
            f'width="{W}" height="{H:.0f}" role="img" '
            f'aria-label="{data["total"]} contributions in the last year">')
    return head + "".join(o) + "</svg>"


if __name__ == "__main__":
    data = json.loads((ROOT / "data" / "contributions.json").read_text())
    for theme in THEMES:
        p = ROOT / f"heatmap-{theme}.svg"
        p.write_text(build(data, theme))
        print(f"{p.name}  {p.stat().st_size/1024:.0f} KB")
