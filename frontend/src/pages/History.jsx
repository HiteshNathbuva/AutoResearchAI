import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useResearch } from "../context/ResearchContext";
import { api } from "../services/api";

export default function History() {
  const { remove, loading } = useResearch();
  const [items, setItems] = useState([]);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("loading");

  const refresh = useCallback(() => {
    setStatus("loading");
    api.sessions()
      .then((d) => { setItems(d.sessions); setStatus("ready"); })
      .catch((e) => { setError(e.message); setStatus("ready"); });
  }, []);

  useEffect(() => {
    let cancelled = false;
    api.sessions()
      .then((d) => !cancelled && (setItems(d.sessions), setStatus("ready")))
      .catch((e) => !cancelled && (setError(e.message), setStatus("ready")));
    return () => { cancelled = true; };
  }, []);

  const onDelete = async (id) => {
    if (!window.confirm("Delete this research session? This cannot be undone.")) return;
    try {
      await remove(id);
      setItems((prev) => prev.filter((s) => s.session_id !== id));
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <section>
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Research history</h1>
        <button onClick={refresh} className="rounded-lg border border-white/20 px-3 py-2 text-sm hover:border-cyan-400">Refresh</button>
      </div>
      {error && <p role="alert" className="mt-4 rounded-lg bg-red-500/15 p-3 text-red-200">{error}</p>}
      {status === "loading" && <p className="mt-6 text-slate-400">Loading your research sessions…</p>}
      {status === "ready" && !error && items.length === 0 && (
        <div className="mt-6 rounded-xl border border-dashed border-white/15 p-10 text-center text-slate-400">
          <p>No research has been saved yet.</p>
          <Link to="/" className="mt-3 inline-block rounded-lg bg-cyan-500 px-4 py-2 font-semibold text-slate-950">Start your first research</Link>
        </div>
      )}
      <div className="mt-6 space-y-3">
        {items.map((s) => (
          <div key={s.session_id} className="flex items-center justify-between gap-4 rounded-xl border border-white/10 bg-slate-900 p-4 transition hover:border-cyan-400/60">
            <Link to={`/reports/${s.session_id}`} className="min-w-0 flex-1">
              <b className="block truncate">{s.query}</b>
              <p className="mt-1 text-sm text-slate-400">
                {s.status} · {s.confidence || "Unverified"} confidence{s.reading_time ? ` · ${s.reading_time} min read` : ""} · {new Date(s.updated_at).toLocaleString()}
              </p>
            </Link>
            <div className="flex shrink-0 gap-2">
              {s.has_report && <span className="rounded-full bg-cyan-500/15 px-3 py-1 text-xs text-cyan-300">Report ready</span>}
              <button
                onClick={() => onDelete(s.session_id)}
                disabled={loading}
                aria-label={`Delete session for ${s.query}`}
                className="rounded-lg border border-red-400/40 px-3 py-1.5 text-sm text-red-300 hover:bg-red-500/10 disabled:opacity-50"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
