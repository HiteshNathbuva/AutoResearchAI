# Roadmap

This roadmap reflects the implemented system honestly. Items under "Shipped" are
covered by the automated test suite; later items are forward-looking and not yet
built.

## Shipped

- Four-agent sequential workflow: Planner → Research → Verifier → Writer.
- OpenRouter (OpenAI-compatible) LLM client with bounded retries, fast failure
  for non-retryable errors, and backoff with jitter.
- Background job execution with an in-process bounded worker pool, immediate
  session creation, step checkpoints, polling, duplicate-job protection and
  persisted failure state.
- SQLite session persistence with WAL mode, busy timeout, an `updated_at`
  index, idempotent additive migrations and disciplined connection handling.
- Optional real web research: Tavily search plus an SSRF-safe fetcher,
  standard-library extraction, bounded resources, graceful degradation and
  deterministic source/citation tracking.
- REST API with typed schemas, liveness and readiness probes.
- React workspace with sanitized Markdown rendering, clickable source
  citations, live workflow progress, request timeouts/cancellation, history,
  saved reports, honest provenance/error banners and a 404 page.
- Offline pytest suite (mocked LLM and retrieval), ruff lint, ESLint and a CI
  workflow.

## Next candidates

- Structured (schema-validated) LLM outputs to replace prose parsing of the
  confidence marker.
- A supervisor/critique loop with an iteration cap and a per-run token/cost
  budget, and parallel research of plan sections.
- User accounts, per-user session ownership, authentication and rate limiting.
- PDF/DOCX report export.
- Follow-up/conversational research and report versioning.
- Container image and an example single-host deployment that serves the built
  SPA and API together.

## Scaling considerations

The current design is intentionally single-process: one SQLite database and one
in-process job pool. Horizontal scaling would require a durable job queue
(for example ARQ/RQ with Redis), a client/server database, and moving session
ownership to authenticated users.
