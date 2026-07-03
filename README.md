# 🎭 Playwright AI Automation

**A multi-agent AI system that turns a design document into a fully executed, self-validating Playwright test suite.**

Upload a design doc → a 5-agent LangGraph pipeline plans, architects, generates, reviews, and stress-tests the automation → Playwright scripts run automatically → you get JSON/HTML reports and a live performance dashboard.

[![Python](https://img.shields.io/badge/Python-96.5%25-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-1C3C3C)](https://www.langchain.com/langgraph)
[![Playwright](https://img.shields.io/badge/Playwright-Test%20Engine-2EAD33?logo=playwright&logoColor=white)](https://playwright.dev/)
[![DeepSeek](https://img.shields.io/badge/DeepSeek-LLM-4D6BFE)](https://www.deepseek.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 Overview

**Playwright AI Automation** is a collaborative internship project that automates the entire lifecycle of web test creation — from reading a raw design document to producing an executed, reported, and performance-profiled Playwright test suite, with (almost) zero manual scripting.

Instead of a single LLM call generating brittle test code, the system routes the task through **five specialized agents**, each responsible for one phase of professional test engineering: strategy, architecture, code generation, review, and edge-case hardening. Their combined output is compiled by an LLM router, sent to DeepSeek, converted into executable Playwright scripts, run, and measured — all through a single FastAPI endpoint.

---

## ✨ Key Features

- 🧠 **5-Agent LangGraph Pipeline** — Strategy, Architecture, Code Gen, Review, and Edge Cases agents collaborate through a shared `TypedDict` state.
- 🪄 **Think-Tag Scaffolding** — Agents reason in structured `<think>` blocks before producing final output, improving code quality and reducing hallucinated selectors.
- ⚡ **FastAPI Upload-to-Report Pipeline** — A single `POST /upload-doc` endpoint drives the entire flow: parse → plan → generate → review → execute → report.
- 🕷️ **Integrated Web Scraper** — Extracts real DOM elements (`website_elements.json`) so generated scripts target actual selectors, not guesses.
- 🧪 **Automated Test Execution** — Generated Playwright scripts are run automatically by the Test Executor, no manual trigger required.
- 📊 **Performance Engine** — Tracks execution metrics via `psutil` and renders them on a live Performance Dashboard.
- 📄 **Multi-Format Reporting** — Every run produces a `results.json`, a styled `report.html`, and dashboard metrics.
- 🔄 **Pluggable LLM Backend** — Built around DeepSeek (local or API) behind an LLM Router, with `deepseek-chat` / `deepseek-reasoner` support.

---

## 🏗️ Architecture

The system is organized into four layers: a **FastAPI layer** that ingests the design document, a **LangGraph Pipeline** that plans and generates the test suite through five collaborating agents, an **Execution Layer** that runs the generated scripts and profiles performance, and an **Output Layer** that returns structured reports back to the user.

![Architecture Diagram](./architecture-diagram.png)

**Flow summary:**

1. **User uploads** a design document via `POST /upload-doc`.
2. **Doc Parser** extracts requirements and hands them to the **LangGraph State**.
3. The **Strategy Agent** drafts a test plan → passed to the **Code Gen Agent**, which produces raw code.
4. The **Review Agent** refines the code → the **Architecture Agent** adds structural/architectural context → the **Edge Cases Agent** (with think-tag scaffolding) hardens the suite against edge cases, producing the **final suite**.
5. The **LLM Router** forwards the final suite to **DeepSeek** (local or API).
6. The **Response Merger** consolidates the model output.
7. The **Playwright Script Generator** converts it into executable test files, run by the **Test Executor**, and profiled by the **Performance Engine**.
8. Results are returned as `results.json`, `report.html`, and a live **Performance Dashboard**, viewable in the browser.

---

## 🎯 Use Case Flow

![Use Case Diagram](./use-case-diagram.png)

| Stage | Component | Responsibility |
|---|---|---|
| 1️⃣ | `Design Doc → FastAPI App` | Accepts the uploaded design document |
| 2️⃣ | `LangGraph Pipeline` | Orchestrates all five agents against a shared state |
| 3️⃣ | `Strategy Agent` | Defines the high-level test strategy and coverage plan |
| 4️⃣ | `Code Gen Agent` | Generates raw Playwright automation code |
| 5️⃣ | `Review Agent` | Refines and validates generated code |
| 6️⃣ | `Architecture Agent` | Adds structural/design context for maintainability |
| 7️⃣ | `Edge Cases Agent` | Hardens the suite using think-tag reasoning |
| 8️⃣ | `LLM Router → DeepSeek` | Executes the final generation call |
| 9️⃣ | `Playwright Script Generator` | Converts model output into runnable `.spec` files |
| 🔟 | `Test Executor + Performance Engine` | Runs tests and profiles performance |
| ✅ | `JSON / HTML Report + Dashboard` | Delivers results back to the user |

---

## 🗂️ Project Structure

```
playwright-ai-automation/
├── agents/                     # Strategy, Architecture, Code Gen, Review, Edge Cases agents
├── app/                        # FastAPI application (routes, upload handling)
├── scraper/                    # DOM/element scraper feeding real selectors to agents
├── generated_tests/            # Auto-generated Playwright test scripts
├── performance/                # Performance tracking engine (psutil-based)
├── reports/                    # JSON / HTML report output + dashboard assets
├── uploads/                    # Uploaded design documents
├── llm_playwright_generator.py # Core LLM → Playwright script generation logic
├── run_pipeline.py             # Entry point to run the full LangGraph pipeline
├── report_generator.py         # Builds JSON/HTML reports from execution results
├── test_runner.py              # Executes generated Playwright test suites
├── test_scraper.py             # Tests for the scraper module
├── test_llm.py / test_prompts.py # LLM integration & prompt tests
├── website_elements.json       # Scraped DOM elements used for selector grounding
├── main.py                     # FastAPI application entry point
├── requirements.txt
└── .env.example
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| API / Backend | FastAPI |
| Agent Orchestration | LangGraph |
| LLM | DeepSeek (`deepseek-chat` / `deepseek-reasoner`) |
| Test Automation | Playwright |
| Web Scraping | Custom Python scraper |
| Performance Monitoring | psutil |
| Reporting | JSON, HTML, custom performance dashboard |
| Language | Python 3.x |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js (required by Playwright's browser binaries)
- A DeepSeek API key (or local DeepSeek endpoint)

### Installation

```bash
# Clone the repository
git clone https://github.com/Rohith-kanamarlapudi/playwright-ai-automation.git
cd playwright-ai-automation

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

### Configuration

Copy the example environment file and add your credentials:

```bash
cp .env.example .env
```

Set your DeepSeek API key and any other required values inside `.env`.

### Running the Application

**Start the FastAPI server:**

```bash
uvicorn main:app --reload
```

**Or run the pipeline directly:**

```bash
python run_pipeline.py
```

Then upload a design document to the `/upload-doc` endpoint (via Swagger UI at `http://localhost:8000/docs`, or `curl`/Postman) to trigger the full pipeline: planning → generation → review → execution → reporting.

---

## 📊 Sample Output

After a run, check the `reports/` directory for:

- `results.json` — structured, machine-readable test results
- `report.html` — a styled, human-readable test report
- **Performance Dashboard** — execution time, resource usage, and pass/fail metrics per test

---

## 🗺️ Roadmap

- [ ] Full end-to-end demo integrating scraper + FastAPI + YAML tooling (v0.2.0)
- [ ] Expanded edge-case coverage via richer think-tag scaffolding
- [ ] CI-friendly headless execution mode
- [ ] Multi-LLM backend support beyond DeepSeek

---

## 👥 Contributors

Built during an **AI Agents Developer Internship at Ideabytes** by:

- **Rohith Kanamarlapudi** — [@Rohith-kanamarlapudi](https://github.com/Rohith-kanamarlapudi) — LangGraph multi-agent pipeline, agent design, performance engine
- **Harshith** — Scraper, FastAPI application, YAML tooling

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
