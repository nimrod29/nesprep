/**
 * ChatMessage - individual message display with warm styling.
 */

import { cn } from "@/shared/utils";
import type { ChatMessage as ChatMessageType } from "@/shared/hooks";
import { ShiftPlanTable } from "./ShiftPlanTable";

interface ChatMessageProps {
  message: ChatMessageType;
}

export function ChatMessage({ message }: ChatMessageProps) {
  if (message.type === "plan" && message.weekPlans) {
    return (
      <div className="flex justify-start gap-3">
        <div className="shrink-0 h-8 w-8 rounded-full bg-primary-500 text-white flex items-center justify-center text-sm font-bold mt-1">
          N
        </div>
        <ShiftPlanTable weekPlans={message.weekPlans} />
      </div>
    );
  }

  const isUser = message.type === "user";

  return (
    <div
      className={cn(
        "flex",
        isUser ? "justify-end" : "justify-start gap-3"
      )}
    >
      {!isUser && (
        <div className="shrink-0 h-8 w-8 rounded-full bg-primary-500 text-white flex items-center justify-center text-sm font-bold mt-1">
          N
        </div>
      )}
      <div
        className={cn(
          "max-w-[75%] rounded-2xl px-4 py-3",
          isUser
            ? "bg-primary-500 text-white rounded-ee-md"
            : "bg-white border border-primary-100 shadow-sm text-primary-900 rounded-es-md"
        )}
      >
        <p className="whitespace-pre-wrap break-words">{message.content}</p>
        <p
          className={cn(
            "text-xs mt-1",
            isUser ? "text-white/70" : "text-primary-400"
          )}
        >
          {formatTime(message.timestamp)}
        </p>
      </div>
    </div>
  );
}

function formatTime(date: Date): string {
  return date.toLocaleTimeString("he-IL", {
    hour: "2-digit",
    minute: "2-digit",
  });
}
