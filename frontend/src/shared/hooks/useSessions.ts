/**
 * useSessions hook - manages session list state.
 */

import { useState, useEffect, useCallback } from "react";
import { getSessions, createSession, deleteSession, type Session } from "../api";

export function useSessions(managerId: number | null) {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSessions = useCallback(async () => {
    if (!managerId) return;

    setIsLoading(true);
    setError(null);
    try {
      const data = await getSessions(managerId);
      setSessions(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load sessions");
    } finally {
      setIsLoading(false);
    }
  }, [managerId]);

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  const create = useCallback(
    async (title?: string, weekStart?: string) => {
      if (!managerId) return null;

      try {
        const session = await createSession({
          manager_id: managerId,
          title,
          week_start: weekStart,
        });
        setSessions((prev) => [session, ...prev]);
        return session;
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to create session");
        return null;
      }
    },
    [managerId]
  );

  const remove = useCallback(async (sessionId: number) => {
    try {
      await deleteSession(sessionId);
      setSessions((prev) => prev.filter((s) => s.id !== sessionId));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete session");
    }
  }, []);

  return {
    sessions,
    isLoading,
    error,
    refresh: fetchSessions,
    create,
    remove,
  };
}
