"""Contribution calendar as an animated SVG, revealed on a diagonal wipe."""
import json
from datetime import date, timedelta
from pathlib import Path

from theme import THEMES, MONO

ROOT = Path(__file__).resolve().parent.parent
CELL, GAP, R = 11, 3, 2.5
PAD_L, PAD_T, PAD_B = 30, 34, 40

SCALES = {
    "dark":  ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"],
    "light": ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"],
}
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def level(count, peak):
    """Scale to the account's own busiest day. GitHub's absolute thresholds
    flatten a low-volume year into a single shade."""
    if count <= 0:
        return 0
    return min(4, 1 + int(count / max(peak, 1) * 3.999))


def build(data, theme):
    t, scale = THEMES[theme], SCALES[theme]
    fg = "#F8FAFC" if theme == "dark" else "#0F172A"
    mute = "#94A3B8" if theme == "dark" else "#475569"

    days = data["days"]
    peak = data["best_day"]["count"]
    start = date.fromisoformat(min(days))
    start -= timedelta(days=(start.weekday() + 1) % 7)      # back to a Sunday
    end = date.fromisoformat(max(days))
    weeks = ((end - start).days // 7) + 1

    w = PAD_L + weeks * (CELL + GAP) + 24
    h = PAD_T + 7 * (CELL + GAP) + PAD_B

    cells, labels, seen = [], [], set()
    for wk in range(weeks):
        for dow in range(7):
            d = start + timedelta(days=wk * 7 + dow)
            if d > end:
                continue
            key = d.isoformat()
            if key not in days:
                continue
            x = PAD_L + wk * (CELL + GAP)
            y = PAD_T + dow * (CELL + GAP)
            lv = level(days[key], peak)
            delay = 0.25 + (wk + dow) * 0.010                # diagonal wipe
            cells.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="{R}" '
                f'fill="{scale[lv]}" opacity="1">'
                f'<title>{days[key]} on {key}</title>'
                f'<animate attributeName="opacity" from="0" to="1" '
                f'begin="{delay:.2f}s" dur=".9s" fill="freeze" '
                f'calcMode="spline" keyTimes="0;1" keySplines=".25 .1 .25 1"/>'
                f'</rect>')
            if d.day <= 7 and d.month not in seen:
                seen.add(d.month)
                labels.append(f'<text x="{x}" y="{PAD_T-10}" fill="{mute}" '
                              f'font-size="10">{MONTHS[d.month-1]}</text>')

    legend_x = w - 24 - 5 * (CELL + GAP) - 34
    legend = [f'<text x="{legend_x-30}" y="{h-PAD_B+34}" fill="{mute}" font-size="10">Less</text>']
    for i, c in enumerate(scale):
        legend.append(f'<rect x="{legend_x + i*(CELL+GAP)}" y="{h-PAD_B+24}" '
                      f'width="{CELL}" height="{CELL}" rx="{R}" fill="{c}"/>')
    legend.append(f'<text x="{legend_x + 5*(CELL+GAP)+4}" y="{h-PAD_B+34}" '
                  f'fill="{mute}" font-size="10">More</text>')

    stats = (f'{data["total"]} contributions   ·   '
             f'{data["current_streak"]} day streak   ·   '
             f'best {data["longest_streak"]}   ·   '
             f'peak {peak} on {data["best_day"]["date"]}')

    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" role="img" '
        f'aria-label="{data["total"]} contributions in the last year">',
        "<defs>",
        f'<linearGradient id="edge" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{w}" y2="0">',
        f'<stop offset="0" stop-color="{t["g1"]}" stop-opacity=".45"/>',
        f'<stop offset=".5" stop-color="{t["g2"]}" stop-opacity=".45"/>',
        f'<stop offset="1" stop-color="{t["g3"]}" stop-opacity=".45"/>',
        '<animateTransform attributeName="gradientTransform" type="translate" '
        f'values="0 0; {w*0.4:.0f} 0; 0 0" dur="12s" repeatCount="indefinite"/>',
        "</linearGradient></defs>",
        f'<rect width="{w}" height="{h}" rx="14" fill="{t["panel"]}"/>',
        f'<rect x=".75" y=".75" width="{w-1.5}" height="{h-1.5}" rx="13.25" '
        f'fill="none" stroke="url(#edge)" stroke-width="1.5"/>',
        f'<g font-family="{MONO}">',
        *labels, *cells, *legend,
        f'<text x="{PAD_L}" y="{h-PAD_B+34}" fill="{fg}" font-size="11" opacity="1">{stats}'
        f'<animate attributeName="opacity" from="0" to="1" begin="1.5s" dur=".6s" fill="freeze"/>'
        "</text>",
        "</g></svg>",
    ])


if __name__ == "__main__":
    data = json.loads((ROOT / "data" / "contributions.json").read_text())
    for theme in THEMES:
        p = ROOT / f"heatmap-{theme}.svg"
        p.write_text(build(data, theme))
        print(f"{p.name}  {p.stat().st_size/1024:.1f} KB")
