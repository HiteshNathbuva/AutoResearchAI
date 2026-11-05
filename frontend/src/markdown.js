// Minimal, safe Markdown-to-HTML renderer for research reports.
// All text is escaped before formatting; only markdown syntax produces tags.
const escape = (text) =>
  text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

const inline = (text) =>
  text
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/(^|[^*])\*([^*\n]+)\*/g, "$1<em>$2</em>")
    .replace(
      /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,
      '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>'
    )
    .replace(
      /(https?:\/\/[^\s<>"']+)/g,
      (match, url, offset, string) =>
        string.slice(Math.max(0, offset - 9), offset).includes('href="') ? match : `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`
    );

export function renderMarkdown(markdown) {
  const lines = escape(markdown || "").split(/\r?\n/);
  const out = [];
  let list = null;
  for (const line of lines) {
    const heading = /^(#{1,4})\s+(.*)$/.exec(line);
    const bullet = /^\s*[-*]\s+(.*)$/.exec(line);
    const numbered = /^\s*(\d+)[.)]\s+(.*)$/.exec(line);
    if (/^\s*(-{3,}|\*{3,})\s*$/.test(line)) {
      if (list) { out.push(`</${list}>`); list = null; }
      out.push("<hr class='border-white/10 my-4'/>");
      continue;
    }
    if (heading || bullet || numbered || line.trim() === "") {
      if (list) { out.push(`</${list}>`); list = null; }
    }
    if (heading) {
      const level = heading[1].length;
      out.push(`<h${level + 1} class="font-bold text-${level === 1 ? "2xl lg:text-3xl" : "xl"} mt-6 mb-2 text-cyan-200">${inline(heading[2])}</h${level + 1}>`);
    } else if (bullet) {
      if (!list) { out.push('<ul class="list-disc pl-6 space-y-1">'); list = "ul"; }
      out.push(`<li>${inline(bullet[1])}</li>`);
    } else if (numbered) {
      if (!list) { out.push('<ol class="list-decimal pl-6 space-y-1">'); list = "ol"; }
      out.push(`<li>${inline(numbered[2])}</li>`);
    } else if (line.trim() !== "") {
      out.push(`<p class="leading-7">${inline(line)}</p>`);
    }
  }
  if (list) out.push(`</${list}>`);
  return out.join("");
}

// Extract plain URLs from markdown text (for a References section fallback).
export function extractLinks(markdown) {
  const urls = new Set();
  const pattern = /(?:\[[^\]]+\]\((https?:\/\/[^\s)]+)\))|(https?:\/\/[^\s<>"')\]]+)/g;
  let match;
  while ((match = pattern.exec(markdown || "")) !== null) {
    urls.add(match[1] || match[2]);
  }
  return [...urls];
}

export function extractTitle(markdown, fallback = "Research Report") {
  const match = /^#\s+(.+)$/m.exec(markdown || "");
  return match ? match[1].trim() : fallback;
}
