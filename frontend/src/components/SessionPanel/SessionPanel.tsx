/**
 * SessionPanel - Collapsible sidebar for session history.
 *
 * Features:
 * - Collapses to a thin strip with toggle button
 * - Positions on start side (right in RTL, left in LTR)
 * - Persists open/closed state to localStorage
 */

import { useState, useEffect, useCallback } from "react";
import { ChevronLeft, ChevronRight, Plus, Calendar, LogOut } from "lucide-react";
import { cn } from "@/shared/utils";
import { type Session } from "@/shared/api";
import { SessionList } from "./SessionList";

const STORAGE_KEY = "nesprep-session-panel-open";
const PANEL_WIDTH = 280;
const COLLAPSED_WIDTH = 48;

interface SessionPanelProps {
  sessions: Session[];
  isLoading: boolean;
  activeSessionId: number | null;
  onSelectSession: (id: number) => void;
  onNewSession: () => void;
  onDeleteSession: (id: number) => void;
  onLogout: () => void;
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
  className,
}: SessionPanelProps) {
  const [isOpen, setIsOpen] = useState(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored !== null ? stored === "true" : true;
  });

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, String(isOpen));
  }, [isOpen]);

  const handleToggle = useCallback(() => {
    setIsOpen((prev) => !prev);
  }, []);

  const handleSelect = useCallback(
    (id: number) => {
      onSelectSession(id);
    },
    [onSelectSession]
  );

  const handleDelete = useCallback(
    async (id: number) => {
      onDeleteSession(id);
    },
    [onDeleteSession]
  );

  // RTL: In RTL mode, "start" is right side
  // The chevron should point inward when open, outward when closed
  const ChevronIcon = isOpen ? ChevronRight : ChevronLeft;

  return (
    <div
      className={cn(
        "relative flex flex-col h-full bg-white dark:bg-zinc-800",
        "border-e border-gray-200 dark:border-zinc-700",
        "transition-all duration-300 ease-in-out",
        className
      )}
      style={{
        width: isOpen ? PANEL_WIDTH : COLLAPSED_WIDTH,
        minWidth: isOpen ? PANEL_WIDTH : COLLAPSED_WIDTH,
      }}
    >
      {/* Toggle button */}
      <button
        onClick={handleToggle}
        className={cn(
          "absolute top-4 z-10 p-1.5 rounded-full",
          "bg-white dark:bg-zinc-800 border border-gray-200 dark:border-zinc-700",
          "shadow-sm transition-colors hover:bg-gray-50 dark:hover:bg-zinc-700",
          "start-full -translate-x-1/2 rtl:translate-x-1/2"
        )}
        aria-label={isOpen ? "כווץ פאנל" : "הרחב פאנל"}
      >
        <ChevronIcon className="h-4 w-4 text-gray-500 dark:text-gray-400" />
      </button>

      {isOpen ? (
        <>
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-zinc-700">
            <div className="flex items-center gap-2">
              <Calendar className="h-5 w-5 text-gray-500 dark:text-gray-400" />
              <h2 className="font-medium text-gray-900 dark:text-gray-100">
                סידורים
              </h2>
            </div>
            <button
              onClick={onNewSession}
              className={cn(
                "p-1.5 rounded-md transition-colors",
                "text-gray-500 dark:text-gray-400",
                "hover:text-primary-600 dark:hover:text-primary-400",
                "hover:bg-primary-50 dark:hover:bg-primary-900/20"
              )}
              aria-label="סידור חדש"
              title="סידור חדש"
            >
              <Plus className="h-5 w-5" />
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

          {/* Footer with logout */}
          <div className="mt-auto border-t border-gray-200 dark:border-zinc-700 p-3">
            <button
              onClick={onLogout}
              className={cn(
                "w-full flex items-center justify-center gap-2 p-2 rounded-md",
                "text-gray-500 dark:text-gray-400",
                "hover:text-red-600 dark:hover:text-red-400",
                "hover:bg-red-50 dark:hover:bg-red-900/20",
                "transition-colors"
              )}
            >
              <LogOut className="h-4 w-4 rtl:scale-x-[-1]" />
              <span className="text-sm">התנתק</span>
            </button>
          </div>
        </>
      ) : (
        /* Collapsed state */
        <div className="flex flex-col items-center pt-14 gap-4">
          <button
            onClick={onNewSession}
            className={cn(
              "p-2 rounded-md transition-colors",
              "text-gray-500 dark:text-gray-400",
              "hover:text-primary-600 dark:hover:text-primary-400",
              "hover:bg-primary-50 dark:hover:bg-primary-900/20"
            )}
            aria-label="סידור חדש"
            title="סידור חדש"
          >
            <Plus className="h-5 w-5" />
          </button>
          <div
            className="p-2 text-gray-400 dark:text-gray-500"
            title="סידורים"
          >
            <Calendar className="h-5 w-5" />
          </div>
          <button
            onClick={onLogout}
            className={cn(
              "mt-auto mb-4 p-2 rounded-md transition-colors",
              "text-gray-500 dark:text-gray-400",
              "hover:text-red-600 dark:hover:text-red-400",
              "hover:bg-red-50 dark:hover:bg-red-900/20"
            )}
            aria-label="התנתק"
            title="התנתק"
          >
            <LogOut className="h-4 w-4 rtl:scale-x-[-1]" />
          </button>
        </div>
      )}
    </div>
  );
}
