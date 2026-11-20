#!/usr/bin/env python3
"""
animated_dividers.py - generate crisp, looping animated SVG motion dividers
for Muhammad Ashir's Proof Loop GitHub profile.
"""
from __future__ import annotations

import pathlib


def build_pulse_divider(filename: str, label: str, accent: str = "#39d353", secondary: str = "#58a6ff") -> str:
    w, h = 1280, 44
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{label}">
<defs>
  <linearGradient id="lineG" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{accent}" stop-opacity="0"/>
    <stop offset=".2" stop-color="{accent}" stop-opacity=".45"/>
    <stop offset=".5" stop-color="{secondary}" stop-opacity=".65"/>
    <stop offset=".8" stop-color="{accent}" stop-opacity=".45"/>
    <stop offset="1" stop-color="{accent}" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="cometG" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{accent}" stop-opacity="0"/>
    <stop offset=".7" stop-color="{accent}" stop-opacity=".85"/>
    <stop offset="1" stop-color="#ffffff" stop-opacity="1"/>
  </linearGradient>
  <filter id="gl" x="-20%" y="-80%" width="140%" height="260%">
    <feGaussianBlur stdDeviation="2.4" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
</defs>

<line x1="40" y1="22" x2="510" y2="22" stroke="url(#lineG)" stroke-width="1.2"/>
<line x1="770" y1="22" x2="1240" y2="22" stroke="url(#lineG)" stroke-width="1.2"/>

<!-- Sweeping left->right cryptographic packet -->
<rect y="20.6" width="110" height="2.8" rx="1.4" fill="url(#cometG)" filter="url(#gl)">
  <animate attributeName="x" values="40;400;40" dur="5.6s" repeatCount="indefinite"/>
  <animate attributeName="opacity" values="0;1;0" dur="5.6s" repeatCount="indefinite"/>
</rect>

<!-- Sweeping right->left cryptographic packet -->
<rect y="20.6" width="110" height="2.8" rx="1.4" fill="url(#cometG)" filter="url(#gl)">
  <animate attributeName="x" values="1130;770;1130" dur="5.6s" begin="2.8s" repeatCount="indefinite"/>
  <animate attributeName="opacity" values="0;1;0" dur="5.6s" begin="2.8s" repeatCount="indefinite"/>
</rect>

<!-- Center pill -->
<rect x="520" y="7" width="240" height="30" rx="15" fill="#09131a" stroke="{accent}" stroke-opacity=".42" stroke-width="1.2"/>
<circle cx="542" cy="22" r="3.8" fill="{accent}">
  <animate attributeName="opacity" values="1;.22;1" dur="1.5s" repeatCount="indefinite"/>
</circle>
<text x="648" y="26" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-weight="700" font-size="10.2" fill="#dce6ef" text-anchor="middle" letter-spacing="1.8">{label}</text>
</svg>
"""


def main() -> None:
    out = pathlib.Path("assets")
    out.mkdir(parents=True, exist_ok=True)
    specs = [
        ("pulse-loop.svg", "INFER · GUARD · ATTEST · SETTLE", "#39d353", "#58a6ff"),
        ("pulse-receipts.svg", "CRYPTOGRAPHIC RECEIPTS", "#2fd48a", "#39d353"),
        ("pulse-channel.svg", "VERIFIED OPERATOR CHANNEL", "#58a6ff", "#39d353"),
    ]
    for fn, lbl, c1, c2 in specs:
        p = out / fn
        p.write_text(build_pulse_divider(fn, lbl, c1, c2), encoding="utf-8")
        print(f"wrote {p}")


if __name__ == "__main__":
    main()
