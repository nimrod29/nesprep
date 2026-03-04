/**
 * ChatMessage - individual message display.
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
      <div className="flex justify-start">
        <ShiftPlanTable weekPlans={message.weekPlans} />
      </div>
    );
  }

  const isUser = message.type === "user";

  return (
    <div
      className={cn(
        "flex",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      <div
        className={cn(
          "max-w-[80%] rounded-2xl px-4 py-3",
          isUser
            ? "bg-primary-500 text-white rounded-ee-md"
            : "bg-gray-100 dark:bg-zinc-700 text-gray-900 dark:text-gray-100 rounded-es-md"
        )}
      >
        <p className="whitespace-pre-wrap break-words">{message.content}</p>
        <p
          className={cn(
            "text-xs mt-1",
            isUser
              ? "text-primary-100"
              : "text-gray-500 dark:text-gray-400"
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
