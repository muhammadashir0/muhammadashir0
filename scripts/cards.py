#!/usr/bin/env python3
"""
cards.py - render GitHub stat and repo cards as SVGs. Stdlib only.

Replaces github-readme-stats / github-profile-trophy / streak-stats, which are
shared public instances that go down (503), run out of quota (402) or time out.
These are files in your own repo, so they render as long as GitHub renders.

    python scripts/cards.py --user muhammadashir0 --out assets

Writes <out>/card-stats-{dark,light}.svg plus one card per repo listed in
assets/projects.json, as <out>/card-<repo>-{dark,light}.svg.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

UA = {"User-Agent": "cards.py"}

THEMES = {
    "dark": {
        "bg": "#0d1117", "border": "#30363d", "title": "#39d353",
        "text": "#c9d1d9", "muted": "#8b949e", "value": "#e6edf3",
        "accent": "#39d353",
    },
    "light": {
        "bg": "#ffffff", "border": "#d0d7de", "title": "#1a7f37",
        "text": "#1f2328", "muted": "#57606a", "value": "#1f2328",
        "accent": "#1a7f37",
    },
}

# GitHub linguist colours
LANG_COLOR = {
    "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "Python": "#3572A5",
    "HTML": "#e34c26", "CSS": "#563d7c", "C++": "#f34b7d", "C": "#555555",
    "Java": "#b07219", "Go": "#00ADD8", "Rust": "#dea584", "Shell": "#89e051",
    "PLpgSQL": "#336790", "Vue": "#41b883", "Ruby": "#701516", "PHP": "#4F5D95",
    "Jupyter Notebook": "#DA5B0B", "SCSS": "#c6538c", "Svelte": "#ff3e00",
}

FONT = "ui-sans-serif,-apple-system,Segoe UI,Helvetica,Arial,sans-serif"

# Octicon outlines
ICON_STAR = ("M8 .25a.75.75 0 01.673.418l1.882 3.815 4.21.612a.75.75 0 01.416 1.279l-3.046 "
             "2.97.719 4.192a.75.75 0 01-1.088.791L8 12.347l-3.766 1.98a.75.75 0 "
             "01-1.088-.79l.72-4.194L.818 6.374a.75.75 0 01.416-1.28l4.21-.611L7.327.668A.75.75 0 018 .25z")
ICON_FORK = ("M5 5.372v.878c0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75v-.878a2.25 2.25 0 "
             "111.5 0v.878a2.25 2.25 0 01-2.25 2.25h-1.5v2.128a2.251 2.251 0 11-1.5 "
             "0V8.5h-1.5A2.25 2.25 0 013.5 6.25v-.878a2.25 2.25 0 111.5 0zM5 3.25a.75.75 0 "
             "10-1.5 0 .75.75 0 001.5 0zm6.75.75a.75.75 0 100-1.5.75.75 0 000 1.5zm-3 "
             "8.75a.75.75 0 100-1.5.75.75 0 000 1.5z")
ICON_REPO = ("M2 2.5A2.5 2.5 0 014.5 0h8.75a.75.75 0 01.75.75v12.5a.75.75 0 01-.75.75h-2.5a.75.75 "
             "0 110-1.5h1.75v-2h-8a1 1 0 00-.714 1.7.75.75 0 01-1.072 1.05A2.495 2.495 0 012 "
             "11.5v-9zm10.5-1h-8a1 1 0 00-1 1v6.708A2.486 2.486 0 014.5 9h8V1.5zM5 12.25a.25.25 "
             "0 01.25-.25h7a.25.25 0 01.25.25v1.25a.25.25 0 01-.25.25h-7a.25.25 0 01-.25-.25v-1.25z")


def rest(path: str, token: str | None) -> dict | list:
    url = f"https://api.github.com{path}"
    headers = dict(UA)
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {}


def fetch_contributions(user: str, token: str | None) -> tuple[int, int, int] | None:
    """Fetch 1-year contribution counts and streaks via GraphQL."""
    if not token:
        return None
    query = """
    query($user: String!) {
      user(login: $user) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                contributionCount
                date
              }
            }
          }
        }
      }
    }
    """
    body = json.dumps({"query": query, "variables": {"user": user}}).encode("utf-8")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={**UA, "Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None

    try:
        cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    except (KeyError, TypeError):
        return None

    total = cal["totalContributions"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    days.sort(key=lambda d: d["date"])

    longest = cur = 0
    for d in days:
        if d["contributionCount"] > 0:
            cur += 1
            if cur > longest:
                longest = cur
        else:
            cur = 0

    current = 0
    for d in reversed(days):
        if d["contributionCount"] > 0:
            current += 1
        elif current > 0:
            break

    return total, current, longest


def icon(path_d: str, x: float, y: float, size: float, fill: str) -> str:
    scale = size / 16.0
    return (f'<g transform="translate({x:.2f},{y:.2f}) scale({scale:.4f})">'
            f'<path fill-rule="evenodd" fill="{fill}" d="{path_d}"/></g>')


def esc(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def text_width(s: str, size: float) -> float:
    return len(s) * size * 0.53


def wrap(text: str, size: float, max_w: float, max_lines: int) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if text_width(trial, size) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
            if len(lines) == max_lines:
                break
    if cur and len(lines) < max_lines:
        lines.append(cur)
    if len(lines) == max_lines and words:
        used = len(" ".join(lines).split())
        if used < len(words):
            while lines and text_width(lines[-1] + "…", size) > max_w:
                lines[-1] = lines[-1].rsplit(" ", 1)[0]
            lines[-1] += "…"
    return lines


def frame(w, h, c, body, label):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" role="img" aria-label="{esc(label)}" '
        f'font-family="{FONT}">'
        f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="10" '
        f'fill="{c["bg"]}" stroke="{c["border"]}"/>'
        f"{body}</svg>"
    )


def render_stats(user, stats, theme):
    c = THEMES[theme]
    pad = 22
    tiles = [(v, k) for k, v in stats]
    cols = 3
    rows = (len(tiles) + cols - 1) // cols
    rh, W = 46, 480
    H = pad + 52 + (rows - 1) * rh + 17 + pad
    tw = (W - 2 * pad) / cols

    out = [
        f'<text x="{pad}" y="{pad + 14}" font-size="15" font-weight="700" '
        f'fill="{c["title"]}">{esc(user)}</text>',
        f'<text x="{W - pad}" y="{pad + 14}" font-size="11" text-anchor="end" '
        f'fill="{c["muted"]}">at a glance</text>',
        f'<line x1="{pad}" y1="{pad + 26}" x2="{W - pad}" y2="{pad + 26}" '
        f'stroke="{c["border"]}"/>',
    ]
    top = pad + 52
    for i, (value, label) in enumerate(tiles):
        cx = pad + (i % cols) * tw
        cy = top + (i // cols) * rh
        out.append(
            f'<text x="{cx:.0f}" y="{cy:.0f}" font-size="23" font-weight="700" '
            f'fill="{c["value"]}">{esc(value)}</text>'
        )
        out.append(
            f'<text x="{cx:.0f}" y="{cy + 17:.0f}" font-size="10.5" '
            f'fill="{c["muted"]}">{esc(label)}</text>'
        )
    return frame(W, H, c, "".join(out), f"{user} GitHub statistics")


def render_repo(repo, theme):
    c = THEMES[theme]
    W, H = 420, 132
    pad = 18
    out = []

    out.append(icon(ICON_REPO, pad, pad, 15, c["muted"]))
    out.append(
        f'<text x="{pad + 22}" y="{pad + 12}" font-size="14.5" font-weight="700" '
        f'fill="{c["title"]}">{esc(repo["name"])}</text>'
    )

    desc = repo.get("description") or "No description yet."
    for i, line in enumerate(wrap(desc, 11.5, W - 2 * pad, 3)):
        out.append(
            f'<text x="{pad}" y="{pad + 36 + i * 16}" font-size="11.5" '
            f'fill="{c["text"]}">{esc(line)}</text>'
        )

    fy = H - pad - 2
    x = pad
    if repo.get("language"):
        col = LANG_COLOR.get(repo["language"], c["muted"])
        out.append(f'<circle cx="{x + 5}" cy="{fy - 4}" r="5" fill="{col}"/>')
        out.append(
            f'<text x="{x + 15}" y="{fy}" font-size="11" fill="{c["muted"]}">'
            f'{esc(repo["language"])}</text>'
        )
        x += 15 + text_width(repo["language"], 11) + 18

    for path, count in ((ICON_STAR, repo.get("stars", 0)),
                        (ICON_FORK, repo.get("forks", 0))):
        out.append(icon(path, x, fy - 11, 12, c["muted"]))
        out.append(
            f'<text x="{x + 17}" y="{fy}" font-size="11" fill="{c["muted"]}">'
            f'{count}</text>'
        )
        x += 17 + text_width(str(count), 11) + 18

    return frame(W, H, c, "".join(out), f'{repo["name"]} repository card')


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--user", required=True)
    p.add_argument("--out", type=Path, default=Path("assets"))
    p.add_argument("--projects", type=Path, default=Path("assets/projects.json"),
                   help="repos to render cards for, with description overrides")
    args = p.parse_args(argv)

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    args.out.mkdir(parents=True, exist_ok=True)

    user = rest(f"/users/{args.user}", token)
    if not isinstance(user, dict) or not user.get("login"):
        user = {"public_repos": 8, "followers": 0}

    repos = []
    page = 1
    while True:
        batch = rest(f"/users/{args.user}/repos?per_page=100&page={page}&type=owner", token)
        if not isinstance(batch, list) or not batch:
            break
        repos += batch
        if len(batch) < 100:
            break
        page += 1

    owned = [r for r in repos if not r.get("fork")]
    stars = sum(r.get("stargazers_count", 0) for r in owned)

    tiles = [("Total stars", f"{stars:,}"),
             ("Public repos", f"{user.get('public_repos', 8):,}"),
             ("Followers", f"{user.get('followers', 0):,}")]

    contrib = fetch_contributions(args.user, token)
    if contrib:
        total, current, longest = contrib
        tiles += [("Contributions (1y)", f"{total:,}"),
                  ("Current streak", f"{current:,}"),
                  ("Longest streak", f"{longest:,}")]
    else:
        print("  note: no usable token, skipping contribution tiles", file=sys.stderr)

    for theme in ("dark", "light"):
        dest = args.out / f"card-stats-{theme}.svg"
        dest.write_text(render_stats(args.user, tiles, theme), encoding="utf-8")
    print(f"wrote card-stats-*.svg  ({len(tiles)} tiles)")

    if not args.projects.exists():
        print(f"no {args.projects}, skipping repo cards")
        return

    wanted = json.loads(args.projects.read_text(encoding="utf-8"))["projects"]
    by_name = {r["name"].lower(): r for r in repos if "name" in r}

    for entry in wanted:
        src = by_name.get(entry["repo"].lower())
        if src:
            card = {
                "name": src["name"],
                "description": entry.get("description") or src.get("description"),
                "language": entry.get("language") or src.get("language") or "Python",
                "stars": src.get("stargazers_count", 0),
                "forks": src.get("forks_count", 0),
            }
        else:
            card = {
                "name": entry["repo"],
                "description": entry.get("description", ""),
                "language": entry.get("language", "Python"),
                "stars": entry.get("stars", 0),
                "forks": entry.get("forks", 0),
            }
        for theme in ("dark", "light"):
            dest = args.out / f"card-{card['name']}-{theme}.svg"
            dest.write_text(render_repo(card, theme), encoding="utf-8")
        print(f"wrote card-{card['name']}-*.svg  ({card['stars']}star {card['forks']}fork {card['language']})")


if __name__ == "__main__":
    main()
