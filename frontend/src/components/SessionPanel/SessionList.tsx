/**
 * SessionList - ChatGPT-style grouped session list.
 */

import { MoreHorizontal, Trash2 } from "lucide-react";
import { useState } from "react";
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
  const [menuOpenId, setMenuOpenId] = useState<number | null>(null);

  if (isLoading) {
    return (
      <div className="flex-1 overflow-y-auto px-2 pt-2 space-y-2">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="h-10 rounded-lg bg-sidebar-surface animate-pulse"
          />
        ))}
      </div>
    );
  }

  if (sessions.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-4">
        <p className="text-sm text-sidebar-text/50 text-center">
          אין סידורים עדיין
        </p>
      </div>
    );
  }

  const grouped = groupSessionsByDate(sessions);

  return (
    <div className="flex-1 overflow-y-auto px-2 pt-1">
      {grouped.map((group) => (
        <div key={group.label} className="mb-3">
          <div className="text-[11px] text-sidebar-text/40 font-medium tracking-wider ps-3 py-2">
            {group.label}
          </div>
          <div className="space-y-0.5">
            {group.sessions.map((session) => (
              <div key={session.id} className="relative group">
                <button
                  onClick={() => {
                    setMenuOpenId(null);
                    onSelect(session.id);
                  }}
                  className={cn(
                    "w-full text-start py-2.5 px-3 rounded-lg transition-colors",
                    "text-sm truncate",
                    activeId === session.id
                      ? "bg-sidebar-surface text-white"
                      : "text-sidebar-text hover:bg-sidebar-surface/60"
                  )}
                >
                  {session.title || `סידור חדש`}
                </button>

                {/* Three-dot menu */}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setMenuOpenId(menuOpenId === session.id ? null : session.id);
                  }}
                  className={cn(
                    "absolute top-1/2 -translate-y-1/2 end-1",
                    "p-1 rounded-md transition-opacity",
                    "text-sidebar-text/40 hover:text-sidebar-text",
                    "opacity-0 group-hover:opacity-100",
                    menuOpenId === session.id && "opacity-100"
                  )}
                >
                  <MoreHorizontal className="h-4 w-4" />
                </button>

                {/* Delete dropdown */}
                {menuOpenId === session.id && (
                  <div
                    className={cn(
                      "absolute end-1 top-full z-10 mt-1",
                      "bg-sidebar-surface border border-sidebar-border rounded-lg shadow-lg",
                      "py-1 min-w-[120px]"
                    )}
                  >
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setMenuOpenId(null);
                        onDelete(session.id);
                      }}
                      className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-400 hover:bg-red-900/20 transition-colors"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                      <span>מחיקה</span>
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

interface SessionGroup {
  label: string;
  sessions: Session[];
}

function groupSessionsByDate(sessions: Session[]): SessionGroup[] {
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const yesterday = new Date(today.getTime() - 86400000);
  const weekAgo = new Date(today.getTime() - 7 * 86400000);
  const monthAgo = new Date(today.getTime() - 30 * 86400000);

  const groups: Record<string, Session[]> = {
    "היום": [],
    "אתמול": [],
    "7 ימים אחרונים": [],
    "חודש אחרון": [],
    "ישן יותר": [],
  };

  for (const session of sessions) {
    const created = new Date(session.created_at);
    if (created >= today) {
      groups["היום"].push(session);
    } else if (created >= yesterday) {
      groups["אתמול"].push(session);
    } else if (created >= weekAgo) {
      groups["7 ימים אחרונים"].push(session);
    } else if (created >= monthAgo) {
      groups["חודש אחרון"].push(session);
    } else {
      groups["ישן יותר"].push(session);
    }
  }

  return Object.entries(groups)
    .filter(([, s]) => s.length > 0)
    .map(([label, s]) => ({ label, sessions: s }));
}
