"""Scrape the public contributions calendar. No token, no API quota — GitHub
serves this fragment as plain HTML to anonymous callers."""
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.request import Request, urlopen

from profile import USERNAME

ROOT = Path(__file__).resolve().parent.parent
URL = f"https://github.com/users/{USERNAME}/contributions"


def fetch():
    req = Request(URL, headers={"User-Agent": "profile-art/1.0 (+github actions)"})
    with urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def parse(html):
    """Pull (date, count) out of the calendar.

    GitHub dropped `data-count` from the <td>s — only `data-level` (0-4) is
    left there, and using that as a count undercounts badly (545 -> 85). The
    real numbers now live in the <tool-tip> text keyed to each cell's id.
    """
    ids = dict(re.findall(
        r'<td[^>]*data-date="(\d{4}-\d{2}-\d{2})"[^>]*id="([^"]+)"', html))
    if not ids:                                   # attribute order flipped
        ids = {d: i for i, d in re.findall(
            r'<td[^>]*id="([^"]+)"[^>]*data-date="(\d{4}-\d{2}-\d{2})"', html)}
    by_id = {v: k for k, v in ids.items()}

    days = {d: 0 for d in ids}
    for tip_for, text in re.findall(
            r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>', html):
        d = by_id.get(tip_for)
        if d is None:
            continue
        m = re.match(r"\s*(No|[\d,]+)\s+contribution", text)
        if m:
            days[d] = 0 if m.group(1) == "No" else int(m.group(1).replace(",", ""))
    return days


def streaks(days):
    cur = best = 0
    for d in sorted(days):
        if days[d] > 0:
            cur += 1
            best = max(best, cur)
        else:
            cur = 0
    # a blank today shouldn't break a streak that is still live
    tail = 0
    for d in sorted(days, reverse=True):
        if days[d] > 0:
            tail += 1
        elif tail or d != max(days):
            break
    return tail, best


if __name__ == "__main__":
    days = parse(fetch())
    if not days:
        sys.exit("no contribution cells found — GitHub markup may have changed")
    cur, best = streaks(days)
    total = sum(days.values())
    peak = max(days, key=days.get)
    out = {
        "user": USERNAME,
        "generated": date.today().isoformat(),
        "days": days,
        "total": total,
        "current_streak": cur,
        "longest_streak": best,
        "best_day": {"date": peak, "count": days[peak]},
    }
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data" / "contributions.json").write_text(json.dumps(out, indent=1))
    print(f"{len(days)} days, {total} contributions, "
          f"streak {cur} (best {best}), peak {days[peak]} on {peak}")
