import { useState } from "react";
import { useResearch } from "../../context/ResearchContext";

export default function ResearchInput() {
  const [query, setQuery] = useState("");
  const { research, loading, error, clearError } = useResearch();
  const submit = async (e) => {
    e.preventDefault();
    const trimmed = query.trim();
    if (!trimmed || trimmed.length < 3 || loading) return;
    await research(trimmed).catch(() => {});
  };
  return (
    <section className="rounded-2xl border border-white/10 bg-slate-900/70 p-6">
      <h2 className="text-2xl font-bold">Research workspace</h2>
      <form onSubmit={submit} className="mt-5">
        <label className="sr-only" htmlFor="query">Research question</label>
        <textarea
          id="query"
          value={query}
          onChange={(e) => { setQuery(e.target.value); clearError(); }}
          required
          minLength={3}
          maxLength={4000}
          rows={4}
          placeholder="Ask a research question, e.g. “What are the current limitations of small language models on edge devices?”"
          className="w-full rounded-xl border border-white/15 bg-slate-950 p-4 text-white placeholder:text-slate-500 focus:border-cyan-400"
        />
        <div className="mt-3 flex items-center justify-between gap-3">
          <span className="text-sm text-slate-400">{query.length}/4000</span>
          <button
            disabled={loading || query.trim().length < 3}
            className="rounded-lg bg-cyan-500 px-5 py-3 font-semibold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? "Researching…" : "Start research"}
          </button>
        </div>
        {error && <div role="alert" className="mt-4 rounded-lg bg-red-500/15 p-3 text-red-200">{error} You can revise the question and try again.</div>}
      </form>
    </section>
  );
}
