"""Single source of truth for everything the generated art says."""

USERNAME = "adityasinghin01-hash"
HANDLE = "aditya"
NAME = "Aditya Singh"

# Rendered as label ······· value. Keep values under ~34 characters; the info
# column is fixed width and longer strings collide with the leader dots.
IDENTITY = [
    ("Subject", NAME),
    ("Role",    "Backend developer · student"),
    ("Base",    "Meerut, Uttar Pradesh, IN"),
    ("Status",  "Open to internships"),
]

SECTIONS = [
    ("STACK.NODE", [
        ("Lang",  "Python, JavaScript, Java"),
        ("Back",  "Node, Express, REST, MongoDB"),
        ("Front", "React, Vite, Tailwind"),
        ("AI",    "Claude Code, Codex CLI"),
    ]),
    ("BUILD.LOG", [
        ("FuelPrint", "1st of 30 · IDEAVERSE"),
        ("tote",      "AI memory, any computer"),
        ("ShiftWise", "Scheduling backend"),
    ]),
    ("GRID.LINKS", [
        ("GitHub", "@" + USERNAME),
        ("X",      "@aditya_s0z"),
    ]),
]

LOCK = "BACKEND / AI / WEB"
CHIPS = ["⌂ GITHUB", USERNAME.upper(), "X", "LINKEDIN"]
FOOTER = "BACKEND / AI-ASSISTED / SHIPPED SOFTWARE"

SOCIALS = [
    ("GitHub",   f"https://github.com/{USERNAME}"),
    ("X",        "https://x.com/aditya_s0z"),
    ("LinkedIn", "https://www.linkedin.com/in/aditya-singh-aa365a386"),
]
