"""Measure how much ink each candidate glyph puts down in the target font,
then pick a ramp whose steps are evenly spaced in coverage.

The hand-written ramp " .`:-=+*cs#%@" was ordered by eye. Several of its steps
sit almost on top of each other in real coverage, which wastes tonal range and
flattens the face.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT = "/System/Library/Fonts/Menlo.ttc"
SIZE = 48

# printable ASCII minus the ones that read as noise or punctuation artefacts
CANDIDATES = ("`^\"'~,._-:;!|/\\()[]{}<>*+=?rcvxzsnuiotjfl"
              "1234567890abdeghkmpqwyACDEFGHJKLOPQRSTUVXYZ"
              "IMNBW#$%&@")


def coverage():
    font = ImageFont.truetype(FONT, SIZE)
    adv = font.getbbox("M")[2]
    h = int(SIZE * 1.05)
    out = {}
    for ch in dict.fromkeys(CANDIDATES):
        im = Image.new("L", (adv, h), 0)
        ImageDraw.Draw(im).text((0, 0), ch, font=font, fill=255)
        out[ch] = np.asarray(im, dtype=np.float32).mean() / 255.0
    out[" "] = 0.0
    return out


def build(levels=24):
    cov = coverage()
    lo = 0.0
    hi = max(cov.values())
    ramp = []
    for i in range(levels):
        target = lo + (hi - lo) * (i / (levels - 1)) ** 0.95
        ch = min(cov, key=lambda c: abs(cov[c] - target))
        if not ramp or ch != ramp[-1]:
            ramp.append(ch)
        cov.pop(ch, None)                     # don't reuse a glyph
    return "".join(ramp)


if __name__ == "__main__":
    cov = coverage()
    top = sorted(cov.items(), key=lambda kv: kv[1])
    print("lightest:", "".join(c for c, _ in top[1:9]))
    print("darkest :", "".join(c for c, _ in top[-9:]))
    r = build()
    print(f"\nramp ({len(r)} steps): {r!r}")
    c2 = coverage()
    print("coverage:", [round(c2[c], 3) for c in r])
