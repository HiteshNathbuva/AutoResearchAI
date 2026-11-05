import { useEffect } from "react";
import { Link, useParams } from "react-router-dom";
import { useResearch } from "../context/ResearchContext";
import MarkdownReport from "../components/research/MarkdownReport";
import SourceList from "../components/research/SourceList";
import DiagnosticsBanner from "../components/research/DiagnosticsBanner";

export default function ReportDetail() {
  const { sessionId } = useParams();
  const { session, load, error, loading } = useResearch();

  useEffect(() => {
    load(sessionId).catch(() => {});
  }, [sessionId, load]);

  if (loading && !session) {
    return (
      <p role="status" className="text-slate-300">
        Loading report…
      </p>
    );
  }

  const notFound = error && /not found|was not found/i.test(error);
  if (error && (!session || notFound)) {
    return (
      <section role="alert" className="rounded-2xl border border-red-400/30 bg-red-500/10 p-6">
        <h1 className="text-2xl font-bold text-red-200">
          {notFound ? "Report not found" : "Unable to load report"}
        </h1>
        <p className="mt-2 text-slate-300">{error}</p>
        <Link to="/history" className="mt-4 inline-block rounded-lg border border-white/20 px-4 py-2 text-sm">
          Back to history
        </Link>
      </section>
    );
  }

  if (!session) return null;

  const content = session.report || session.research;

  return (
    <article>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-3xl font-bold">Research report</h1>
          <p className="mt-2 text-slate-400">
            {session.status} · {session.confidence} confidence · {session.reading_time} min read
          </p>
        </div>
        <Link to="/history" className="rounded-lg border border-white/20 px-4 py-2 text-sm">
          Back to history
        </Link>
      </div>

      {session.status === "Failed" && session.error && (
        <p role="alert" className="mt-4 rounded-lg bg-red-500/15 p-3 text-red-200">
          {session.error}
        </p>
      )}

      <div className="mt-6 rounded-xl border border-white/10 bg-slate-900 p-6">
        <h2 className="sr-only">Question</h2>
        <p className="text-sm uppercase tracking-wide text-cyan-300">Question</p>
        <p className="mt-1 text-lg font-medium text-white">{session.query}</p>
      </div>

      <div className="mt-6 rounded-xl border border-white/10 bg-slate-900 p-6">
        <DiagnosticsBanner diagnostics={session.diagnostics} sources={session.sources} />
        <MarkdownReport content={content} />
        <SourceList sources={session.sources} />
      </div>
    </article>
  );
}
