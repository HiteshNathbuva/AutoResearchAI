// Surfaces the honest provenance of the research: whether it was grounded in
// real fetched web sources, ran without sources, or had web research disabled.
// This is driven entirely by backend diagnostics — never fabricated.
export default function DiagnosticsBanner({ diagnostics = {}, sources = [] }) {
  if (!diagnostics || Object.keys(diagnostics).length === 0) return null;

  const enabled = diagnostics.web_research_enabled;
  const usedWeb = diagnostics.used_web === true;
  const searchFailed = diagnostics.search_status === "failed";

  let tone = "border-slate-500/40 bg-slate-800/40 text-slate-300";
  let message;

  if (usedWeb) {
    const count = diagnostics.source_count ?? sources.length;
    tone = "border-cyan-400/40 bg-cyan-500/10 text-cyan-200";
    message = `Grounded in ${count} web ${count === 1 ? "source" : "sources"} retrieved for this question.`;
  } else if (enabled && searchFailed) {
    tone = "border-amber-400/40 bg-amber-500/10 text-amber-200";
    message =
      "Web research is enabled, but live search/retrieval failed. The answer below is model-generated and is not grounded in fetched sources.";
  } else if (enabled) {
    tone = "border-amber-400/40 bg-amber-500/10 text-amber-200";
    message =
      "No usable web sources were retrieved, so this answer is model-generated rather than grounded in live sources.";
  } else {
    message =
      "Web research is disabled. This answer is model-generated from the model's own knowledge and is not grounded in live sources.";
  }

  return (
    <p role="note" className={`rounded-lg border px-4 py-3 text-sm ${tone}`}>
      {message}
    </p>
  );
}
