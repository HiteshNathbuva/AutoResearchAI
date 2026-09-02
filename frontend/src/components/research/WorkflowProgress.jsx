import { useResearch } from "../../context/ResearchContext";
const steps = ["Planner", "Research", "Verification", "Writer"];

function getStepStatus(step, done, session) {
  if (done.includes(step)) return { label: "Completed", className: "text-cyan-300" };
  // Verification is optional when report is generated directly without verification.
  // If Writer is completed but Verification is not, and status is "Report generated",
  // show Verification as Skipped instead of Pending to avoid inconsistent UI.
  if (step === "Verification" && done.includes("Writer") && session?.status === "Report generated") {
    return { label: "Skipped", className: "text-amber-300" };
  }
  return { label: "Pending", className: "text-slate-400" };
}

export default function WorkflowProgress() {
  const { session, loading } = useResearch();
  if (!session && !loading) return null;
  const done = session?.completed_tasks || [];
  return (
    <section aria-live="polite">
      <h2 className="text-2xl font-bold">Workflow progress</h2>
      <div className="mt-4 grid gap-3 sm:grid-cols-4">
        {steps.map((step) => {
          const status = getStepStatus(step, done, session);
          return (
            <div key={step} className="rounded-xl border border-white/10 p-4">
              <p className={status.className}>{status.label}</p>
              <h3 className="mt-1 font-semibold">{step}</h3>
            </div>
          );
        })}
      </div>
      {loading && <p className="mt-3 text-cyan-300">The agents are working on your request…</p>}
      {session && <p className="mt-3 text-slate-400">Current status: {session.status}</p>}
    </section>
  );
}
