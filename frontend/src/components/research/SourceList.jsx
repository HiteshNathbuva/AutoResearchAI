// Renders the genuinely-consulted web sources as clickable citations.
// Source URLs come from the backend's SSRF-validated fetch layer; we still
// guard the scheme here so only http/https links are ever rendered.
function isHttpUrl(url) {
  try {
    const parsed = new URL(url);
    return parsed.protocol === "http:" || parsed.protocol === "https:";
  } catch {
    return false;
  }
}

export default function SourceList({ sources = [] }) {
  const safe = sources.filter((source) => isHttpUrl(source.url));
  if (safe.length === 0) return null;

  return (
    <section aria-label="Sources" className="mt-8 rounded-xl border border-white/10 bg-slate-950/60 p-5">
      <h2 className="text-lg font-semibold text-white">Sources</h2>
      <ol className="mt-3 space-y-2">
        {safe.map((source) => (
          <li key={source.source_id || source.url} className="flex gap-2 text-sm leading-6">
            <span className="mt-0.5 shrink-0 rounded bg-cyan-500/15 px-1.5 text-cyan-300">
              [{source.source_id}]
            </span>
            <div className="min-w-0">
              <a
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                className="break-words text-cyan-300 underline decoration-cyan-300/50 underline-offset-2 hover:text-cyan-200"
              >
                {source.title || source.url}
              </a>
              {source.domain && <p className="text-xs text-slate-400">{source.domain}</p>}
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}
