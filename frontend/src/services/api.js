// API client. Defaults to relative "/api" so the Vite dev proxy (and any
// same-origin production host) works without CORS. Set VITE_API_URL to target
// a remote backend explicitly.
const API_URL = import.meta.env.VITE_API_URL || "/api";

// Individual HTTP request timeout. Job *start* calls return immediately; the
// long work happens in the background and is observed by polling, so a normal
// request never needs to wait minutes on a single fetch.
const DEFAULT_TIMEOUT_MS = 30_000;

function buildUrl(path) {
  const base = API_URL.endsWith("/") ? API_URL.slice(0, -1) : API_URL;
  return `${base}${path}`;
}

async function request(path, options = {}) {
  const { timeoutMs = DEFAULT_TIMEOUT_MS, signal, ...fetchOptions } = options;
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), timeoutMs);

  if (signal) {
    if (signal.aborted) {
      controller.abort();
    } else {
      signal.addEventListener("abort", () => controller.abort(), { once: true });
    }
  }

  let response;
  try {
    response = await fetch(buildUrl(path), {
      headers: { "Content-Type": "application/json" },
      signal: controller.signal,
      ...fetchOptions,
    });
  } catch (err) {
    if (controller.signal.aborted && !(signal && signal.aborted)) {
      throw new Error("The request timed out. Please try again.", { cause: err });
    }
    const message =
      err && err.message && err.message.includes("Failed to fetch")
        ? "Failed to fetch — the backend is unreachable. Is it running?"
        : (err && err.message) || "Network request failed.";
    throw new Error(message, { cause: err });
  } finally {
    window.clearTimeout(timeoutId);
  }

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || `The request failed with status ${response.status}.`);
  }
  return data;
}

const post = (path, body, signal) =>
  request(path, { method: "POST", body: body ? JSON.stringify(body) : undefined, signal });

export const api = {
  // Background, pollable job endpoints (preferred).
  startResearch: (query, signal) => post("/jobs/research", { query }, signal),
  startVerify: (sessionId, signal) => post(`/jobs/verify/${sessionId}`, undefined, signal),
  startReport: (sessionId, signal) => post(`/jobs/report/${sessionId}`, undefined, signal),
  getJob: (sessionId, signal) => request(`/jobs/${sessionId}`, { signal }),

  // Session/history reads.
  getSession: (sessionId, signal) => request(`/sessions/${sessionId}`, { signal }),
  sessions: (signal) => request("/sessions", { signal }),

  // Synchronous endpoints retained for compatibility and power users.
  research: (query, signal) => post("/research", { query }, signal),
  verify: (sessionId, signal) => post(`/verify/${sessionId}`, undefined, signal),
  report: (sessionId, signal) => post(`/report/${sessionId}`, undefined, signal),
};
