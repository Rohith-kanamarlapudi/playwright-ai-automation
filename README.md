<div align="center">

# 🎭 Playwright AI Automation

### *Give it a URL. Walk away. Come back to a fully executed, self-healing test suite.*

No manual scripting. No guessed selectors. No brittle assertions on live data.

Point it at any web app and **six specialised AI agents** take over — scraping real DOM selectors, planning a test strategy, generating validated Playwright scripts from structured YAML scenarios, self-reviewing and healing failures, executing via pytest, and shipping JSON/HTML reports backed by a persistent run history database and agent observability traces.

**Stress-tested on a production Angular IoT dashboard with Keycloak auth, real-time WebSocket sensor data, and 7 modules (Dashboard, Reports, Alerts, Devices, Alarms, Users, Settings)** — not a toy demo app.
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

[What Is This](#-what-is-this) · [Pipeline](#-pipeline-at-a-glance) · [Key Features](#-key-features) · [Architecture](#️-architecture) · [Live IoT Target](#-built-for-the-live-iot-dashboard) · [Scenarios](#-test-scenarios) · [Use Case Flow](#-use-case-flow) · [Project Structure](#️-project-structure) · [Tech Stack](#️-tech-stack) · [Getting Started](#-getting-started) · [Docker](#-run-with-docker) · [Security](#-security) · [Outputs](#-output-reports) · [Roadmap](#️-roadmap) · [Contributors](#-contributors)

---

## 🧭 What Is This?

**Playwright AI Automation** is a multi-agent AI system built during an internship at [Ideabytes, Hyderabad](https://ideabytes.com). It automates the *entire* lifecycle of web test engineering — from crawling a live application's real DOM, through six specialised AI agents, to a self-healed, reported, and performance-profiled test suite — with no manual test writing.

The system is built around **YAML test scenarios** (`scenarios/`) as its structured intermediate format. Agents produce YAML, the YAML is validated for structure, and `yaml_to_playwright.py` converts it to executable Python. The pipeline doesn't stop at generation — a dedicated **Heal Agent** reads real pytest failures and patches broken selectors and assertions automatically. Every run is stored in a **SQLite run history database** and fully traced in `traces.jsonl` via **AgentLens observability**.

The primary target is **`live.ideabytesiot.com/demolive`** — a production Angular SPA with Keycloak authentication, live WebSocket sensor feeds, auto-refreshing IoT widgets across 7 modules, and real device data that changes every few seconds.

> **The bottom line:** give it a URL, get back a tested, self-healed, reported test suite — with full run history and agent traces.

---

## ⚡ Pipeline at a Glance

```
  Your live app URL
        │
        ▼
  ┌─────────────┐    requests + BeautifulSoup  (static)
  │   Scraper   │ ──────────────────────────────────────►  Real DOM selectors
  │             │    Playwright headless + Keycloak auth    (memory-scored)
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
        │                                              │
        ▼                                              ▼
  ┌─────────────┐    AST check → pytest          traces.jsonl
  │ Test Runner │ ────────────────────────►      agentlens.db
  └─────────────┘    SPA-aware fixtures          (observability)
        │
        ▼
  JSON · HTML · TTFB baseline · Sitemap · SQLite run history
```

---

## ✨ Key Features

| | Feature | What it does |
|---|---|---|
| 🧠 | **6-Agent Pipeline** | Strategy → Architecture → Code Gen → Review → Edge Cases → Heal share a typed `AgentState` |
| 🩹 | **Self-Healing Tests** | Heal Agent parses real pytest `FAILED` output and LLM-patches broken selectors and assertions automatically |
| 📋 | **YAML Scenario Library** | 6 pre-built scenarios (`scenarios/`) covering Login, Logout, Signup, Search, Checkout, Profile — ready to run or extend |
| 🔍 | **Agent Observability** | `traces.jsonl` and `agentlens.db` record every agent invocation, input, output, and timing — full pipeline auditability |
| 🗄️ | **Run History Database** | Every run stored in SQLite — start time, pass/fail counts, generated code, regen count — queryable via `/runs` and `/runs/{id}` |
| 🐳 | **Docker Ready** | `docker compose up api` — full system with Playwright browsers pre-installed, no local setup needed |
| 🎯 | **Selector Memory** | SQLite tracks pass/fail history per selector; future runs boost stable selectors and deprioritise known-broken ones |
| 🌐 | **Live SPA + Auth Support** | Playwright headless fallback for Angular SPAs; Keycloak session handling for auth-gated routes via `scraper/login.py` |
| 🪄 | **Think-Tag Scaffolding** | Agents reason in `<think>` blocks before acting — fewer hallucinated selectors, better test plans |
| 🔁 | **Bounded Self-Review Loop** | Review Agent parses structured output and sets `needs_regen`; LangGraph conditional edge routes back to Code Gen (max 2 passes) |
| ✅ | **YAML Validation Layer** | Code Gen produces YAML → validated (required fields, non-empty steps, no duplicate IDs) → converted via `yaml_to_playwright.py` (30+ step patterns) |
| 🔒 | **AST Safety Check** | Every generated `.py` inspected before execution — `import os/subprocess`, `eval`, `exec` are blocked |
| 🛡️ | **Prompt Injection Guard** | `doc_sanitiser.py` strips injection patterns and enforces size limits before any doc enters a prompt |
| 📊 | **Dual Performance Tracking** | `psutil` per-agent metrics + live TTFB/load-time crawler (3-run average) |
| 🧪 | **SPA-Aware Execution** | Auto-generated `conftest.py` with `wait_for_widget()` and `wait_for_live_data()` helpers; 60s subprocess timeout |
| 🔑 | **Fail-Closed FastAPI Auth** | Auto-generates `APP_API_KEY` at startup if none configured; `ALLOW_UNAUTHENTICATED=true` opts out for local dev |
| ⚙️ | **CI/CD** | GitHub Actions — import smoke, unit tests, pipeline regression, YAML + selector validation, artifact upload |

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
│                  Scraper + Auth + Sanitiser                      │
│  scraper.py (requests + BS4)  ──►  playwright_check.py (SPA)     │
│  login.py (Keycloak session)  ──►  scraper_adapter.py            │
│  doc_sanitiser.py             ──►  selector_utils.py             │
│  selector_memory.py (stability scoring from SQLite history)      │
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
│                                         ▲  regen      │ (max 2) │
│                                         └─────────────┘         │
│                                                       ▼         │
│                                       ┌───────────────────┐     │
│                                       │    Edge Cases     │     │
│                                       └────────┬──────────┘     │
│                                                ▼                │
│                                       ┌───────────────────┐     │
│                                       │    Heal Agent     │◄─── pytest failures
│                                       └────────┬──────────┘     │
└────────────────────────────────────────────────┼────────────────┘
                                                  │ generated_code (healed)
                     ┌────────────────────────────┤
                     ▼                            ▼
          ┌──────────────────┐        ┌───────────────────────┐
          │  Execution Layer │        │  Observability Layer  │
          │  AST check       │        │  traces.jsonl         │
          │  conftest gen    │        │  agentlens.db         │
          │  pytest (60s)    │        │  per-agent timing     │
          └──────────┬───────┘        └───────────────────────┘
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
┌──────────────────┐  ┌──────────────────────────┐
│   Output Layer   │  │    Persistence Layer     │
│  report.json     │  │  SQLite: runs table      │
│  report.html     │  │  SQLite: selector_memory │
│  perf_baseline   │  │  Queryable via /runs API │
│  live_sitemap    │  └──────────────────────────┘
└──────────────────┘
```

---

## 🌐 Built for the Live IoT Dashboard

Every decision in this pipeline traces back to a real problem the live target forced it to solve. This is not a theoretical framework — it ran against a production Angular SPA with real Keycloak auth.

| Production Challenge | How the Pipeline Solves It |
|---|---|
| 🔐 **Keycloak auth (real session required)** | `scraper/login.py` handles Keycloak auth flow; `test_auth.py` validates session before the main scrape |
| 🖥️ **Angular SPA (JS-only rendering)** | Playwright headless fallback waits for `networkidle`; `playwright_check.py` extracts real post-hydration selectors |
| 📡 **Live sensor data changes every run** | All assertions check **structure** (`to_be_visible`) — never exact values (`to_have_text("23.5°C")`) |
| 🔌 **WebSocket-driven widgets** | `wait_for_live_data()` in auto-generated `conftest.py` waits for first WS data push |
| 📈 **Auto-refreshing charts** | `wait_for_widget()` waits for spinners/skeletons to disappear before asserting |
| 📋 **7 distinct app modules** | `scenarios/` contains one YAML scenario per module — Login, Logout, Signup, Search, Checkout, Profile |
| 🧪 **Selector stability across runs** | `test_selector_stability.py` runs 3 consecutive scrapes and compares selector counts; `selector_memory.py` records history |
| 🚦 **Rate limiting from live server** | 2s throttle between crawler requests; `test_live_scraper.py` validates multi-page crawl behaviour |
| ⚠️ **IoT-specific failure modes** | Edge Cases Agent reasons about sensor offline, stale timestamps, empty charts, WS disconnect, mid-refresh navigation |

---

## 📋 Test Scenarios

The `scenarios/` directory contains six validated YAML test scenarios pre-built for the live IoT dashboard. Each maps to a core user journey and can be run directly via the pipeline or extended for new targets.

| Scenario | File | Covers |
|---|---|---|
| 🔑 **Login** | `pw_generate_login_test.yaml` | Keycloak authentication, dashboard redirect, session validation |
| 🚪 **Logout** | `pw_generate_logout_test.yaml` | Session termination, redirect to login, protected route blocking |
| 📝 **Signup** | `pw_generate_signup_test.yaml` | User registration flow, form validation, error handling |
| 🔍 **Search** | `pw_generate_search_test.yaml` | Search across devices/rules, filter behaviour, result rendering |
| 🛒 **Checkout** | `pw_generate_checkout_test.yaml` | Multi-step form flows, input validation, submission |
| 👤 **Profile** | `pw_generate_profile_test.yaml` | User settings, profile update, data persistence |

Run any scenario directly:

```bash
python run_pipeline.py --url https://live.ideabytesiot.com/demolive --scenario scenarios/pw_generate_login_test.yaml
```

---

## 🎯 Use Case Flow

| Stage | Component | What Happens |
|---|---|---|
| 1️⃣ | **Live App / Design Doc** | Target URL or `basic_requirement.txt` requirements doc handed to the pipeline |
| 2️⃣ | **Auth + Scraper** | Keycloak session established via `login.py`; real post-auth DOM scraped across all 7 modules |
| 3️⃣ | **Doc Sanitiser** | Docs stripped of injection patterns before touching any LLM |
| 4️⃣ | **Strategy Agent** | Selector-grounded test plan mapped to real DOM elements, ranked by selector memory scores |
| 5️⃣ | **Architecture Agent** | POM framework designed around the live app's actual Angular component structure |
| 6️⃣ | **Code Gen Agent** | YAML → validated → Playwright Python; triple-checked (syntax + AST + assertions) |
| 7️⃣ | **Review Agent** | Structured quality review — routes back to Code Gen if High risk (max 2 passes) |
| 8️⃣ | **Edge Cases Agent** | IoT edge cases hardened with `<think>` scaffolding |
| 9️⃣ | **Heal Agent** | Reads real pytest failures, LLM-patches broken selectors/assertions, updates code |
| 🔟 | **AST Check + Test Executor** | Safety gate → pytest with SPA-aware browser fixtures; traces written to `traces.jsonl` |
| ✅ | **Reports + Persistence** | JSON/HTML results + TTFB baseline + sitemap + SQLite run record + `agentlens.db` updated |

---

## 🗂️ Project Structure

```
playwright-ai-automation/
│
├── agents/                        # Six LangGraph agents + all shared utilities
│   ├── state.py                   # AgentState TypedDict — typed contract between all agents
│   ├── strategy_agent.py          # Selector-grounded test strategy and task planning
│   ├── architecture_agent.py      # POM framework design from live Angular app structure
│   ├── code_gen_agent.py          # YAML → validate → Playwright Python; triple safety checks
│   ├── review_agent.py            # Structured review + needs_regen + bounded regen loop
│   ├── edge_cases_agent.py        # IoT edge cases with <think> scaffolding
│   ├── heal_agent.py              # Parses pytest FAILED output → LLM patches selectors/assertions
│   ├── llm_client.py              # DeepSeek — lazy init, model validation, unknown-model guard
│   ├── selector_utils.py          # Memory-weighted stability ranking, configurable cap, drop logging
│   ├── scraper_adapter.py         # Flattens multi-page crawl into AgentState selectors[]
│   ├── doc_sanitiser.py           # Strips prompt injection from uploaded docs
│   ├── popup_sanitizer.py         # Handles popup/modal interference during scraping
│   ├── python_fallback.py         # Direct Python generation when YAML path fails
│   ├── pipeline.py                # Single callable entry point (FastAPI + CLI)
│   └── prompts/                   # One prompt file per agent
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
├── db/                            # Persistent storage
│   ├── database.py                # SQLite CRUD — start_run(), finish_run(), get_runs()
│   ├── models.py                  # CREATE TABLE schema for runs
│   ├── selector_memory.py         # Per-selector pass/fail history + stability scoring
│   └── runs.db                    # SQLite database (gitignored in production)
│
├── scraper/                       # Live app DOM extraction
│   ├── scraper.py                 # requests + BeautifulSoup multi-page crawler
│   ├── playwright_check.py        # Playwright headless fallback for Angular SPAs
│   └── login.py                   # Keycloak auth session handling
│
├── performance/                   # Two-layer performance tracking
│   ├── engine.py                  # psutil per-agent CPU/memory/throughput
│   ├── live_crawler.py            # Real TTFB + load time per route (3-run avg)
│   └── benchmark.py
│
├── scenarios/                     # Pre-built YAML test scenarios for the live IoT app
│   ├── pw_generate_login_test.yaml
│   ├── pw_generate_logout_test.yaml
│   ├── pw_generate_signup_test.yaml
│   ├── pw_generate_search_test.yaml
│   ├── pw_generate_checkout_test.yaml
│   └── pw_generate_profile_test.yaml
│
├── tests/                         # Framework unit tests
│   ├── test_core.py               # yaml_validator · selector_utils · scraper_adapter
│   ├── test_sanitiser.py          # doc_sanitiser injection and truncation tests
│   ├── test_runner.py             # Test runner module tests
│   ├── test_prompts.py            # Prompt output format validation
│   └── test_scraper.py            # Scraper module tests
│
├── notes/                         # Live app discovery and run logs
│   ├── day11_discovery.md         # Auth gates, DOM structure, WS mapping
│   ├── day13_pipeline_run.md      # First live pipeline run bug log
│   └── live_app_design_doc.md     # Full IoT app requirements
│
├── reports/                       # Generated report outputs
│   ├── live_perf_baseline.json    # 3-run TTFB and load-time averages
│   └── live_sitemap.md            # Route map with load-time labels
│
├── traces.jsonl                   # Agent execution traces (AgentLens observability)
├── agentlens.db                   # AgentLens SQLite database
├── basic_requirement.txt          # Full IoT app requirements doc fed to the pipeline
├── test_auth.py                   # Validates Keycloak session before scraping
├── test_live_scraper.py           # Tests authenticated multi-page live app crawl
├── test_selector_stability.py     # 3-run selector stability check across live app pages
├── .github/workflows/ci.yml       # CI: imports · unit tests · regression · validation · upload
├── Dockerfile                     # Production image with Playwright browsers pre-installed
├── docker-compose.yml             # api service + pipeline service (--profile run)
├── .dockerignore
├── run_pipeline.py                # CLI: --url --max-pages → scrape → agents → pytest → report
├── llm_playwright_generator.py    # Wrapper: scraper JSON → agent pipeline
├── test_runner.py                 # AST check → subprocess pytest → stdout capture
├── report_generator.py            # Assembles JSON + HTML from execution results
├── main.py                        # LangGraph graph: 6 nodes, edges, conditional routing
├── pytest.ini                     # testpaths: tests/ test_llm.py test_prompts.py
├── requirements.txt               # Pinned versions
├── requirements_pinned.txt        # Full pip freeze from known-good working environment
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
| **Web Scraping** | requests + BeautifulSoup + Playwright headless (SPA + Keycloak auth) |
| **Persistence** | SQLite — run history DB + selector memory + AgentLens traces |
| **Observability** | AgentLens — `traces.jsonl` + `agentlens.db` (per-agent invocation audit) |
| **Performance** | psutil (agent metrics) · requests TTFB crawler (live routes) |
| **Security** | Python AST inspection · prompt injection sanitiser · fail-closed API key · subprocess timeout |
| **Containerisation** | Docker + docker-compose |
| **Reporting** | JSON · styled HTML · Markdown sitemap |
| **CI** | GitHub Actions — smoke · unit tests · pipeline regression · artifact upload |
| **Language** | Python 3.11+ |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js *(Playwright browser binaries need it)*
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
SELECTOR_CAP=25
SPA_WAIT_TIMEOUT=15000   # ms — Angular SPA hydration wait

# ── FastAPI auth ──────────────────────────────────────────────
APP_API_KEY=your-secret-key      # auto-generated at startup if not set
ALLOW_UNAUTHENTICATED=false

# ── Run History ───────────────────────────────────────────────
DB_PATH=db/runs.db

# ── Session (Keycloak) ────────────────────────────────────────
SESSION_COOKIE=                  # set if routes require auth
```

### 3. Run

```bash
# Validate auth session before running
python test_auth.py

# Full pipeline against the live IoT dashboard
python run_pipeline.py --url https://live.ideabytesiot.com/demolive --max-pages 7

# Run a specific YAML scenario
python run_pipeline.py --url https://live.ideabytesiot.com/demolive \
  --scenario scenarios/pw_generate_login_test.yaml

# Web interface
uvicorn app.main:app --reload
# → http://localhost:8000

# Check run history
curl http://localhost:8000/runs -H "X-API-Key: your-key"

# Selector stability check (3 runs)
python test_selector_stability.py

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

Reports, the run history database, and observability traces are persisted on host volumes — they survive container restarts.

---

## 🔒 Security

> The pipeline executes LLM-generated Python. Every layer is hardened.

| Layer | Protection |
|---|---|
| **AST Safety Check** | Generated `.py` parsed with `ast` before execution — blocks `import os/subprocess`, `eval()`, `exec()`, `__import__()`. Returns code `-2`; flags for regen. |
| **Prompt Injection Guard** | `doc_sanitiser.py` strips injection patterns, enforces 8000-char limit, removes HTML tags. Warnings logged. |
| **Fail-Closed API Auth** | Auto-generates `APP_API_KEY` at startup if none configured — endpoints never accidentally open. `ALLOW_UNAUTHENTICATED=true` opts out for local dev. |
| **Subprocess Timeout** | `subprocess.TimeoutExpired` kills generated tests after 60 seconds. |
| **Auth Credential Safety** | Keycloak session cookies live in `.env` and `/tmp/` — never committed. `auth.json` gitignored. |
| **Rate Throttling** | 2s sleep between live crawler requests — production servers stay unharmed. |

---

## 📊 Output Reports

Every pipeline run produces a full set of outputs:

| Output | Format | Contents |
|---|---|---|
| `test_execution_report.json` | JSON | Tests run · passed · failed · execution time · stdout/stderr |
| `test_execution_report.html` | HTML | Styled browser-viewable test report |
| `perf_baseline.json` | JSON | Per-agent CPU % · memory MB · throughput |
| `live_perf_baseline.json` | JSON | 3-run TTFB and load-time averages per live route |
| `live_sitemap.md` | Markdown | Route map with load-time labels |
| **SQLite `runs` table** | DB | Full run history — queryable via `/runs` and `/runs/{id}` |
| **SQLite `selector_memory`** | DB | Per-selector pass/fail history for stability scoring |
| **`traces.jsonl`** | JSONL | Every agent invocation, input, output, and timing |
| **`agentlens.db`** | SQLite | AgentLens structured observability data |

---

## 🗺️ Roadmap

**Shipped ✅**

- [x] 6-agent LangGraph pipeline — Strategy → Architecture → Code Gen → Review → Edge Cases → **Heal**
- [x] Self-healing test loop — Heal Agent parses real pytest failures, patches selectors/assertions automatically
- [x] YAML scenario library — 6 pre-built scenarios covering the full live IoT app (`scenarios/`)
- [x] Agent observability — `traces.jsonl` + `agentlens.db` for full pipeline auditability
- [x] SQLite run history database — every run stored, queryable via `/runs` REST API
- [x] Selector memory — cross-run stability scoring, boosts reliable selectors on future runs
- [x] Docker + docker-compose — one-command setup, Playwright browsers pre-installed
- [x] YAML validation layer before code generation
- [x] Bounded self-review loop — conditional graph edge, max 2 regen passes
- [x] AST safety check on all generated test files
- [x] Prompt injection protection for uploaded documents
- [x] Memory-weighted selector stability ranking, configurable cap, drop-count logging
- [x] YAML → Playwright converter with 30+ step keyword patterns
- [x] SPA-aware scraping with Playwright headless + Keycloak auth
- [x] Structural assertions for live data (presence over exact values)
- [x] SPA wait helpers auto-injected into every generated `conftest.py`
- [x] Live-site TTFB performance baseline (3-run average per route)
- [x] IoT-specific edge case prompting (sensor offline, WS disconnect, stale data, empty charts)
- [x] Fail-closed FastAPI API key auth (auto-generates key at startup)
- [x] GitHub Actions CI — smoke · unit tests · pipeline regression · validation · artifact upload
- [x] Full end-to-end validation on `live.ideabytesiot.com/demolive` (7 modules, Keycloak auth)

**Coming next 🔜**

- [ ] Multi-LLM backend support (OpenAI, Anthropic, Ollama, Gemini) via `LLM_PROVIDER` env var
- [ ] Visual regression testing — pixel-diff screenshots between runs
- [ ] Webhook notifications — push results to Slack / Teams on pipeline completion
- [ ] Plugin system — drop a `.py` in `plugins/` to add custom agents without modifying core

---

## 👥 Contributors

Built during an **AI Agents Developer Internship at [Ideabytes](https://ideabytes.com), Hyderabad.**

<br/>

**Rohith Kanamarlapudi** — [@Rohith-kanamarlapudi](https://github.com/Rohith-kanamarlapudi)

> LangGraph 6-agent pipeline · self-healing Heal Agent (pytest failure parsing + LLM patching) · YAML scenario library (`scenarios/`) · YAML tooling (`yaml_validator`, `yaml_to_playwright` — 30+ step patterns) · SQLite run history DB + REST API · selector memory cross-run scoring · Docker containerisation · bounded self-review loop · AST safety layer · prompt injection guard (`doc_sanitiser.py`) · memory-weighted selector ranking (`selector_utils.py`) · performance engine (psutil + live TTFB crawler) · SPA-aware conftest with IoT wait helpers · structural assertion mode · IoT edge case prompting · CI/CD (GitHub Actions) · fail-closed FastAPI auth · agent observability integration · live app hardening

<br/>

**Harshith Kanamarlapudi** — [@harshithnova](https://github.com/harshithnova)

> Playwright scraper + Angular SPA hydration fallback (`playwright_check.py`) · Keycloak auth session handling (`scraper/login.py`) · FastAPI application + upload endpoint · LLM generator · test runner · HTML/JSON report generation · popup/modal interference handling (`popup_sanitizer.py`) · multi-page authenticated crawl (`test_live_scraper.py`) · selector stability testing (`test_selector_stability.py`) · flake handling for live-data non-determinism · final report addendum