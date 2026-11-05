/* eslint-disable react-refresh/only-export-components */
import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import { api } from "../services/api";

const ResearchContext = createContext(null);
const POLL_INTERVAL_MS = 1500;
const TERMINAL_STATUSES = new Set([
  "Research completed",
  "Verified report generated",
  "Report generated",
  "Failed",
]);

export function ResearchProvider({ children }) {
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const abortRef = useRef(null);
  const pollTimerRef = useRef(null);

  const clearPollTimer = useCallback(() => {
    if (pollTimerRef.current) {
      window.clearTimeout(pollTimerRef.current);
      pollTimerRef.current = null;
    }
  }, []);

  const cancel = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
    clearPollTimer();
    setLoading(false);
  }, [clearPollTimer]);

  // Stop any in-flight polling if the provider unmounts (e.g. route change).
  useEffect(() => clearPollTimer, [clearPollTimer]);

  const pollUntilDone = useCallback(
    (sessionId, controller) =>
      new Promise((resolve, reject) => {
        const tick = async () => {
          if (controller.signal.aborted) {
            resolve(null);
            return;
          }
          try {
            const job = await api.getJob(sessionId, controller.signal);
            setSession(job);

            const finished = !job.job_active || TERMINAL_STATUSES.has(job.status);
            if (finished) {
              if (job.status === "Failed") {
                setError(job.error || "The research workflow failed.");
              }
              resolve(job);
              return;
            }
            pollTimerRef.current = window.setTimeout(tick, POLL_INTERVAL_MS);
          } catch (err) {
            if (controller.signal.aborted) {
              resolve(null);
              return;
            }
            reject(err);
          }
        };
        pollTimerRef.current = window.setTimeout(tick, 250);
      }),
    []
  );

  const runJob = useCallback(
    async (starter) => {
      cancel();
      const controller = new AbortController();
      abortRef.current = controller;
      setLoading(true);
      setError("");
      try {
        const accepted = await starter(controller.signal);
        return await pollUntilDone(accepted.session_id, controller);
      } catch (err) {
        if (!controller.signal.aborted) {
          setError(err.message || "The request could not be completed.");
        }
        throw err;
      } finally {
        if (abortRef.current === controller) {
          abortRef.current = null;
        }
        clearPollTimer();
        setLoading(false);
      }
    },
    [cancel, clearPollTimer, pollUntilDone]
  );

  const research = useCallback(
    (query) => runJob((signal) => api.startResearch(query, signal)),
    [runJob]
  );
  const verify = useCallback(
    (sessionId) => runJob((signal) => api.startVerify(sessionId, signal)),
    [runJob]
  );
  const report = useCallback(
    (sessionId) => runJob((signal) => api.startReport(sessionId, signal)),
    [runJob]
  );

  // Single fetch used by the report detail page (no polling).
  const load = useCallback(async (sessionId) => {
    cancel();
    const controller = new AbortController();
    abortRef.current = controller;
    setLoading(true);
    setError("");
    try {
      const data = await api.getSession(sessionId, controller.signal);
      setSession(data);
      return data;
    } catch (err) {
      setError(err.message || "Unable to load this report.");
      throw err;
    } finally {
      if (abortRef.current === controller) abortRef.current = null;
      setLoading(false);
    }
  }, [cancel]);

  const value = {
    session,
    setSession,
    loading,
    error,
    jobActive: loading,
    clearError: () => setError(""),
    cancel,
    research,
    verify,
    report,
    load,
    sessions: api.sessions,
  };

  return <ResearchContext.Provider value={value}>{children}</ResearchContext.Provider>;
}

export const useResearch = () => useContext(ResearchContext);
