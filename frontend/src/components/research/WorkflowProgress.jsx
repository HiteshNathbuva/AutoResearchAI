import { useResearch } from "../../context/ResearchContext";

const steps = [
  ["Planner", "Understands the question and builds a research plan."],
  ["Research", "Gathers structured findings for the plan."],
  ["Verification", "Checks accuracy, evidence, and unsupported claims."],
  ["Writer", "Produces the final professional report."],
];

export default function WorkflowProgress() {
  const { session, loading } = useResearch();
  if (!session && !loading) return null;
  const done = session?.completed_tasks || [];
  const status = session?.status || "Starting";
  // Map backend status text onto the active stage while running.
  const activeIndex = loading
    ? Math.max(0, ["Planning", "Researching", "Verifying", "Writing"].findIndex((s) => status.includes(s)))
    : -1;
  return (
    <section aria-live="polite" className="rounded-2xl border border-white/10 bg-slate-900/70 p-6">
      <h2 className="text-2xl font-bold">Workflow progress</h2>
      <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {steps.map(([step, desc], i) => {
          const isDone = done.includes(step);
          const isActive = i === activeIndex;
          return (
            <div key={step} className={`rounded-xl border p-4 transition ${isDone ? "border-cyan-400/50 bg-cyan-500/10" : isActive ? "border-cyan-300 bg-slate-800" : "border-white/10 bg-slate-950/50"}`}>
              <p className={`text-xs font-semibold uppercase tracking-wide ${isDone ? "text-cyan-300" : isActive ? "text-cyan-200" : "text-slate-500"}`}>
                {isDone ? "✓ Completed" : isActive ? "● In progress" : "Pending"}
              </p>
              <h3 className="mt-1 font-semibold">{step} Agent</h3>
              <p className="mt-1 text-xs text-slate-400">{desc}</p>
            </div>
          );
        })}
      </div>
      {loading && <p className="mt-4 text-cyan-300">The agents are working on your request… this can take up to a minute.</p>}
      {session && !loading && <p className="mt-4 text-slate-400">Current status: {session.status}</p>}
    </section>
  );
}
