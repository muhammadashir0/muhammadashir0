# Muhammad Ashir — Dynamic GitHub Profile Architecture

This repository matches the special GitHub username repository pattern:
`github.com/muhammadashir0/muhammadashir0`. The `README.md` at the root of this repo is automatically rendered on your public GitHub profile.

Inspired by the high-performance aesthetics of top visual engineering profiles, this setup uses **self-hosted CSS/SMIL animated SVG scenes embedding your signature cartoon portraits (`assets/scene-*.svg`)** and **automated GitHub Actions workflows** rather than flat static images or volatile 3rd-party servers.

**Signature idea:** `THE PROOF LOOP` — **INFER → GUARD → ATTEST → SETTLE**. Tagline: *"I turn model output into verifiable action."* Guiding line: *"Trust is a system property, not a prompt."*

---

## What's Included

1. **Animated signature hero (`assets/scene-hero.svg`)**
   - Multi-pose looping character reel (waving, executive portrait, presenting) inside an emerald HUD viewfinder with rotating orbital hexes, holographic scanner line, animated gradient typography, cycling engineering roles, live GitHub stats, and the 4-stage Proof Loop pipeline.
2. **Signature cartoon character renders (`assets/character-signature.png`, `assets/signature-*.png`)**
   - Transparent poses of the same signature character: base portrait, wave, presenting, flashlight and laptop — embedded directly into crisp animated SVG scenes with embedded Space Grotesk + JetBrains Mono WOFF2 fonts.
3. **`~/` whoami Terminal Section + Pulse Dividers (`assets/pulse-*.svg`)**
   - Clean terminal-aesthetic presentation (`$ verify --operator muhammad-ashir --guardrails=strict`) framed by animated cryptographic packet dividers.
4. **`~/` the proof loop (`assets/scene-showcase.svg`)**
   - Floating character presenting your four real shipped repositories mapped across a live orbiting circuit packet loop: Europulse Fraud Guard (`01 · INFER`), MandatePay (`02 · GUARD`), RegLedger AI (`03 · ATTEST`), and Portfolio (`04 · SHOWCASE`).
5. **`~/` signal stack (`assets/scene-tools.svg`)**
   - Animated volumetric torch cone, glowing lens flare, drifting particles, and 20 staggered brand-colored technology chips with real vector logos.
6. **`~/` skill radar**
   - Dual spider/radar charts: core competencies and language/runtime distribution.
7. **`~/` contribution calendar & snake**
   - 3D isometric contribution calendar and the animated contribution snake.
8. **`~/` receipts (`assets/scene-stats.svg`)**
   - Swinging holographic operator clearance badge (drop-in physics, pendulum sway, sweeping foil reflection, orbiting security dot) beside live daily-synced GitHub metrics and animated capability bars.
9. **`~/` selected work**
   - Interactive 2x2 repository card matrix for your four flagship projects.
10. **`~/` open channel (`assets/scene-connect.svg`)**
   - Floating laptop portrait, expanding signal beacon, and pulsing contact cards with nudging arrows.
11. **`~/` field notes (`assets/scene-quotes.svg`)**
   - Three animated engineering doctrine cards beside your signature portrait.

Every animated scene is self-contained inside `assets/scene-*.svg` (embedded fonts, icons, and character art), so animations play natively inside GitHub's README image sandbox on desktop and mobile. Wording, tools, links and quotes live in `assets/sections.json`.

---

## Local Asset Generation

You can regenerate any asset locally with Python:

```bash
# 1. Regenerate Dot-Matrix Portrait
python scripts/dotify.py assets/avatar.png -o assets/portrait --cols 100 --equalize --detail 0.5 --color --reveal

# 2. Regenerate Radar Charts
python scripts/radar.py --data assets/skills.json -o assets/radar
python scripts/radar.py --github muhammadashir0 --fallback assets/languages.json -o assets/radar-langs --limit 7 --values --curve 0.4

# 3. Regenerate Stat & Repo Cards
python scripts/cards.py --user muhammadashir0 --projects assets/projects.json --out assets

# 4. Regenerate the animated signature SVG scenes & motion dividers (needs Pillow)
pip install pillow
python scripts/animated_scenes.py --github muhammadashir0 --out assets
python scripts/animated_dividers.py
```

Open `preview.html` in any browser to inspect all live animated scenes, replay entrance animations, and check radar/repo cards.

---

## GitHub Actions Workflows

This repo includes 4 production-grade GitHub Actions workflows inside `.github/workflows/`:

| Workflow | Frequency | Output |
|---|---|---|
| **Charts and cards (`radar.yml`)** | Daily at 03:30 UTC | Re-renders radar charts, repository star/fork cards, and animated `scene-*.svg` banners |
| **Snake (`snake.yml`)** | Every 12 hours | Generates the animated snake eating your contribution graph |
| **Metrics (`metrics.yml`)** | Every 6 hours | 3D isometric calendar, coding habits, languages, achievements |

### Enabling Automated Actions on GitHub

1. Go to repository **Settings** → **Actions** → **General** → **Workflow permissions**.
2. Select **Read and write permissions** and click **Save**.
3. (Optional for metrics) Go to https://github.com/settings/tokens to generate a Personal Access Token (classic) with `read:user` and `repo` scopes, and add it to repository **Settings** → **Secrets and variables** → **Actions** as **`METRICS_TOKEN`**.
