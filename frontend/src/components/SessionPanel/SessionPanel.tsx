/**
 * SessionPanel - ChatGPT-style sidebar with dark espresso theme.
 *
 * Features:
 * - Fully hidden when closed (0px), toggled from chat header
 * - Dark warm espresso background
 * - Grouped session list by date
 */

import { useCallback } from "react";
import { Plus, LogOut } from "lucide-react";
import { cn } from "@/shared/utils";
import { type Session } from "@/shared/api";
import { SessionList } from "./SessionList";

const PANEL_WIDTH = 260;

interface SessionPanelProps {
  sessions: Session[];
  isLoading: boolean;
  activeSessionId: number | null;
  onSelectSession: (id: number) => void;
  onNewSession: () => void;
  onDeleteSession: (id: number) => void;
  onLogout: () => void;
  managerName: string | null;
  isOpen: boolean;
  onToggle: () => void;
  className?: string;
}

export function SessionPanel({
  sessions,
  isLoading,
  activeSessionId,
  onSelectSession,
  onNewSession,
  onDeleteSession,
  onLogout,
  managerName,
  isOpen,
  onToggle,
  className,
}: SessionPanelProps) {
  const handleSelect = useCallback(
    (id: number) => {
      onSelectSession(id);
    },
    [onSelectSession]
  );

  const handleDelete = useCallback(
    (id: number) => {
      onDeleteSession(id);
    },
    [onDeleteSession]
  );

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/40 md:hidden"
          onClick={onToggle}
        />
      )}

      <div
        className={cn(
          "flex flex-col h-full bg-sidebar",
          "transition-all duration-300 ease-in-out overflow-hidden",
          "fixed md:relative z-40 md:z-auto",
          isOpen ? "end-0 md:end-auto" : "end-full md:end-auto",
          className
        )}
        style={{
          width: isOpen ? PANEL_WIDTH : 0,
          minWidth: isOpen ? PANEL_WIDTH : 0,
        }}
      >
        {/* Header */}
        <div className="px-4 pt-4 pb-2">
          <img
            src="/assets/nespresso-logo.png"
            alt="Nespresso"
            className="h-4 w-auto opacity-50 mb-4 brightness-200"
          />
          <button
            onClick={onNewSession}
            className={cn(
              "w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg",
              "bg-sidebar-surface border border-sidebar-border",
              "text-sidebar-text text-sm",
              "hover:bg-sidebar-border transition-colors"
            )}
          >
            <Plus className="h-4 w-4" />
            <span>סידור חדש</span>
          </button>
        </div>

        {/* Session list */}
        <SessionList
          sessions={sessions}
          activeId={activeSessionId}
          isLoading={isLoading}
          onSelect={handleSelect}
          onDelete={handleDelete}
        />

        {/* Footer with manager name + logout */}
        <div className="border-t border-sidebar-border p-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-sidebar-text truncate">
              {managerName || "מנהל"}
            </span>
            <button
              onClick={onLogout}
              className={cn(
                "p-1.5 rounded-md transition-colors",
                "text-sidebar-text/60",
                "hover:text-red-400 hover:bg-red-900/20"
              )}
              aria-label="התנתק"
              title="התנתק"
            >
              <LogOut className="h-4 w-4 rtl:scale-x-[-1]" />
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
