<div align="center">

# 🧠 AutoResearchAI

### Multi-Agent AI Research Platform

Plan, research, verify, and save evidence-backed research reports with a
multi-agent FastAPI + React workflow.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-API-green?logo=fastapi)
![React](https://img.shields.io/badge/React-19-61dafb?logo=react)
![Vite](https://img.shields.io/badge/Vite-8-purple?logo=vite)
![License](https://img.shields.io/badge/License-MIT-blue)

</div>

---

## 📖 Overview

AutoResearchAI turns a single research question into a structured, transparent
research run. A planner breaks the question down, a research agent gathers
evidence (optionally from the live web), a verifier checks the claims, and a
writer produces a readable Markdown report. Every run is persisted, can be
monitored while it executes, and can be reopened later.

Long-running work runs as a **background job**: the API accepts the request
immediately, checkpoints progress to the database after every step, and the
frontend polls for live status. Failures are persisted with a safe message
instead of disappearing.

---

## ✨ Features

- 🤖 Four specialized agents: Planner, Research, Verifier, Writer
- ⏳ Background jobs with live progress polling, duplicate-job protection and persisted failures
- 🌐 Optional real web research (Tavily search + SSRF-safe fetching + extraction)
- 🛡️ SSRF protection: every URL and redirect is validated before connecting
- 📑 Deterministic source tracking with clickable, sanitized citations
- 📄 Sanitized Markdown report rendering (raw HTML/`javascript:` are stripped)
- 💾 SQLite persistence — sessions, reports and progress survive restarts
- ⚡ FastAPI REST API with typed schemas, liveness and readiness probes
- 🧰 OpenRouter (OpenAI-compatible) LLM client with bounded, classified retries
- 🧪 Offline test suite (mocked LLM and retrieval), ruff + ESLint, CI workflow

---

## 🏗 Architecture

```text
React SPA (Vite) ──relative /api──▶ FastAPI
                                      │
                          sync routes │ background job routes (202 + poll)
                                      ▼
                               JobRunner (bounded thread pool)
                                      │
                            WorkflowOrchestrator
                 Planner → Research → Verifier → Writer
                                      │
                 LLMClient (OpenRouter)   WebResearchService (optional)
                                      │
                                 SQLite (WAL)
```

See [`docs/architecture.md`](docs/architecture.md) and
[`docs/workflow.md`](docs/workflow.md) for details.

---

## 🧰 Tech stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.11+, FastAPI, Uvicorn |
| LLM | OpenRouter via the OpenAI-compatible SDK |
| Persistence | SQLite (standard library, WAL mode) |
| Web research | Tavily Search API + `httpx`, standard-library extraction |
| Validation/settings | Pydantic, pydantic-settings |
| Frontend | React 19, Vite, Tailwind CSS, React Router |
| Markdown | react-markdown + remark-gfm + rehype-sanitize |
| Tests/QA | pytest, ruff, ESLint |

---

## 🚀 Getting started

### 1. Clone and enter the repository

**Windows PowerShell**

```powershell
git clone https://github.com/HiteshNathbuva/AutoResearchAI.git
cd AutoResearchAI
```

**macOS / Linux**

```bash
git clone https://github.com/HiteshNathbuva/AutoResearchAI.git
cd AutoResearchAI
```

### 2. Backend environment

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
copy .env.example .env
```

**macOS / Linux**

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
```

### 3. Configure environment

Open `.env` and set at least the required key:

```env
OPENROUTER_API_KEY=your_openrouter_key_here
```

**Required**

| Variable | Purpose |
|----------|---------|
| `OPENROUTER_API_KEY` | OpenRouter API key. The app cannot complete real LLM calls without it. |

**Optional — model and runtime**

| Variable | Default | Purpose |
|----------|---------|---------|
| `MODEL_NAME` | `deepseek/deepseek-chat-v3-0324:free` | OpenRouter model identifier |
| `TEMPERATURE`, `MAX_TOKENS` | `0.7`, `4096` | Sampling controls |
| `LLM_TIMEOUT_SECONDS`, `LLM_MAX_RETRIES` | `60`, `2` | Provider timeout and transient retries |
| `JOB_MAX_WORKERS` | `2` | Concurrent background research jobs |
| `JOB_POLL_INTERVAL_SECONDS` | `1.5` | Polling hint returned to clients |
| `DATABASE_PATH` | `database/autoresearch.sqlite3` | SQLite file location |
| `CORS_ORIGINS` | localhost Vite origins | Comma-separated allowed origins |

**Optional — real web research** (disabled unless `WEB_RESEARCH_ENABLED=true`)

| Variable | Default | Purpose |
|----------|---------|---------|
| `WEB_RESEARCH_ENABLED` | `false` | Turn on the bounded web research pass |
| `SEARCH_PROVIDER` | `auto` | `auto`, `tavily`, or `none` |
| `TAVILY_API_KEY` | _empty_ | Tavily key. Without it the app degrades to model-only research |
| `SEARCH_MAX_RESULTS`, `MAX_FETCHED_SOURCES` | `5`, `5` | Bounds on results and fetched pages |
| `FETCH_TIMEOUT_SECONDS`, `FETCH_MAX_REDIRECTS`, `FETCH_MAX_BYTES` | `10`, `3`, `2000000` | Fetch limits |
| `EXTRACT_MAX_CHARS` | `8000` | Extracted text cap per source |

When web research is disabled, misconfigured, or fails, the application never
crashes and never fabricates sources: it records the situation in `diagnostics`
and falls back to model-only research, and the UI shows an honest provenance
notice.

### 4. Run the backend

```bash
python -m uvicorn backend.main:app --reload
```

- API docs (Swagger): <http://127.0.0.1:8000/docs>
- Health: <http://127.0.0.1:8000/api/health>

### 5. Run the frontend

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173>. The Vite dev server proxies `/api` to the backend,
so no CORS configuration is needed for local development. For a remote backend,
set `VITE_API_URL` in `frontend/.env` (see `frontend/.env.example`).

---

## 🔌 API reference

All routes are prefixed with `/api`.

### Background jobs (used by the frontend)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/jobs/research` | Start a research job. Returns `202` with `session_id`, `poll_url`, `poll_interval_seconds`. |
| `POST` | `/api/jobs/verify/{session_id}` | Start verification + report writing on a session (`202`). |
| `POST` | `/api/jobs/report/{session_id}` | Start report generation on a session (`202`). |
| `GET` | `/api/jobs/{session_id}` | Poll a job: full session payload plus `job_active`. |
| `GET` | `/api/sessions` | List session summaries (`?limit=1..100`). |
| `GET` | `/api/sessions/{session_id}` | Retrieve a full persisted session. |
| `GET` | `/api/health` | Static liveness probe. |
| `GET` | `/api/ready` | Readiness probe including a database check. |

Poll `GET /api/jobs/{id}` until `status` is one of `Research completed`,
`Verified report generated`, `Report generated`, or `Failed`. Starting another
job on a session that is already running returns `409`.

### Synchronous endpoints (retained for compatibility)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/research` | Run Planner + Research inline and persist the session. |
| `POST` | `/api/verify/{session_id}` | Run Verifier + Writer inline. |
| `POST` | `/api/report/{session_id}` | Run the Writer inline. |

Validation errors return `422`, unknown sessions `404`, and upstream LLM
failures on synchronous routes `502` with a generic, secret-free message.

---

## ✅ Testing and quality checks

```bash
# Backend: fully offline (a dummy key and fake LLM are wired in conftest)
pytest
ruff check .

# Frontend
cd frontend
npm run lint
npm run build
```

---

## 🚢 Deployment notes

- The backend is a **long-running stateful process** (in-process job pool +
  SQLite). Run it on a host that supports persistent processes — a container,
  VM, or platform such as Render/Railway/Fly.io. A conventional Vercel static
  deployment cannot run this FastAPI server or its background worker without
  being re-architected into serverless functions and an external database.
- The frontend is a static Vite build (`frontend/dist`) that can be hosted on
  any static host. Point it at the API with `VITE_API_URL` at build time, or
  serve both behind one origin and use relative `/api` paths.
- Provide secrets through environment variables; never commit a real `.env`.
- With one SQLite file and an in-process worker, run a **single backend
  instance**. Scaling horizontally requires an external queue and a
  client/server database (see [`docs/roadmap.md`](docs/roadmap.md)).

---

## 🔒 Security

- Secrets are loaded from environment variables and are never logged or sent to
  the browser.
- Every fetched URL and redirect is validated against an SSRF blocklist before
  any connection; content types, response sizes and redirects are bounded.
- Retrieved web content is treated as untrusted data and delimited in prompts.
- Report Markdown is sanitized before rendering; external links open safely.
- The system has no authentication yet — do not expose it publicly without
  adding auth and rate limiting.

---

## ⚠️ Known limitations

- No built-in authentication, multi-tenancy or rate limiting.
- Single-process only (SQLite + in-process job runner).
- The confidence label is parsed from model prose; structured outputs are on the
  roadmap.
- Without `OPENROUTER_API_KEY` (and optionally `TAVILY_API_KEY`) the workflow
  cannot produce live results; tests and startup still work offline.
- PDF/DOCX export and follow-up research are not yet implemented.

---

## 📄 License

MIT © [Hitesh Nathbuva](https://github.com/HiteshNathbuva)
