# AutoResearchAI — Repository Engineering Assessment

**Basis:** working tree of `arena/01a000a6-autoresearchai` @ `b4dc1bf` (79 tracked files, single commit, no `.github/`). Findings marked **[verified]** were confirmed by executing the code in a throwaway venv (`/tmp`) with a fake API key and a fake LLM stub — no repository files were created, modified, or committed during inspection.

> **Scope note:** This document is an analysis-only artifact. No application or source file was modified, refactored, or deleted to produce it. Sections 1–8 describe **what exists**. Sections 9–16 classify **implementation status and defects**. Section 17 and the closing sections are **recommendations**, explicitly separated from existing implementation.

---

## Table of Contents

1. [Current project architecture and folder structure](#1-current-project-architecture-and-folder-structure)
2. [Backend architecture](#2-backend-architecture)
3. [Agent architecture](#3-agent-architecture)
4. [Current workflow pipeline](#4-current-workflow-pipeline)
5. [WorkflowState and session management](#5-workflowstate-and-session-management)
6. [API layer and frontend integration](#6-api-layer-and-frontend-integration)
7. [Prompt architecture](#7-prompt-architecture)
8. [LLM abstraction and OpenRouter integration](#8-llm-abstraction-and-openrouter-integration)
9. [What is fully implemented](#9-what-is-fully-implemented)
10. [What is partially implemented](#10-what-is-partially-implemented)
11. [What is missing for the planned production-grade multi-agent architecture](#11-what-is-missing-for-the-planned-production-grade-multi-agent-architecture)
12. [Architectural inconsistencies and technical debt](#12-architectural-inconsistencies-and-technical-debt)
13. [Security and configuration concerns](#13-security-and-configuration-concerns)
14. [Testing gaps](#14-testing-gaps)
15. [Scalability concerns](#15-scalability-concerns)
16. [Frontend limitations](#16-frontend-limitations)
17. [Recommended implementation order](#17-recommended-implementation-order)
18. [Does the architecture match the intended "Multi-Agent Research Platform"?](#does-the-architecture-match-the-intended-multi-agent-research-platform)
19. [NEXT STEP](#-next-step-do-this-first)

---

## 1. Current project architecture and folder structure

```
AutoResearchAI/
├── backend/                    ← the only real application code
│   ├── main.py                 (19 lines) FastAPI app factory-less entry
│   ├── api/routes.py           (92) all 6 endpoints
│   ├── agents/                 planner / research / verifier / writer  ← NO __init__.py
│   ├── core/                   agent.py, config.py, exceptions.py, llm.py,
│   │                           logger.py, session.py, state.py, workflow.py
│   ├── schemas/api.py          (51) request/response models
│   ├── utils/prompt_loader.py  (39)
│   ├── models/   __init__.py only  ← EMPTY placeholder
│   └── services/ __init__.py only  ← EMPTY placeholder
├── prompts/     planner.md, researcher.md, verifier.md, writer.md (real)
│                supervisor.md, memory.md  ← 0 bytes
├── tests/       5 script-style files, 0 pytest tests
├── docs/        architecture.md, roadmap.md, workflow.md  ← ALL 0 bytes
├── agents/      __init__.py only  ← EMPTY duplicate of backend/agents
├── tools/       __init__.py only  ← EMPTY (no search/retrieval tooling)
├── memory/      __init__.py only  ← EMPTY (no RAG/vector store)
├── database/    __init__.py + sqlite/__init__.py  ← EMPTY, unused by code
├── frontend/    React 19 + Vite 8 + Tailwind 3 SPA (~147 LOC of src)
├── requirements.txt  ← UTF-16LE + BOM + CRLF [verified]
├── .env.example  .gitignore  LICENSE  README.md
```

**Structural observations (existing state, not recommendations):**

- Two parallel package trees for the same concept: root `agents/`, `tools/`, `memory/`, `database/` are aspirational stubs from an earlier design; the live code lives entirely under `backend/`. The README's "Project Structure" section lists `backend/prompts/` — the prompts are actually at repo root, and `prompt_loader.py` resolves `parents[2]/prompts`, so the README is wrong but the code is self-consistent.
- `backend/agents/` has **no `__init__.py`** while every other package does — it works only as an implicit namespace package. Inconsistent and fragile for packaging/`pip install -e`.
- All three `docs/*.md` files and two `prompts/*.md` files are **empty (0 bytes)** — documentation exists as filenames only.
- No `pyproject.toml`, `setup.cfg`, `pytest.ini`, `conftest.py`, `Dockerfile`, `docker-compose.yml`, `Makefile`, lint/format/type-check config, or CI workflow anywhere.
- Total backend Python: ~700 LOC. This is an early-stage skeleton with production *intent*, not a production system.

---

## 2. Backend architecture

**Layering as it exists:**

```
main.py  →  api/routes.py  →  core/workflow.py  →  backend/agents/*  →  core/llm.py → OpenRouter
                   ↓                    ↕
           core/session.py  ←→  core/state.py          utils/prompt_loader.py → prompts/*.md
                   ↓
             SQLite file
```

**Wiring is entirely module-level import-time singletons:**

| Object | Where | Consequence |
|---|---|---|
| `settings = Settings()` | `core/config.py:32` | Import of *anything* validates env; missing key = `ValidationError` at import **[verified]** |
| `session_manager = SessionManager()` | `core/session.py:90` | Import creates `database/` dir + SQLite file as a side effect |
| `workflow = WorkflowOrchestrator()` | `api/routes.py:13` | Import constructs 4 agents → **4 separate `OpenAI` clients** **[verified]** |

There is no dependency injection, no app factory (`create_app()`), no FastAPI lifespan/startup hooks, no `Depends()` usage anywhere. `main.py` mutates a module-global `app`. `ENVIRONMENT` is defined in config but **read nowhere** — there is no dev/prod behavioural difference (Swagger `/docs` is always exposed, no debug gating).

All route handlers are sync `def`, so each request occupies an AnyIO threadpool worker (default 40) for the entire multi-LLM-call duration.

---

## 3. Agent architecture

`core/agent.py` — `BaseAgent(ABC)`:

- `__init__(name, role)` and **instantiates its own `LLMClient()`** (line 42) — no injection, no sharing.
- `execute()` abstract; `validate()` is a **`None`-only check**, so `""` passes and reaches the LLM **[verified: `PlannerAgent().execute("")` executes normally]**.
- `cleanup()` returns `None`; docstring TODOs for lifecycle hooks, callbacks, execution metrics, memory integration — **none implemented**.
- No logging, no timing, no retry policy, no token/cost accounting, no per-agent model/temperature override.

**The four agents (each ~50–90 lines, all identical in shape: load prompt → build 2 messages → one `llm.chat()` call):**

| Agent | Prompt | Input | Output | Contract |
|---|---|---|---|---|
| Planner | `planner.md` | `str` (query) | `str` (plan) | **str → str** |
| Research | `researcher.md` | `WorkflowState` | mutated state | state → state |
| Verifier | `verifier.md` | `WorkflowState` (uses `.research` only) | mutated state | state → state |
| Writer | `writer.md` | `WorkflowState` | mutated state | state → state |

**Critical inconsistency:** `BaseAgent.execute(input_data)` has one signature but two incompatible contracts. Passing a string to Research/Verifier raises `AttributeError: 'str' object has no attribute 'query'/'research'` **[verified]** — and that is exactly what `tests/test_research_agent.py` and `tests/test_verifier_agent.py` do, so those tests are dead against current code.

Agents mutate the shared state **in place *and* return it** — ownership is ambiguous and there is no immutability or step-scoped copy. Docstrings are stale (`research_agent` documents `input_data (str)` while the signature is `state`).

Notably absent: no Supervisor/Router agent (despite `prompts/supervisor.md` existing as an empty file), no tool-using agent, no memory-aware agent, no critique→re-research feedback loop.

---

## 4. Current workflow pipeline

`WorkflowOrchestrator` (62 lines) exposes three **synchronous, linear** methods:

```
execute_pipeline(query)          Planner → Research           → status "Research completed", confidence "Unverified"
verify_report(state)             Verifier → Writer            → status "Verified report generated"
generate_report(state)           Writer                       → status "Report generated"
```

**[verified with a stubbed LLM]:** `execute_pipeline` = 2 LLM calls, `verify_report` = 2 more; `completed_tasks` becomes `['Planner','Research','Verification','Writer']`.

Problems in the pipeline as designed:

- **`verify_report` conflates two responsibilities** — it runs the Verifier *and* the Writer. Calling `/verify` therefore silently produces/overwrites `final_report`. Calling `/report` afterwards re-runs the Writer and rewrites the same field, downgrading `status` while keeping the verified `confidence`. The state machine is implicit and non-monotonic; there is no `WorkflowState` status enum and no legal-transition validation.
- **No persistence until the whole pipeline finishes.** `session_manager.create_session()` is called only *after* Planner+Research complete (`routes.py:39`), so a multi-minute request has no intermediate checkpoint, no resumability, and the frontend's `WorkflowProgress` can only ever show a completed run — never live progress.
- **No per-step error isolation**: any agent failure aborts the whole call and *nothing* is persisted — failed runs leave no audit trail.
- **`_confidence_from_verification` is brittle substring matching** on `"confidence: high|medium|low"`. **[verified]** `"**Confidence:** High"` → `Unverified`; `"Confidence:  High"` (double space) → `Unverified`; `"Confidence: **High**"` → `Unverified`. The verifier prompt emits emoji-and-markdown-heavy output, so bold-wrapped labels are a realistic and likely failure. There is no structured output contract (no JSON mode / function calling / schema validation) between prompt and parser.
- **Presentation logic inside the orchestrator**: `reading_time = words/200` is duplicated in three methods.
- Verifier only sees `state.research` — not the query or the plan — so it cannot actually assess *completeness against the plan* as its prompt claims.
- No parallelism (plan sections are researched in a single call), no iteration/refinement loop, no step timeouts, no cancellation, no budget cap on LLM spend per workflow.

---

## 5. WorkflowState and session management

**`core/state.py` — `WorkflowState`** (plain Python class, not Pydantic):

- Fields: `query`/`user_query` (duplicated), `research`/`research_notes` (duplicated), `plan`, `verification`, `final_report`, `status`, `confidence`, `reading_time`, `memory`, `completed_tasks`, `current_step`, `metadata{created_at,updated_at}`.
- The duplicate aliases are dual-written by setters — legacy compatibility debt with no single source of truth.
- **`memory` is never written, never read, and is dropped by `to_dict()`/`from_dict()`** **[verified: round-trip returns `{}`]**.
- Free-form `str` status/confidence (no enums), no typing/validation, no run id, no per-step timings, no token counts, no model name, no cost, no error field.

**`core/session.py` — `SessionManager`** (SQLite, `threading.RLock`, one table `research_sessions`):

- Implemented: `create_session`, `get_session`, `update_session`, `list_sessions(limit)`. Uses parameterised SQL throughout (no injection risk).
- **Connection leak [verified]:** `_connect()` opens a new connection per call and uses `with self._connect() as connection:` — in sqlite3 the context manager commits the *transaction*, it does **not close the connection**. Open FDs grew 9 → 40 across 200 `create_session` calls and only dropped after a forced `gc.collect()`. Under load this is FD exhaustion waiting to happen.
- Single global `RLock` **serialises every DB operation** process-wide; `check_same_thread=False`; no WAL mode, no `busy_timeout`, no connection pool.
- **No schema migrations/versioning** (`CREATE TABLE IF NOT EXISTS` only) — any future column change silently breaks existing DBs.
- No indexes beyond the PK, yet `list_sessions` does `ORDER BY updated_at DESC`.
- `list_sessions` **SELECTs the full `final_report` text** merely to compute `has_report` — needless payload transfer.
- `update_session` rewrites `created_at` from state (harmless today, but a correctness landmine).
- No `delete_session`, no offset/cursor pagination, no `user_id`/tenant column, no soft delete, no TTL/retention cleanup, no full-text or vector index over past research.
- Single-file SQLite + in-process lock ⇒ **one process only**; the `database/sqlite/` package is unused dead structure.

---

## 6. API layer and frontend integration

**Actual endpoints** (`APIRouter(prefix="/api")` + one root route) — **all [verified] live via TestClient**:

| Method | Path | Status | Notes |
|---|---|---|---|
| GET | `/` | 200 | app/version/status banner |
| GET | `/api/health` | 200 | `{"status":"healthy"}` — static; checks neither DB nor LLM |
| POST | `/api/research` | 200 / 422 / 502 | full Planner+Research, then persists |
| GET | `/api/sessions?limit=` | 200 | `limit` 1–100 |
| GET | `/api/sessions/{id}` | 200 / 404 | |
| POST | `/api/verify/{id}` | 200 / 404 / 422 / 502 | runs Verifier **+ Writer** |
| POST | `/api/report/{id}` | 200 / 404 / 422 / 502 | runs Writer |

**README drift:** the README documents `POST /research`, `POST /verify/{id}`, `POST /report/{id}` and "GET / — health check". The real paths are `/api/...`; `/api/health`, `/api/sessions`, `/api/sessions/{id}` are undocumented.

**Schema layer:** `ResearchResponse`, `VerificationResponse`, `ReportResponse` are **empty subclasses of `SessionResponse`** — three names, one identical flat payload, no per-stage differentiation. The payload always includes `plan`, i.e. the internal research plan the README calls "Planner Agent (Hidden)" is exposed to clients. `_response()` builds every response through one untyped helper.

**Error handling in routes:** a repeated try/except triple per endpoint — `KeyError → 404`, `ValueError → 422`, `Exception → 502` with a generic message. Consequences: genuine server bugs (e.g. the `AttributeError` class of failure) are reported as **502 "upstream" errors**, hiding defects; `LLMError` (which *is* upstream) is indistinguishable from a `TypeError`; no `RequestValidationError` handler, no global exception handlers, no error codes, no correlation IDs. `_not_found()` raises inside a helper, so handlers have implicit `None` return paths.

Missing at the API layer: no auth, no rate limiting, no API versioning (`/api`, not `/api/v1`), no async job submission (`202 + job id`), no SSE/WebSocket progress channel, no export endpoints (PDF/DOCX), no DELETE, no pagination metadata, no idempotency keys, no request-size/time limits, no `TrustedHostMiddleware`.

**Frontend↔backend integration** (`frontend/src/services/api.js`, 10 lines):

- Hardcoded absolute base URL: `import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api"`, and **`vite.config.js` defines no dev `server.proxy`** — so the browser always calls the backend cross-origin. This works only where the FQDN is reachable from the user's browser; it breaks in containerised/proxied/preview deployments.
- CORS is therefore load-bearing: `main.py` allows `settings.cors_origins` with `allow_methods=["*"]`, `allow_headers=["*"]`, `allow_credentials=False`.
- `request()` has **no timeout / AbortController, no retry, no auth header**. Given `/api/research` performs two LLM calls, long runs hang the UI indefinitely with no cancel.
- `ResearchContext` holds one global `{session, loading, error}`; no cache, no de-dupe, no request cancellation, no persistence — a page refresh loses the active session on Home.

---

## 7. Prompt architecture

- Prompts are **externalised Markdown files** loaded at call time by `utils/prompt_loader.py` — a genuinely good design choice.
- Real content exists for `planner.md` (47 L), `researcher.md` (113 L), `verifier.md` (76 L), `writer.md` (101 L). They are detailed, role-scoped, format-prescriptive, and consistent in voice.
- `supervisor.md` and `memory.md` are **0 bytes** — the supervisor/memory concepts were planned and never built.

Weaknesses:

- **No caching**: every agent call re-reads the file from disk (fine at current volume, wasteful at scale).
- **No templating/variable substitution**: `load_prompt` returns raw text; per-call context is hand-concatenated into f-strings inside each agent (see `writer_agent.py:52-85`, where a large block of *instructions* lives in the Python user message rather than in the prompt file — instruction logic is split across two places).
- **No versioning, no prompt registry, no eval harness, no A/B or regression testing.** Prompt edits are unversioned behaviour changes.
- **Output format is enforced only by natural-language instruction**, yet Python code parses it (`_confidence_from_verification`). This is an undeclared contract between prose and code with no validator — the single most likely source of silent production breakage.
- **Prompt-injection surface:** the user query is inserted verbatim into a system-prompted chat with no sanitisation, delimiting, or output filtering. A crafted query can override role constraints (e.g. force the Research Agent to emit a final report, or leak the system prompt).
- No token budgeting: `MAX_TOKENS=4096` is global; the Writer receives query+plan+research+verification concatenated with no truncation strategy, so long research will silently blow context on smaller models.

---

## 8. LLM abstraction and OpenRouter integration

`core/llm.py` (42 lines) — `LLMClient` wraps the `openai` SDK against `base_url=https://openrouter.ai/api/v1`.

What works: configurable model/temperature/max_tokens/timeout, bounded retry loop (`LLM_MAX_RETRIES + 1` attempts), empty-content detection, `LLMError` translation, `logger.exception` on final failure.

Weaknesses:

- **`except Exception` retries everything** — 401 invalid key, 400 malformed request, and context-length errors are retried identically to 429/5xx, tripling latency and cost on non-retryable failures. **[verified: a fake key produced 3 connection attempts then a 502.]**
- **Fixed linear sleep** `0.5 * (attempt + 1)`, no jitter, no `Retry-After` honouring, no distinction of rate-limit backoff. `time.sleep` in a sync route occupies a threadpool worker.
- **`LLMError` discards the provider's message** ("The AI provider could not complete this request."), so the API cannot distinguish rate-limit from auth from context-overflow — and neither can operators.
- **No usage/telemetry**: `response.usage` is ignored → no token counts, no cost tracking, no latency metrics, no per-request logging of model actually used (OpenRouter can route/fall back).
- **No streaming**, no async client (`AsyncOpenAI`), no per-call temperature/max_tokens override, no `extra_headers` (`HTTP-Referer`/`X-Title`, which OpenRouter uses for attribution), no model fallback chain, no structured-output/JSON mode, no response caching.
- **`switch_model()` mutates instance state and is never called anywhere.** Combined with the module-level singleton orchestrator, if it *were* wired to a request parameter it would leak model choice across concurrent requests.
- **4 clients per process** (one per agent) instead of a shared client — 4× connection pools, and no single place to add instrumentation.
- The retry loop has no post-loop `return`/`raise` (unreachable today, but an implicit-`None` code smell).
- `.env.example` and `Settings` are perfectly in sync (12/12 keys) **[verified]** — one of the cleaner parts of the repo.

---

## 9. What is fully implemented

These work end-to-end today (LLM-mocked run confirmed **[verified]**):

1. **FastAPI app boots and serves** — root banner, `/api/health`, Swagger at `/docs`.
2. **Four-agent sequential pipeline** — Planner → Research (+ optional Verifier → Writer).
3. **Prompt externalisation + loader** for the four real prompts.
4. **OpenRouter LLM client** with timeout, bounded retries, empty-response guard, and error translation.
5. **SQLite session persistence** — create/read/update/list, parameterised SQL, thread-locked, state survives restart.
6. **Six REST endpoints** with Pydantic request validation (`query` 3–4000 chars → 422 **[verified]**) and typed response models.
7. **Typed configuration** via `pydantic-settings` with `.env` loading, range-validated numerics, and CSV→list CORS parsing.
8. **Centralised logger factory** with handler-duplication guard.
9. **CORS middleware** driven by config.
10. **React SPA** — routing (5 routes + catch-all), context state, research/verify/report/history/detail flows, client-side Markdown-file download. **`npm ci` and `npm run build` both succeed; ESLint is clean on `src/`** **[verified]**.
11. `.gitignore` is comprehensive; `.env` is not tracked; no secrets in the repo **[verified]**.

---

## 10. What is partially implemented

| Area | Present | Gap |
|---|---|---|
| **Base agent** | ABC + `validate` + `cleanup` | `validate` is a `None` check only; hooks/metrics/memory are TODO comments; two contradictory `execute` contracts |
| **Exception taxonomy** | 6 custom classes in `exceptions.py` | Only `LLMError` is ever used; `AgentError`/`WorkflowError`/`ResearchError`/`ConfigurationError` are **dead code**; `MemoryError` shadows the builtin **[verified]** |
| **Workflow orchestration** | 3 linear methods | No status enum/state machine, no step retries, no checkpointing, no parallelism, no timeouts, no budget caps; verify+write conflated |
| **WorkflowState** | serialisable dict round-trip | Duplicated fields, unused `memory` dropped on serialise, no validation, no run metrics |
| **Session management** | CRUD + list | Connection leak, no migrations, no indexes, no delete, no pagination, no ownership, single-process |
| **Confidence scoring** | substring parser | Fails on the bold/markdown output the prompts actually encourage **[verified]** |
| **Error handling** | per-route try/except | Blanket 502 masks bugs; no global handlers; no correlation IDs; failed runs unpersisted |
| **Logging** | `get_logger` | Used in exactly 2 modules; plaintext only; no request IDs, no JSON, no file/rotation, no latency/token logs, no secret redaction |
| **Tests** | 5 files exist | **0 pytest tests collected [verified]**; see §14 |
| **Reading time / confidence** | computed | Presentation logic embedded in the orchestrator, duplicated 3× |
| **Frontend** | pages render | Raw-text report display (no Markdown renderer), no timeouts, no live progress, dead components/deps, see §16 |
| **Docs** | 3 filenames | All 0 bytes; README contradicts actual API paths and folder layout |
| **Dependencies** | `requirements.txt` | UTF-16LE+BOM+CRLF encoding **[verified]**; no test/lint/type deps; no `pyproject.toml` |

---

## 11. What is missing for the planned production-grade multi-agent architecture

**Agentic capability (the largest product gap):**

- **No tools of any kind.** `tools/` is empty. The "Research Agent" is pure parametric LLM recall — no web search, no scraping, no arXiv/Semantic Scholar, no citations, no source URLs, no retrieval grounding. For a *research* platform this means output is structurally unverifiable, and the "Verifier" is an LLM grading another LLM's recollection with no external ground truth.
- **No memory / RAG.** `memory/` empty, `prompts/memory.md` empty, `WorkflowState.memory` unused and unpersisted. No embeddings, vector store, chunking, or knowledge base — so the "Knowledge Hub" page is static prose.
- **No supervisor / router / planner-executor loop.** `prompts/supervisor.md` is empty. No dynamic agent selection, no re-planning, no critique→re-research iteration, no multi-round convergence, no agent-to-agent messaging.
- **No structured LLM outputs** (JSON schema / tool calling), so no reliable machine-readable handoff between agents.

**Platform/infra:**

- No async job execution (Celery/RQ/ARQ/`BackgroundTasks`), no queue, no worker tier — long LLM workflows run inline in the HTTP request.
- No progress streaming (SSE/WebSocket) despite the UI having a `WorkflowProgress` component.
- No real database (Postgres), no ORM, no Alembic migrations, no connection pooling.
- No caching (Redis), no rate limiting, no circuit breaker, no idempotency.
- **No authentication/authorisation, no users, no multi-tenancy, no API keys, no quotas.**
- No observability: no metrics (Prometheus), no tracing (OpenTelemetry), no structured logs, no LLM cost/token dashboards, no Sentry.
- **No containerisation** (no Dockerfile/compose), no deployment manifests, no reverse-proxy/static-serving strategy, no health/readiness split, no graceful shutdown.
- **No CI/CD** (`.github/` absent), no lint/format/type gates (ruff/black/mypy), no pre-commit, no coverage, no dependency scanning, no `pyproject.toml`.
- No export pipeline (PDF/DOCX are README "Coming Soon"; no `reportlab`/`python-docx`/`weasyprint` in requirements).
- No follow-up/conversational research, no report versioning/diffing, no sharing/permalinks.
- Non-functional requirements undefined: no SLOs, no timeout budget, no cost ceiling, no data-retention or PII policy.

---

## 12. Architectural inconsistencies and technical debt

1. **Dual agent contract** — `PlannerAgent.execute(str) → str` vs the other three `execute(state) → state`, both under one abstract signature **[verified breakage]**.
2. **Duplicate/dead package trees** — root `agents/`, `tools/`, `memory/`, `database/`, `database/sqlite/`, `backend/models/`, `backend/services/` are all empty `__init__.py` shells.
3. **`backend/agents/` lacks `__init__.py`** while all siblings have one.
4. **Import-time side effects everywhere** — settings validation, DB file creation, and 4 LLM client constructions all happen on import. This is the root cause of the untestability in §14.
5. **Duplicated state fields** — `query`/`user_query`, `research`/`research_notes` dual-written for legacy compatibility.
6. **Prose↔code contract** — Python parses markdown the prompt only *asks* for, with no validation **[verified fragility]**.
7. **Mixed code styles** — `core/agent.py` and `exceptions.py` are verbose Google-style-docstring code; `workflow.py`, `routes.py`, `session.py`, and the entire frontend are aggressively compressed multi-statement one-liners (e.g. `History.jsx` is one 700-char line). Two different authorship conventions, no formatter to reconcile them.
8. **Stale docstrings** — `research_agent`/`verifier_agent` document `input_data (str)`; `test_*` headers describe workflows that no longer exist.
9. **README ≠ reality** — endpoint paths, folder structure ("backend/prompts"), "Planner Agent (Hidden)" (the plan is returned in every API response), and "✅ Completed" claims for things that are thin or brittle.
10. **Empty-subclass schemas** — three response models with zero differentiation.
11. **Presentation logic in the orchestrator** (`reading_time`), duplicated 3×.
12. **Dead API surface** — `LLMClient.switch_model()`, `BaseAgent.cleanup()`, 5 of 6 exception classes, `HeroSection.jsx`, `Reports.jsx` (renders `History` verbatim), `frontend/src/assets/*`, `public/icons.svg`, `framer-motion` + `lucide-react` (**imported nowhere** **[verified]**).
13. **`requirements.txt` is UTF-16LE with a BOM** **[verified]** — `pip` tolerated it in my test, but it is non-standard, breaks naïve tooling/diffs, and pins are exact-`==` with no separate dev/test extras.
14. **Vite `outDir: "build"` vs ESLint `globalIgnores(['dist'])`** — after a build, `npx eslint .` lints the minified bundle and reports **118 errors** **[verified]**; clean before build. Lint is not build-order-safe.
15. **`frontend/package-lock.json` is matched by `.gitignore` (line 175) yet is tracked** **[verified]** — contradictory; reproducible installs depend on an ignored-by-policy file.
16. **`frontend/README.md` is the untouched Vite template**; `index.html` `<title>` is literally `frontend`.
17. **`ENVIRONMENT` config key read nowhere** — no environment-specific behaviour exists.
18. **`MemoryError` shadows a Python builtin.**

---

## 13. Security and configuration concerns

**High**

1. **No authentication or authorisation on any endpoint.** Anyone reachable can trigger paid LLM workflows and read *all* sessions via `GET /api/sessions` — session data is globally listable, not per-user. UUID4 ids are unguessable, but listing removes that as a control.
2. **No rate limiting or quota** → direct cost-based DoS. One `POST /api/research` = 2 LLM calls up to 4096 completion tokens; `/verify` adds 2 more; both are unauthenticated and repeatable.
3. **Prompt injection unmitigated** — raw user query concatenated into system-prompted messages, no delimiting/sanitisation, no output moderation. Roles are enforced only by prose.
4. **Swagger `/docs` always exposed** — `ENVIRONMENT` is never checked, so full API introspection is public in any deployment.

**Medium**

5. **Fail-at-import config** — `OPENROUTER_API_KEY: str = Field(..., min_length=1)` plus a module-level `Settings()` means a missing key is an *import* crash, not a startup diagnostic **[verified]**; the traceback surfaces the field name.
6. **No secret hygiene beyond `.env`** — no secret-manager path, no key rotation, no redaction filter in the logger; `logger.exception` dumps full tracebacks (currently benign, but request bodies/prompts are one careless log call away from leaking).
7. **SQLite DB written into the repo tree** by default (`database/autoresearch.sqlite3`), created at import with default file permissions; unencrypted research content at rest; no backup story.
8. **CORS `allow_methods=["*"]`, `allow_headers=["*"]`** with no `TrustedHostMiddleware`, no HTTPS enforcement, no security headers (CSP/HSTS/X-Frame-Options).
9. **Blanket `502`** for internal bugs — good for not leaking internals, bad because it also hides them from monitoring (no error class, no correlation id).
10. **No request timeout or body/size ceiling** at the app layer; a 4000-char query with `MAX_TOKENS=4096` × 4 calls can hold a threadpool worker for minutes.
11. **Frontend has no auth/CSRF concern today only because there is no auth** — adding cookies later would require revisiting `allow_credentials=False` and origin policy.
12. **Exact-pinned deps with no vulnerability scanning**, and several pins (`fastapi 0.139.0`, `starlette 1.3.1`, `pydantic 2.13.4`, `vite 8`, `react 19.2.7`, `eslint 10`) are far ahead of common baselines — no Dependabot/`pip-audit`/`npm audit` gate.

---

## 14. Testing gaps

**Current state [all verified]:**

- `pytest --collect-only` → **"no tests collected"** (with a key set); **without** `OPENROUTER_API_KEY` it is **5 collection errors** before any test runs, because importing the modules constructs `Settings()`.
- All 5 files are `main()` + `print()` scripts with **zero assertions**.
- `tests/test_workflow.py` calls **`input()` twice** — interactive, unrunnable in CI.
- Every test requires a **live API key, network access, and real spend** — no mocks, no fixtures, no fakes, no `conftest.py`, no `responses`/`respx` stubbing.
- `tests/test_research_agent.py` and `tests/test_verifier_agent.py` pass a `str` where a `WorkflowState` is required → **`AttributeError` on execution [verified]**. They are stale artefacts.
- `pytest` is not in `requirements.txt` at all; no `pytest.ini`/`pyproject` config, no coverage tooling, no CI to run any of it.

**Untested surface (0% coverage):** `config.py`, `logger.py`, `state.py` (to_dict/from_dict round-trip, the dropped `memory`), `session.py` (all CRUD, the FD leak, concurrency), `routes.py` (all 6 endpoints, 404/422/502 paths), `schemas/api.py`, `prompt_loader.py` (missing-file branch), `workflow.py` (`_confidence_from_verification` — the exact function I broke in 4 of 7 input variants), `llm.py` (retry counts, non-retryable classification, empty-content guard), `writer_agent` no-verification branch.

**Missing test categories entirely:** unit tests with a fake LLM, API contract tests (`TestClient`), DB integration tests against a temp file, concurrency tests, prompt/output-format regression tests, LLM-output eval harness, frontend tests (no Vitest/RTL/Playwright — zero test files under `frontend/`), load tests, security tests.

---

## 15. Scalability concerns

1. **Single-process by construction** — global `SessionManager` + `threading.RLock` + one SQLite file. Running two Uvicorn workers gives you two lock domains over one file and `SQLITE_BUSY` under write contention (no WAL, no `busy_timeout`). **Horizontal scaling is currently impossible.**
2. **Long synchronous requests** — a full research+verify cycle is 4 sequential LLM calls, each up to `LLM_TIMEOUT_SECONDS=60` with up to 3 attempts. Worst case per endpoint approaches minutes, exceeding typical load-balancer/CDN idle timeouts (30–60 s). No job queue, no `202 Accepted` pattern, no resumability.
3. **Threadpool exhaustion** — sync `def` handlers + blocking SDK calls + `time.sleep` backoff cap effective concurrency at ~40 in-flight requests, each holding a worker for its entire duration.
4. **FD leak on the DB path** [verified] compounds under sustained traffic.
5. **Unbounded per-request cost** — no token accounting, no per-user or global budget, no cache. Identical queries always cost full price.
6. **Payload growth** — full plan + research + verification + report are returned in *every* response and stored as unbounded TEXT; `list_sessions` reads the whole report per row just to compute a boolean.
7. **No index on `updated_at`** for the sort path; no cursor pagination (offset-less `LIMIT` only).
8. **4 LLM clients per process**; prompt files re-read from disk on every agent call.
9. **No backpressure, circuit breaker, or degradation mode** when OpenRouter rate-limits — retries amplify load into an already-failing dependency.
10. **No horizontal-scale-safe state** — `WorkflowState` lives in memory during a request and is only checkpointed at the end; a restart mid-run loses everything.

---

## 16. Frontend limitations

Build health is genuinely fine (`npm ci` ✅, `npm run build` ✅ 241 kB JS / 77 kB gzip, ESLint clean on `src/`) **[verified]**. The limitations are functional and structural:

1. **Reports render as raw text** — `whitespace-pre-wrap` in `ResearchResult.jsx` and `ReportDetail.jsx`. The backend produces heavily-formatted Markdown (`#`, `•`, tables, emoji) and there is **no Markdown renderer dependency** at all **[verified]**. The core deliverable is displayed as unformatted plaintext with literal `#` characters.
2. **No live workflow progress** — `WorkflowProgress` reads `session.completed_tasks`, which only exists *after* the request resolves. During the multi-minute wait it shows a static "agents are working" line. No SSE/polling.
3. **No request timeout or cancellation** — `fetch` with no `AbortController`; a hung backend hangs the UI permanently with no cancel button.
4. **Results vanish during actions** — `if (!session || loading) return null` unmounts `ResearchResult` while verify/report runs, so the user loses the text they were reading.
5. **No client persistence** — refresh on `/` loses the active session (no localStorage/URL state); no cache or de-dupe (`ReportDetail` refetches every mount).
6. **`History` effect has no cleanup/abort** → `setState` on an unmounted component and a possible response race.
7. **Duplicate/placeholder pages** — `Reports.jsx` renders `History` verbatim (two routes, one view); `KnowledgeHub` is hardcoded prose; the `*` catch-all silently renders Home instead of a 404.
8. **Dead code and unused deps** — `HeroSection.jsx` never imported; `framer-motion` and `lucide-react` declared but imported nowhere; `src/assets/hero.png|react.svg|vite.svg` and `public/icons.svg` unreferenced **[all verified]**.
9. **Hardcoded absolute API base + no Vite dev proxy** — cross-origin by default and non-portable across environments (see §6).
10. **No error boundary**, no toast system, error text is string-concatenated (`{error}. You can revise…` yields double punctuation), errors are thrown-and-swallowed with bare `.catch(()=>{})` in 5 places.
11. **Accessibility/SEO/polish** — `<title>frontend</title>`, no meta description, no favicon branding beyond the default, no skip link, no focus management on route change; `aria-live`/`role="alert"` are used in a few spots (good) but inconsistently.
12. **No tests, no TypeScript, no Prettier**; readability is severely hurt by the one-line-per-file compression style.
13. **No export UI beyond a client-side `.md` Blob download** — PDF/DOCX (README "Coming Soon") have no backend or frontend hook.

---

## 17. Recommended implementation order

> Everything below is **my recommendation**, not existing implementation.

**Phase 0 — Foundation & correctness (unblocks everything else)**

1. Remove import-time side effects: `get_settings()` (cached), `create_app()` factory, FastAPI `lifespan` for DB/LLM, `Depends()` for `SessionManager`/`WorkflowOrchestrator`/`LLMClient`.
2. One shared `LLMClient` injected into agents (kill the 4-client pattern and `switch_model` mutation).
3. Unify the agent contract: `execute(state) -> state` for all four (fixes the Planner outlier and the two broken tests).
4. Fix the SQLite connection leak (explicit `close()`/context-managed connection), enable WAL + `busy_timeout`, add an `updated_at` index, stop selecting `final_report` in `list_sessions`.
5. Fix `requirements.txt` encoding → UTF-8/LF; split runtime vs dev deps; add `pyproject.toml`.
6. Real `pytest` suite with a fake LLM: state round-trip, session CRUD, prompt loader, confidence parser, all 6 endpoints via `TestClient`. Delete/replace the interactive scripts. Add `.github/workflows/ci.yml` (pytest + ruff + mypy + `npm ci && npm run build && npm run lint`), and fix `globalIgnores(['dist'])` → `['build']`.

**Phase 1 — Robustness & contracts**

7. `WorkflowState` → Pydantic model; `Status`/`Confidence` enums; drop duplicate fields; add `run_id`, per-step timings, tokens, cost, `error`.
8. Replace prose-parsed confidence with **structured output** (JSON schema / tool call) validated by Pydantic, with a text fallback.
9. Split `verify_report` into `verify()` and `write()`; add an explicit state machine with legal transitions; persist a checkpoint after **every** step (so failures and partial runs are recorded).
10. LLM layer: classify retryable vs non-retryable errors, exponential backoff + jitter, preserve provider error detail in a typed error hierarchy, record `usage` tokens/cost, add OpenRouter attribution headers.
11. Error/observability layer: global exception handlers, typed error responses with codes, `X-Request-ID` middleware + correlation IDs, structured JSON logging with secret redaction, `/api/health` (liveness) vs `/api/ready` (DB + provider reachability). Stop mapping internal bugs to 502.
12. Use the exception taxonomy that already exists (or delete the dead classes); rename `MemoryError`.

**Phase 2 — Async execution & real-time UX**

13. `POST /api/v1/research` → `202` + `job_id`; execute via a worker (ARQ/RQ/Celery, or `BackgroundTasks` as a stepping stone); add `GET /jobs/{id}`.
14. SSE (or WebSocket) progress stream; wire `WorkflowProgress` to live step events.
15. Frontend: add a Markdown renderer (sanitised), `AbortController` + timeouts + cancel button, keep results visible during actions, persist active session, error boundary, real 404, remove dead components/deps, add a Vite dev proxy + relative API base.
16. Async LLM client (`AsyncOpenAI`) and async DB access.

**Phase 3 — Make it an actual research platform**

17. `tools/` layer: web search (Tavily/Brave/SerpAPI), fetch+extract, arXiv/Scholar; tool-calling loop in the Research Agent; **citations with source URLs persisted in state and rendered in reports**. This is what turns "LLM recall" into research.
18. Supervisor/Router agent (fill `prompts/supervisor.md`) + critique→re-research loop with iteration caps and a cost budget; parallel fan-out of plan sections with bounded concurrency.
19. `memory/` layer: embeddings + vector store + chunking; wire `WorkflowState.memory`, persist it, and back the Knowledge Hub with it; add follow-up/conversational research.
20. Prompt registry: versioned prompts, in-process cache, variable templating (move the Writer's inline instructions into `writer.md`), plus an eval/regression harness.

**Phase 4 — Production hardening & deployment**

21. Auth (API keys or OAuth/JWT) + `user_id` on sessions + per-user listing/ownership + quotas + rate limiting (Redis).
22. Postgres + SQLAlchemy + Alembic migrations; retention/TTL policy; `DELETE`/soft-delete; cursor pagination.
23. Export service: Markdown → PDF/DOCX endpoints.
24. Dockerfile(s) + compose (api, worker, redis, postgres, nginx serving the built SPA), env-gated `/docs`, `TrustedHostMiddleware`, security headers, graceful shutdown.
25. Metrics + tracing + cost dashboards + Sentry; `pip-audit`/`npm audit`/Dependabot; caching layer.
26. Fill the three empty `docs/*.md`, correct the README (real `/api/v1` paths, honest ✅/🚧 status, real folder tree), replace the Vite template README, resolve the `package-lock.json` ignore-vs-tracked contradiction, delete the empty root `agents/`/`tools/`/`memory/`/`database/`/`backend/models`/`backend/services` shells or give them content.

---

## Does the architecture match the intended "Multi-Agent Research Platform"?

**Partially — the skeleton matches, the substance does not.** The role-specialised agent decomposition, externalised prompts, orchestrator, shared state, session persistence, REST layer, and SPA are all genuinely present and coherent. But:

- The **multi-agent** part is a **fixed 4-step linear chain of single LLM calls** — no supervisor, no routing, no tool use, no memory, no iteration, no agent-to-agent negotiation. It is a prompt-chaining pipeline wearing multi-agent clothing.
- The **research** part performs **no research** — zero external retrieval, zero citations. The Verifier fact-checks recollection against nothing.
- The **platform/production** part is missing its load-bearing walls: no auth, no rate limiting, no async execution, no migrations, no containers, no CI, no observability, and a test suite that collects **zero** tests.

Treat the README's "✅ Completed" list as *scaffolded*, not *production-ready*.

---

## ⏭ NEXT STEP (do this first)

**A Phase-0 "foundation hardening" sprint — specifically: make the app injectable and testable, then land a real test suite + CI.**

Concretely, in one focused change set:

1. `get_settings()` (cached) + `create_app()` + `lifespan`; remove the three module-level singletons (`settings`, `session_manager`, `workflow`) and wire dependencies via `Depends()`.
2. One shared `LLMClient`, injected into all agents.
3. Unify `BaseAgent.execute(state) -> state` across all four agents.
4. Close SQLite connections properly (+ WAL, `busy_timeout`, `updated_at` index).
5. Replace `tests/` with real `pytest` tests driven by a fake LLM — covering the endpoint matrix, session CRUD, state round-trip, and `_confidence_from_verification` (which I broke on 4 of 7 realistic inputs) — and add a CI workflow that runs backend tests plus the frontend build/lint.

**Why this first:** the single biggest structural blocker in the repo is that **importing the code requires a live API key and creates a database** — which is precisely why zero tests can run today. Every subsequent phase (async jobs, retrieval tools, auth, Postgres) will be built on this wiring, and doing it *before* the codebase grows is an order of magnitude cheaper. It also converts the two already-broken test files and the brittle confidence parser from invisible risks into caught regressions.

Runners-up, deliberately deferred: **structured LLM outputs** (Phase 1 — the highest-probability silent production failure) and **the search/citation tool layer** (Phase 3 — the highest product value, but pointless to build on untestable foundations).

---

## Verification Appendix — how the **[verified]** findings were produced

All experiments ran outside the repository (throwaway venv at `/tmp/v`, frontend copy at `/tmp/fe`) with `OPENROUTER_API_KEY=fake` and `DATABASE_PATH` pointed at `/tmp`. No repository file was created, modified, or deleted; no commit or push was made.

| # | Finding | Method | Result |
|---|---|---|---|
| 1 | Config crashes at import without key | `env -u OPENROUTER_API_KEY python -c "import backend.core.config"` | `ValidationError: OPENROUTER_API_KEY Field required` |
| 2 | All 6 endpoints + error codes | `fastapi.testclient.TestClient(app)` | `/`→200, `/api/health`→200, `/api/sessions`→200, unknown session→404, `/api/verify/nope`→404, 2-char query→422, research with bad key→502 |
| 3 | DB created as import side effect | checked `DATABASE_PATH` file after import | file created automatically |
| 4 | Pipeline call counts + state transitions | monkeypatched `LLMClient` with a stub, ran `execute_pipeline` then `verify_report` | 2 + 2 LLM calls; `completed_tasks=['Planner','Research','Verification','Writer']`; `verify_report` sets `final_report` |
| 5 | `memory` dropped on serialise | `to_dict()` → `from_dict()` round-trip | `to_dict` keys exclude `memory`; restored `memory == {}` |
| 6 | Confidence parser fragility | 7 realistic verifier-output variants | `Confidence: High`→High, `confidence: medium`→Medium, `Overall Score…\nConfidence: High`→High; **`**Confidence:** High`, `Confidence: **High**`, `Confidence:  High`, `Confidence - Low` → `Unverified`** |
| 7 | Agent contract mismatch | `ResearchAgent().execute("str")`, `VerifierAgent().execute("str")` | `AttributeError: 'str' object has no attribute 'query'` / `'research'` |
| 8 | `validate()` allows empty string | `PlannerAgent().execute("")` with stub LLM | executes, returns `''` |
| 9 | SQLite connection/FD leak | 200 `create_session` calls, counted `/proc/self/fd` | 9 → 40 open FDs; dropped to 7 only after `gc.collect()` |
| 10 | Zero tests collected | `pytest --collect-only` with key set / without key | `no tests collected` / `5 collection errors` |
| 11 | `requirements.txt` encoding | byte inspection (`od -c`), UTF-16 decode | BOM `\xff\xfe`, UTF-16LE, CRLF, 24 pins; `pip install --dry-run` succeeded |
| 12 | `.env.example` ↔ `Settings` parity | field extraction + set diff | 12/12 keys match, no drift either direction |
| 13 | Frontend builds and lints | `npm ci`, `npm run build`, `npx eslint .` in `/tmp/fe` | install ✅; build ✅ (241.51 kB JS / 77.06 kB gzip, 36 modules); ESLint clean on `src/` |
| 14 | ESLint lints its own build output | `npx eslint .` after `npm run build` | **118 errors**, all in `build/assets/index-*.js`; clean after `rm -rf build` |
| 15 | Unused frontend deps/assets | `grep -rn` across `src/` + `index.html` | `framer-motion`, `lucide-react`, `HeroSection.jsx`, `icons.svg`, `hero.png`, `react.svg`, `vite.svg` — zero references |
| 16 | `package-lock.json` ignored yet tracked | `git check-ignore -v --no-index`, `git ls-files` | matched by `.gitignore:175`, still tracked |
| 17 | No dev proxy / no CI / empty docs | `grep proxy vite.config.js`, `ls .github`, `wc -c docs/*.md prompts/{memory,supervisor}.md` | no proxy; `.github` absent; all five files 0 bytes |
| 18 | Dead code / unused config | `grep -rn` for `ENVIRONMENT`, `switch_model`, `cleanup`, `AgentError`, `supervisor.md`, `memory.md` | each referenced only at its definition site |
| 19 | Python syntax integrity | `ast.parse` over every `*.py` | all files parse cleanly |
| 20 | Repository left untouched | `git status --porcelain` | empty output — clean working tree |

---

## Final Overall Assessment

**Verdict: a well-organised, coherent early-stage prototype (~700 LOC backend, ~147 LOC frontend `src`, one commit) that is architecturally *legible* but not architecturally *complete*, and is several phases away from production deployment.**

**What is genuinely good and worth preserving:**

- Clean layer separation (`api` → `workflow` → `agents` → `llm`) with prompts externalised to versionable Markdown — this is the right shape and most teams get it wrong.
- Typed configuration via `pydantic-settings` with range validation, and perfect `.env.example` ↔ `Settings` parity (12/12 keys) **[verified]**.
- Parameterised SQL everywhere (no injection risk), state that is genuinely serialisable and survives restart, and a working `WorkflowState`/`SessionManager` round-trip.
- A frontend that installs, builds, and lints cleanly, covering the whole user journey (research → verify → report → history → detail).
- No secrets committed; a thorough `.gitignore`.

**The three findings that most block production:**

1. **Untestability by construction.** Importing the code validates env, creates a database, and constructs four LLM clients. Consequence: **zero tests collect** (5 import errors without a key) **[verified]**. Every quality gate the project needs is blocked behind this one issue.
2. **Prose-to-code contracts with no validator.** `_confidence_from_verification` parses markdown the prompt merely *requests*; it silently returns `Unverified` for 4 of 7 realistic verifier outputs, including the bold-label form the prompt's own style encourages **[verified]**. This is the archetype of a defect that passes review and fails in production.
3. **No agentic substance.** `tools/` and `memory/` are empty directories; `prompts/supervisor.md` is 0 bytes. There is no retrieval, no citation, no external ground truth — so a "research platform" ships unverifiable parametric recall, and its "fact check" agent grades one model's memory using another model's memory.

**Runners-up that will bite at first real traffic:** the SQLite connection/FD leak (9 → 40 FDs over 200 writes **[verified]**), multi-minute synchronous request paths that exceed normal load-balancer timeouts, a single-process-only persistence design (global `RLock` + one SQLite file, no WAL), and the absence of auth or rate limiting on unauthenticated endpoints that spend money per call.

**Documentation credibility:** the README's "✅ Completed" list and API table do not match the code — real paths are `/api/*`, three endpoints are undocumented, the "hidden" planner output is returned in every response, and the documented folder layout is wrong. Read the repository, not the README. All three `docs/*.md` files are empty **[verified]**.

**Gap between intent and reality:** the intended **Multi-Agent Research Platform** is, today, a **fixed four-step prompt chain** — correctly decomposed by role, but with no supervisor, no routing, no tools, no memory, no iteration, and no agent-to-agent messaging. The skeleton matches the vision; the substance does not yet.

**Bottom line:** this is a strong foundation with honest bones and a small, fixable set of structural mistakes — not a system that should be deployed. The highest-leverage move is *not* to add features but to make the existing code injectable and testable, then lock it behind CI. Do Phase 0 first; every later phase compounds on that wiring, and doing it now is an order of magnitude cheaper than doing it at 5,000 LOC.

---

*Assessment produced under analysis-only constraints. No application or source file was modified, created, or deleted; nothing was committed or pushed. `git status --porcelain` returned empty after all verification work **[verified]**. This document is the only file added.*
