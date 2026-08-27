#!/usr/bin/env python3
"""
radar.py - render a spider / radar chart as a standalone SVG. Stdlib only.

Two sources of data:

  1. a JSON file you control (default)
        python scripts/radar.py --data assets/skills.json -o assets/radar

  2. live language stats from the GitHub API (with optional fallback)
        python scripts/radar.py --github YOUR_USERNAME --fallback assets/languages.json -o assets/radar-langs

Writes <out>-dark.svg and <out>-light.svg so the README can swap them with
<picture> + prefers-color-scheme.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

THEMES = {
    "dark": {
        "grid": "#30363d",
        "spoke": "#21262d",
        "label": "#c9d1d9",
        "value": "#8b949e",
        "title": "#e6edf3",
        "fill": "#39d353",
        "stroke": "#3fb950",
        "vertex": "#7ee787",
        "bg": "none",
    },
    "light": {
        "grid": "#d0d7de",
        "spoke": "#e6eaef",
        "label": "#1f2328",
        "value": "#57606a",
        "title": "#1f2328",
        "fill": "#2da44e",
        "stroke": "#1a7f37",
        "vertex": "#116329",
        "bg": "none",
    },
}

UA = {"User-Agent": "radar.py"}


# --------------------------------------------------------------------------- #
# data sources
# --------------------------------------------------------------------------- #


def _api(url: str, token: str | None) -> dict | list:
    headers = dict(UA)
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def from_json(path: Path) -> tuple[str, list[tuple[str, float]]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    title = raw.get("title", path.stem)
    axes = [(item["label"], float(item["value"])) for item in raw["axes"]]
    return title, axes


def from_github(user: str, token: str | None, limit: int, exclude: set[str],
                curve: float):
    """Sum language bytes across the user's non-fork public repos."""
    totals: dict[str, int] = {}
    page = 1
    while True:
        repos = _api(
            f"https://api.github.com/users/{user}/repos"
            f"?per_page=100&page={page}&type=owner&sort=pushed",
            token,
        )
        if not repos:
            break
        for repo in repos:
            if repo.get("fork") or repo.get("archived"):
                continue
            try:
                langs = _api(repo["languages_url"], token)
            except urllib.error.HTTPError:
                continue
            for name, count in langs.items():
                if name.lower() in exclude:
                    continue
                totals[name] = totals.get(name, 0) + count
        if len(repos) < 100:
            break
        page += 1

    if not totals:
        raise ValueError(f"no language data found for '{user}'")

    top = sorted(totals.items(), key=lambda kv: -kv[1])[:limit]
    peak = top[0][1]
    axes = [(n, round(100 * (c / peak) ** curve, 1)) for n, c in top]
    return f"{user} · language mix", axes


# --------------------------------------------------------------------------- #
# rendering
# --------------------------------------------------------------------------- #


FONT = "ui-sans-serif,-apple-system,Segoe UI,Helvetica,Arial,sans-serif"
LBL, VAL, TTL = 13, 11, 15  # font sizes: axis label, axis value, title


def ring(radius, n, start=-math.pi / 2):
    return [
        (radius * math.cos(start + i * 2 * math.pi / n),
         radius * math.sin(start + i * 2 * math.pi / n))
        for i in range(n)
    ]


def text_width(s, font_size):
    return len(s) * font_size * 0.62


def render(title, axes, theme, size=440, rings=4, show_values=False,
           animate=True):
    c = THEMES[theme]
    n = len(axes)
    max_radius = size * 0.35
    cx = cy = size / 2

    # Measure labels
    widths = [text_width(lbl, LBL) for lbl, _ in axes]
    max_w = max(widths) if widths else 0
    inset = max(max_w + 16, 44)
    max_radius = (size / 2) - inset

    outer = ring(max_radius, n)

    poly = [
        (cx + max_radius * (v / 100) * math.cos(-math.pi / 2 + i * 2 * math.pi / n),
         cy + max_radius * (v / 100) * math.sin(-math.pi / 2 + i * 2 * math.pi / n))
        for i, (_, v) in enumerate(axes)
    ]
    center_poly = [(cx, cy) for _ in axes]
    data_points = " ".join(f"{x:.1f},{y:.1f}" for x, y in poly)
    center_points = " ".join(f"{x:.1f},{y:.1f}" for x, y in center_poly)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
        f'width="{size}" height="{size}" role="img" aria-label="{esc(title)}" '
        f'font-family="{FONT}">'
    ]

    parts.append("<style>")
    if c["bg"] != "none":
        parts.append(f"svg {{ background: {c['bg']}; }}")
    parts.append(".grid { fill: none; stroke-width: 1; }")
    parts.append(".spoke { stroke-width: 1; }")
    parts.append(".data-fill { fill-opacity: 0.22; }")
    parts.append(".data-stroke { fill: none; stroke-width: 2; }")
    parts.append(".vertex { stroke-width: 2; }")
    parts.append("</style>")

    if title:
        parts.append(
            f'<text x="{cx}" y="{TTL + 6}" text-anchor="middle" font-size="{TTL}" '
            f'font-weight="700" fill="{c["title"]}">{esc(title)}</text>'
        )

    parts.append(f'<g transform="translate(0, 0)">')

    for r_idx in range(1, rings + 1):
        frac = r_idx / rings
        pts = " ".join(f"{cx + x:.1f},{cy + y:.1f}"
                       for x, y in ring(max_radius * frac, n))
        stroke = c["grid"] if r_idx == rings else c["spoke"]
        parts.append(f'<polygon points="{pts}" class="grid" stroke="{stroke}"/>')

    for x, y in outer:
        parts.append(f'<line x1="{cx}" y1="{cy}" x2="{cx + x:.1f}" y2="{cy + y:.1f}" '
                     f'class="spoke" stroke="{c["spoke"]}"/>')

    if animate:
        parts.append(
            f'<polygon class="data-fill" fill="{c["fill"]}">'
            f'<animate attributeName="points" dur="0.9s" fill="freeze" '
            f'calcMode="spline" keyTimes="0;1" keySplines="0.16 1 0.3 1" '
            f'from="{center_points}" to="{data_points}"/>'
            f'</polygon>'
            f'<polygon points="{data_points}" class="data-stroke" stroke="{c["stroke"]}">'
            f'<animate attributeName="points" dur="0.9s" fill="freeze" '
            f'calcMode="spline" keyTimes="0;1" keySplines="0.16 1 0.3 1" '
            f'from="{center_points}" to="{data_points}"/>'
            f'</polygon>'
        )
    else:
        parts.append(
            f'<polygon points="{data_points}" class="data-fill" fill="{c["fill"]}"/>'
            f'<polygon points="{data_points}" class="data-stroke" stroke="{c["stroke"]}"/>'
        )

    for x, y in poly:
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" class="vertex" '
                     f'fill="{c["fill"]}" stroke="{c["vertex"]}"/>')

    pad = 12
    for i, (lbl, v) in enumerate(axes):
        angle = -math.pi / 2 + i * 2 * math.pi / n
        lx = cx + (max_radius + pad) * math.cos(angle)
        ly = cy + (max_radius + pad) * math.sin(angle)

        ca = math.cos(angle)
        if abs(ca) < 0.15:
            anchor = "middle"
        elif ca > 0:
            anchor = "start"
        else:
            anchor = "end"

        sa = math.sin(angle)
        if abs(sa) < 0.2:
            dy = LBL * 0.35
        elif sa > 0:
            dy = LBL * 0.8
        else:
            dy = 0

        parts.append(
            f'<text x="{lx:.1f}" y="{ly + dy:.1f}" text-anchor="{anchor}" '
            f'font-size="{LBL}" font-weight="600" fill="{c["label"]}">{esc(lbl)}</text>'
        )
        if show_values:
            parts.append(
                f'<text x="{lx:.1f}" y="{ly + dy + VAL + 4:.1f}" text-anchor="{anchor}" '
                f'font-size="{VAL}" fill="{c["value"]}">{v:g}</text>'
            )

    parts.append("</g></svg>")
    return "".join(parts)


def esc(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    src = p.add_mutually_exclusive_group()
    src.add_argument("--data", type=Path, default=Path("assets/skills.json"))
    src.add_argument("--github", metavar="USER",
                     help="build the radar from GitHub language stats instead")
    p.add_argument("-o", "--out", type=Path, default=Path("assets/radar"),
                   help="output path WITHOUT extension")
    p.add_argument("--fallback", type=Path, default=Path("assets/languages.json"),
                   help="fallback json if github has fewer than 3 languages")
    p.add_argument("--title", help="override the chart title ('' for none)")
    p.add_argument("--size", type=int, default=440)
    p.add_argument("--rings", type=int, default=4)
    p.add_argument("--limit", type=int, default=7,
                   help="max axes when using --github")
    p.add_argument("--exclude", default="html,css,shell,makefile,dockerfile,batchfile",
                   help="comma-separated languages to skip in --github mode")
    p.add_argument("--curve", type=float, default=0.5,
                   help="--github axis scaling: 1.0 linear, 0.5 sqrt (default), "
                        "0.3 flattens a one-language-dominant profile")
    p.add_argument("--values", action="store_true", help="print the number per axis")
    p.add_argument("--no-animate", dest="animate", action="store_false",
                   help="disable the grow-in animation")
    args = p.parse_args(argv)

    if args.github:
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        excl = {s.strip().lower() for s in args.exclude.split(",") if s.strip()}
        try:
            title, axes = from_github(args.github, token, args.limit, excl, args.curve)
            if len(axes) < 3:
                if args.fallback and args.fallback.exists():
                    print(f"GitHub languages < 3, falling back to {args.fallback}", file=sys.stderr)
                    title, axes = from_json(args.fallback)
                else:
                    sys.exit("a radar chart needs at least 3 axes")
        except Exception as e:
            if args.fallback and args.fallback.exists():
                print(f"GitHub fetch failed ({e}), falling back to {args.fallback}", file=sys.stderr)
                title, axes = from_json(args.fallback)
            else:
                sys.exit(f"failed to load data: {e}")
    else:
        if not args.data.exists():
            sys.exit(f"no data file: {args.data}")
        title, axes = from_json(args.data)

    if args.title is not None:
        title = args.title
    if len(axes) < 3:
        sys.exit("a radar chart needs at least 3 axes")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    for theme in ("dark", "light"):
        svg = render(title, axes, theme, args.size, args.rings, args.values,
                     args.animate)
        dest = args.out.with_name(f"{args.out.name}-{theme}.svg")
        dest.write_text(svg, encoding="utf-8")
        print(f"wrote {dest}  ({len(axes)} axes)")


if __name__ == "__main__":
    main()
