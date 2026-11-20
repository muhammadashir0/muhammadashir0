#!/usr/bin/env python3
"""
animated_scenes.py - build living, animated SVG profile scenes around the
signature cartoon portraits of Muhammad Ashir.

Why SVG instead of flat PNG?
  - Real CSS + SMIL motion directly inside GitHub's README image sandbox
    (no JavaScript required, works on github.com + mobile + preview).
  - Embedded Space Grotesk + JetBrains Mono WOFF2 fonts so typography is sharp
    editorial display type on every OS.
  - Embedded WebP/PNG-quantized signature portraits of Muhammad Ashir with
    multi-pose looping reels, floating parallax, swinging lanyard physics,
    sweeping holographic foil, volumetric torch beam, and staggered brand chips.

Usage:
    pip install pillow
    python scripts/animated_scenes.py --github muhammadashir0 --out assets
"""

from __future__ import annotations

import argparse
import base64
import html
import io
import json
import math
import os
import pathlib
import sys
import urllib.error
import urllib.request


try:
    from PIL import Image
except ImportError:
    Image = None  # type: ignore


def esc(val: object) -> str:
    return html.escape(str(val), quote=True)


def encode_character(path: pathlib.Path, max_side: int = 500, fallback_uri: str = "") -> str:
    """Resize & quantize RGBA character portrait with Floyd-Steinberg dithering to universal PNG data URI."""
    if Image is None:
        if fallback_uri:
            return fallback_uri
        raise RuntimeError("Pillow not installed and no pre-encoded character found in svg_bundle.json")
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    if max(w, h) > max_side:
        scale = max_side / float(max(w, h))
        im = im.resize((int(round(w * scale)), int(round(h * scale))), Image.LANCZOS)

    # Composite RGB on dark card tone (#081118) where alpha>0 before RGB quantization, then reattach exact alpha
    alpha = im.getchannel("A")
    rgb_bg = Image.new("RGBA", im.size, (8, 17, 24, 255))
    rgb_comp = Image.alpha_composite(rgb_bg, im).convert("RGB")
    pal = rgb_comp.quantize(colors=256, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG).convert("RGBA")
    pal.putalpha(alpha)

    buf = io.BytesIO()
    pal.save(buf, "PNG", optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def font_defs(bundle: dict) -> str:
    f = bundle["fonts"]
    return f"""
@font-face{{font-family:'SG';src:url(data:font/woff2;base64,{f['SG']}) format('woff2');font-weight:700;font-style:normal}}
@font-face{{font-family:'SGM';src:url(data:font/woff2;base64,{f['SGM']}) format('woff2');font-weight:500;font-style:normal}}
@font-face{{font-family:'JBM';src:url(data:font/woff2;base64,{f['JBM']}) format('woff2');font-weight:400;font-style:normal}}
@font-face{{font-family:'JBMB';src:url(data:font/woff2;base64,{f['JBMB']}) format('woff2');font-weight:700;font-style:normal}}
text{{font-family:'JBM',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}
.sg{{font-family:'SG','Space Grotesk','Segoe UI',Helvetica,Arial,sans-serif;font-weight:700}}
.sgm{{font-family:'SGM','Space Grotesk','Segoe UI',Helvetica,Arial,sans-serif;font-weight:500}}
.jb{{font-family:'JBM','JetBrains Mono',ui-monospace,Menlo,Consolas,monospace}}
.jbb{{font-family:'JBMB','JetBrains Mono',ui-monospace,Menlo,Consolas,monospace;font-weight:700}}
@keyframes fadeUp{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:translateY(0)}}}}
@keyframes fadeIn{{from{{opacity:0}}to{{opacity:1}}}}
@keyframes fadeL{{from{{opacity:0;transform:translateX(-16px)}}to{{opacity:1;transform:translateX(0)}}}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
@keyframes spinRev{{to{{transform:rotate(-360deg)}}}}
@keyframes floatY{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-8px)}}}}
@keyframes pulseGlow{{0%,100%{{opacity:.38}}50%{{opacity:.82}}}}
@keyframes blink{{0%,49%{{opacity:1}}50%,100%{{opacity:0}}}}
.fu{{animation:fadeUp .72s cubic-bezier(.2,.8,.2,1) both}}
.fi{{animation:fadeIn .75s ease both}}
.fl{{animation:fadeL .72s cubic-bezier(.2,.8,.2,1) both}}
.flt{{animation:floatY 6.8s ease-in-out infinite}}
.spin{{transform-box:fill-box;transform-origin:center;animation:spin 16s linear infinite}}
.spin2{{transform-box:fill-box;transform-origin:center;animation:spinRev 24s linear infinite}}
.blink{{animation:blink 1.05s step-end infinite}}
@media (prefers-reduced-motion:reduce){{
  *,*::before,*::after{{animation:none!important;transition:none!important}}
}}
""".strip()


def hex_points(cx: float, cy: float, r: float) -> str:
    pts = []
    for i in range(6):
        ang = math.pi / 3.0 * i - math.pi / 2.0
        pts.append(f"{cx + r * math.cos(ang):.1f},{cy + r * math.sin(ang):.1f}")
    return " ".join(pts)


def common_shell_defs(prefix: str, w: int, h: int) -> str:
    return f"""
<linearGradient id="{prefix}bg" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#070d12"/>
  <stop offset=".52" stop-color="#0a131b"/>
  <stop offset="1" stop-color="#060b10"/>
</linearGradient>
<linearGradient id="{prefix}edge" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#39d353" stop-opacity=".62"/>
  <stop offset=".48" stop-color="#1f333d" stop-opacity=".85"/>
  <stop offset="1" stop-color="#58a6ff" stop-opacity=".55"/>
</linearGradient>
<linearGradient id="{prefix}bar" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#39d353"/>
  <stop offset=".55" stop-color="#2fd48a"/>
  <stop offset="1" stop-color="#58a6ff"/>
</linearGradient>
<radialGradient id="{prefix}emerald" cx="50%" cy="50%" r="50%">
  <stop offset="0" stop-color="#39d353" stop-opacity=".30"/>
  <stop offset=".55" stop-color="#2fd48a" stop-opacity=".09"/>
  <stop offset="1" stop-color="#39d353" stop-opacity="0"/>
</radialGradient>
<radialGradient id="{prefix}cyan" cx="50%" cy="50%" r="50%">
  <stop offset="0" stop-color="#58a6ff" stop-opacity=".22"/>
  <stop offset="1" stop-color="#58a6ff" stop-opacity="0"/>
</radialGradient>
<pattern id="{prefix}grid" width="28" height="28" patternUnits="userSpaceOnUse">
  <path d="M 28 0 L 0 0 0 28" fill="none" stroke="#39d353" stroke-opacity=".055" stroke-width="1"/>
  <circle cx="14" cy="14" r=".85" fill="#e6edf3" fill-opacity=".06"/>
</pattern>
<filter id="{prefix}glow" x="-25%" y="-25%" width="150%" height="150%">
  <feGaussianBlur stdDeviation="3" result="b"/>
  <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
<filter id="{prefix}blur60" x="-50%" y="-50%" width="200%" height="200%">
  <feGaussianBlur stdDeviation="56"/>
</filter>
<clipPath id="{prefix}clip"><rect width="{w}" height="{h}" rx="24"/></clipPath>
""".strip()


# ---------------------------------------------------------------------------
# 1. HERO SCENE (1280 x 580)
# ---------------------------------------------------------------------------
def build_hero(cfg: dict, bundle: dict, chars: dict) -> str:
    w, h = 1280, 580
    m = cfg["metrics"]
    roles = [
        "AI Systems Engineer · Regulated FinTech",
        "Agentic Payment Rails & Cryptographic Mandates",
        "PSD3 Fraud Graph Neural Nets & Biometrics",
        "Grounded RAG · Tamper-Evident Audit Ledgers",
    ]
    # 4 roles x 3.2s = 12.8s cycle
    role_svg = []
    for idx, rtext in enumerate(roles):
        delay = 1.5 + idx * 3.2
        init_op = "1" if idx == 0 else "0"
        role_svg.append(
            f'<text class="role jb" x="82" y="305" font-size="18" fill="#e6edf3" opacity="{init_op}" '
            f'style="animation-delay:{delay:.2f}s">{esc(rtext)}</text>'
        )

    stages = [
        ("01", "INFER", "#39d353", "0s"),
        ("02", "GUARD", "#2fd48a", "1.6s"),
        ("03", "ATTEST", "#58a6ff", "3.2s"),
        ("04", "SETTLE", "#39d353", "4.8s"),
    ]
    stage_nodes = []
    sx0 = 52
    for idx, (num, label, col, begin) in enumerate(stages):
        x = sx0 + idx * 148
        y = 478
        stage_nodes.append(f"""
        <g class="fu" style="animation-delay:{1.05 + idx * 0.12:.2f}s">
          <rect x="{x}" y="{y}" width="130" height="44" rx="12" fill="#0d1720" fill-opacity=".9" stroke="#223642" stroke-width="1.2"/>
          <rect x="{x}" y="{y}" width="130" height="44" rx="12" fill="{col}" fill-opacity="0" stroke="{col}" stroke-width="1.8" stroke-opacity="0">
            <animate attributeName="stroke-opacity" values="0;.95;.2;0" keyTimes="0;.08;.26;1" dur="6.4s" begin="{begin}" repeatCount="indefinite"/>
            <animate attributeName="fill-opacity" values="0;.13;.03;0" keyTimes="0;.08;.26;1" dur="6.4s" begin="{begin}" repeatCount="indefinite"/>
          </rect>
          <circle cx="{x + 20}" cy="{y + 22}" r="3.5" fill="{col}">
            <animate attributeName="opacity" values=".35;1;.35" dur="1.8s" begin="{begin}" repeatCount="indefinite"/>
          </circle>
          <text class="jb" x="{x + 31}" y="{y + 26}" font-size="10.5" fill="#7d8b99">{num}</text>
          <text class="jbb" x="{x + 53}" y="{y + 26}" font-size="12" fill="#eef4f8" letter-spacing="1.2">{label}</text>
        </g>
        """)
        if idx < 3:
            ax = x + 134
            ay = y + 22
            stage_nodes.append(f"""
            <g opacity=".8">
              <line x1="{ax}" y1="{ay}" x2="{ax + 10}" y2="{ay}" stroke="{col}" stroke-width="1.6" stroke-linecap="round"/>
              <path d="M{ax + 7} {ay - 3.5} L{ax + 11.5} {ay} L{ax + 7} {ay + 3.5}" fill="none" stroke="{col}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
            </g>
            """)

    stat_items = [
        (str(m["publicRepos"]), "PUBLIC REPOS", "#39d353"),
        (str(m["stars"]), "GITHUB STARS", "#2fd48a"),
        (str(m["contributions"]), "COMMITS (YR)", "#58a6ff"),
        (f'{m["streak"]}d', "ACTIVE STREAK", "#39d353"),
    ]
    stat_pills = []
    for idx, (val, lbl, col) in enumerate(stat_items):
        bx = 52 + idx * 148
        by = 394
        stat_pills.append(f"""
        <g class="fu" style="animation-delay:{0.75 + idx * 0.1:.2f}s">
          <rect x="{bx}" y="{by}" width="136" height="62" rx="14" fill="#ffffff" fill-opacity=".03" stroke="#213440"/>
          <rect x="{bx + 14}" y="{by}" width="34" height="2.4" rx="1.2" fill="{col}"/>
          <text class="sg" x="{bx + 16}" y="{by + 34}" font-size="24" fill="#f0f6fc">{esc(val)}</text>
          <text class="jb" x="{bx + 16}" y="{by + 51}" font-size="9" fill="#8b98a5" letter-spacing="1.4">{lbl}</text>
        </g>
        """)

    particles = []
    pts_spec = [(740, 440, 2.4, "0s", "5.2s"), (820, 470, 1.8, "1.1s", "6.0s"),
                (1130, 430, 2.2, "2.3s", "5.6s"), (1185, 360, 1.6, "0.7s", "4.8s"),
                (760, 280, 2.0, "3.0s", "5.8s"), (1080, 220, 1.9, "1.9s", "6.4s")]
    for px, py, pr, pdelay, pdur in pts_spec:
        particles.append(
            f'<circle class="spark" cx="{px}" cy="{py}" r="{pr}" fill="#39d353" '
            f'style="animation-delay:{pdelay};animation-duration:{pdur}"/>'
        )

    hex_outer = hex_points(972, 275, 212)
    hex_inner = hex_points(972, 275, 174)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Muhammad Ashir — AI Systems Engineer · The Proof Loop">
<title>Muhammad Ashir — I turn model output into verifiable action</title>
<desc>Animated signature hero featuring Muhammad Ashir's illustrated character reel, cycling engineering roles, live GitHub stats, and the 4-stage Proof Loop (Infer, Guard, Attest, Settle).</desc>
<defs>
<style>
{font_defs(bundle)}
.role{{animation:roleCycle 12.8s cubic-bezier(.2,.8,.2,1) infinite}}
@keyframes roleCycle{{
  0%{{opacity:0;transform:translateY(12px)}}
  4%{{opacity:1;transform:translateY(0)}}
  22%{{opacity:1;transform:translateY(0)}}
  26%{{opacity:0;transform:translateY(-12px)}}
  100%{{opacity:0;transform:translateY(-12px)}}
}}
.spark{{animation:riseSpark 5.5s ease-in-out infinite;opacity:0}}
@keyframes riseSpark{{
  0%{{transform:translateY(0) scale(.8);opacity:0}}
  20%{{opacity:.85}}
  80%{{opacity:.45}}
  100%{{transform:translateY(-115px) scale(1.15);opacity:0}}
}}
.corner{{stroke-dasharray:60;animation:drawCorner .85s ease both}}
@keyframes drawCorner{{from{{stroke-dashoffset:60}}to{{stroke-dashoffset:0}}}}
.scanline{{animation:scanY 5.8s ease-in-out infinite}}
@keyframes scanY{{
  0%,100%{{transform:translateY(0);opacity:0}}
  12%{{opacity:.55}}
  88%{{opacity:.55}}
  96%{{transform:translateY(420px);opacity:0}}
}}
</style>
{common_shell_defs("h", w, h)}
<linearGradient id="hNameG" x1="0" y1="0" x2="1" y2="0" gradientUnits="objectBoundingBox">
  <stop offset="0" stop-color="#ffffff"/>
  <stop offset=".38" stop-color="#7ee787"/>
  <stop offset=".7" stop-color="#39d353"/>
  <stop offset="1" stop-color="#58a6ff"/>
  <animateTransform attributeName="gradientTransform" type="translate" values="-.28 0;.28 0;-.28 0" dur="7.5s" repeatCount="indefinite"/>
</linearGradient>
<linearGradient id="hCharFadeB" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#fff"/>
  <stop offset=".84" stop-color="#fff"/>
  <stop offset="1" stop-color="#000"/>
</linearGradient>
<mask id="hCharMask" maskUnits="userSpaceOnUse" x="680" y="18" width="570" height="540">
  <rect x="680" y="18" width="570" height="540" fill="url(#hCharFadeB)"/>
</mask>
<clipPath id="hTermClip">
  <rect x="52" y="44" width="585" height="26">
    <animate attributeName="width" values="0;585" dur="1.05s" begin="0s" fill="freeze"/>
  </rect>
</clipPath>
<clipPath id="hSubClip">
  <rect x="52" y="96" width="380" height="34">
    <animate attributeName="width" values="0;0;380" keyTimes="0;.35;1" dur="1.25s" begin="0s" fill="freeze"/>
  </rect>
</clipPath>
</defs>

<g clip-path="url(#hclip)">
  <rect width="{w}" height="{h}" fill="url(#hbg)"/>
  <rect width="{w}" height="{h}" fill="url(#hgrid)"/>

  <!-- Ambient emerald & cyan aurora glows -->
  <g filter="url(#hblur60)">
    <circle cx="980" cy="275" r="245" fill="url(#hemerald)">
      <animate attributeName="r" values="230;265;230" dur="6.5s" repeatCount="indefinite"/>
    </circle>
    <circle cx="220" cy="150" r="195" fill="url(#hcyan)" opacity=".75"/>
    <circle cx="620" cy="520" r="180" fill="url(#hemerald)" opacity=".55"/>
  </g>

  <!-- Subtle giant MA monogram watermark -->
  <text class="sg" x="48" y="340" font-size="250" fill="#39d353" opacity=".028" letter-spacing="-10">MA</text>

  <!-- RIGHT STAGE: Rotating orbital hex telemetry + animated character reel -->
  <g opacity=".72">
    <polygon points="{hex_outer}" fill="none" stroke="#39d353" stroke-opacity=".22" stroke-width="1.3" stroke-dasharray="10 8" class="spin"/>
    <polygon points="{hex_inner}" fill="none" stroke="#58a6ff" stroke-opacity=".20" stroke-width="1.2" stroke-dasharray="4 10" class="spin2"/>
    <circle cx="972" cy="275" r="228" fill="none" stroke="#39d353" stroke-opacity=".10" stroke-width="1"/>
  </g>

  {"".join(particles)}

  <!-- Multi-pose looping character reel (9.6s smooth crossfade: Wave -> Signature -> Present) -->
  <g mask="url(#hCharMask)">
    <g class="flt">
      <!-- Pose 1: Waving hello -->
      <image x="706" y="26" width="526" height="526" href="{chars['wave']}" opacity="1" preserveAspectRatio="xMidYMid meet">
        <animate attributeName="opacity" values="1;1;0;0;0;1" keyTimes="0;0.30;0.35;0.65;0.95;1" dur="10.2s" repeatCount="indefinite"/>
      </image>
      <!-- Pose 2: Signature executive portrait -->
      <image x="706" y="26" width="526" height="526" href="{chars['base']}" opacity="0" preserveAspectRatio="xMidYMid meet">
        <animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.30;0.35;0.63;0.68;1" dur="10.2s" repeatCount="indefinite"/>
      </image>
      <!-- Pose 3: Presenting the architecture -->
      <image x="706" y="26" width="526" height="526" href="{chars['present']}" opacity="0" preserveAspectRatio="xMidYMid meet">
        <animate attributeName="opacity" values="0;0;0;1;1;0" keyTimes="0;0.63;0.68;0.95;0.99;1" dur="10.2s" repeatCount="indefinite"/>
      </image>
    </g>
  </g>

  <!-- Holographic scanner beam across character frame -->
  <rect class="scanline" x="704" y="64" width="532" height="2" fill="url(#hbar)" opacity=".5"/>

  <!-- HUD Viewfinder corners + reel status bar -->
  <path class="corner" d="M700 86V54H732" fill="none" stroke="#39d353" stroke-opacity=".85" stroke-width="2.2" stroke-linecap="round" style="animation-delay:.25s"/>
  <path class="corner" d="M1238 86V54H1206" fill="none" stroke="#39d353" stroke-opacity=".85" stroke-width="2.2" stroke-linecap="round" style="animation-delay:.35s"/>
  <path class="corner" d="M700 470V502H732" fill="none" stroke="#58a6ff" stroke-opacity=".8" stroke-width="2.2" stroke-linecap="round" style="animation-delay:.45s"/>
  <path class="corner" d="M1238 470V502H1206" fill="none" stroke="#58a6ff" stroke-opacity=".8" stroke-width="2.2" stroke-linecap="round" style="animation-delay:.55s"/>

  <!-- Top-right live attestation + follow CTA badge -->
  <g class="fi" style="animation-delay:.55s">
    <rect x="716" y="62" width="194" height="26" rx="13" fill="#081219" fill-opacity=".86" stroke="#39d353" stroke-opacity=".45"/>
    <circle cx="732" cy="75" r="4" fill="#39d353">
      <animate attributeName="opacity" values="1;.25;1" dur="1.5s" repeatCount="indefinite"/>
    </circle>
    <text class="jbb" x="744" y="79" font-size="9.8" fill="#7ee787" letter-spacing="1.4">ATTESTED · LIVE REEL</text>

    <rect x="1032" y="62" width="192" height="26" rx="13" fill="#08131a" fill-opacity=".9" stroke="#39d353" stroke-width="1.4">
      <animate attributeName="stroke-opacity" values=".45;1;.45" dur="2.2s" repeatCount="indefinite"/>
    </rect>
    <text class="jbb" x="1128" y="79" font-size="9.4" fill="#7ee787" text-anchor="middle" letter-spacing="1.0">+ FOLLOW FOR AI BUILDS</text>
  </g>

  <!-- Bottom HUD playback bar under character -->
  <g class="fi" style="animation-delay:.65s">
    <rect x="716" y="508" width="506" height="40" rx="12" fill="#081118" fill-opacity=".86" stroke="#1e3340"/>
    <circle cx="736" cy="528" r="4.5" fill="#39d353">
      <animate attributeName="r" values="3.5;5.2;3.5" dur="2s" repeatCount="indefinite"/>
    </circle>
    <text class="jbb" x="750" y="525" font-size="10.5" fill="#eef4f8" letter-spacing="1.7">ASHIR.PROOF_LOOP.REEL</text>
    <text class="jb" x="1206" y="525" font-size="10" fill="#8b98a5" text-anchor="end" letter-spacing="1.2">ILMENAU, DE · SYNCED</text>
    <rect x="750" y="535" width="456" height="3.2" rx="1.6" fill="#ffffff" fill-opacity=".10"/>
    <rect x="750" y="535" width="0" height="3.2" rx="1.6" fill="url(#hbar)">
      <animate attributeName="width" values="0;456" dur="10.2s" repeatCount="indefinite"/>
    </rect>
  </g>

  <!-- LEFT COLUMN: Terminal prompt + animated display typography -->
  <text clip-path="url(#hTermClip)" x="52" y="63" font-size="13">
    <tspan class="jbb" fill="#39d353">ashir@proof-loop</tspan><tspan fill="#7d8b99">:~$ </tspan><tspan fill="#e6edf3">verify </tspan><tspan fill="#58a6ff">--operator ashir --guardrails=strict</tspan><tspan class="blink" fill="#39d353"> &#9608;</tspan>
  </text>

  <text clip-path="url(#hSubClip)" class="jbb" x="52" y="118" font-size="12.5" fill="#39d353" letter-spacing="2.8">// THE PROOF LOOP · OPERATOR 001</text>

  <g class="fu" style="animation-delay:.22s">
    <text class="sg" x="48" y="186" font-size="64" letter-spacing="-1.6" fill="url(#hNameG)" filter="url(#hglow)">Muhammad Ashir</text>
  </g>

  <rect x="52" y="204" width="164" height="4" rx="2" fill="url(#hbar)">
    <animate attributeName="width" values="0;164" dur="1.1s" begin=".25s" fill="freeze"/>
  </rect>

  <!-- Signature catchphrase -->
  <g class="fu" style="animation-delay:.38s">
    <text class="sgm" x="52" y="246" font-size="22" fill="#9fb0bf">I turn model output into <tspan class="sg" fill="#eef4f8">verifiable action.</tspan></text>
  </g>

  <!-- Cycling role indicator -->
  <g class="fi" style="animation-delay:.55s">
    <rect x="52" y="280" width="596" height="38" rx="10" fill="#0d1821" fill-opacity=".85" stroke="#1f3542"/>
    <circle cx="68" cy="299" r="4.2" fill="#39d353">
      <animate attributeName="opacity" values="1;.3;1" dur="1.4s" repeatCount="indefinite"/>
    </circle>
  </g>
  {"".join(role_svg)}

  <text class="jb fu" x="52" y="352" font-size="12.5" fill="#8b98a5" style="animation-delay:.65s">
    Cryptographic guardrails, deterministic evals &amp; compliant AI infrastructure for real money.
  </text>
  <text class="jb fu" x="52" y="372" font-size="12.5" fill="#7ee787" style="animation-delay:.72s">
    &#8220;Trust is a system property, not a prompt.&#8221;
  </text>

  <!-- 4 Live Stat Pills -->
  {"".join(stat_pills)}

  <!-- 4-Stage Sequential Proof Loop Pipeline -->
  {"".join(stage_nodes)}

  <!-- Outer card border -->
  <rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="23.25" fill="none" stroke="url(#hedge)" stroke-width="1.5"/>
</g>
</svg>
"""


# ---------------------------------------------------------------------------
# 2. PROOF LOOP / ARCHITECTURE SHOWCASE SCENE (1280 x 550)
# ---------------------------------------------------------------------------
def build_showcase(cfg: dict, bundle: dict, chars: dict) -> str:
    w, h = 1280, 550
    systems = cfg["systems"]
    stages = [
        ("01 · INFER", "#58a6ff", "0s"),
        ("02 · GUARD", "#39d353", "1.8s"),
        ("03 · ATTEST", "#2fd48a", "3.6s"),
        ("04 · SETTLE", "#7ee787", "5.4s"),
    ]

    cards_svg = []
    # 2x2 grid on the left/right? Character presenting on LEFT (x=28..455), 2x2 flagship cards on RIGHT (x=475..1242)
    positions = [(476, 152), (866, 152), (476, 336), (866, 336)]
    cw, ch = 372, 164

    icon_paths = {
        "shield": '<path d="M12 2L4 5.5v5.8c0 5.1 3.4 9.8 8 11.2 4.6-1.4 8-6.1 8-11.2V5.5L12 2zm-1.2 13.2l-3.3-3.3 1.4-1.4 1.9 1.9 4.5-4.5 1.4 1.4-5.9 5.9z"/>',
        "ledger": '<path d="M4 4h16v3H4V4zm0 5h16v3H4V9zm0 5h10v3H4v-3zm13 0l2 2 3-3 1.4 1.4-4.4 4.4-3.4-3.4L17 14z"/>',
        "target": '<path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm0 18a8 8 0 1 1 8-8 8 8 0 0 1-8 8zm0-13a5 5 0 1 0 5 5 5 5 0 0 0-5-5zm0 7a2 2 0 1 1 2-2 2 2 0 0 1-2 2z"/>',
        "graph": '<path d="M6 3a3 3 0 1 0 2.8 4h6.4A3 3 0 1 0 18 5c-.8 0-1.6.3-2.1.9H8.8A3 3 0 0 0 6 3zm12 12a3 3 0 0 0-2.6 1.6l-6.5-3.2a3 3 0 1 0-.9 1.8l6.5 3.2A3 3 0 1 0 18 15z"/>',
    }

    # Map real owned repositories in sections.json order across the 4 gates
    default_stages = [
        ("01 · INFER", "#58a6ff", "0s"),
        ("02 · GUARD", "#39d353", "1.9s"),
        ("03 · ATTEST", "#2fd48a", "3.8s"),
        ("04 · LIVE", "#7ee787", "5.7s"),
    ]
    mapped = []
    for idx, sys_item in enumerate(systems[:4]):
        d_stage, d_col, d_begin = default_stages[idx]
        mapped.append((
            sys_item,
            sys_item.get("stage", d_stage),
            sys_item.get("color", d_col),
            d_begin,
        ))

    for idx, ((cx, cy), (sys_item, stage_tag, col, begin)) in enumerate(zip(positions, mapped)):
        d1 = sys_item["desc"][0]
        d2 = sys_item["desc"][1] if len(sys_item["desc"]) > 1 else ""
        ic = icon_paths.get(sys_item.get("icon", "shield"), icon_paths["shield"])
        name_size = "15" if len(sys_item["name"]) > 16 else "19"
        cards_svg.append(f"""
        <g class="fu" style="animation-delay:{0.35 + idx * 0.14:.2f}s">
          <rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="18" fill="#0c161f" fill-opacity=".92" stroke="#203542" stroke-width="1.2"/>
          <rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="18" fill="none" stroke="{col}" stroke-width="1.8" stroke-opacity="0">
            <animate attributeName="stroke-opacity" values="0;.9;.18;0" keyTimes="0;.08;.28;1" dur="7.6s" begin="{begin}" repeatCount="indefinite"/>
          </rect>
          <rect x="{cx + 18}" y="{cy + 18}" width="40" height="40" rx="12" fill="{col}" fill-opacity=".13" stroke="{col}" stroke-opacity=".4"/>
          <g transform="translate({cx + 26},{cy + 26}) scale(1.0)" fill="{col}">{ic}</g>
          <rect x="{cx + cw - 110}" y="{cy + 20}" width="92" height="22" rx="11" fill="{col}" fill-opacity=".11" stroke="{col}" stroke-opacity=".38"/>
          <text class="jbb" x="{cx + cw - 64}" y="{cy + 35}" font-size="8.6" fill="{col}" text-anchor="middle" letter-spacing="0.8">{esc(stage_tag)}</text>

          <text class="sg" x="{cx + 66}" y="{cy + 44}" font-size="{name_size}" fill="#f0f6fc">{esc(sys_item['name'])}</text>
          <text class="sgm" x="{cx + 22}" y="{cy + 86}" font-size="13.5" fill="#9fb0bf">{esc(d1)}</text>
          <text class="sgm" x="{cx + 22}" y="{cy + 106}" font-size="13.5" fill="#9fb0bf">{esc(d2)}</text>

          <line x1="{cx + 22}" y1="{cy + 124}" x2="{cx + cw - 22}" y2="{cy + 124}" stroke="#1c2f3b"/>
          <circle cx="{cx + 30}" cy="{cy + 143}" r="3.2" fill="{col}">
            <animate attributeName="opacity" values="1;.3;1" dur="2s" begin="{begin}" repeatCount="indefinite"/>
          </circle>
          <text class="jbb" x="{cx + 42}" y="{cy + 147}" font-size="10.2" fill="#7ee787" letter-spacing="1.3">{esc(sys_item['stack'])}</text>
        </g>
        """)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="The Proof Loop — Real Shipped AI &amp; FinTech Systems">
<title>The Proof Loop — Europulse Fraud Guard, MandatePay, RegLedger AI, Portfolio</title>
<desc>Muhammad Ashir presenting his 4-stage Proof Loop systems architecture with live animated data packets flowing between Infer, Guard, Attest, and Settle.</desc>
<defs>
<style>
{font_defs(bundle)}
</style>
{common_shell_defs("s", w, h)}
<linearGradient id="sArtFade" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#fff"/>
  <stop offset=".86" stop-color="#fff"/>
  <stop offset="1" stop-color="#000"/>
</linearGradient>
<mask id="sArtMask" maskUnits="userSpaceOnUse" x="14" y="54" width="450" height="476">
  <rect x="14" y="54" width="450" height="476" fill="url(#sArtFade)"/>
</mask>
</defs>

<g clip-path="url(#sclip)">
  <rect width="{w}" height="{h}" fill="url(#sbg)"/>
  <rect width="{w}" height="{h}" fill="url(#sgrid)"/>

  <g filter="url(#sblur60)">
    <circle cx="240" cy="300" r="220" fill="url(#semerald)"/>
    <circle cx="960" cy="260" r="240" fill="url(#scyan)" opacity=".75"/>
  </g>

  <!-- Orbiting hex behind character -->
  <polygon points="{hex_points(236, 286, 178)}" fill="none" stroke="#39d353" stroke-opacity=".22" stroke-width="1.3" stroke-dasharray="8 8" class="spin"/>

  <!-- Character presenting on the left with gentle floating parallax -->
  <g mask="url(#sArtMask)">
    <g class="flt">
      <image x="16" y="62" width="442" height="442" href="{chars['present']}" preserveAspectRatio="xMidYMid meet"/>
    </g>
  </g>

  <!-- Header -->
  <g class="fu" style="animation-delay:.15s">
    <text class="jbb" x="476" y="62" font-size="12" fill="#39d353" letter-spacing="2.4">// 01 · THE PROOF LOOP ARCHITECTURE</text>
    <text class="sg" x="476" y="104" font-size="32" fill="#f0f6fc" letter-spacing="-.6">Every AI action passes four gates.</text>
    <text class="sgm" x="476" y="130" font-size="14.5" fill="#8b98a5">Benchmarked before inference, policy-checked before execution, attested on-ledger before settlement.</text>
  </g>

  <!-- Animated circuit connector loop behind cards -->
  <path id="sLoopPath" d="M 662 234 L 1052 234 L 1052 418 L 662 418 Z" fill="none" stroke="#39d353" stroke-opacity=".18" stroke-width="1.5" stroke-dasharray="6 6"/>
  <circle r="4.5" fill="#39d353" filter="url(#sglow)">
    <animateMotion dur="7.6s" repeatCount="indefinite" path="M 662 234 L 1052 234 L 1052 418 L 662 418 Z"/>
  </circle>
  <circle r="3.8" fill="#58a6ff" filter="url(#sglow)">
    <animateMotion dur="7.6s" begin="3.8s" repeatCount="indefinite" path="M 662 234 L 1052 234 L 1052 418 L 662 418 Z"/>
  </circle>

  {"".join(cards_svg)}

  <!-- Bottom caption -->
  <g class="fi" style="animation-delay:.9s">
    <rect x="44" y="492" width="386" height="34" rx="10" fill="#09131a" fill-opacity=".88" stroke="#1f3542"/>
    <circle cx="64" cy="509" r="3.8" fill="#39d353">
      <animate attributeName="opacity" values="1;.25;1" dur="1.6s" repeatCount="indefinite"/>
    </circle>
    <text class="jbb" x="78" y="513" font-size="10.2" fill="#eef4f8" letter-spacing="1.4">INFER &#8594; GUARD &#8594; ATTEST &#8594; SETTLE</text>
  </g>

  <rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="23.25" fill="none" stroke="url(#sedge)" stroke-width="1.5"/>
</g>
</svg>
"""


# ---------------------------------------------------------------------------
# 3. SIGNAL STACK / FLASHLIGHT SCENE (1280 x 540)
# ---------------------------------------------------------------------------
def build_tools(cfg: dict, bundle: dict, chars: dict) -> str:
    w, h = 1280, 540
    icons = bundle["icons"]

    # 20 colorful brand chips in a 5x4 illuminated grid
    stack = [
        ("Python", "Python", "#3776AB"),
        ("PyTorch", "PyTorch", "#EE4C2C"),
        ("TensorFlow", "TensorFlow", "#FF6F00"),
        ("LangChain", "LangChain", "#2FD48A"),
        ("RAG", "RAG", "#39D353"),

        ("FastAPI", "FastAPI", "#009688"),
        ("PostgreSQL", "PostgreSQL", "#4169E1"),
        ("MongoDB", "MongoDB", "#47A248"),
        ("Redis", "Redis", "#FF4438"),
        ("MCP", "MCP", "#58A6FF"),

        ("Docker", "Docker", "#2496ED"),
        ("Linux", "Linux", "#FCC624"),
        ("Bash", "Bash", "#4EAA25"),
        ("Git", "Git", "#F05032"),
        ("HMAC", "HMAC", "#39D353"),

        ("Pandas", "Pandas", "#8C7AE6"),
        ("NumPy", "NumPy", "#4DABCF"),
        ("NetworkX", "NetworkX", "#58A6FF"),
        ("Postman", "Postman", "#FF6C37"),
        ("Jupyter", "Jupyter", "#F37626"),
    ]

    chips_svg = []
    cols = 5
    x0, y0 = 434, 152
    cw, ch = 154, 62
    gx, gy = 14, 18

    for idx, (label, icon_key, hex_col) in enumerate(stack):
        r = idx // cols
        c = idx % cols
        cx = x0 + c * (cw + gx)
        cy = y0 + r * (ch + gy)
        ic_path = icons[icon_key]["path"]
        delay = 0.28 + c * 0.14 + r * 0.08
        pulse_begin = f"{1.6 + idx * 0.34:.2f}s"
        chips_svg.append(f"""
        <g class="chip" style="animation-delay:{delay:.2f}s">
          <rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="14" fill="#0b151e" fill-opacity=".86"/>
          <rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="14" fill="{hex_col}" fill-opacity=".09"/>
          <rect x="{cx + 0.6}" y="{cy + 0.6}" width="{cw - 1.2}" height="{ch - 1.2}" rx="13.4" fill="none" stroke="{hex_col}" stroke-opacity=".34" stroke-width="1.2">
            <animate attributeName="stroke-opacity" values=".32;.96;.32;.32" keyTimes="0;.06;.18;1" dur="6.8s" begin="{pulse_begin}" repeatCount="indefinite"/>
          </rect>
          <rect x="{cx + 12}" y="{cy + 13}" width="36" height="36" rx="10" fill="{hex_col}" fill-opacity=".15"/>
          <g transform="translate({cx + 20},{cy + 21}) scale(0.8333)" fill="{hex_col}">
            <path d="{ic_path}"/>
          </g>
          <text class="jbb" x="{cx + 56}" y="{cy + 35}" font-size="12.2" fill="#eef4f8">{esc(label)}</text>
        </g>
        """)

    # Flashlight lens in signature-flashlight.png: image placed at x=-6, y=82, w=430, h=430
    # In 1024x1024 source, flashlight lens is around (905, 405) -> scaled: x = -6 + 430*(905/1024) = 374, y = 82 + 430*(405/1024) = 252
    lx, ly = 374, 252

    dust_svg = []
    for dx, dy, dr, dd in [(520, 240, 1.8, "0s"), (690, 195, 1.4, "1.3s"), (860, 290, 1.9, "2.4s"),
                           (1040, 215, 1.5, "3.6s"), (760, 385, 1.6, "4.2s"), (1140, 340, 1.4, "2.0s"),
                           (610, 330, 1.3, "5.0s")]:
        dust_svg.append(
            f'<circle class="dust" cx="{dx}" cy="{dy}" r="{dr}" fill="#7ee787" opacity="0" style="animation-delay:{dd}"/>'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Signal Stack — Illuminated Engineering Arsenal">
<title>Signal Stack — What Muhammad Ashir Builds With</title>
<desc>Muhammad Ashir shines a tactical torch across 20 illuminated AI, data, cryptography, and backend technology chips.</desc>
<defs>
<style>
{font_defs(bundle)}
.chip{{animation:chipPop .58s cubic-bezier(.2,.8,.3,1.22) both}}
@keyframes chipPop{{
  0%{{opacity:0;transform:translateX(-16px) scale(.86)}}
  70%{{opacity:1;transform:translateX(2px) scale(1.03)}}
  100%{{opacity:1;transform:translateX(0) scale(1)}}
}}
.beam{{animation:beamPulse 4.8s ease-in-out infinite;transform-origin:{lx}px {ly}px}}
@keyframes beamPulse{{
  0%,100%{{opacity:.62;transform:rotate(-0.8deg)}}
  35%{{opacity:.88;transform:rotate(0.9deg)}}
  68%{{opacity:.54;transform:rotate(-0.3deg)}}
}}
.dust{{animation:dustDrift 6.8s linear infinite}}
@keyframes dustDrift{{
  0%{{transform:translate(0,0);opacity:0}}
  18%{{opacity:.85}}
  82%{{opacity:.5}}
  100%{{transform:translate(48px,-24px);opacity:0}}
}}
</style>
{common_shell_defs("t", w, h)}
<linearGradient id="tBeam" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#dcffe4" stop-opacity=".90"/>
  <stop offset=".14" stop-color="#39d353" stop-opacity=".36"/>
  <stop offset=".55" stop-color="#2fd48a" stop-opacity=".14"/>
  <stop offset="1" stop-color="#58a6ff" stop-opacity=".02"/>
</linearGradient>
<radialGradient id="tLens" cx="50%" cy="50%" r="50%">
  <stop offset="0" stop-color="#ffffff" stop-opacity=".98"/>
  <stop offset=".32" stop-color="#7ee787" stop-opacity=".68"/>
  <stop offset="1" stop-color="#39d353" stop-opacity="0"/>
</radialGradient>
<filter id="tSoft" x="-30%" y="-30%" width="160%" height="160%">
  <feGaussianBlur stdDeviation="16"/>
</filter>
<linearGradient id="tCharFade" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#fff"/>
  <stop offset=".88" stop-color="#fff"/>
  <stop offset="1" stop-color="#000"/>
</linearGradient>
<mask id="tCharMask" maskUnits="userSpaceOnUse" x="0" y="70" width="435" height="465">
  <rect x="0" y="70" width="435" height="465" fill="url(#tCharFade)"/>
</mask>
</defs>

<g clip-path="url(#tclip)">
  <rect width="{w}" height="{h}" fill="url(#tbg)"/>
  <rect width="{w}" height="{h}" fill="url(#tgrid)"/>

  <g filter="url(#tblur60)">
    <circle cx="210" cy="320" r="200" fill="url(#temerald)"/>
    <circle cx="960" cy="280" r="240" fill="url(#tcyan)" opacity=".65"/>
  </g>

  <!-- Volumetric flashlight cone sweeping across the chips -->
  <g class="beam">
    <path d="M {lx} {ly} L 1268 48 L 1268 492 Z" fill="url(#tBeam)"/>
    <path d="M {lx} {ly} L 1268 122 L 1268 422 Z" fill="url(#tBeam)" opacity=".65" filter="url(#tSoft)"/>
  </g>

  <!-- Character holding flashlight -->
  <g mask="url(#tCharMask)">
    <image x="-6" y="82" width="430" height="430" href="{chars['flashlight']}" preserveAspectRatio="xMidYMid meet"/>
  </g>

  <!-- Bright lens flare right on the flashlight head -->
  <circle cx="{lx}" cy="{ly}" r="52" fill="url(#tLens)" class="beam"/>

  {"".join(dust_svg)}

  <!-- Header -->
  <g class="fu" style="animation-delay:.12s">
    <text class="jbb" x="434" y="58" font-size="12" fill="#39d353" letter-spacing="2.4">// 02 · SIGNAL STACK · 20 CORE TOOLS</text>
    <text class="sg" x="434" y="98" font-size="31" fill="#f0f6fc" letter-spacing="-.5">Illuminating the production stack.</text>
    <text class="sgm" x="434" y="125" font-size="14.5" fill="#8b98a5">Boring where money moves. Sharp where models reason, retrieve, and sign.</text>
  </g>

  <!-- 20 Brand Chips -->
  {"".join(chips_svg)}

  <!-- Footer tag -->
  <text class="jb fi" x="434" y="498" font-size="11" fill="#7d8b99" letter-spacing="1.4" style="animation-delay:1.1s">
    INTELLIGENCE &#183; SERVICES &amp; DATA &#183; CRYPTOGRAPHIC GUARDRAILS &#183; EVALUATION HARNESSES
  </text>

  <rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="23.25" fill="none" stroke="url(#tedge)" stroke-width="1.5"/>
</g>
</svg>
"""


# ---------------------------------------------------------------------------
# 4. RECEIPTS / SWINGING OPERATOR LANYARD + LIVE TELEMETRY (1280 x 620)
# ---------------------------------------------------------------------------
def build_stats(cfg: dict, bundle: dict, chars: dict) -> str:
    w, h = 1280, 620
    m = cfg["metrics"]
    ident = cfg["identity"]
    skills = cfg["skills"]

    big_tiles = [
        (str(m["publicRepos"]), "PUBLIC REPOSITORIES", "shipped & documented", "#39d353", 424, 146),
        (str(m["stars"]), "STARS EARNED", "across flagship repos", "#2fd48a", 834, 146),
        (str(m["contributions"]), "CONTRIBUTIONS", "last 12 months on GitHub", "#58a6ff", 424, 274),
        (f'{m["streak"]}d', "CURRENT STREAK", "consecutive active days", "#7ee787", 834, 274),
    ]
    tiles_svg = []
    for idx, (val, title, sub, col, tx, ty) in enumerate(big_tiles):
        tiles_svg.append(f"""
        <g class="fu" style="animation-delay:{0.35 + idx * 0.12:.2f}s">
          <rect x="{tx}" y="{ty}" width="392" height="112" rx="16" fill="#0c161f" fill-opacity=".9" stroke="#203542"/>
          <rect x="{tx + 20}" y="{ty}" width="54" height="3" rx="1.5" fill="{col}"/>
          <text class="sg" x="{tx + 24}" y="{ty + 54}" font-size="38" fill="#f0f6fc">{esc(val)}</text>
          <text class="jbb" x="{tx + 24}" y="{ty + 78}" font-size="10.5" fill="{col}" letter-spacing="1.5">{esc(title)}</text>
          <text class="jb" x="{tx + 24}" y="{ty + 96}" font-size="10.5" fill="#7d8b99">{esc(sub)}</text>
          <circle cx="{tx + 364}" cy="{ty + 28}" r="4" fill="{col}">
            <animate attributeName="opacity" values="1;.25;1" dur="{1.8 + idx * 0.4:.1f}s" repeatCount="indefinite"/>
          </circle>
        </g>
        """)

    # Animated capability bars
    bars_svg = []
    bar_colors = ["#39d353", "#2fd48a", "#58a6ff", "#7ee787"]
    for idx, sk in enumerate(skills):
        by = 456 + idx * 32
        full_w = int(round(470 * (sk["value"] / 100.0)))
        col = bar_colors[idx % len(bar_colors)]
        dur = 1.4 + idx * 0.22
        bars_svg.append(f"""
        <text class="sgm" x="448" y="{by + 12}" font-size="13" fill="#dce6ef">{esc(sk['label'])}</text>
        <rect x="658" y="{by + 1}" width="470" height="12" rx="6" fill="#152430"/>
        <rect x="658" y="{by + 1}" width="{full_w}" height="12" rx="6" fill="{col}">
          <animate attributeName="width" values="0;{full_w}" dur="{dur:.2f}s" begin="0.4s" fill="freeze" calcMode="spline" keySplines=".2 .8 .2 1"/>
        </rect>
        <text class="jbb" x="1146" y="{by + 12}" font-size="12" fill="{col}">{sk['value']}%</text>
        """)

    # Lanyard strap centered at x=212, text cleanly centered down the middle
    # Barcode lines on ID card
    barcode_bars = []
    bx_cur = 82.0
    widths = [2.6, 1.4, 1.4, 3.2, 1.4, 2.4, 1.4, 3.4, 1.4, 1.4, 2.6, 1.4, 3.2, 1.4, 2.2, 1.4, 1.4, 3.0, 1.4, 2.6,
              1.4, 3.2, 1.4, 1.4, 2.4, 1.4, 3.2, 1.4, 2.6, 1.4, 1.4, 3.2, 2.2, 1.4, 2.8]
    for bw in widths:
        barcode_bars.append(f'<rect x="{bx_cur:.1f}" y="534" width="{bw:.1f}" height="16" fill="#7ee787" fill-opacity=".75"/>')
        bx_cur += bw + 3.2

    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Operator Clearance Badge and Live GitHub Receipts">
<title>Operator Clearance Badge &amp; Live GitHub Telemetry</title>
<desc>Swinging holographic operator badge of Muhammad Ashir beside live daily-refreshed GitHub telemetry and capability meters.</desc>
<defs>
<style>
{font_defs(bundle)}
.swing{{
  transform-box:view-box;
  transform-origin:212px -36px;
  animation:badgeDrop 2.2s cubic-bezier(.28,1,.48,1) both, badgeSway 6.2s ease-in-out 2.2s infinite;
}}
@keyframes badgeDrop{{
  0%{{transform:translateY(-620px) rotate(-4deg)}}
  28%{{transform:translateY(0) rotate(0deg)}}
  48%{{transform:rotate(3.0deg)}}
  68%{{transform:rotate(-2.0deg)}}
  84%{{transform:rotate(0.9deg)}}
  100%{{transform:rotate(0deg)}}
}}
@keyframes badgeSway{{
  0%,100%{{transform:rotate(-1.7deg)}}
  50%{{transform:rotate(1.7deg)}}
}}
.foil{{animation:foilSweep 6.2s ease-in-out infinite}}
@keyframes foilSweep{{
  0%{{transform:translateX(-340px) skewX(-16deg)}}
  55%,100%{{transform:translateX(440px) skewX(-16deg)}}
}}
</style>
{common_shell_defs("r", w, h)}
<linearGradient id="rStrap" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#0d3a22"/>
  <stop offset=".5" stop-color="#238636"/>
  <stop offset="1" stop-color="#0d3a22"/>
</linearGradient>
<linearGradient id="rMetal" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#e6edf3"/>
  <stop offset=".45" stop-color="#8b98a5"/>
  <stop offset=".6" stop-color="#546370"/>
  <stop offset="1" stop-color="#c9d1d9"/>
</linearGradient>
<linearGradient id="rBadgeBg" x1="0" y1="0" x2=".8" y2="1">
  <stop offset="0" stop-color="#10202b"/>
  <stop offset=".55" stop-color="#0a141c"/>
  <stop offset="1" stop-color="#0c1c18"/>
</linearGradient>
<linearGradient id="rFoil" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#39d353" stop-opacity="0"/>
  <stop offset=".35" stop-color="#39d353" stop-opacity=".14"/>
  <stop offset=".5" stop-color="#ffffff" stop-opacity=".22"/>
  <stop offset=".65" stop-color="#58a6ff" stop-opacity=".14"/>
  <stop offset="1" stop-color="#58a6ff" stop-opacity="0"/>
</linearGradient>
<filter id="rShadow" x="-25%" y="-20%" width="150%" height="150%">
  <feDropShadow dx="0" dy="16" stdDeviation="14" flood-color="#000" flood-opacity=".65"/>
</filter>
<clipPath id="rCardClip"><rect x="56" y="144" width="312" height="438" rx="20"/></clipPath>
<clipPath id="rPhotoClip"><rect x="132" y="196" width="160" height="176" rx="16"/></clipPath>
</defs>

<g clip-path="url(#rclip)">
  <rect width="{w}" height="{h}" fill="url(#rbg)"/>
  <rect width="{w}" height="{h}" fill="url(#rgrid)"/>

  <g filter="url(#rblur60)">
    <circle cx="212" cy="340" r="210" fill="url(#remerald)"/>
    <circle cx="940" cy="290" r="240" fill="url(#rcyan)" opacity=".7"/>
  </g>

  <!-- RIGHT DASHBOARD HEADER -->
  <g class="fu" style="animation-delay:.15s">
    <text class="jbb" x="424" y="58" font-size="12" fill="#39d353" letter-spacing="2.4">// 03 · LIVE RECEIPTS &amp; TELEMETRY</text>
    <text class="sg" x="424" y="100" font-size="32" fill="#f0f6fc" letter-spacing="-.5">Proof, not promises.</text>
    <text class="sgm" x="424" y="126" font-size="14.5" fill="#8b98a5">Synced automatically from GitHub every day via GitHub Actions.</text>

    <rect x="1044" y="56" width="182" height="30" rx="15" fill="#39d353" fill-opacity=".10" stroke="#39d353" stroke-opacity=".42"/>
    <circle cx="1064" cy="71" r="4.2" fill="#39d353">
      <animate attributeName="opacity" values="1;.2;1" dur="1.5s" repeatCount="indefinite"/>
    </circle>
    <text class="jbb" x="1078" y="75" font-size="10.2" fill="#7ee787" letter-spacing="1.4">DAILY AUTO-SYNC</text>
  </g>

  <!-- 4 Big Metric Tiles -->
  {"".join(tiles_svg)}

  <!-- Capability Meter Panel -->
  <g class="fu" style="animation-delay:.75s">
    <rect x="424" y="404" width="802" height="178" rx="18" fill="#0c161f" fill-opacity=".9" stroke="#203542"/>
    <text class="jbb" x="448" y="434" font-size="11" fill="#39d353" letter-spacing="1.8">CORE ENGINEERING WEIGHTS</text>
    <text class="jb" x="1200" y="434" font-size="10.5" fill="#7d8b99" text-anchor="end">VERIFIED REPO FOOTPRINT</text>
    {"".join(bars_svg)}
  </g>

  <!-- LEFT: SWINGING OPERATOR LANYARD BADGE -->
  <g class="swing">
    <!-- Lanyard strap -->
    <path d="M 190 -44 L 234 -44 L 230 98 L 194 98 Z" fill="url(#rStrap)"/>
    <text class="jbb" font-size="7.6" fill="#dcffe4" fill-opacity=".9" letter-spacing="1.8" text-anchor="middle" transform="translate(209,32) rotate(90)">PROOF.LOOP</text>
    <!-- Metal clasp -->
    <rect x="184" y="94" width="56" height="24" rx="6" fill="url(#rMetal)"/>
    <rect x="198" y="100" width="28" height="7" rx="3.5" fill="#0d1720" fill-opacity=".65"/>
    <circle cx="212" cy="132" r="13" fill="none" stroke="url(#rMetal)" stroke-width="5"/>

    <!-- Card drop shadow -->
    <g filter="url(#rShadow)">
      <rect x="56" y="144" width="312" height="438" rx="20" fill="url(#rBadgeBg)" stroke="url(#rbar)" stroke-opacity=".65" stroke-width="1.6"/>
    </g>

    <g clip-path="url(#rCardClip)">
      <rect x="56" y="144" width="312" height="438" fill="url(#rgrid)"/>
      <rect x="56" y="144" width="312" height="38" fill="#39d353" fill-opacity=".12"/>
      <circle cx="78" cy="163" r="4" fill="#39d353">
        <animate attributeName="opacity" values="1;.25;1" dur="1.7s" repeatCount="indefinite"/>
      </circle>
      <text class="jbb" x="90" y="167" font-size="10" fill="#7ee787" letter-spacing="1.7">OPERATOR CLEARANCE</text>
      <text class="jb" x="348" y="167" font-size="10" fill="#8b98a5" text-anchor="end">ID #MA-01</text>

      <!-- Portrait frame + orbiting security dot -->
      <rect x="128" y="192" width="168" height="184" rx="18" fill="#071018" stroke="url(#rbar)" stroke-width="2"/>
      <g clip-path="url(#rPhotoClip)">
        <circle cx="212" cy="278" r="80" fill="url(#remerald)"/>
        <image x="126" y="194" width="172" height="176" href="{chars['base']}" preserveAspectRatio="xMidYMin slice"/>
      </g>
      <path id="rOrbit" d="M 146 192 H 278 A 18 18 0 0 1 296 210 V 358 A 18 18 0 0 1 278 376 H 146 A 18 18 0 0 1 128 358 V 210 A 18 18 0 0 1 146 192 Z" fill="none"/>
      <circle r="3.4" fill="#7ee787" filter="url(#rglow)">
        <animateMotion dur="6.4s" repeatCount="indefinite"><mpath href="#rOrbit"/></animateMotion>
      </circle>

      <!-- Verified cryptographic stamp -->
      <g transform="translate(318,228)">
        <circle r="24" fill="#08131a" stroke="#39d353" stroke-width="1.6"/>
        <text class="jbb" y="-2" text-anchor="middle" font-size="8.5" fill="#7ee787" letter-spacing="1">TIER</text>
        <text class="sg" y="13" text-anchor="middle" font-size="14" fill="#39d353">L1</text>
      </g>

      <text class="sg" x="212" y="408" font-size="23" fill="#f0f6fc" text-anchor="middle">{esc(ident['name'])}</text>
      <text class="jbb" x="212" y="428" font-size="10.8" fill="#39d353" text-anchor="middle" letter-spacing="1.6">AI SYSTEMS ENGINEER</text>

      <line x1="80" y1="444" x2="344" y2="444" stroke="#1f3440"/>

      <text class="jb" x="82" y="463" font-size="8.8" fill="#7d8b99" letter-spacing="1.4">BASE</text>
      <text class="sgm" x="82" y="479" font-size="12.5" fill="#eef4f8">{esc(ident['base'])}</text>

      <text class="jb" x="224" y="463" font-size="8.8" fill="#7d8b99" letter-spacing="1.4">FOCUS</text>
      <text class="sgm" x="224" y="479" font-size="12.5" fill="#eef4f8">Agents &#183; FinTech</text>

      <text class="jb" x="82" y="498" font-size="8.8" fill="#7d8b99" letter-spacing="1.4">GUARDRAIL</text>
      <text class="sgm" x="82" y="514" font-size="12.5" fill="#7ee787">HMAC + Policy</text>

      <text class="jb" x="224" y="498" font-size="8.8" fill="#7d8b99" letter-spacing="1.4">STATUS</text>
      <text class="sgm" x="224" y="514" font-size="12.5" fill="#eef4f8">Shipping</text>

      {"".join(barcode_bars)}
      <text class="jb" x="212" y="568" font-size="9.5" fill="#8b98a5" text-anchor="middle" letter-spacing="1.2">@muhammadashir0</text>

      <!-- Sweeping holographic foil reflection -->
      <g class="foil">
        <rect x="-60" y="144" width="130" height="440" fill="url(#rFoil)"/>
      </g>
    </g>
  </g>

  <rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="23.25" fill="none" stroke="url(#redge)" stroke-width="1.5"/>
</g>
</svg>
"""


# ---------------------------------------------------------------------------
# 5. OPEN CHANNEL / CONNECT SCENE (1280 x 470)
# ---------------------------------------------------------------------------
def build_connect(cfg: dict, bundle: dict, chars: dict) -> str:
    w, h = 1280, 470
    icons = bundle["icons"]

    channels = [
        ("GitHub", "@muhammadashir0", "GitHub", "#39d353", "2.0s"),
        ("LinkedIn", "in/muhammadashir1", "LinkedIn", "#0A66C2", "3.4s"),
        ("Email", "ashirali0998@gmail.com", "Gmail", "#EA4335", "4.8s"),
        ("Portfolio", "datascienceportfol.io", "Chrome", "#58A6FF", "6.2s"),
    ]
    positions = [(544, 152), (898, 152), (544, 266), (898, 266)]
    cw, ch = 336, 96

    cards_svg = []
    for idx, ((cx, cy), (title, val, ic_key, col, begin)) in enumerate(zip(positions, channels)):
        ic_path = icons[ic_key]["path"]
        ic_fill = "#eef4f8" if ic_key == "GitHub" else col
        cards_svg.append(f"""
        <g class="fu" style="animation-delay:{0.35 + idx * 0.12:.2f}s">
          <rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="16" fill="#0c161f" fill-opacity=".92" stroke="#203542"/>
          <rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="16" fill="none" stroke="{col}" stroke-width="1.8" stroke-opacity="0">
            <animate attributeName="stroke-opacity" values="0;.88;0;0" keyTimes="0;.08;.24;1" dur="7.2s" begin="{begin}" repeatCount="indefinite"/>
          </rect>
          <rect x="{cx + 18}" y="{cy + 24}" width="48" height="48" rx="13" fill="{col}" fill-opacity=".14" stroke="{col}" stroke-opacity=".35"/>
          <g transform="translate({cx + 30},{cy + 36}) scale(1.0)" fill="{ic_fill}">
            <path d="{ic_path}"/>
          </g>
          <text class="sg" x="{cx + 82}" y="{cy + 45}" font-size="17.5" fill="#f0f6fc">{title}</text>
          <text class="jb" x="{cx + 82}" y="{cy + 67}" font-size="11.5" fill="#8b98a5">{esc(val)}</text>
          <g class="arrow" transform="translate({cx + cw - 30},{cy + 48})" style="animation-delay:{idx * 0.25:.2f}s">
            <path d="M-7 0H7M2 -5L7 0L2 5" fill="none" stroke="{col}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </g>
        </g>
        """)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Open Channel — Connect with Muhammad Ashir">
<title>Open Channel — Build High-Trust AI Systems Together</title>
<desc>Muhammad Ashir at his terminal beside pulsing direct channel cards for GitHub, LinkedIn, Email, and Portfolio.</desc>
<defs>
<style>
{font_defs(bundle)}
.arrow{{animation:nudgeX 1.85s ease-in-out infinite}}
@keyframes nudgeX{{
  0%,100%{{transform:translate(0,0)}}
  50%{{transform:translate(6px,0)}}
}}
.ring{{animation:ringOut 3.2s ease-out infinite;transform-origin:418px 82px}}
@keyframes ringOut{{
  0%{{transform:scale(.5);opacity:.9}}
  100%{{transform:scale(2.4);opacity:0}}
}}
</style>
{common_shell_defs("c", w, h)}
<linearGradient id="cCharFade" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#fff"/>
  <stop offset=".88" stop-color="#fff"/>
  <stop offset="1" stop-color="#000"/>
</linearGradient>
<mask id="cCharMask" maskUnits="userSpaceOnUse" x="18" y="24" width="490" height="440">
  <rect x="18" y="24" width="490" height="440" fill="url(#cCharFade)"/>
</mask>
</defs>

<g clip-path="url(#cclip)">
  <rect width="{w}" height="{h}" fill="url(#cbg)"/>
  <rect width="{w}" height="{h}" fill="url(#cgrid)"/>

  <g filter="url(#cblur60)">
    <circle cx="260" cy="260" r="220" fill="url(#cemerald)"/>
    <circle cx="920" cy="240" r="220" fill="url(#ccyan)" opacity=".7"/>
  </g>

  <!-- Floating laptop portrait on left -->
  <g mask="url(#cCharMask)">
    <g class="flt">
      <image x="28" y="34" width="446" height="436" href="{chars['laptop']}" preserveAspectRatio="xMidYMid meet"/>
    </g>
  </g>

  <!-- Signal beacon ping -->
  <circle cx="418" cy="82" r="10" fill="none" stroke="#39d353" stroke-width="1.8" class="ring"/>
  <circle cx="418" cy="82" r="4.5" fill="#39d353"/>

  <!-- Header -->
  <g class="fu" style="animation-delay:.15s">
    <text class="jbb" x="544" y="60" font-size="12" fill="#39d353" letter-spacing="2.4">// 04 · OPEN CHANNEL</text>
    <text class="sg" x="544" y="102" font-size="31" fill="#f0f6fc" letter-spacing="-.5">Building where AI meets real money?</text>
    <text class="sgm" x="544" y="129" font-size="14.5" fill="#8b98a5">Open for AI systems roles, financial LLM research, and high-trust engineering collaborations.</text>
  </g>

  {"".join(cards_svg)}

  <!-- Bottom availability & follow CTA bar -->
  <g class="fu" style="animation-delay:.85s">
    <rect x="544" y="384" width="690" height="46" rx="14" fill="#0b1720" stroke="#223b47"/>
    <circle cx="568" cy="407" r="4.5" fill="#39d353">
      <animate attributeName="opacity" values="1;.25;1" dur="1.4s" repeatCount="indefinite"/>
    </circle>
    <text class="jbb" x="584" y="411" font-size="10.8" fill="#7ee787" letter-spacing="1.2">SHIPPING OPEN-SOURCE AI &amp; FINTECH IN GERMANY</text>
    <rect x="1008" y="393" width="212" height="28" rx="14" fill="#238636" fill-opacity=".35" stroke="#39d353">
      <animate attributeName="stroke-opacity" values=".4;1;.4" dur="2s" repeatCount="indefinite"/>
    </rect>
    <text class="jbb" x="1114" y="411" font-size="9.2" fill="#ffffff" text-anchor="middle" letter-spacing="0.9">&#9733; STAR &amp; FOLLOW ON GITHUB</text>
  </g>

  <rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="23.25" fill="none" stroke="url(#cedge)" stroke-width="1.5"/>
</g>
</svg>
"""


# ---------------------------------------------------------------------------
# 6. FIELD NOTES / OPERATING PRINCIPLES SCENE (1280 x 520)
# ---------------------------------------------------------------------------
def build_quotes(cfg: dict, bundle: dict, chars: dict) -> str:
    w, h = 1280, 520
    quotes = cfg["quotes"]

    accents = [
        ("PRINCIPLE 01 · GUARDRAILS", "#39d353", "0s"),
        ("PRINCIPLE 02 · DETERMINISM", "#58a6ff", "2.4s"),
        ("PRINCIPLE 03 · RESILIENCE", "#2fd48a", "4.8s"),
    ]
    qcards = []
    for idx, (lines, (tag, col, begin)) in enumerate(zip(quotes, accents)):
        qy = 140 + idx * 108
        joined = " ".join(lines)
        qcards.append(f"""
        <g class="fu" style="animation-delay:{0.3 + idx * 0.16:.2f}s">
          <rect x="442" y="{qy}" width="786" height="92" rx="16" fill="#0c161f" fill-opacity=".92" stroke="#203542"/>
          <rect x="442" y="{qy}" width="5" height="92" rx="2.5" fill="{col}"/>
          <rect x="442" y="{qy}" width="786" height="92" rx="16" fill="none" stroke="{col}" stroke-width="1.6" stroke-opacity="0">
            <animate attributeName="stroke-opacity" values="0;.8;.15;0" keyTimes="0;.08;.30;1" dur="7.2s" begin="{begin}" repeatCount="indefinite"/>
          </rect>
          <text class="jbb" x="468" y="{qy + 28}" font-size="10" fill="{col}" letter-spacing="1.8">{tag}</text>
          <text class="sgm" x="468" y="{qy + 58}" font-size="14.6" fill="#eef4f8">&#8220;{esc(joined)}&#8221;</text>
          <text class="sg" x="1206" y="{qy + 66}" font-size="44" fill="{col}" opacity=".16" text-anchor="end">&#8221;</text>
        </g>
        """)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Field Notes — Operating Principles of Muhammad Ashir">
<title>Field Notes — Operating Principles</title>
<desc>Signature portrait of Muhammad Ashir beside three animated engineering principles on cryptographic guardrails, auditability, and resilient systems.</desc>
<defs>
<style>
{font_defs(bundle)}
</style>
{common_shell_defs("q", w, h)}
<linearGradient id="qCharFade" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#fff"/>
  <stop offset=".86" stop-color="#fff"/>
  <stop offset="1" stop-color="#000"/>
</linearGradient>
<mask id="qCharMask" maskUnits="userSpaceOnUse" x="20" y="50" width="400" height="450">
  <rect x="20" y="50" width="400" height="450" fill="url(#qCharFade)"/>
</mask>
</defs>

<g clip-path="url(#qclip)">
  <rect width="{w}" height="{h}" fill="url(#qbg)"/>
  <rect width="{w}" height="{h}" fill="url(#qgrid)"/>

  <g filter="url(#qblur60)">
    <circle cx="220" cy="280" r="210" fill="url(#qemerald)"/>
    <circle cx="960" cy="260" r="220" fill="url(#qcyan)" opacity=".65"/>
  </g>

  <polygon points="{hex_points(218, 276, 168)}" fill="none" stroke="#39d353" stroke-opacity=".22" stroke-width="1.3" stroke-dasharray="9 7" class="spin2"/>

  <g mask="url(#qCharMask)">
    <g class="flt">
      <image x="24" y="64" width="390" height="426" href="{chars['base']}" preserveAspectRatio="xMidYMid meet"/>
    </g>
  </g>

  <g class="fu" style="animation-delay:.14s">
    <text class="jbb" x="442" y="58" font-size="12" fill="#39d353" letter-spacing="2.4">// 05 · FIELD NOTES &amp; DOCTRINE</text>
    <text class="sg" x="442" y="100" font-size="31" fill="#f0f6fc" letter-spacing="-.5">Rules I write before I write code.</text>
    <text class="sgm" x="442" y="124" font-size="14" fill="#8b98a5">Steal the loop. Keep the cryptographic receipts.</text>
  </g>

  {"".join(qcards)}

  <g class="fi" style="animation-delay:.9s">
    <text class="jbb" x="442" y="488" font-size="11" fill="#7ee787" letter-spacing="2.0">TRUST IS A SYSTEM PROPERTY, NOT A PROMPT.</text>
    <text class="jb" x="1228" y="488" font-size="11" fill="#7d8b99" text-anchor="end">&#8212; Muhammad Ashir</text>
  </g>

  <rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="23.25" fill="none" stroke="url(#qedge)" stroke-width="1.5"/>
</g>
</svg>
"""


# ---------------------------------------------------------------------------
# GitHub live metrics fetch (same contract as portrait_sections.py)
# ---------------------------------------------------------------------------
def rest(path: str, token: str):
    headers = {"User-Agent": "animated_scenes.py"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        req = urllib.request.Request(f"https://api.github.com{path}", headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode("utf-8"))
    except (urllib.error.URLError, ValueError, OSError):
        return {}


def refresh_metrics(owner: str, token: str, defaults: dict) -> dict:
    if not owner:
        return dict(defaults)
    metrics = dict(defaults)
    user = rest(f"/users/{owner}", token)
    repos = rest(f"/users/{owner}/repos?per_page=100&type=owner", token)
    if isinstance(user, dict) and user.get("login"):
        metrics["publicRepos"] = user.get("public_repos", metrics["publicRepos"])
    if isinstance(repos, list) and repos:
        metrics["stars"] = sum(r.get("stargazers_count", 0) for r in repos)
    if token:
        query = """query($user:String!){user(login:$user){contributionsCollection{contributionCalendar{
          totalContributions weeks{contributionDays{contributionCount date}}}}}}"""
        req = urllib.request.Request(
            "https://api.github.com/graphql",
            data=json.dumps({"query": query, "variables": {"user": owner}}).encode(),
            headers={
                "User-Agent": "animated_scenes.py",
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read().decode())
            cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
            metrics["contributions"] = cal["totalContributions"]
            days = sorted(
                (d for week in cal["weeks"] for d in week["contributionDays"]),
                key=lambda d: d["date"],
            )
            while days and days[-1]["contributionCount"] == 0:
                days.pop()
            streak = 0
            for day in reversed(days):
                if day["contributionCount"] == 0:
                    break
                streak += 1
            metrics["streak"] = streak
        except Exception:
            pass
    return metrics


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default="assets/sections.json")
    ap.add_argument("--bundle", default="scripts/svg_bundle.json")
    ap.add_argument("--out", default="assets")
    ap.add_argument("--github", default="")
    args = ap.parse_args()

    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    cfg = json.loads(pathlib.Path(args.config).read_text(encoding="utf-8"))
    bundle = json.loads(pathlib.Path(args.bundle).read_text(encoding="utf-8"))
    cfg["metrics"] = refresh_metrics(args.github, os.environ.get("GITHUB_TOKEN", ""), cfg["metrics"])

    pre = bundle.get("chars", {})
    chars = {
        "base": pre.get("base") if Image is None else encode_character(out / "character-signature.png", max_side=460, fallback_uri=pre.get("base", "")),
        "wave": pre.get("wave") if Image is None else encode_character(out / "signature-wave.png", max_side=500, fallback_uri=pre.get("wave", "")),
        "present": pre.get("present") if Image is None else encode_character(out / "signature-present.png", max_side=480, fallback_uri=pre.get("present", "")),
        "flashlight": pre.get("flashlight") if Image is None else encode_character(out / "signature-flashlight.png", max_side=480, fallback_uri=pre.get("flashlight", "")),
        "laptop": pre.get("laptop") if Image is None else encode_character(out / "signature-laptop.png", max_side=480, fallback_uri=pre.get("laptop", "")),
    }

    scenes = [
        ("scene-hero.svg", build_hero),
        ("scene-showcase.svg", build_showcase),
        ("scene-tools.svg", build_tools),
        ("scene-stats.svg", build_stats),
        ("scene-connect.svg", build_connect),
        ("scene-quotes.svg", build_quotes),
    ]

    for filename, fn in scenes:
        svg_text = fn(cfg, bundle, chars)
        dest = out / filename
        dest.write_text(svg_text, encoding="utf-8")
        kb = dest.stat().st_size / 1024.0
        print(f"wrote {dest} ({kb:.1f} KB)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
