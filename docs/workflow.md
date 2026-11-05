# Workflow

## Agents and sequence

1. **Planner** turns the user's question into a structured research plan.
2. **Research** answers the question. When web research is enabled it first runs
   one bounded search + safe-fetch pass, injects the retrieved evidence as
   clearly delimited, untrusted data, and appends a deterministic `# Sources`
   section. When web research is disabled or fails it falls back to LLM-only
   research and records the situation in `diagnostics`.
3. **Verifier** reviews the research for unsupported or conflicting claims and
   emits a confidence marker that the orchestrator parses tolerantly.
4. **Writer** produces the final Markdown report, applying verification feedback
   silently when present. Chain-of-thought leakage is stripped defensively.

## Status vocabulary

`Queued → Planning → Researching → Research completed`
`→ Verifying → Writing verified report → Verified report generated`
or `→ Writing report → Report generated`
and `Failed` on any unrecoverable error, with a safe `error` message.

Terminal statuses are `Research completed`, `Verified report generated`,
`Report generated`, and `Failed` (see `backend/core/statuses.py`).

## Synchronous versus background execution

Two equivalent entry points exist.

### Synchronous (simple, blocking)

- `POST /api/research`
- `POST /api/verify/{session_id}`
- `POST /api/report/{session_id}`

The response is returned only after the LLM calls finish. These remain supported
for backward compatibility and for deterministic offline tests.

### Background jobs (recommended for the UI)

- `POST /api/jobs/research` → `202 Accepted` with `session_id`, `poll_url` and
  `poll_interval_seconds`.
- `POST /api/jobs/verify/{session_id}` and `POST /api/jobs/report/{session_id}`
  schedule follow-up work on an existing session.
- `GET /api/jobs/{session_id}` returns the full session payload plus
  `job_active`.

A session row is created immediately in the `Queued` state, and the orchestrator
checkpoints the state after every step. The frontend polls the job endpoint and
stops when the status is terminal. Starting a second job for a session that is
already running returns `409 Conflict`.

## Failure handling

- Agent/LLM failures inside a background job are caught, persisted as
  `Failed` with a bounded, secret-free message, and surfaced by the UI. The
  successfully gathered content up to that point is retained.
- Web-search or fetch failures never fail the request; they are recorded in
  `diagnostics` and the run degrades to model-only research.
- Unknown sessions return `404`; invalid requests return `422`; workflow
  validation errors return `422`; upstream LLM failures on synchronous routes
  return `502` with a generic message.

## Health and readiness

- `GET /api/health` is a static liveness probe.
- `GET /api/ready` checks database connectivity and returns `503` when storage
  is unavailable.
