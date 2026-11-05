import { Link } from "react-router-dom";
import { useResearch } from "../../context/ResearchContext";
import MarkdownReport from "./MarkdownReport";
import SourceList from "./SourceList";
import DiagnosticsBanner from "./DiagnosticsBanner";

export default function ResearchResult() {
  const { session, loading, verify, report } = useResearch();
  if (!session) return null;

  const safeRun = (fn) => fn(session.session_id).catch(() => {});
  const content = session.report || session.research;
  const hasReport = Boolean(session.report);
  const hasVerification = Boolean(session.verification);
  const failed = session.status === "Failed";

  const download = () => {
    const blob = new Blob([content], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "research-report.md";
    anchor.click();
    URL.revokeObjectURL(url);
  };

  return (
    <section className="rounded-2xl border border-white/10 bg-slate-900/70 p-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold">{hasReport ? "Professional report" : "Research result"}</h2>
          <p className="mt-1 text-slate-400">
            Confidence: {session.confidence} · {session.reading_time} min read
          </p>
        </div>
        {!failed && (
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => safeRun(verify)}
              disabled={loading || hasVerification}
              className="rounded-lg border border-white/20 px-3 py-2 text-sm font-medium disabled:cursor-not-allowed disabled:opacity-50"
            >
              {hasVerification ? "Verified" : "Verify"}
            </button>
            <button
              type="button"
              onClick={() => safeRun(report)}
              disabled={loading}
              className="rounded-lg bg-cyan-500 px-3 py-2 text-sm font-semibold text-slate-950 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Generate report
            </button>
          </div>
        )}
      </div>

      {failed && session.error && (
        <p role="alert" className="mt-4 rounded-lg bg-red-500/15 p-3 text-red-200">
          {session.error}
        </p>
      )}

      {loading && (
        <p className="mt-4 rounded-lg border border-cyan-400/30 bg-cyan-500/10 px-4 py-2 text-sm text-cyan-200">
          Updating this session… the content below stays available while the agents work.
        </p>
      )}

      <DiagnosticsBanner diagnostics={session.diagnostics} sources={session.sources} />

      <article className="mt-6">
        <MarkdownReport content={content} />
      </article>

      <SourceList sources={session.sources} />

      {!failed && content && (
        <div className="mt-6 flex flex-wrap gap-3">
          <button
            type="button"
            onClick={download}
            className="rounded-lg border border-white/20 px-3 py-2 text-sm"
          >
            Download Markdown
          </button>
          <Link
            className="rounded-lg border border-white/20 px-3 py-2 text-sm"
            to={`/reports/${session.session_id}`}
          >
            Open report
          </Link>
        </div>
      )}
    </section>
  );
}
