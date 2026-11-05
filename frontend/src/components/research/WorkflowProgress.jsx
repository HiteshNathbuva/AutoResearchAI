import { useResearch } from "../../context/ResearchContext";

const STEPS = ["Planner", "Research", "Verification", "Writer"];

// Map an in-flight workflow status to the step currently executing.
const ACTIVE_STEP_BY_STATUS = {
  Planning: "Planner",
  Researching: "Research",
  Verifying: "Verification",
  "Writing verified report": "Writer",
  "Writing report": "Writer",
};

function stepState(step, done, status, loading) {
  if (done.includes(step)) return { label: "Completed", className: "text-cyan-300", dot: "bg-cyan-400" };

  // Verification is optional when a report is generated without verifying.
  if (
    step === "Verification" &&
    done.includes("Writer") &&
    status === "Report generated"
  ) {
    return { label: "Skipped", className: "text-amber-300", dot: "bg-amber-400" };
  }

  if (status === "Failed" && ACTIVE_STEP_BY_STATUS[status] === undefined && loading === false) {
    return { label: "Pending", className: "text-slate-500", dot: "bg-slate-600" };
  }

  const activeStep = ACTIVE_STEP_BY_STATUS[status];
  if (activeStep === step && loading) {
    return { label: "In progress", className: "text-cyan-200", dot: "bg-cyan-300 animate-pulse" };
  }

  return { label: "Pending", className: "text-slate-400", dot: "bg-slate-600" };
}

export default function WorkflowProgress() {
  const { session, loading } = useResearch();
  if (!session && !loading) return null;

  const done = session?.completed_tasks || [];
  const status = session?.status || (loading ? "Planning" : "");
  const failed = session?.status === "Failed";

  return (
    <section aria-live="polite">
      <h2 className="text-2xl font-bold">Workflow progress</h2>
      <div className="mt-4 grid gap-3 sm:grid-cols-4">
        {STEPS.map((step) => {
          const state = stepState(step, done, status, loading);
          return (
            <div
              key={step}
              className="rounded-xl border border-white/10 bg-slate-900/60 p-4"
              data-step={step}
              data-state={state.label}
            >
              <div className="flex items-center gap-2">
                <span className={`h-2.5 w-2.5 rounded-full ${state.dot}`} aria-hidden="true" />
                <p className={state.className}>{state.label}</p>
              </div>
              <h3 className="mt-2 font-semibold">{step}</h3>
            </div>
          );
        })}
      </div>

      {loading && (
        <p className="mt-3 flex items-center gap-2 text-cyan-300">
          <span className="h-2 w-2 animate-ping rounded-full bg-cyan-300" aria-hidden="true" />
          The agents are working on your request…
        </p>
      )}
      {session && (
        <p className="mt-3 text-sm text-slate-400">
          Current status: <span className="text-slate-200">{session.status}</span>
        </p>
      )}
      {failed && session?.error && (
        <p role="alert" className="mt-3 rounded-lg bg-red-500/15 p-3 text-red-200">
          {session.error}
        </p>
      )}
    </section>
  );
}
