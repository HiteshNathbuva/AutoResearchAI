import { useEffect, useState } from "react";
import { api, apiUrl } from "../../services/api";

// Verifies backend connectivity once on mount and shows a helpful banner
// instead of silent 404s when the API is unreachable or misconfigured.
export default function ConnectionBanner() {
  const [state, setState] = useState("checking");
  useEffect(() => {
    let cancelled = false;
    api.health()
      .then(() => !cancelled && setState("ok"))
      .catch(() => !cancelled && setState("down"));
    return () => { cancelled = true; };
  }, []);
  if (state === "ok") return null;
  if (state === "checking") return null;
  return (
    <div role="alert" className="mb-8 rounded-xl border border-amber-400/30 bg-amber-500/10 p-4 text-sm text-amber-200">
      <p className="font-semibold">Backend not reachable at <code>{apiUrl}</code></p>
      <p className="mt-1">Start the FastAPI server locally (<code>uvicorn backend.main:app --port 8000</code>) or set <code>VITE_API_URL</code> to your deployed backend URL.</p>
    </div>
  );
}
