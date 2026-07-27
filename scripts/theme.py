"""Palette and grid constants shared by every generator.

Kept free of third-party imports on purpose: the scheduled workflow only runs
the heatmap, which is stdlib-only, and pulling these from the portrait module
dragged Pillow into that path and failed every run with ModuleNotFoundError.
"""

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace"
ADVANCE = 0.6                    # monospace advance as a fraction of font-size
LINE = 1.05                      # line height as a fraction of font-size

THEMES = {
    "dark": dict(
        ground="#04070F", panel="#0A1120", sub="#070D19",
        line="rgba(150,180,235,.12)", line2="rgba(150,180,235,.22)",
        ink="#E8EEF9", mute="#8A9BB8", dim="#5C6D8A",
        violet="#7C3AED", cyan="#22D3EE", emerald="#10B981",
        wind="#9BE8FF",
        # portrait ramp: indigo -> cyan -> sky. A violet-to-emerald spread over
        # 140+ rows reads as a rainbow rather than as one portrait.
        ramp=((109, 120, 245), (34, 211, 238), (96, 205, 255)),
        levels=("#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"),
    ),
    "light": dict(
        ground="#FFFFFF", panel="#F6F9FD", sub="#FBFDFF",
        line="rgba(15,32,64,.10)", line2="rgba(15,32,64,.18)",
        ink="#0B1220", mute="#5A6B85", dim="#8496AE",
        violet="#2563EB", cyan="#0891B2", emerald="#059669",
        wind="#0EA5E9",
        ramp=((49, 86, 220), (8, 145, 178), (14, 150, 210)),
        levels=("#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"),
    ),
}


def ramp_color(stops, t):
    """Sample the three-stop portrait ramp at t in [0, 1]."""
    a, b = (stops[0], stops[1]) if t < 0.55 else (stops[1], stops[2])
    u = t / 0.55 if t < 0.55 else (t - 0.55) / 0.45
    return "rgb(%d,%d,%d)" % tuple(round(a[i] + (b[i] - a[i]) * u) for i in range(3))
