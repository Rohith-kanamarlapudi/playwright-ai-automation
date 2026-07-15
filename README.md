<div align="center">

# 🎭 Playwright AI Automation

### *Give it a URL. Walk away. Come back to a fully executed, self-healing test suite.*

No manual scripting. No guessed selectors. No brittle assertions on live data.

Point it at any web app and **six specialised AI agents** take over — scraping real DOM selectors, planning a test strategy, generating and self-reviewing Playwright scripts, hardening for edge cases, executing via pytest, **automatically healing failures**, and shipping JSON/HTML reports backed by a persistent run history database.

**Stress-tested on a production IoT dashboard SPA with real-time WebSocket sensor data** — not a toy demo app.
[`live.ideabytesiot.com/demolive`](https://live.ideabytesiot.com/demolive)

<br/>

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white&style=for-the-badge)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white&style=for-the-badge)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-1C3C3C?style=for-the-badge)](https://www.langchain.com/langgraph)
[![Playwright](https://img.shields.io/badge/Playwright-Test%20Engine-2EAD33?logo=playwright&logoColor=white&style=for-the-badge)](https://playwright.dev/)
[![DeepSeek](https://img.shields.io/badge/DeepSeek-LLM-4D6BFE?style=for-the-badge)](https://www.deepseek.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white&style=for-the-badge)](https://www.docker.com/)
[![CI](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?logo=githubactions&logoColor=white&style=for-the-badge)](https://github.com/Rohith-kanamarlapudi/playwright-ai-automation/actions)

</div>

---

### 📌 Jump to

[What Is This](#-what-is-this) · [Pipeline](#-pipeline-at-a-glance) · [Key Features](#-key-features) · [Architecture](#️-architecture) · [Built for Live IoT](#-built-for-the-live-iot-dashboard) · [Use Case Flow](#-use-case-flow) · [Project Structure](#️-project-structure) · [Tech Stack](#️-tech-stack) · [Getting Started](#-getting-started) · [Docker](#-run-with-docker) · [Security](#-security) · [Output Reports](#-output-reports) · [Roadmap](#️-roadmap) · [Contributors](#-contributors)

---

## 🧭 What Is This?

**Playwright AI Automation** is a multi-agent AI system built during an internship at [Ideabytes, Hyderabad](https://ideabytes.com). It automates the *entire* lifecycle of web test engineering — from crawling a live application's real DOM, to delivering an executed, self-healed, performance-profiled test report — without a human writing a single test case.

Most "AI writes your tests" tools stop at generation. This one doesn't get to call itself done until the tests have actually *run* against a live target — and if they fail, a dedicated **Healing Agent** reads the real pytest error output and patches the broken selectors and assertions automatically, then re-runs. The system was built and proven against a real production system: **`live.ideabytesiot.com/demolive`**, a client-facing IoT dashboard SPA with live WebSocket sensor feeds and auto-refreshing charts. That meant the pipeline had to survive genuinely hard conditions — SPA hydration delays, sensor readings that change every few seconds, WebSocket-driven widgets, and rate limiting from a live server that couldn't be hammered.

Rather than betting everything on one fragile LLM call, the work is split across **six specialised agents**, each owning one phase of professional QA engineering. They share a typed state contract, reason out loud in `<think>` blocks before acting, and the pipeline self-corrects — a review agent triggers bounded regeneration whenever quality falls short, and the healing agent closes the loop when tests actually fail at runtime. Every run is stored in a **persistent SQLite database** so you can track pass rates over time and query historical results via the API.

> **The bottom line:** hand it a URL, get back a tested, self-healed, reported, and performance-profiled test suite — with full run history — no scripting required.

---

## ⚡ Pipeline at a Glance

```
  Your live app URL
        │
        ▼
  ┌─────────────┐    requests + BeautifulSoup  (static pages)
  │   Scraper   │ ──────────────────────────────────────────►  Real DOM selectors
  │             │    Playwright headless fallback  (SPAs)       (memory-scored)
  └─────────────┘
        │
        ▼
  ┌──────────────────────────────────────────────────────────────────┐
  │                      LangGraph Pipeline                          │
  │                                                                  │
  │   Strategy ──► Architecture ──► Code Gen ──► Review              │
  │                                     ▲            │               │
  │                                     └─── regen ──┘  (max 2)      │
  │                                          if High risk            │
  │                                                 ▼                │
  │                                          Edge Cases              │
  │                                                 ▼                │
  │                                           Heal Agent ◄── failures│
  └──────────────────────────────────────────────────────────────────┘
        │
        ▼
  ┌─────────────┐    AST safety check → pytest execution
  │ Test Runner │ ──────────────────────────────────────────►  Pass / Fail
  └─────────────┘    60s timeout · SPA-aware fixtures              │
        │                                                           │
        ▼                                                           ▼
  JSON · HTML · TTFB baseline · Sitemap             SQLite run history + selector memory
```

---

## ✨ Key Features

| | Feature | What it does |
|---|---|---|
| 🧠 | **6-Agent Pipeline** | Strategy, Architecture, Code Gen, Review, Edge Cases, and Heal agents share a typed `AgentState` — every agent reads from and writes back to the same state |
| 🩹 | **Self-Healing Tests** | Heal Agent reads real pytest `FAILED` output, parses every failure, and asks the LLM to patch broken selectors and assertions — automatically, no human intervention |
| 🗄️ | **Run History Database** | Every pipeline run stored in SQLite — start time, pass/fail counts, generated code, regen count — queryable via `/runs` and `/runs/{id}` API endpoints |
| 🐳 | **Docker Ready** | `docker compose up api` — full system running with Playwright browsers pre-installed and reports persisted on a volume. No local Python or Node.js required |
| 🎯 | **Selector Memory** | SQLite tracks which selectors pass and fail across runs; `selector_utils.py` applies historical stability scores to boost reliable selectors and deprioritise known-broken ones |
| 🌐 | **Live SPA Support** | Playwright headless fallback handles SPAs that return empty shells to requests crawlers; `networkidle` waits and `data-testid`/`aria-label` prioritisation keep extraction stable |
| 🪄 | **Think-Tag Scaffolding** | Agents reason in `<think>` blocks before producing output — fewer hallucinated selectors, better test plans |
| 🔁 | **Bounded Self-Review Loop** | Review Agent parses its own structured output and sets `needs_regen`; LangGraph conditional edge routes back to Code Gen automatically (max 2 passes) |
| ✅ | **YAML Validation Layer** | Code Gen produces YAML first, validates structure (required fields, non-empty steps, no duplicate IDs), then converts via `yaml_to_playwright.py`; direct Python fallback if YAML fails |
| 🔒 | **AST Safety Check** | Every generated `.py` inspected with Python's `ast` before execution — `import os`, `subprocess`, `eval`, `exec` are blocked and flagged for regen |
| 🛡️ | **Prompt Injection Guard** | `doc_sanitiser.py` strips injection patterns, enforces size limits, and escapes HTML before any uploaded doc enters a prompt |
| 🕷️ | **Selector-Grounded Tests** | Real DOM elements scraped from the live app; `selector_utils.py` ranks by memory-weighted stability and caps with logged drop counts — no guessed selectors |
| 📊 | **Dual Performance Tracking** | `psutil` per-agent metrics + a live TTFB/load-time crawler that hits real routes across 3 consecutive runs |
| 🧪 | **SPA-Aware Execution** | `conftest.py` auto-generated per run with `wait_for_widget()` and `wait_for_live_data()` helpers; 60s subprocess timeout guard |
| 📄 | **Rich Reports** | `test_execution_report.json`, `test_execution_report.html`, `live_perf_baseline.json`, `live_sitemap.md` — every run |
| 🔑 | **Fail-Closed FastAPI Auth** | Auto-generates an `APP_API_KEY` at startup if none is configured — endpoints are never accidentally open. `ALLOW_UNAUTHENTICATED=true` explicitly opts out for local dev |
| ⚙️ | **CI/CD** | GitHub Actions — import smoke, unit tests, pipeline regression, YAML validation, selector quality checks, and artifact upload on every push and PR |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         FastAPI Layer                            │
│   POST /upload-doc      POST /agents/run      GET /runs          │
│   (X-API-Key protected) (X-API-Key protected) GET /runs/{id}     │
└──────────────────┬───────────────────────────────────────────────┘
                   │ design_doc + target_url
                   ▼
┌──────────────────────────────────────────────────────────────────┐
│                     Scraper + Sanitiser                          │
│  scraper.py (requests + BS4)  ──►  playwright_check.py (SPA)     │
│  login.py (Keycloak auth)     ──►  scraper_adapter.py            │
│  doc_sanitiser.py (injection guard)                              │
│  selector_utils.py (memory-weighted stability ranking)           │
└──────────────────┬───────────────────────────────────────────────┘
                   │ selectors[] (memory-scored) · clean design_doc
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LangGraph Pipeline                         │
│   AgentState (TypedDict) ── shared typed contract               │
│                                                                 │
│   ┌──────────┐  ┌──────────────┐  ┌──────────┐  ┌────────┐      │
│   │ Strategy │─►│ Architecture │─►│ Code Gen │─►│ Review │      │
│   └──────────┘  └──────────────┘  └──────────┘  └───┬────┘      │
│                                         ▲  regen      │         │
│                                         └─────────────┘ (max 2) │
│                                                       ▼         │
│                                            ┌──────────────┐     │
│                                            │  Edge Cases  │     │
│                                            └──────┬───────┘     │
│                                                   ▼             │
│                                            ┌──────────────┐     │
│                                            │  Heal Agent  │◄── failures
│                                            └──────┬───────┘     │
└───────────────────────────────────────────────────┼─────────────┘
                                                     │ generated_code (healed)
                                                     ▼
┌──────────────────────────────────────────────────────────────────┐
│                       Execution Layer                            │
│   AST check → conftest gen → pytest subprocess (60s cap)         │
│   Performance Engine (psutil) + Live TTFB Crawler (3-run avg)    │
└──────────────────┬───────────────────┬───────────────────────────┘
                   ▼                   ▼
        ┌──────────────────┐  ┌────────────────────────────┐
        │   Output Layer   │  │    Persistence Layer       │
        │  report.json     │  │  SQLite: runs table        │
        │  report.html     │  │  SQLite: selector_memory   │
        │  perf_baseline   │  │  Queryable via /runs API   │
        │  live_sitemap    │  └────────────────────────────┘
        └──────────────────┘
```

---

## 🌐 Built for the Live IoT Dashboard

The pipeline's primary target is **[`live.ideabytesiot.com/demolive`](https://live.ideabytesiot.com/demolive)** — a production IoT dashboard SPA with live WebSocket sensor feeds and auto-refreshing charts. Nothing here was designed in the abstract; every decision traces back to a real problem this specific app forced the pipeline to solve.

| Production Challenge | How the Pipeline Solves It |
|---|---|
| 🖥️ **JS-only rendering** | Playwright headless fallback waits for `networkidle` before scraping — no empty shells |
| 📡 **Live data changes every run** | All assertions check **structure** (`to_be_visible`) — never exact values (`to_have_text("23.5°C")`) |
| 🔌 **WebSocket-driven widgets** | `wait_for_live_data()` in auto-generated `conftest.py` waits for first WS data push |
| 📈 **Auto-refreshing charts** | `wait_for_widget()` waits for spinners/skeletons to disappear before asserting |
| 🚦 **Rate limiting** | 2s throttle between crawler requests — never hammers the live server |
| 🔐 **Auth-gated routes** | `scraper/login.py` handles Keycloak sessions; credentials live in `.env`, never committed |
| 🎯 **Unstable live DOM** | `data-testid` → `aria-label` → `#id` → `input[name]` → text-based (last resort) — further weighted by selector memory scores from previous runs |
| 🩹 **Flaky test failures** | Heal Agent reads actual pytest `FAILED` output, patches selectors/timeouts/assertions with LLM, re-runs automatically |
| ⚠️ **IoT failure modes** | Edge Cases Agent reasons about sensor offline, stale timestamps, empty charts, WS disconnect, mid-refresh navigation |

---

## 🎯 Use Case Flow

Eleven stages, one command. Here's what happens between the URL going in and the report coming out:

| Stage | Component | What Happens |
|---|---|---|
| 1️⃣ | **Live App / Design Doc** | Target URL or uploaded requirements handed to the pipeline |
| 2️⃣ | **Scraper + SPA Fallback** | Real DOM scraped; Playwright headless takes over for JS-rendered content |
| 3️⃣ | **Doc Sanitiser** | Uploaded docs stripped of injection patterns before touching any LLM |
| 4️⃣ | **Strategy Agent** | Selector-grounded test plan — tasks mapped to real DOM elements, ranked by selector memory |
| 5️⃣ | **Architecture Agent** | POM framework designed around the live app's actual component structure |
| 6️⃣ | **Code Gen Agent** | YAML → validated → Playwright Python; triple-checked (syntax + AST + assertions) |
| 7️⃣ | **Review Agent** | Structured quality review — routes back to Code Gen if High risk (max 2 passes) |
| 8️⃣ | **Edge Cases Agent** | IoT edge cases hardened with `<think>` scaffolding |
| 9️⃣ | **Heal Agent** | Reads real pytest failures, patches broken selectors/assertions with LLM, updates generated code |
| 🔟 | **AST Check + Test Executor** | Safety gate → pytest with SPA-aware browser fixtures |
| ✅ | **Reports + Run History** | JSON/HTML results + TTFB baseline + sitemap + SQLite run record stored for trend analysis |

---

## 🗂️ Project Structure

```
playwright-ai-automation/
│
├── agents/                        # Six LangGraph agents + all shared utilities
│   ├── state.py                   # AgentState TypedDict — typed contract between all agents
│   ├── strategy_agent.py          # Selector-grounded test strategy and task planning
│   ├── architecture_agent.py      # POM framework design from live app structure
│   ├── code_gen_agent.py          # YAML → validate → Playwright Python; triple safety checks
│   ├── review_agent.py            # Structured review + needs_regen + bounded regen loop
│   ├── edge_cases_agent.py        # IoT edge cases with <think> scaffolding
│   ├── heal_agent.py              # Parses pytest failures → LLM patches selectors/assertions
│   ├── llm_client.py              # DeepSeek — lazy init, model validation, unknown-model guard
│   ├── selector_utils.py          # Memory-weighted stability ranking, configurable cap, drop logging
│   ├── scraper_adapter.py         # Flattens multi-page crawl into AgentState selectors[]
│   ├── doc_sanitiser.py           # Strips prompt injection from uploaded docs
│   ├── popup_sanitizer.py         # Handles popup/modal interference during scraping
│   ├── python_fallback.py         # Direct Python generation when YAML path fails
│   ├── pipeline.py                # Single callable entry point (FastAPI + CLI)
│   └── prompts/                   # One prompt file per agent — safe to iterate independently
│       ├── strategy_prompt.py
│       ├── yaml_prompt.py
│       └── code_gen_prompt.py
│
├── app/                           # FastAPI application
│   ├── main.py                    # /upload-doc + /agents/run + /runs (API key protected)
│   ├── llm_generator.py           # DeepSeek direct call — fallback path
│   ├── yaml_validator.py          # Structural YAML validation before code gen
│   ├── yaml_to_playwright.py      # 30+ YAML step keywords → Playwright Python
│   ├── static/style.css           # Styled report UI
│   └── templates/                 # Jinja2 index + results pages
│
├── db/                            # Persistent run history and selector memory
│   ├── database.py                # SQLite CRUD — start_run(), finish_run(), get_runs()
│   ├── models.py                  # CREATE TABLE schema for runs
│   └── selector_memory.py         # Per-selector pass/fail history + stability scoring
│
├── scraper/                       # Live app DOM extraction
│   ├── scraper.py                 # requests + BeautifulSoup multi-page crawler
│   ├── playwright_check.py        # Playwright headless fallback for Angular/React SPAs
│   └── login.py                   # Keycloak session handling for auth-gated routes
│
├── performance/                   # Two-layer performance tracking
│   ├── engine.py                  # psutil per-agent CPU/memory/throughput
│   ├── live_crawler.py            # Real TTFB + load time per route (3-run avg)
│   └── benchmark.py               # Benchmarking utilities
│
├── tests/                         # The framework tests itself
│   ├── test_core.py               # yaml_validator · selector_utils · scraper_adapter
│   └── test_sanitiser.py          # doc_sanitiser injection and truncation tests
│
├── notes/                         # Live app discovery and run logs
│   ├── day11_discovery.md
│   ├── day13_pipeline_run.md
│   └── live_app_design_doc.md
│
├── .github/workflows/ci.yml       # CI: imports · unit tests · pipeline regression · YAML + selector validation · artifact upload
├── Dockerfile                     # Production image with Playwright browsers pre-installed
├── docker-compose.yml             # api service + pipeline service (--profile run)
├── .dockerignore
├── run_pipeline.py                # CLI: --url --max-pages → scrape → agents → pytest → report
├── llm_playwright_generator.py    # Wrapper: reads scraper JSON → runs agent pipeline
├── test_runner.py                 # AST check → subprocess pytest → stdout/stderr capture
├── report_generator.py            # Assembles JSON + HTML from execution results
├── main.py                        # LangGraph graph: 6 nodes, edges, conditional routing
├── pytest.ini                     # testpaths, asyncio_mode, custom marks
├── requirements.txt               # Pinned versions
└── .env.example
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Agent Orchestration** | LangGraph — `StateGraph`, conditional edges, 6-node bounded pipeline |
| **LLM** | DeepSeek `deepseek-chat` / `deepseek-reasoner` via OpenAI-compatible API |
| **API / Backend** | FastAPI + Jinja2 (fail-closed API key auth) |
| **Test Automation** | Playwright (sync API) + pytest |
| **Web Scraping** | requests + BeautifulSoup + Playwright headless (SPA + Keycloak auth fallback) |
| **Persistence** | SQLite — run history DB + per-selector memory scoring |
| **Performance** | psutil (agent metrics) · requests TTFB crawler (live routes) |
| **Security** | Python AST inspection · prompt injection sanitiser · fail-closed API key auth · subprocess timeout |
| **Containerisation** | Docker + docker-compose |
| **Reporting** | JSON · styled HTML · Markdown sitemap |
| **CI** | GitHub Actions — smoke · unit tests · pipeline regression · artifact upload |
| **Language** | Python 3.11+ |

---

## 🚀 Getting Started

You'll be running your first AI-generated, self-healed test suite in about five minutes.

### Prerequisites

- Python 3.10+
- Node.js *(Playwright's browser binaries need it)*
- A [DeepSeek API key](https://platform.deepseek.com) — `deepseek-chat` model

### 1. Clone & Install

```bash
git clone https://github.com/Rohith-kanamarlapudi/playwright-ai-automation.git
cd playwright-ai-automation

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
playwright install chromium
```

### 2. Configure

```bash
cp .env.example .env
```

```env
# ── LLM ──────────────────────────────────────────────────────
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com

# ── Target application ────────────────────────────────────────
TARGET_URL=https://live.ideabytesiot.com/demolive
BASE_URL=https://live.ideabytesiot.com/demolive
MAX_PAGES=10

# ── Scraper tuning ────────────────────────────────────────────
SELECTOR_CAP=25          # raise for large SPAs
SPA_WAIT_TIMEOUT=15000   # ms — SPA hydration wait

# ── FastAPI auth ──────────────────────────────────────────────
APP_API_KEY=your-secret-key      # auto-generated at startup if not set
ALLOW_UNAUTHENTICATED=false      # true for local dev only

# ── Run History ───────────────────────────────────────────────
DB_PATH=db/runs.db               # SQLite database path
```

### 3. Run

```bash
# Full pipeline against the live IoT dashboard
python run_pipeline.py --url https://live.ideabytesiot.com/demolive --max-pages 7

# Against any other target
python run_pipeline.py --url https://your-app.com --max-pages 5

# Web interface (upload a design doc)
uvicorn app.main:app --reload
# → http://localhost:8000

# Query run history
curl http://localhost:8000/runs -H "X-API-Key: your-key"

# Framework unit tests
pytest tests/ test_llm.py test_prompts.py -v
```

---

## 🐳 Run with Docker

No Python, no Node.js, no `playwright install` — just Docker.

```bash
cp .env.example .env   # add your DEEPSEEK_API_KEY

# Start the web interface
docker compose up api

# Run the full pipeline (one-shot)
docker compose --profile run up pipeline
```

Reports and the run history database are persisted on host volumes — they survive container restarts.

---

## 🔒 Security

> The pipeline executes LLM-generated Python. Every layer is hardened against the worst case.

| Layer | Protection |
|---|---|
| **AST Safety Check** | Generated `.py` parsed with `ast` before execution — blocks `import os/subprocess`, `eval()`, `exec()`, `__import__()`. Returns code `-2` and flags for regen. |
| **Prompt Injection Guard** | `doc_sanitiser.py` strips `"Ignore all previous instructions"` and similar, enforces 8000-char limit, removes HTML tags. All warnings logged. |
| **Fail-Closed API Auth** | Auto-generates an `APP_API_KEY` at startup if none is configured — endpoints are never accidentally open. Set `ALLOW_UNAUTHENTICATED=true` to explicitly opt out for local dev. |
| **Subprocess Timeout** | `subprocess.TimeoutExpired` kills generated tests after 60 seconds — no hanging pipelines. |
| **Auth Credential Safety** | Session cookies and Keycloak login state live in `.env` and `/tmp/` — never committed to git. `auth.json` is gitignored. |
| **Rate Throttling** | 2s sleep between live crawler requests — production servers stay unharmed. |

---

## 📊 Output Reports

Every pipeline run produces a full set of reports in `reports/` and a permanent record in the run history DB:

| Output | Format | Contents |
|---|---|---|
| `test_execution_report.json` | JSON | Tests run · passed · failed · execution time · stdout/stderr |
| `test_execution_report.html` | HTML | Styled, browser-viewable test report |
| `perf_baseline.json` | JSON | Per-agent CPU % · memory MB · throughput (agents/sec) |
| `live_perf_baseline.json` | JSON | 3-run TTFB and load-time averages per live route |
| `live_sitemap.md` | Markdown | Route map with load-time labels — ready for demo slides |
| `per_agent_perf.json` | JSON | Individual timing breakdown per agent |
| **SQLite `runs` table** | DB | Full run history — queryable via `/runs` and `/runs/{id}` |
| **SQLite `selector_memory`** | DB | Per-selector pass/fail history — feeds stability scoring on the next run |

---

## 🗺️ Roadmap

**Shipped ✅**

- [x] 6-agent LangGraph pipeline — Strategy → Architecture → Code Gen → Review → Edge Cases → **Heal**
- [x] Self-healing test loop — Heal Agent parses real pytest failures and patches selectors/assertions automatically
- [x] SQLite run history database — every run stored, queryable via `/runs` and `/runs/{id}` REST API
- [x] Selector memory — cross-run stability scoring boosts reliable selectors on every subsequent run
- [x] Docker + docker-compose — one-command setup, Playwright browsers pre-installed, reports persisted
- [x] YAML validation layer before code generation
- [x] Bounded self-review loop — conditional graph edge, max 2 regen passes
- [x] AST safety check on all generated test files
- [x] Prompt injection protection for uploaded documents
- [x] Memory-weighted selector stability ranking, configurable cap, drop-count logging
- [x] YAML → Playwright converter with 30+ step keyword patterns
- [x] SPA-aware scraping with Playwright headless fallback + Keycloak auth support
- [x] Structural assertions for live data (presence over exact values)
- [x] SPA wait helpers auto-injected into every generated `conftest.py`
- [x] Live-site TTFB performance baseline (3-run average per route)
- [x] IoT-specific edge case prompting (sensor offline, WS disconnect, stale data, empty charts)
- [x] Fail-closed FastAPI API key authentication (auto-generates key at startup)
- [x] GitHub Actions CI — smoke · unit tests · pipeline regression · YAML + selector validation · artifact upload
- [x] Full end-to-end validation on `live.ideabytesiot.com/demolive`

**Coming next 🔜**

- [ ] Multi-LLM backend support (OpenAI, Anthropic, Ollama, Gemini) via `LLM_PROVIDER` env var
- [ ] Visual regression testing — pixel-diff screenshots between runs
- [ ] Webhook notifications — push results to Slack / Teams on run completion
- [ ] Plugin system — drop a `.py` in `plugins/` to add custom agents without modifying core
- [ ] Accessibility audit agent (axe-core via Playwright)

---

## 👥 Contributors

Built during an **AI Agents Developer Internship at [Ideabytes](https://ideabytes.com), Hyderabad.**

<br/>

**Rohith Kanamarlapudi** — [@Rohith-kanamarlapudi](https://github.com/Rohith-kanamarlapudi)

> LangGraph multi-agent pipeline architecture · 6-agent graph design with conditional routing · self-healing test loop (Heal Agent — parses pytest failures, LLM-patches selectors & assertions automatically) · SQLite run history database (`db/database.py`, `db/models.py`) + `/runs` REST API · selector memory system (`db/selector_memory.py`) with cross-run stability scoring · Docker containerisation (`Dockerfile`, `docker-compose.yml`) · agent prompt engineering & think-tag scaffolding · YAML tooling (`yaml_validator`, `yaml_to_playwright` — 30+ step patterns, locator & assertion fixes) · bounded self-review loop with conditional graph routing · AST safety layer · prompt injection protection (`doc_sanitiser.py`) · memory-weighted selector prioritisation & cap logging (`selector_utils.py`) · performance engine (psutil metrics + live TTFB crawler) · SPA-aware conftest generation with IoT wait helpers · structural assertion mode for live data · IoT edge case prompting · CI/CD pipeline (GitHub Actions — smoke, unit, regression, selector validation, artifact upload) · fail-closed FastAPI auth · live app adaptation & hardening

<br/>

**Harshith Kanamarlapudi** — [@harshithnova](https://github.com/harshithnova)

> Playwright scraper & SPA hydration fallback (`playwright_check.py`) · Keycloak auth session handling (`scraper/login.py`) · FastAPI application & upload endpoint · LLM generator · test runner · HTML/JSON report generation · dynamic element handling for live IoT widgets · popup/modal interference handling (`popup_sanitizer.py`) · multi-page crawl execution & retry logic · flake handling for live-data non-determinism · final report addendum · pipeline orchestration