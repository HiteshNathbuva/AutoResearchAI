import { useEffect } from "react";
import { Link, useParams } from "react-router-dom";
import { useResearch } from "../context/ResearchContext";
import ReportView from "../components/research/ReportView";
import { extractTitle } from "../markdown";

export default function ReportDetail() {
  const { sessionId } = useParams();
  const { session, load, error, loading, setSession } = useResearch();

  useEffect(() => {
    load(sessionId).catch(() => {});
    return () => setSession(null);
  }, [sessionId, load, setSession]);

  if (loading) return <p className="text-slate-400">Loading report…</p>;
  if (error) {
    return (
      <div role="alert" className="rounded-xl bg-red-500/15 p-4 text-red-200">
        {error}
        <Link to="/history" className="ml-3 underline">Back to history</Link>
      </div>
    );
  }
  if (!session) return null;

  const content = session.report || session.research;
  if (!content) {
    return (
      <div className="rounded-xl border border-dashed border-white/15 p-10 text-center text-slate-400">
        <p>This session has no saved output yet.</p>
        <Link to="/" className="mt-3 inline-block rounded-lg bg-cyan-500 px-4 py-2 font-semibold text-slate-950">Run new research</Link>
      </div>
    );
  }

  const download = () => {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([content], { type: "text/markdown" }));
    a.download = `${extractTitle(content, "research-report").replace(/[^\w\s-]/g, "").trim().slice(0, 60) || "research-report"}.md`;
    a.click();
    URL.revokeObjectURL(a.href);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-sm text-slate-400">
          Query: <span className="text-slate-200">{session.query}</span>
        </p>
        <button onClick={download} className="rounded-lg border border-white/20 px-3 py-2 text-sm hover:border-cyan-400">Download Markdown</button>
      </div>
      <ReportView
        title={session.report ? "Professional report" : "Research result"}
        meta={`${session.status} · ${session.confidence} confidence · ${session.reading_time} min read`}
        content={content}
      />
      {session.verification && <ReportView title="Verification review" meta="Verifier Agent findings" content={session.verification} />}
    </div>
  );
}
