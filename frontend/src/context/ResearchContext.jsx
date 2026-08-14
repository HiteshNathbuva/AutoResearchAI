/* eslint-disable react-refresh/only-export-components */
import { createContext, useCallback, useContext, useState } from "react";
import { api } from "../services/api";
const ResearchContext = createContext(null);
export function ResearchProvider({ children }) {
  const [session, setSession] = useState(null); const [loading, setLoading] = useState(false); const [error, setError] = useState("");
  const run = useCallback(async (action) => { setLoading(true); setError(""); try { const data = await action(); setSession(data); return data; } catch (e) { setError(e.message); throw e; } finally { setLoading(false); } }, []);
  return <ResearchContext.Provider value={{ session, setSession, loading, error, clearError: () => setError(""), research: (q) => run(() => api.research(q)), verify: (id) => run(() => api.verify(id)), report: (id) => run(() => api.report(id)), load: (id) => run(() => api.session(id)), sessions: api.sessions }}>{children}</ResearchContext.Provider>;
}
export const useResearch = () => useContext(ResearchContext);
