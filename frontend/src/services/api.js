// The API base URL is resolved in this order:
// 1. VITE_API_URL (explicit backend URL, e.g. https://my-backend.onrender.com/api)
// 2. Same-origin "/api" (works when frontend and backend are deployed together,
//    e.g. a single Vercel project serving /api/* functions).
const API_URL = (import.meta.env.VITE_API_URL || "/api").replace(/\/+$/, "");

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch {
    throw new Error(`Cannot reach the research server at ${API_URL}. Check that the backend is running or deployed.`);
  }
  if (response.status === 204) return null;
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = typeof data.detail === "string" ? data.detail : "The request could not be completed.";
    const error = new Error(detail);
    error.status = response.status;
    throw error;
  }
  return data;
}

export const apiUrl = API_URL;
export const api = {
  health: () => request("/health"),
  research: (query) => request("/research", { method: "POST", body: JSON.stringify({ query }) }),
  verify: (id) => request(`/verify/${encodeURIComponent(id)}`, { method: "POST" }),
  report: (id) => request(`/report/${encodeURIComponent(id)}`, { method: "POST" }),
  sessions: () => request("/sessions"),
  session: (id) => request(`/sessions/${encodeURIComponent(id)}`),
  deleteSession: (id) => request(`/sessions/${encodeURIComponent(id)}`, { method: "DELETE" }),
};
