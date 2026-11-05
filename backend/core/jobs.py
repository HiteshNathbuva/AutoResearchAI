"""In-process background job runner for long-running research workflows.

A research/verify/report request makes several sequential LLM calls and can run
for far longer than a normal HTTP request. Executing it inline would occupy a
server worker for minutes, give the user no progress signal, and leave no trace
when it fails. Instead the API accepts the request, persists a session
immediately (status ``Queued``), and hands the work to a small bounded thread
pool here.

Every workflow transition is checkpointed back to SQLite through the
orchestrator's progress callback, so a client can poll
``GET /api/sessions/{id}`` (or ``GET /api/jobs/{id}``) for live status, and a
failure is persisted with a safe error message instead of disappearing.

The SQLite database (WAL mode plus a process-wide lock) is the source of truth;
the in-memory structures only track which sessions are currently executing. No
Redis, Celery, or external broker is required, which matches the project's
single-process deployment model. Scaling to multiple processes would require a
durable external queue.
"""

from __future__ import annotations

import threading
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from backend.core.logger import get_logger
from backend.core.session import SessionManager
from backend.core.state import WorkflowState
from backend.core.statuses import QUEUED
from backend.core.workflow import WorkflowOrchestrator

logger = get_logger(__name__)


class JobConflictError(RuntimeError):
    """Raised when a job is requested for a session that is already running."""


class JobRunner:
    """Runs workflow jobs in a bounded pool and checkpoints their progress."""

    def __init__(self, workflow: WorkflowOrchestrator, sessions: SessionManager,
                 max_workers: int = 2):
        self.workflow = workflow
        self.sessions = sessions
        self._executor = ThreadPoolExecutor(
            max_workers=max_workers, thread_name_prefix="research-job"
        )
        self._lock = threading.RLock()
        self._active: set[str] = set()
        self._futures: dict[str, object] = {}

    # ------------------------------------------------------------------
    # Lifecycle / introspection
    # ------------------------------------------------------------------

    def is_active(self, session_id: str) -> bool:
        """Return ``True`` while a job for ``session_id`` is queued or running."""

        with self._lock:
            return session_id in self._active

    def close(self) -> None:
        """Cancel pending jobs and release the pool without blocking shutdown."""

        with self._lock:
            futures = list(self._futures.values())
        for future in futures:
            future.cancel()  # type: ignore[attr-defined]
        # In-flight calls still respect their own HTTP timeouts; do not block.
        self._executor.shutdown(wait=False)

    # ------------------------------------------------------------------
    # Public entry points used by the API
    # ------------------------------------------------------------------

    def start_research(self, query: str) -> str:
        """Persist a queued session and schedule the research pipeline."""

        state = WorkflowState()
        state.update_query(query)
        state.clear_error()
        state.update_status(QUEUED)
        state.current_step = QUEUED
        session_id = self.sessions.create_session(state)
        created_at = state.metadata["created_at"]
        self._submit(session_id, self._run_research, session_id, query, created_at)
        return session_id

    def start_verify(self, session_id: str) -> str:
        """Schedule verification (plus report writing) for an existing session."""

        self._require_session(session_id)
        self._require_idle(session_id)
        created_at = self.sessions.get_session(session_id).metadata["created_at"]
        self._submit(session_id, self._run_verify, session_id, created_at)
        return session_id

    def start_report(self, session_id: str) -> str:
        """Schedule report generation for an existing session."""

        self._require_session(session_id)
        self._require_idle(session_id)
        created_at = self.sessions.get_session(session_id).metadata["created_at"]
        self._submit(session_id, self._run_report, session_id, created_at)
        return session_id

    # ------------------------------------------------------------------
    # Internal execution
    # ------------------------------------------------------------------

    def _submit(self, session_id: str, fn, *args) -> None:
        with self._lock:
            self._active.add(session_id)
        future = self._executor.submit(self._guard, session_id, fn, *args)
        with self._lock:
            self._futures[session_id] = future

    def _guard(self, session_id: str, fn, *args) -> None:
        """Top-level worker wrapper: record failures and clear the active flag."""

        try:
            fn(*args)
        except Exception as error:  # noqa: BLE001 - the runner must never raise out of a thread
            logger.exception("Background job for session %s failed", session_id)
            self._record_failure(session_id, error)
        finally:
            with self._lock:
                self._active.discard(session_id)
                self._futures.pop(session_id, None)

    def _checkpoint(self, session_id: str, created_at: str, state: WorkflowState) -> None:
        """Persist intermediate state while preserving the original timestamp."""

        state.metadata["created_at"] = created_at
        self.sessions.update_session(session_id, state)

    def _run_research(self, session_id: str, query: str, created_at: str) -> None:
        on_update = partial(self._checkpoint, session_id, created_at)
        state = self.workflow.execute_pipeline(query, on_update=on_update)
        self._checkpoint(session_id, created_at, state)

    def _run_verify(self, session_id: str, created_at: str) -> None:
        state = self.sessions.get_session(session_id)
        on_update = partial(self._checkpoint, session_id, created_at)
        state = self.workflow.verify_report(state, on_update=on_update)
        self._checkpoint(session_id, created_at, state)

    def _run_report(self, session_id: str, created_at: str) -> None:
        state = self.sessions.get_session(session_id)
        on_update = partial(self._checkpoint, session_id, created_at)
        state = self.workflow.generate_report(state, on_update=on_update)
        self._checkpoint(session_id, created_at, state)

    def _record_failure(self, session_id: str, error: BaseException) -> None:
        try:
            state = self.sessions.get_session(session_id)
        except KeyError:
            logger.error("Cannot persist failure: session %s no longer exists", session_id)
            return
        state.mark_failed(self._safe_message(error))
        try:
            self.sessions.update_session(session_id, state)
        except Exception:  # noqa: BLE001 - persistence failure must not crash the worker
            logger.exception("Could not persist failure state for session %s", session_id)

    def _require_idle(self, session_id: str) -> None:
        with self._lock:
            if session_id in self._active:
                raise JobConflictError(
                    f"A job for session '{session_id}' is already running."
                )

    def _require_session(self, session_id: str) -> None:
        try:
            self.sessions.get_session(session_id)
        except KeyError as error:
            raise KeyError(session_id) from error

    @staticmethod
    def _safe_message(error: BaseException) -> str:
        """Return a user-safe message.

        ``LLMError`` and ``ValueError`` messages in this codebase contain no
        secrets; the LLM layer deliberately hides provider payloads. The state
        layer additionally bounds the stored length.
        """

        message = str(error).strip()
        return message or "The research workflow failed."
