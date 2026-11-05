# Architecture

AutoResearchAI is a single-process multi-agent research application composed of a
FastAPI backend, an SQLite persistence layer, an optional bounded web-research
tool layer, and a React single-page frontend.

## High-level request flow

```text
Browser (React SPA, Vite)
        │  relative /api requests (Vite dev proxy or same-origin in production)
        ▼
FastAPI app (backend/main.py, lifespan-wired resources)
        │
        ▼
API routes (backend/api/routes.py)
        │  sync endpoints (immediate)  +  background job endpoints (HTTP 202)
        ▼
JobRunner (backend/core/jobs.py, bounded ThreadPoolExecutor)
        │  checkpoints progress after every step
        ▼
WorkflowOrchestrator (backend/core/workflow.py)
        │
        ├─► PlannerAgent
        ├─► ResearchAgent  ──► optional WebResearchService (search + safe fetch)
        ├─► VerifierAgent
        └─► WriterAgent
                  │
                  ▼
             LLMClient (OpenRouter, OpenAI-compatible)
                  │
                  ▼
        SessionManager ──► SQLite (WAL, parameterised SQL, migrations)
```

## Backend layers

- **`backend/core/config.py`** — Pydantic settings. Resolved lazily via
  `get_settings()` so importing modules has no side effects and no key is
  required at import time.
- **`backend/core/container.py`** — composition root. Builds one shared
  `LLMClient`, the four agents, the `SessionManager`, the `WorkflowOrchestrator`
  and the `JobRunner`.
- **`backend/core/agent.py`** — `BaseAgent` with a single
  `execute(state) -> state` contract; prompts are externalised Markdown files
  loaded by `backend/utils/prompt_loader.py`.
- **`backend/core/workflow.py`** — fixed, validated agent sequence with an
  optional progress callback used to checkpoint state.
- **`backend/core/jobs.py`** — in-process background runner. The API persists a
  `Queued` session immediately, then runs the workflow off the request thread;
  failures are persisted with a safe error message.
- **`backend/core/state.py` / `statuses.py`** — serialisable shared state and the
  canonical status vocabulary.
- **`backend/core/session.py`** — SQLite sessions with WAL mode, a busy timeout,
  an index on `updated_at`, idempotent additive migrations, and connections that
  are always closed.
- **`backend/tools/web/`** — provider-agnostic search (Tavily), an SSRF-safe
  fetcher that validates every URL and redirect before connecting, a standard
  library HTML/text extractor, deterministic source registry/citations, and a
  service that degrades gracefully to LLM-only research on any failure.

## Reliability and safety properties

- One shared LLM client; non-retryable provider errors (auth, bad request,
  permission, not found) fail fast while transient errors use bounded retries
  with backoff and jitter.
- Web fetching is allow-listed to HTTP/HTTPS text content, blocks loopback,
  private, link-local, CGNAT and cloud-metadata destinations, bounds redirects,
  response size and extracted text, and treats all retrieved content as
  untrusted data (never instructions).
- The database is the source of truth; in-memory job tracking only records which
  sessions are currently executing, so progress and failures survive restarts.

## Deployment model

The design targets a single long-lived server process (for example Uvicorn behind
a reverse proxy, or a container). The in-process worker pool intentionally avoids
Redis/Celery; scaling to multiple processes would require replacing `JobRunner`
with a durable external queue and moving sessions to a client/server database.
