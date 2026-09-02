const API_URL = import.meta.env.VITE_API_URL || "/api";
async function request(path, options = {}) {
  // Support both absolute and relative API_URL. When using proxy (/api),
  // fetch will be same-origin and avoid CORS issues.
  const base = API_URL.endsWith("/") ? API_URL.slice(0, -1) : API_URL;
  const url = `${base}${path}`;
  let response;
  try {
    response = await fetch(url, { headers: { "Content-Type": "application/json" }, ...options });
  } catch (err) {
    // Network failure (e.g., backend down or CORS) -> surface clear message
    const message =
      err.message && err.message.includes("Failed to fetch")
        ? "Failed to fetch - backend unreachable"
        : err.message || "Failed to fetch";
    throw new Error(message, { cause: err });
  }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || "The request could not be completed.");
  return data;
}
export const api = {
  research: (query) => request("/research", { method: "POST", body: JSON.stringify({ query }) }),
  verify: (id) => request(`/verify/${id}`, { method: "POST" }),
  report: (id) => request(`/report/${id}`, { method: "POST" }),
  sessions: () => request("/sessions"),
  session: (id) => request(`/sessions/${id}`),
};
