/**
 * SessionList - displays list of sessions with selection.
 */

import { Calendar, Trash2 } from "lucide-react";
import { cn } from "@/shared/utils";
import type { Session } from "@/shared/api";

interface SessionListProps {
  sessions: Session[];
  activeId: number | null;
  isLoading: boolean;
  onSelect: (id: number) => void;
  onDelete: (id: number) => void;
}

export function SessionList({
  sessions,
  activeId,
  isLoading,
  onSelect,
  onDelete,
}: SessionListProps) {
  if (isLoading) {
    return (
      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="h-16 rounded-lg bg-gray-100 dark:bg-zinc-700 animate-pulse"
          />
        ))}
      </div>
    );
  }

  if (sessions.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-4">
        <p className="text-sm text-gray-500 dark:text-gray-400 text-center">
          אין סידורים עדיין
          <br />
          <span className="text-xs">לחץ על + ליצירת סידור חדש</span>
        </p>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-2 space-y-1">
      {sessions.map((session) => (
        <button
          key={session.id}
          onClick={() => onSelect(session.id)}
          className={cn(
            "w-full text-start p-3 rounded-lg transition-colors group",
            "hover:bg-gray-100 dark:hover:bg-zinc-700",
            activeId === session.id &&
              "bg-primary-50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-800"
          )}
        >
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1 min-w-0">
              <p className="font-medium text-gray-900 dark:text-gray-100 truncate">
                {session.title || `סידור ${session.id}`}
              </p>
              <div className="flex items-center gap-1 mt-1 text-xs text-gray-500 dark:text-gray-400">
                <Calendar className="h-3 w-3" />
                <span>{formatDate(session.week_start)}</span>
              </div>
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDelete(session.id);
              }}
              className={cn(
                "p-1.5 rounded-md opacity-0 group-hover:opacity-100 transition-opacity",
                "text-gray-400 hover:text-red-500 dark:hover:text-red-400",
                "hover:bg-red-50 dark:hover:bg-red-900/20"
              )}
              title="מחק סידור"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          </div>
          <div className="mt-1">
            <span
              className={cn(
                "text-xs px-2 py-0.5 rounded-full",
                getStatusStyle(session.status)
              )}
            >
              {getStatusLabel(session.status)}
            </span>
          </div>
        </button>
      ))}
    </div>
  );
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString("he-IL", {
    day: "numeric",
    month: "short",
  });
}

function getStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    draft: "טיוטה",
    analyzing: "מנתח",
    planning: "מתכנן",
    validating: "מאמת",
    completed: "הושלם",
    failed: "נכשל",
  };
  return labels[status] || status;
}

function getStatusStyle(status: string): string {
  const styles: Record<string, string> = {
    draft: "bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300",
    analyzing: "bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400",
    planning: "bg-yellow-100 text-yellow-600 dark:bg-yellow-900/30 dark:text-yellow-400",
    validating: "bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400",
    completed: "bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400",
    failed: "bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400",
  };
  return styles[status] || styles.draft;
}
