"""Single source of truth for everything the generated art says."""

USERNAME = "adityasinghin01-hash"
HANDLE = "aditya"
NAME = "Aditya Singh"

# Rendered as label ······· value. Keep values under ~34 characters; the info
# column is fixed width and longer strings collide with the leader dots.
IDENTITY = [
    ("Subject", NAME),
    ("Role",    "Student — building & shipping"),
    ("Base",    "Meerut, Uttar Pradesh, IN"),
    ("Status",  "Learning / Building / Shipping"),
]

SECTIONS = [
    ("STACK.NODE", [
        ("Lang",  "TypeScript, Python, JS"),
        ("Front", "React, Vite, Tailwind, GSAP"),
        ("Back",  "Node, Express, Firebase"),
        ("Also",  "Three.js, deck.gl, Flutter"),
    ]),
    ("BUILD.LOG", [
        ("NETRA",     "Crime analytics — KSP"),
        ("ShiftWise", "Conflict-free rosters"),
        ("Cert",      "AWS AI Practitioner"),
    ]),
    ("GRID.LINKS", [
        ("GitHub", "@" + USERNAME),
        ("X",      "@aditya_s0z"),
    ]),
]

LOCK = "AI / DATA / WEB"
CHIPS = ["⌂ GITHUB", USERNAME.upper(), "X", "LINKEDIN"]
FOOTER = "AI SYSTEMS / DATA PIPELINES / SHIPPED SOFTWARE"

SOCIALS = [
    ("GitHub",   f"https://github.com/{USERNAME}"),
    ("X",        "https://x.com/aditya_s0z"),
    ("LinkedIn", "https://www.linkedin.com/in/aditya-singh-aa365a386"),
]
