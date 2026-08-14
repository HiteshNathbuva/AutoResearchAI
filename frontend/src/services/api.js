const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";
async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, { headers: { "Content-Type": "application/json" }, ...options });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || "The request could not be completed.");
  return data;
}
export const api = { research: (query) => request("/research", { method: "POST", body: JSON.stringify({ query }) }),
  verify: (id) => request(`/verify/${id}`, { method: "POST" }), report: (id) => request(`/report/${id}`, { method: "POST" }),
  sessions: () => request("/sessions"), session: (id) => request(`/sessions/${id}`) };
