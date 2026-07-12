<div align="center">

# 🎭 Playwright AI Automation

### *Give it a URL. Walk away. Come back to a fully executed, self-validating test suite.*

No manual scripting. No guessed selectors. No brittle assertions on live data.

Point it at any web app and five specialised AI agents take over — scraping real DOM selectors, planning a test strategy, generating and self-reviewing Playwright scripts, hardening for edge cases, executing everything via pytest, and shipping JSON/HTML reports with a live performance baseline.

**Stress-tested on a production IoT dashboard SPA with real-time WebSocket sensor data** — not a toy demo app.
[`live.ideabytesiot.com/demolive`](https://live.ideabytesiot.com/demolive)

<br/>

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white&style=for-the-badge)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white&style=for-the-badge)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-1C3C3C?style=for-the-badge)](https://www.langchain.com/langgraph)
[![Playwright](https://img.shields.io/badge/Playwright-Test%20Engine-2EAD33?logo=playwright&logoColor=white&style=for-the-badge)](https://playwright.dev/)
[![DeepSeek](https://img.shields.io/badge/DeepSeek-LLM-4D6BFE?style=for-the-badge)](https://www.deepseek.com/)
[![CI](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?logo=githubactions&logoColor=white&style=for-the-badge)](https://github.com/Rohith-kanamarlapudi/playwright-ai-automation/actions)

</div>

---

### 📌 Jump to

[What Is This](#-what-is-this) · [Pipeline](#-pipeline-at-a-glance) · [Key Features](#-key-features) · [Architecture](#️-architecture) · [Built for Live IoT](#-built-for-the-live-iot-dashboard) · [Use Case Flow](#-use-case-flow) · [Project Structure](#️-project-structure) · [Tech Stack](#️-tech-stack) · [Getting Started](#-getting-started) · [Security](#-security) · [Output Reports](#-output-reports) · [Roadmap](#️-roadmap) · [Contributors](#-contributors)

---

## 🧭 What Is This?

**Playwright AI Automation** is a multi-agent AI system built during an internship at [Ideabytes, Hyderabad](https://ideabytes.com). It automates the *entire* lifecycle of web test engineering — from crawling a live application's real DOM, to delivering an executed, performance-profiled test report — without a human writing a single test case.

Most "AI writes your tests" tools stop at generation. This one doesn't get to call itself done until the tests have actually *run* against a live target. The system was built and proven against a real production system: **`live.ideabytesiot.com/demolive`**, a client-facing IoT dashboard SPA with live WebSocket sensor feeds and auto-refreshing charts. That meant the pipeline had to survive genuinely hard conditions — SPA hydration delays, sensor readings that change every few seconds, WebSocket-driven widgets, and rate limiting from a live server that couldn't be hammered.

Rather than betting everything on one fragile LLM call, the work is split across **five specialised agents**, each owning one phase of professional QA engineering. They share a typed state contract, reason out loud in `<think>` blocks before acting, and the pipeline self-corrects on the fly — a review agent triggers bounded regeneration whenever quality falls short of the bar.

> **The bottom line:** hand it a URL, get back a tested, reported, and performance-profiled test suite — no scripting required.

---

## ⚡ Pipeline at a Glance

```
  Your live app URL
        │
        ▼
  ┌─────────────┐    requests + BeautifulSoup  (static pages)
  │   Scraper   │ ──────────────────────────────────────────►  Real DOM selectors
  │             │    Playwright headless fallback  (SPAs)
  └─────────────┘
        │
        ▼
  ┌──────────────────────────────────────────────────────────────┐
  │                     LangGraph Pipeline                        │
  │                                                               │
  │   Strategy ──► Architecture ──► Code Gen ──► Review          │
  │                                     ▲            │            │
  │                                     └─── regen ──┘  (max 2)  │
  │                                          if High risk         │
  │                                                 ▼             │
  │                                          Edge Cases           │
  └──────────────────────────────────────────────────────────────┘
        │
        ▼
  ┌─────────────┐    AST safety check → pytest execution
  │ Test Runner │ ──────────────────────────────────────────►  Pass / Fail
  └─────────────┘    60s timeout · SPA-aware fixtures
        │
        ▼
  JSON report  ·  HTML report  ·  TTFB baseline  ·  Sitemap
```

---

## ✨ Key Features

| | Feature | What it does |
|---|---|---|
| 🧠 | **5-Agent Pipeline** | Strategy, Architecture, Code Gen, Review, and Edge Cases agents share a typed `AgentState` — every agent reads from and writes back to the same state |
| 🌐 | **Live SPA Support** | Playwright headless fallback handles SPAs that return empty shells to requests crawlers; `networkidle` waits and `data-testid`/`aria-label` prioritisation keep extraction stable |
| 🪄 | **Think-Tag Scaffolding** | Agents reason in `<think>` blocks before producing output — fewer hallucinated selectors, better test plans |
| 🔁 | **Bounded Self-Review Loop** | Review Agent parses its own structured output and sets `needs_regen`; LangGraph conditional edge routes back to Code Gen automatically (max 2 passes) |
| ✅ | **YAML Validation Layer** | Code Gen produces YAML first, validates structure (required fields, non-empty steps, no duplicate IDs), then converts via `yaml_to_playwright.py`; direct Python fallback if YAML fails |
| 🔒 | **AST Safety Check** | Every generated `.py` inspected with Python's `ast` before execution — `import os`, `subprocess`, `eval`, `exec` are blocked and flagged for regen |
| 🛡️ | **Prompt Injection Guard** | `doc_sanitiser.py` strips injection patterns, enforces size limits, and escapes HTML before any uploaded doc enters a prompt |
| 🕷️ | **Selector-Grounded Tests** | Real DOM elements scraped from the live app; `selector_utils.py` ranks by stability and caps with logged drop counts — no guessed selectors |
| 📊 | **Dual Performance Tracking** | `psutil` per-agent metrics + a live TTFB/load-time crawler that hits real routes across 3 consecutive runs |
| 🧪 | **SPA-Aware Execution** | `conftest.py` auto-generated per run with `wait_for_widget()` and `wait_for_live_data()` helpers; 60s subprocess timeout guard |
| 📄 | **Rich Reports** | `test_execution_report.json`, `test_execution_report.html`, `live_perf_baseline.json`, `live_sitemap.md` — every run |
| 🔑 | **FastAPI Auth** | `X-API-Key` header protects all generation endpoints — unauthenticated callers can't burn your API credits |
| ⚙️ | **CI/CD** | GitHub Actions runs import smoke tests and unit tests on every push and PR |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI Layer                             │
│   POST /upload-doc          POST /agents/run        GET /        │
│   (X-API-Key protected)     (X-API-Key protected)               │
└──────────────────┬──────────────────────────────────────────────┘
                   │ design_doc + target_url
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Scraper + Sanitiser                            │
│  scraper.py (requests + BS4)  ──►  playwright_check.py (SPA)    │
│  scraper_adapter.py (normalise)  ──►  doc_sanitiser.py (guard)  │
└──────────────────┬──────────────────────────────────────────────┘
                   │ selectors[], clean design_doc
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LangGraph Pipeline                             │
│                                                                   │
│   AgentState (TypedDict) ── shared typed contract                 │
│                                                                   │
│   ┌──────────┐  ┌──────────────┐  ┌──────────┐  ┌────────┐     │
│   │ Strategy │─►│ Architecture │─►│ Code Gen │─►│ Review │     │
│   └──────────┘  └──────────────┘  └──────────┘  └───┬────┘     │
│                                         ▲  regen      │          │
│                                         └─────────────┘ (max 2) │
│                                                       ▼          │
│                                            ┌──────────────┐     │
│                                            │  Edge Cases  │     │
│                                            └──────┬───────┘     │
└───────────────────────────────────────────────────┼─────────────┘
                                                     │ generated_code
                                                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Execution Layer                              │
│   AST check → conftest gen → pytest subprocess (60s cap)         │
│   Performance Engine (psutil) + Live TTFB Crawler (3-run avg)    │
└──────────────────┬──────────────────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Output Layer                                │
│   test_execution_report.json     test_execution_report.html      │
│   live_perf_baseline.json        live_sitemap.md                  │
└─────────────────────────────────────────────────────────────────┘
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
| 🔐 **Auth-gated routes** | `SESSION_COOKIE` env var; public vs. gated routes mapped on first run |
| 🎯 **Unstable live DOM** | `data-testid` → `aria-label` → `#id` → `input[name]` → text-based (last resort) |
| ⚠️ **IoT failure modes** | Edge Cases Agent reasons about sensor offline, stale timestamps, empty charts, WS disconnect, mid-refresh navigation |

---

## 🎯 Use Case Flow

Ten stages, one command. Here's what happens between the URL going in and the report coming out:

| Stage | Component | What Happens |
|---|---|---|
| 1️⃣ | **Live App / Design Doc** | Target URL or uploaded requirements handed to the pipeline |
| 2️⃣ | **Scraper + SPA Fallback** | Real DOM scraped; Playwright headless takes over for JS-rendered content |
| 3️⃣ | **Doc Sanitiser** | Uploaded docs stripped of injection patterns before touching any LLM |
| 4️⃣ | **Strategy Agent** | Selector-grounded test plan — tasks mapped to real DOM elements |
| 5️⃣ | **Architecture Agent** | POM framework designed around the live app's actual component structure |
| 6️⃣ | **Code Gen Agent** | YAML → validated → Playwright Python; triple-checked (syntax + AST + assertions) |
| 7️⃣ | **Review Agent** | Structured quality review — routes back to Code Gen if High risk (max 2 passes) |
| 8️⃣ | **Edge Cases Agent** | IoT edge cases hardened with `<think>` scaffolding |
| 9️⃣ | **DeepSeek LLM** | All generation calls via OpenAI-compatible API; lazy init, model-validated |
| 🔟 | **AST Check + Test Executor** | Safety gate → pytest with SPA-aware browser fixtures |
| ✅ | **Reports + Perf Dashboard** | JSON/HTML results + TTFB baseline + load-time sitemap |

---

## 🗂️ Project Structure

```
playwright-ai-automation/
│
├── agents/                        # Five LangGraph agents + all shared utilities
│   ├── state.py                   # AgentState TypedDict — typed contract between agents
│   ├── strategy_agent.py          # Selector-grounded test strategy and task planning
│   ├── architecture_agent.py      # POM framework design from live app structure
│   ├── code_gen_agent.py          # YAML → validate → Playwright Python; triple safety checks
│   ├── review_agent.py            # Structured review + needs_regen + bounded regen loop
│   ├── edge_cases_agent.py        # IoT edge cases with <think> scaffolding
│   ├── llm_client.py              # DeepSeek — lazy init, model validation, unknown-model guard
│   ├── selector_utils.py          # Stability ranking, configurable cap, drop-count logging
│   ├── scraper_adapter.py         # Flattens multi-page crawl into AgentState selectors[]
│   ├── doc_sanitiser.py           # Strips prompt injection from uploaded docs
│   ├── python_fallback.py         # Direct Python generation when YAML path fails
│   ├── pipeline.py                # Single callable entry point (FastAPI + CLI)
│   └── prompts/                   # One prompt file per agent — safe to iterate independently
│
├── app/                           # FastAPI application
│   ├── main.py                    # /upload-doc + /agents/run (API key protected)
│   ├── llm_generator.py           # DeepSeek direct call — fallback path
│   ├── yaml_validator.py          # Structural YAML validation before code gen
│   ├── yaml_to_playwright.py      # 30+ YAML step keywords → Playwright Python
│   └── templates/                 # Jinja2 results page
│
├── scraper/                       # Live app DOM extraction
│   ├── scraper.py                 # requests + BeautifulSoup multi-page crawler
│   └── playwright_check.py        # Playwright headless fallback for SPAs
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
├── .github/workflows/ci.yml       # CI: import smoke test + unit tests on every PR
├── run_pipeline.py                # CLI: --url --max-pages → scrape → agents → pytest → report
├── llm_playwright_generator.py    # Wrapper: reads scraper JSON → runs agent pipeline
├── test_runner.py                 # AST check → subprocess pytest → stdout/stderr capture
├── report_generator.py            # Assembles JSON + HTML from execution results
├── main.py                        # LangGraph graph: nodes, edges, conditional routing
├── pytest.ini                     # testpaths, asyncio_mode, custom marks
├── requirements.txt
└── .env.example
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Agent Orchestration** | LangGraph — `StateGraph`, conditional edges, bounded regen loop |
| **LLM** | DeepSeek `deepseek-chat` / `deepseek-reasoner` via OpenAI-compatible API |
| **API / Backend** | FastAPI + Jinja2 |
| **Test Automation** | Playwright (sync API) + pytest |
| **Web Scraping** | requests + BeautifulSoup + Playwright headless (SPA fallback) |
| **Performance** | psutil (agent metrics) · requests TTFB crawler (live routes) |
| **Security** | Python AST inspection · prompt injection sanitiser · API key auth · subprocess timeout |
| **Reporting** | JSON · styled HTML · Markdown sitemap |
| **CI** | GitHub Actions |
| **Language** | Python 3.11+ |

---

## 🚀 Getting Started

You'll be running your first AI-generated, self-executed test suite in about five minutes.

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
SELECTOR_CAP=20          # raise for large SPAs (default 15)
SPA_WAIT_TIMEOUT=15000   # ms — SPA hydration wait

# ── FastAPI auth (leave empty to skip in dev) ─────────────────
APP_API_KEY=your-secret-key

# ── Session (if the live app requires login) ──────────────────
SESSION_COOKIE=
```

### 3. Run

```bash
# Full pipeline against the live IoT dashboard
python run_pipeline.py --url https://live.ideabytesiot.com/demolive --max-pages 7

# Against any other target
python run_pipeline.py --url https://your-app.com --max-pages 5

# Web interface (upload a design doc)
uvicorn main:app --reload
# → http://localhost:8000

# Framework unit tests
pytest tests/ test_llm.py test_prompts.py -v
```

---

## 🔒 Security

> The pipeline executes LLM-generated Python. Every layer is hardened against the worst case.

| Layer | Protection |
|---|---|
| **AST Safety Check** | Generated `.py` parsed with `ast` before execution — blocks `import os/subprocess`, `eval()`, `exec()`, `__import__()`. Returns code `-2` and flags for regen. |
| **Prompt Injection Guard** | `doc_sanitiser.py` strips `"Ignore all previous instructions"` and similar, enforces 8000-char limit, removes HTML tags. All warnings logged. |
| **API Key Auth** | `X-API-Key` header required on all generation endpoints when `APP_API_KEY` is set. |
| **Subprocess Timeout** | `subprocess.TimeoutExpired` kills generated tests after 60 seconds — no hanging pipelines. |
| **Rate Throttling** | 2s sleep between live crawler requests — production servers stay unharmed. |

---

## 📊 Output Reports

Every pipeline run produces a full set of reports in `reports/` — no digging through logs required:

| Report | Format | Contents |
|---|---|---|
| `test_execution_report.json` | JSON | Tests run · passed · failed · execution time · stdout/stderr |
| `test_execution_report.html` | HTML | Styled, browser-viewable test report |
| `perf_baseline.json` | JSON | Per-agent CPU % · memory MB · throughput (agents/sec) |
| `live_perf_baseline.json` | JSON | 3-run TTFB and load-time averages per live route |
| `live_sitemap.md` | Markdown | Route map with load-time labels — ready for demo slides |
| `per_agent_perf.json` | JSON | Individual timing breakdown per agent |

---

## 🗺️ Roadmap

**Shipped ✅**

- [x] 5-agent LangGraph pipeline with shared `AgentState` TypedDict
- [x] YAML validation layer before code generation
- [x] Bounded self-review loop — conditional graph edge, max 2 regen passes
- [x] AST safety check on all generated test files
- [x] Prompt injection protection for uploaded documents
- [x] Selector stability ranking, configurable cap, drop-count logging
- [x] YAML → Playwright converter with 30+ step keyword patterns
- [x] SPA-aware scraping with Playwright headless fallback
- [x] Structural assertions for live data (presence over exact values)
- [x] SPA wait helpers auto-injected into every generated `conftest.py`
- [x] Live-site TTFB performance baseline (3-run average per route)
- [x] IoT-specific edge case prompting (sensor offline, WS disconnect, stale data, empty charts)
- [x] FastAPI API key authentication
- [x] GitHub Actions CI — smoke test + unit tests on every PR
- [x] Full end-to-end validation on `live.ideabytesiot.com/demolive`

**Coming next 🔜**

- [ ] Multi-LLM backend support (OpenAI, Anthropic, Ollama)
- [ ] Docker container for fully isolated test execution
- [ ] Visual regression testing layer
- [ ] Accessibility (axe-core) assertions in Edge Cases Agent

---

## 👥 Contributors

Built during an **AI Agents Developer Internship at [Ideabytes](https://ideabytes.com), Hyderabad.**

**Rohith Kanamarlapudi** — [@Rohith-kanamarlapudi](https://github.com/Rohith-kanamarlapudi)

> LangGraph multi-agent pipeline · agent design & prompt engineering · think-tag scaffolding · YAML tooling (`yaml_validator`, `yaml_to_playwright` — 30+ step patterns, locator & assertion fixes) · bounded self-review loop with conditional graph routing · AST safety layer · prompt injection protection (`doc_sanitiser.py`) · selector prioritisation & cap logging (`selector_utils.py`) · performance engine (psutil metrics + live TTFB crawler) · SPA-aware conftest generation with IoT wait helpers · structural assertion mode for live data · IoT edge case prompting · CI/CD (GitHub Actions) · FastAPI API key auth · live app adaptation & hardening

<br/>

**Harshith Kanamarlapudi** — [@harshithnova](https://github.com/harshithnova)

> Playwright scraper & SPA hydration fallback (`playwright_check.py`) · FastAPI application & upload endpoint · LLM generator · test runner · HTML/JSON report generation · dynamic element handling for live IoT widgets · multi-page crawl execution & retry logic · flake handling for live-data non-determinism · final report addendum · pipeline orchestration 
