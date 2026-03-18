/**
 * App - main application component.
 *
 * Layout: SessionPanel (start side) + Chat (main area)
 * Handles auth state and session selection.
 */

import { useState, useCallback, useEffect, useRef } from "react";
import { useAuth } from "@/shared/auth";
import { useSessions } from "@/shared/hooks";
import { wsService } from "@/shared/websocket";
import { SessionPanel, Chat, HomePage } from "@/components";

const PENDING_PROMPT_KEY = "nesprep-pending-prompt";

function AppContent() {
  const { managerId, managerName, logout, reconnect } = useAuth();
  const { sessions, isLoading: sessionsLoading, create, remove } = useSessions(managerId);
  const [activeSessionId, setActiveSessionId] = useState<number | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const pendingPromptHandled = useRef(false);

  // Reconnect WebSocket on mount if authenticated
  useEffect(() => {
    if (managerId) {
      reconnect();
    }
  }, [managerId, reconnect]);

  // Handle pending prompt from landing page
  useEffect(() => {
    if (pendingPromptHandled.current) return;
    const pending = sessionStorage.getItem(PENDING_PROMPT_KEY);
    if (!pending || !managerId) return;

    pendingPromptHandled.current = true;
    sessionStorage.removeItem(PENDING_PROMPT_KEY);

    (async () => {
      const session = await create();
      if (session) {
        setActiveSessionId(session.id);
        wsService.joinSession({ shift_plan_id: session.id });
        // Small delay to ensure WebSocket join completes
        setTimeout(() => {
          wsService.sendChatMessage(String(session.id), pending);
        }, 500);
      }
    })();
  }, [managerId, create]);

  const handleNewSession = useCallback(async () => {
    const session = await create();
    if (session) {
      setActiveSessionId(session.id);
      wsService.joinSession({ shift_plan_id: session.id });
    }
  }, [create]);

  const handleNewSessionWithMessage = useCallback(
    async (message: string) => {
      const session = await create();
      if (session) {
        setActiveSessionId(session.id);
        wsService.joinSession({ shift_plan_id: session.id });
        setTimeout(() => {
          wsService.sendChatMessage(String(session.id), message);
        }, 500);
      }
    },
    [create]
  );

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
    <div className="flex h-screen bg-primary-100">
      <SessionPanel
        sessions={sessions}
        isLoading={sessionsLoading}
        activeSessionId={activeSessionId}
        onSelectSession={handleSelectSession}
        onNewSession={handleNewSession}
        onDeleteSession={handleDeleteSession}
        onLogout={handleLogout}
        managerName={managerName}
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen((p) => !p)}
      />
      <div className="flex-1 min-w-0">
        <Chat
          sessionId={activeSessionId}
          onToggleSidebar={() => setSidebarOpen((p) => !p)}
          onNewSessionWithMessage={handleNewSessionWithMessage}
        />
      </div>
    </div>
  );
}

export default function App() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-primary-100">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <HomePage />;
  }

  return <AppContent />;
}
