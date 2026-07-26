"""Photo -> ASCII character grid.

Expects a studio portrait on a white seamless background. The background is
keyed out by a border-connected flood fill, then CLAHE runs *inside the
subject mask only* so the face gets the whole tonal range to itself.

Luminance maps to glyph density (bright -> '@'), which is the correct polarity
for light text glowing on a dark terminal. The ink-on-paper polarity renders a
hollow face and is only kept here for reference.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# Ordered by measured ink coverage of each glyph in Menlo (see build_ramp.py),
# not by eye. The old hand-picked ramp had steps sitting nearly on top of each
# other in real coverage, which wasted tonal range and flattened the face.
RAMP = " _`.,:~;+=vt1IV5$UHRWB0N"
CELL_RATIO = 8.4 / 14.7         # advance / line height, matches the SVG grid


def subject_mask(gray, thresh=228):
    """True where the subject is. Near-white pixels reachable from the border
    are background."""
    # .copy() matters: fromarray aliases the numpy buffer, and PIL's in-place
    # floodfill is then invisible to np.array() on the way back out.
    binary = Image.fromarray(((gray >= thresh) * 255).astype(np.uint8)).copy()
    h, w = gray.shape
    px = binary.load()
    # Seed only from border pixels that are still white. Seeding corners blindly
    # backfires the moment a crop puts dark clothing in one, and walking the
    # border also catches background regions the shoulders cut in two.
    border = ([(x, 0) for x in range(0, w, 4)] + [(x, h - 1) for x in range(0, w, 4)]
              + [(0, y) for y in range(0, h, 4)] + [(w - 1, y) for y in range(0, h, 4)])
    for seed in border:
        if px[seed] == 255:
            ImageDraw.floodfill(binary, seed, 128, thresh=10)
    return np.array(binary) != 128


def clahe(a, mask, tiles=8, clip=2.5):
    """CLAHE built from masked pixels only, so the blown-out background can't
    flatten the subject's histogram."""
    h, w = a.shape
    th, tw = max(h // tiles, 1), max(w // tiles, 1)
    out = np.zeros_like(a, dtype=np.float32)
    maps = np.zeros((tiles, tiles, 256), dtype=np.float32)
    for ty in range(tiles):
        for tx in range(tiles):
            sl = (slice(ty * th, (ty + 1) * th), slice(tx * tw, (tx + 1) * tw))
            vals = a[sl][mask[sl]]
            if vals.size < 32:                       # tile is ~all background
                maps[ty, tx] = np.arange(256, dtype=np.float32)
                continue
            hist = np.bincount(vals, minlength=256).astype(np.float32)
            limit = clip * vals.size / 256.0
            excess = np.maximum(hist - limit, 0).sum()
            hist = np.minimum(hist, limit) + excess / 256.0
            maps[ty, tx] = np.cumsum(hist) / vals.size * 255.0
    ys = np.clip((np.arange(h) / th) - 0.5, 0, tiles - 1)
    xs = np.clip((np.arange(w) / tw) - 0.5, 0, tiles - 1)
    y0, x0 = ys.astype(int), xs.astype(int)
    y1, x1 = np.minimum(y0 + 1, tiles - 1), np.minimum(x0 + 1, tiles - 1)
    fy, fx = (ys - y0)[:, None], (xs - x0)[None, :]
    for yy, xx, wgt in ((y0, x0, (1 - fy) * (1 - fx)), (y0, x1, (1 - fy) * fx),
                        (y1, x0, fy * (1 - fx)), (y1, x1, fy * fx)):
        out += maps[yy[:, None], xx[None, :], a] * wgt
    return np.clip(out, 0, 255).astype(np.uint8)


def autocrop(img, mask, pad=24):
    ys, xs = np.where(mask)
    w, h = img.size
    return img.crop((max(xs.min() - pad, 0), max(ys.min() - pad, 0),
                     min(xs.max() + pad, w), min(ys.max() + pad, h)))


def asciify(img, cols=150, gamma=0.9, sharp=1.7, trim_bottom=0.80):
    """Returns a list of equal-length strings."""
    if trim_bottom < 1.0:                            # drop generator watermark
        w, h = img.size
        img = img.crop((0, 0, w, int(h * trim_bottom)))

    gray = np.asarray(img.convert("L"))
    mask = subject_mask(gray)
    img = autocrop(img, mask)
    gray = np.asarray(img.convert("L"))
    mask = subject_mask(gray)

    eq = clahe(gray, mask)
    vals = eq[mask]
    lo, hi = np.percentile(vals, 1), np.percentile(vals, 99)
    norm = np.clip((eq.astype(np.float32) - lo) / max(hi - lo, 1), 0, 1)
    norm = np.power(norm, gamma)
    norm[~mask] = 0.0

    h, w = gray.shape
    rows = max(int(cols * (h / w) * CELL_RATIO), 1)

    src = Image.fromarray((norm * 255).astype(np.uint8))
    # Sharpen before the reduction: whatever survives to a 150-wide grid has to
    # be exaggerated first, or area-averaging swallows the eyes and mouth.
    if sharp:
        src = src.filter(ImageFilter.UnsharpMask(radius=max(w // cols, 2),
                                                 percent=int(sharp * 100),
                                                 threshold=2))
    small = np.asarray(src.resize((cols, rows), Image.LANCZOS)) / 255.0
    cov = np.asarray(Image.fromarray((mask * 255).astype(np.uint8))
                     .resize((cols, rows), Image.LANCZOS)) / 255.0

    # Re-stretch after resampling — the reduction compresses contrast, and the
    # ramp needs the full range to use all 24 steps.
    inside = small[cov >= 0.5]
    if inside.size:
        a, b = np.percentile(inside, 2), np.percentile(inside, 98)
        small = np.clip((small - a) / max(b - a, 1e-3), 0, 1)

    idx = np.clip((small * (len(RAMP) - 1)).round().astype(int), 0, len(RAMP) - 1)
    idx[cov < 0.30] = 0                              # outside the silhouette
    return ["".join(RAMP[i] for i in row) for row in idx]
