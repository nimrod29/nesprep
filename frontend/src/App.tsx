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
import { SessionPanel } from "@/components/SessionPanel";
import { Chat } from "@/components/Chat";
import { cn } from "@/shared/utils";

function LoginScreen({ onLogin }: { onLogin: (name: string) => void }) {
  const [name, setName] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (name.trim()) {
      onLogin(name.trim());
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-zinc-900">
      <div className="w-full max-w-md p-8 bg-white dark:bg-zinc-800 rounded-xl shadow-lg">
        <div className="text-center mb-8">
          <div className="text-6xl mb-4">📅</div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            NesPrep
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-2">
            סידור משמרות חכם
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label
              htmlFor="name"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
            >
              שם המנהל
            </label>
            <input
              id="name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="הכניסו את שמכם"
              className={cn(
                "w-full px-4 py-3 rounded-lg",
                "bg-gray-100 dark:bg-zinc-700",
                "border border-gray-200 dark:border-zinc-600",
                "text-gray-900 dark:text-gray-100",
                "placeholder:text-gray-500 dark:placeholder:text-gray-400",
                "focus:outline-none focus:border-primary-500"
              )}
              autoFocus
            />
          </div>

          <button
            type="submit"
            disabled={!name.trim()}
            className={cn(
              "w-full py-3 rounded-lg font-medium transition-colors",
              name.trim()
                ? "bg-primary-500 hover:bg-primary-600 text-white"
                : "bg-gray-300 dark:bg-zinc-600 text-gray-500 cursor-not-allowed"
            )}
          >
            התחבר
          </button>
        </form>
      </div>
    </div>
  );
}

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
  const { isAuthenticated, isLoading, login } = useAuth();

  const handleLogin = useCallback(
    async (name: string) => {
      await login({ name });
    },
    [login]
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-zinc-900">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LoginScreen onLogin={handleLogin} />;
  }

  return <AppContent />;
}
