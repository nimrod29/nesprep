/**
 * Chat - main chat interface component.
 */

import { useCallback } from "react";
import { cn } from "@/shared/utils";
import { useChatState } from "@/shared/hooks";
import { ChatContent } from "./ChatContent";
import { ChatErrorBanner } from "./ChatErrorBanner";
import { PromptBox } from "../PromptBox";

interface ChatProps {
  sessionId: number | null;
  className?: string;
}

export function Chat({ sessionId, className }: ChatProps) {
  const {
    messages,
    isAgentTyping,
    statusLog,
    error,
    sendMessage,
    clearError,
  } = useChatState(sessionId);

  const handleSubmit = useCallback(
    (text: string) => {
      sendMessage(text);
    },
    [sendMessage]
  );

  const handleRetry = useCallback(() => {
    const lastUserMessage = [...messages]
      .reverse()
      .find((m) => m.type === "user");
    if (lastUserMessage) {
      sendMessage(lastUserMessage.content);
    }
  }, [messages, sendMessage]);

  if (!sessionId) {
    return (
      <div
        className={cn(
          "flex flex-col items-center justify-center h-full",
          "bg-gray-50 dark:bg-zinc-900",
          className
        )}
      >
        <div className="text-6xl mb-4">👈</div>
        <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">
          בחרו סידור
        </h2>
        <p className="text-gray-500 dark:text-gray-400">
          בחרו סידור קיים או צרו חדש כדי להתחיל
        </p>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "flex flex-col h-full bg-gray-50 dark:bg-zinc-900",
        className
      )}
    >
      {/* Messages area */}
      <ChatContent
        messages={messages}
        isAgentTyping={isAgentTyping}
        statusLog={statusLog}
        className="min-h-0"
      />

      {/* Bottom section */}
      <div className="shrink-0 bg-white dark:bg-zinc-800 border-t border-gray-200 dark:border-zinc-700">
        <ChatErrorBanner
          error={error}
          onDismiss={clearError}
          onRetry={handleRetry}
        />
        <div className="p-4">
          <PromptBox
            onSubmit={handleSubmit}
            isLoading={isAgentTyping}
            disabled={!sessionId}
          />
        </div>
      </div>
    </div>
  );
}
