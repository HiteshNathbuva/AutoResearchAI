import { Link } from "react-router-dom";
import { useResearch } from "../../context/ResearchContext";
import ReportView from "./ReportView";

export default function ResearchResult() {
  const { session, loading, verify, report, error } = useResearch();
  if (!session || loading) return null;
  const run = (fn) => () => fn(session.session_id).catch(() => {});
  const content = session.report || session.research;
  const download = () => {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([content], { type: "text/markdown" }));
    a.download = "research-report.md";
    a.click();
    URL.revokeObjectURL(a.href);
  };
  return (
    <section className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-2xl font-bold">{session.report ? "Professional report" : "Research result"}</h2>
        <div className="flex flex-wrap gap-2">
          <button onClick={run(verify)} disabled={loading} className="rounded-lg border border-white/20 px-3 py-2 text-sm hover:border-cyan-400 disabled:opacity-50">Verify findings</button>
          <button onClick={run(report)} disabled={loading || !session.research} className="rounded-lg bg-cyan-500 px-3 py-2 text-sm font-semibold text-slate-950 hover:bg-cyan-400 disabled:opacity-50">Generate report</button>
        </div>
      </div>
      {error && <p role="alert" className="rounded-lg bg-red-500/15 p-3 text-red-200">{error}</p>}
      <ReportView
        title={session.query}
        meta={`Confidence: ${session.confidence} · ${session.reading_time} min read`}
        content={content}
      />
      {session.verification && <ReportView title="Verification review" meta="Verifier Agent findings" content={session.verification} />}
      <div className="flex gap-3">
        <button onClick={download} className="rounded-lg border border-white/20 px-3 py-2 text-sm hover:border-cyan-400">Download Markdown</button>
        <Link className="rounded-lg border border-white/20 px-3 py-2 text-sm hover:border-cyan-400" to={`/reports/${session.session_id}`}>Open saved report</Link>
      </div>
    </section>
  );
}
