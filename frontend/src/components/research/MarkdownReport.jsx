import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeSanitize from "rehype-sanitize";

// Render model/report Markdown safely. rehype-sanitize strips raw HTML and
// dangerous protocols (e.g. javascript: URLs), so retrieved/generated content
// can never inject markup or scripts. External links are forced to open in a
// new tab with no opener access.
const components = {
  h1: ({ children }) => <h1 className="mb-4 mt-2 border-b border-white/10 pb-2 text-2xl font-bold text-white">{children}</h1>,
  h2: ({ children }) => <h2 className="mb-3 mt-7 text-xl font-bold text-cyan-300">{children}</h2>,
  h3: ({ children }) => <h3 className="mb-2 mt-5 text-lg font-semibold text-white">{children}</h3>,
  h4: ({ children }) => <h4 className="mb-2 mt-4 text-base font-semibold text-slate-100">{children}</h4>,
  p: ({ children }) => <p className="my-3 leading-7 text-slate-200">{children}</p>,
  ul: ({ children }) => <ul className="my-3 list-disc space-y-1 pl-6 text-slate-200">{children}</ul>,
  ol: ({ children }) => <ol className="my-3 list-decimal space-y-1 pl-6 text-slate-200">{children}</ol>,
  li: ({ children }) => <li className="leading-7">{children}</li>,
  strong: ({ children }) => <strong className="font-semibold text-white">{children}</strong>,
  em: ({ children }) => <em className="italic text-slate-100">{children}</em>,
  hr: () => <hr className="my-6 border-white/10" />,
  blockquote: ({ children }) => (
    <blockquote className="my-4 border-l-4 border-cyan-400/60 pl-4 italic text-slate-300">{children}</blockquote>
  ),
  a: ({ children, href }) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="text-cyan-300 underline decoration-cyan-300/50 underline-offset-2 hover:text-cyan-200"
    >
      {children}
    </a>
  ),
  code: ({ children, className }) => (
    <code className={`rounded bg-slate-800 px-1.5 py-0.5 text-sm text-cyan-200 ${className || ""}`}>{children}</code>
  ),
  pre: ({ children }) => (
    <pre className="my-4 overflow-x-auto rounded-xl border border-white/10 bg-slate-950 p-4 text-sm text-slate-200">{children}</pre>
  ),
  table: ({ children }) => (
    <div className="my-4 overflow-x-auto">
      <table className="w-full border-collapse text-sm text-slate-200">{children}</table>
    </div>
  ),
  th: ({ children }) => <th className="border border-white/10 bg-slate-800 px-3 py-2 text-left font-semibold text-white">{children}</th>,
  td: ({ children }) => <td className="border border-white/10 px-3 py-2 align-top">{children}</td>,
};

export default function MarkdownReport({ content = "" }) {
  return (
    <div className="markdown-report">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeSanitize]}
        components={components}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
