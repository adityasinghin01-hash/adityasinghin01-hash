"""Palette and grid constants shared by every generator.

Kept free of third-party imports on purpose: the scheduled workflow only runs
the heatmap, which is stdlib-only, and pulling these from make_ascii_svg.py
dragged Pillow into that path and failed every run with ModuleNotFoundError.
"""

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace"
ADV, LH, FS = 8.4, 14.7, 14.0          # advance, line height, font size
PAD = 22

THEMES = {
    "dark":  dict(bg="#030712", panel="#0F172A", stroke="rgba(255,255,255,.08)",
                  g1="#7C3AED", g2="#22D3EE", g3="#10B981", glow=".55", scan=".07"),
    "light": dict(bg="#FFFFFF", panel="#F8FAFC", stroke="rgba(15,23,42,.08)",
                  g1="#2563EB", g2="#06B6D4", g3="#10B981", glow=".28", scan=".05"),
}
