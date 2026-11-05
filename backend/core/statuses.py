"""Canonical workflow status values and transition helpers.

Keeping the status strings in one place gives the API, the background job
runner, the persistence layer and the polling frontend a single vocabulary.
The values are plain strings (not an ``Enum``) so they remain trivial to store
in SQLite and to evolve without breaking existing rows.
"""

from __future__ import annotations

from typing import FrozenSet

#: A job has been accepted and is waiting for a worker thread.
QUEUED = "Queued"
#: Planning / research are in progress.
PLANNING = "Planning"
RESEARCHING = "Researching"
RESEARCH_COMPLETED = "Research completed"
#: Verification / writing are in progress or finished.
VERIFYING = "Verifying"
WRITING_VERIFIED = "Writing verified report"
VERIFIED_REPORT_GENERATED = "Verified report generated"
WRITING_REPORT = "Writing report"
REPORT_GENERATED = "Report generated"
#: A workflow step failed; ``WorkflowState.error`` carries the safe detail.
FAILED = "Failed"

#: Statuses at which no further work is scheduled and polling should stop.
TERMINAL_STATUSES: FrozenSet[str] = frozenset(
    {
        RESEARCH_COMPLETED,
        VERIFIED_REPORT_GENERATED,
        REPORT_GENERATED,
        FAILED,
    }
)


def is_terminal_status(status: str) -> bool:
    """Return ``True`` when a workflow run has reached a final state."""

    return (status or "") in TERMINAL_STATUSES


def is_failure_status(status: str) -> bool:
    """Return ``True`` when the status represents a failed run."""

    return (status or "") == FAILED
