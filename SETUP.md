# Muhammad Ashir — Dynamic GitHub Profile Architecture

This repository matches the special GitHub username repository pattern:
`github.com/muhammadashir0/muhammadashir0`. The `README.md` at the root of this repo is automatically rendered on your public GitHub profile.

Inspired by the high-performance aesthetics of top visual engineering profiles, this setup uses **locally-hosted, self-rendering SVG assets** and **automated GitHub Actions workflows** rather than volatile 3rd-party servers that suffer from timeouts and 503 errors.

---

## What's Included

1. **Top Dot Matrix Portrait (`assets/portrait.svg`)**
   - Generated from `assets/avatar.png` with `scripts/dotify.py`.
   - Uses `--reveal` sweep scan animation and photorealistic dot-matrix rasterization.
2. **Animated JetBrains Mono Typing Banner**
   - Real-time animated SVG dynamically showcasing engineering identities:
     *Muhammad Ashir · AI Systems Engineer · Financial LLMs & Agentic AI · Secure Autonomous Payments*.
3. **`~/` whoami Terminal Section**
   - Clean terminal-aesthetic presentation (`$ cat about.txt`) highlighting your specialization in agent payments, AI systems, and regulated FinTech.
4. **`~/` toolbox**
   - Clean iconography covering Python, PyTorch, FastAPI, Docker, PostgreSQL, MongoDB, Redis, Linux, Bash, and modern AI engineering tools.
5. **`~/` skill radar**
   - Dual spider/radar charts:
     - **Skill Radar**: Core competencies (AI Systems, Financial ML, Policy-as-Code, LLM Evals & RAG, Python/PyTorch, APIs, Audit & Security).
     - **Language & Stack Radar**: Language and runtime distributions.
6. **`~/` contribution calendar & snake**
   - 3D Isometric contribution calendar (`assets/metrics.isocalendar.svg`).
   - GitHub contribution snake animation (`snake.svg` on `output` branch).
7. **`~/` the numbers**
   - Self-hosted stat card (`assets/card-stats-dark.svg`, `assets/card-stats-light.svg`).
   - Language breakdown bar (`assets/metrics.languages.svg`).
   - Verifiable achievement badges (`assets/metrics.achievements.svg`).
8. **`~/` selected work**
   - Interactive 2x2 repository card matrix featuring:
     - **MandatePay** (Agent Payments Authorization Firewall)
     - **RegLedger AI** (Evidence-First AML Compliance Copilot)
     - **FinEval Arena** (Financial LLM Benchmark & Red-Teaming Harness)
     - **CovenantGraph** (Temporal Debt Agreement Intelligence)

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
```

Open `preview.html` in any browser to inspect the dark and light mode SVGs and replay the dot-matrix load-in sweep scan.

---

## GitHub Actions Workflows

This repo includes 3 production-grade GitHub Actions workflows inside `.github/workflows/`:

| Workflow | Frequency | Output |
|---|---|---|
| **Charts and cards (`radar.yml`)** | Daily at 03:30 UTC | Re-renders radar charts and repository star/fork cards |
| **Snake (`snake.yml`)** | Every 12 hours | Generates the animated snake eating your contribution graph |
| **Metrics (`metrics.yml`)** | Every 6 hours | 3D isometric calendar, coding habits, languages, achievements |

### Enabling Automated Actions on GitHub

1. Go to repository **Settings** → **Actions** → **General** → **Workflow permissions**.
2. Select **Read and write permissions** and click **Save**.
3. (Optional for metrics) Go to https://github.com/settings/tokens to generate a Personal Access Token (classic) with `read:user` and `repo` scopes, and add it to repository **Settings** → **Secrets and variables** → **Actions** as **`METRICS_TOKEN`**.
