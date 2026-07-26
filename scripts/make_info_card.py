"""Neofetch-style info card as an animated SVG, sized to sit beside the
ASCII portrait."""
from pathlib import Path
from xml.sax.saxutils import escape

from profile import NAME, USERNAME, INFO, HIGHLIGHTS, TAGLINE
from make_ascii_svg import THEMES, MONO

ROOT = Path(__file__).resolve().parent.parent
W, PAD, LH, FS = 560, 26, 21.0, 13.0


def build(theme):
    t = THEMES[theme]
    fg = "#F8FAFC" if theme == "dark" else "#0F172A"
    mute = "#94A3B8" if theme == "dark" else "#475569"

    body, y, i = [], PAD + 30, 0

    def line(parts, dy=LH, indent=0):
        """parts = [(text, colour, bold)] laid out left to right."""
        nonlocal y, i
        x = PAD + indent
        row = [f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" '
               f'begin="{0.18 + i * 0.055:.3f}s" dur=".34s" fill="freeze"/>']
        for text, col, bold in parts:
            wgt = ' font-weight="600"' if bold else ""
            row.append(f'<text xml:space="preserve" x="{x:.0f}" y="{y:.0f}" fill="{col}"{wgt}>'
                       f'{escape(text)}</text>')
            x += len(text) * (FS * 0.6)
        row.append("</g>")
        body.append("".join(row))
        y += dy
        i += 1

    line([(f"{NAME.lower().replace(' ', '')}", t["g2"], True),
          ("@", mute, False), (USERNAME, t["g1"], True)])
    line([("-" * 46, mute, False)], dy=LH * 1.1)

    for k, v in INFO:
        line([(f"{k:<6}", t["g3"], True), (v, fg, False)])

    y += 6
    line([("Highlights", t["g3"], True)])
    for h in HIGHLIGHTS:
        line([("  • ", t["g2"], False), (h, mute, False)], dy=LH * 0.95)

    y += 8
    line([("$ ", t["g2"], True), (TAGLINE, mute, False)])

    h = y + PAD
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h:.0f}" '
        f'width="{W}" height="{h:.0f}" role="img" aria-label="Profile info card">',
        "<defs>",
        f'<linearGradient id="edge" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="{h:.0f}">',
        f'<stop offset="0" stop-color="{t["g1"]}" stop-opacity=".5"/>',
        f'<stop offset=".5" stop-color="{t["g2"]}" stop-opacity=".5"/>',
        f'<stop offset="1" stop-color="{t["g3"]}" stop-opacity=".5"/>',
        '<animateTransform attributeName="gradientTransform" type="translate" '
        f'values="0 0; {W*0.4:.0f} 0; 0 0" dur="12s" repeatCount="indefinite"/>',
        "</linearGradient></defs>",
        f'<rect width="{W}" height="{h:.0f}" rx="14" fill="{t["panel"]}"/>',
        f'<rect x=".75" y=".75" width="{W-1.5}" height="{h-1.5:.0f}" rx="13.25" '
        f'fill="none" stroke="url(#edge)" stroke-width="1.5"/>',
        # window chrome
        f'<circle cx="{PAD+4}" cy="{PAD-4}" r="5" fill="#FF5F57"/>',
        f'<circle cx="{PAD+22}" cy="{PAD-4}" r="5" fill="#FEBC2E"/>',
        f'<circle cx="{PAD+40}" cy="{PAD-4}" r="5" fill="#28C840"/>',
        f'<g font-family="{MONO}" font-size="{FS}">',
        *body,
        "</g></svg>",
    ]
    return "\n".join(out)


if __name__ == "__main__":
    for theme in THEMES:
        p = ROOT / f"info-{theme}.svg"
        p.write_text(build(theme))
        print(f"{p.name}  {p.stat().st_size/1024:.1f} KB")
