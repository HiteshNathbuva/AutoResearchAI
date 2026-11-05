import { renderMarkdown, extractLinks } from "../../markdown";

export default function ReportView({ title, meta, content }) {
  const links = extractLinks(content);
  return (
    <article className="rounded-2xl border border-white/10 bg-slate-900/70 p-6 sm:p-8">
      <header>
        <h2 className="text-2xl font-bold text-white">{title}</h2>
        {meta && <p className="mt-1 text-sm text-slate-400">{meta}</p>}
      </header>
      <div
        className="prose-report mt-4 max-w-none text-slate-200"
        dangerouslySetInnerHTML={{ __html: renderMarkdown(content) }}
      />
      {links.length > 0 && (
        <section className="mt-8 border-t border-white/10 pt-4">
          <h3 className="text-lg font-bold text-cyan-200">References</h3>
          <ul className="mt-2 list-disc space-y-1 pl-6 text-sm">
            {links.map((url) => (
              <li key={url}>
                <a className="break-all text-cyan-300 underline hover:text-cyan-200" href={url} target="_blank" rel="noopener noreferrer">{url}</a>
              </li>
            ))}
          </ul>
        </section>
      )}
    </article>
  );
}
