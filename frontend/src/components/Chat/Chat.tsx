/**
 * Chat - main chat interface with warm gradient design.
 */

import { useCallback } from "react";
import { Menu } from "lucide-react";
import { cn } from "@/shared/utils";
import { useChatState } from "@/shared/hooks";
import { ChatContent } from "./ChatContent";
import { ChatErrorBanner } from "./ChatErrorBanner";
import { PromptBox } from "../PromptBox";

interface ChatProps {
  sessionId: number | null;
  onToggleSidebar?: () => void;
  onNewSessionWithMessage?: (message: string) => void;
  className?: string;
}

export function Chat({
  sessionId,
  onToggleSidebar,
  onNewSessionWithMessage,
  className,
}: ChatProps) {
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

  const handleEmptyStateSubmit = useCallback(
    (text: string) => {
      if (onNewSessionWithMessage) {
        onNewSessionWithMessage(text);
      }
    },
    [onNewSessionWithMessage]
  );

  // Empty state: no session selected
  if (!sessionId) {
    return (
      <div
        className={cn(
          "flex flex-col h-full",
          "bg-gradient-to-b from-primary-100 via-[#FAF6F0] to-white",
          className
        )}
      >
        {/* Header */}
        <ChatHeader onToggleSidebar={onToggleSidebar} />

        {/* Centered prompt like landing page */}
        <div className="flex-1 flex flex-col items-center justify-center px-4">
          <h2 className="text-2xl font-semibold text-primary-900 mb-2">
            ברוכים הבאים
          </h2>
          <p className="text-primary-600 mb-8 text-center">
            ספרו לי על הבוטיק, העובדים והאילוצים שלהם
          </p>
          <div className="w-full max-w-2xl">
            <PromptBox
              onSubmit={handleEmptyStateSubmit}
              placeholder="לאיזה בוטיק ולאיזה חודש נבנה סידור עבודה?"
            />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "flex flex-col h-full",
        "bg-gradient-to-b from-primary-100 via-[#FAF6F0] to-white",
        className
      )}
    >
      {/* Header */}
      <ChatHeader onToggleSidebar={onToggleSidebar} />

      {/* Messages area */}
      <ChatContent
        messages={messages}
        isAgentTyping={isAgentTyping}
        statusLog={statusLog}
        className="min-h-0"
      />

      {/* Bottom section */}
      <div className="shrink-0">
        <div className="max-w-3xl mx-auto px-4">
          <ChatErrorBanner
            error={error}
            onDismiss={clearError}
            onRetry={handleRetry}
          />
        </div>
        <div className="bg-gradient-to-t from-white via-white to-transparent pt-4 pb-4 px-4">
          <div className="max-w-3xl mx-auto">
            <PromptBox
              onSubmit={handleSubmit}
              isLoading={isAgentTyping}
              disabled={!sessionId}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function ChatHeader({ onToggleSidebar }: { onToggleSidebar?: () => void }) {
  return (
    <div
      className={cn(
        "shrink-0 flex items-center h-14 px-4",
        "bg-white/80 backdrop-blur-sm",
        "border-b border-primary-200/30"
      )}
    >
      <button
        onClick={onToggleSidebar}
        className="p-2 -ms-2 rounded-lg text-primary-800/60 hover:text-primary-800 hover:bg-primary-100 transition-colors"
        aria-label="תפריט"
      >
        <Menu className="h-5 w-5" />
      </button>
      <div className="ms-2 text-sm font-medium text-primary-900">
        NesPrep
      </div>
    </div>
  );
}
