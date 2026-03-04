/**
 * App - main application component.
 *
 * Layout: SessionPanel (start side) + Chat (main area)
 * Handles auth state and session selection.
 */

import { useState, useCallback, useEffect } from "react";
import { useAuth } from "@/shared/auth";
import { useSessions } from "@/shared/hooks";
import { wsService } from "@/shared/websocket";
import { SessionPanel, Chat, HomePage } from "@/components";

function AppContent() {
  const { managerId, logout, reconnect } = useAuth();
  const { sessions, isLoading: sessionsLoading, create, remove } = useSessions(managerId);
  const [activeSessionId, setActiveSessionId] = useState<number | null>(null);

  // Reconnect WebSocket on mount if authenticated
  useEffect(() => {
    if (managerId) {
      reconnect();
    }
  }, [managerId, reconnect]);

  // Auto-select first session if none selected
  useEffect(() => {
    if (!activeSessionId && sessions.length > 0) {
      setActiveSessionId(sessions[0].id);
    }
  }, [activeSessionId, sessions]);

  const handleNewSession = useCallback(async () => {
    const session = await create();
    if (session) {
      setActiveSessionId(session.id);
      // Join the new session via WebSocket
      wsService.joinSession({ shift_plan_id: session.id });
    }
  }, [create]);

  const handleSelectSession = useCallback((id: number) => {
    setActiveSessionId(id);
    wsService.joinSession({ shift_plan_id: id });
  }, []);

  const handleDeleteSession = useCallback(
    async (id: number) => {
      await remove(id);
      if (activeSessionId === id) {
        const remaining = sessions.filter((s) => s.id !== id);
        setActiveSessionId(remaining[0]?.id ?? null);
      }
    },
    [remove, activeSessionId, sessions]
  );

  const handleLogout = useCallback(() => {
    setActiveSessionId(null);
    logout();
  }, [logout]);

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-zinc-900">
      <SessionPanel
        sessions={sessions}
        isLoading={sessionsLoading}
        activeSessionId={activeSessionId}
        onSelectSession={handleSelectSession}
        onNewSession={handleNewSession}
        onDeleteSession={handleDeleteSession}
        onLogout={handleLogout}
      />
      <div className="flex-1 min-w-0">
        <Chat sessionId={activeSessionId} />
      </div>
    </div>
  );
}

export default function App() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-zinc-900">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <HomePage />;
  }

  return <AppContent />;
}
