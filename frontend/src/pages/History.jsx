import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../services/api";

function formatDate(iso) {
  const date = new Date(iso);
  return Number.isNaN(date.getTime()) ? iso : date.toLocaleString();
}

export default function History() {
  const [items, setItems] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const controller = new AbortController();
    api
      .sessions(controller.signal)
      .then((data) => {
        if (!controller.signal.aborted) setItems(data.sessions || []);
      })
      .catch((err) => {
        if (!controller.signal.aborted) setError(err.message);
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, []);

  return (
    <section>
      <h1 className="text-3xl font-bold">Research history</h1>

      {loading && (
        <p role="status" className="mt-6 text-slate-400">
          Loading saved sessions…
        </p>
      )}
      {error && (
        <p role="alert" className="mt-6 rounded-lg bg-red-500/15 p-3 text-red-200">
          {error}
        </p>
      )}

      {!loading && !error && items.length === 0 && (
        <div className="mt-8 rounded-xl border border-white/10 bg-slate-900/60 p-8 text-center">
          <p className="text-slate-300">No research has been saved yet.</p>
          <Link to="/" className="mt-4 inline-block rounded-lg bg-cyan-500 px-5 py-2.5 font-semibold text-slate-950">
            Start your first research
          </Link>
        </div>
      )}

      <div className="mt-6 space-y-3">
        {items.map((session) => (
          <Link
            key={session.session_id}
            to={`/reports/${session.session_id}`}
            className="block rounded-xl border border-white/10 bg-slate-900 p-4 transition-colors hover:border-cyan-400"
          >
            <div className="flex flex-wrap items-center justify-between gap-2">
              <b className="text-white">{session.query}</b>
              {session.has_report && (
                <span className="rounded-full bg-cyan-500/15 px-2.5 py-0.5 text-xs font-medium text-cyan-300">
                  Report
                </span>
              )}
            </div>
            <p className="mt-1 text-sm text-slate-400">
              {session.status}
              {session.confidence ? ` · ${session.confidence} confidence` : ""} · {formatDate(session.updated_at)}
            </p>
          </Link>
        ))}
      </div>
    </section>
  );
}
