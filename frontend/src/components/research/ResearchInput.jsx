import { useState } from "react";
import { useResearch } from "../../context/ResearchContext";

const MIN_LENGTH = 3;
const MAX_LENGTH = 4000;

export default function ResearchInput() {
  const [query, setQuery] = useState("");
  const { research, loading, error, clearError, cancel } = useResearch();

  const tooShort = query.trim().length > 0 && query.trim().length < MIN_LENGTH;

  const submit = async (event) => {
    event.preventDefault();
    if (query.trim().length >= MIN_LENGTH) {
      await research(query.trim()).catch(() => {});
    }
  };

  return (
    <section className="rounded-2xl border border-white/10 bg-slate-900/70 p-6">
      <h2 className="text-2xl font-bold">Research workspace</h2>
      <form onSubmit={submit} className="mt-5">
        <label className="sr-only" htmlFor="query">
          Research question
        </label>
        <textarea
          id="query"
          value={query}
          onChange={(event) => {
            setQuery(event.target.value);
            clearError();
          }}
          required
          minLength={MIN_LENGTH}
          maxLength={MAX_LENGTH}
          rows={4}
          aria-invalid={tooShort}
          aria-describedby="query-help query-error"
          placeholder="Ask a research question, e.g. What are the trade-offs of RAG versus fine-tuning?"
          className="w-full rounded-xl border border-white/15 bg-slate-950 p-4 text-white placeholder:text-slate-500 focus:border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400"
        />
        <div id="query-help" className="mt-3 flex items-center justify-between gap-3">
          <span className={`text-sm ${tooShort ? "text-amber-300" : "text-slate-400"}`}>
            {tooShort
              ? `Please enter at least ${MIN_LENGTH} characters.`
              : `${query.length}/${MAX_LENGTH} characters`}
          </span>
          <span className="flex gap-2">
            {loading && (
              <button
                type="button"
                onClick={cancel}
                className="rounded-lg border border-red-400/50 px-5 py-3 font-semibold text-red-200 hover:bg-red-500/10"
              >
                Cancel
              </button>
            )}
            <button
              type="submit"
              disabled={loading || query.trim().length < MIN_LENGTH}
              className="rounded-lg bg-cyan-500 px-5 py-3 font-semibold text-slate-950 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? "Researching…" : "Start research"}
            </button>
          </span>
        </div>
        {error && (
          <div id="query-error" role="alert" className="mt-4 rounded-lg bg-red-500/15 p-3 text-red-200">
            {error} You can revise the question and try again.
          </div>
        )}
      </form>
    </section>
  );
}
