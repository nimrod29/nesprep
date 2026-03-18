/**
 * ChatContent - scrollable message list with typing indicator.
 */

import { useEffect, useRef } from "react";
import { Loader2, Check } from "lucide-react";
import { cn } from "@/shared/utils";
import type { ChatMessage as ChatMessageType, StatusEntry } from "@/shared/hooks";
import { ChatMessage } from "./ChatMessage";

interface ChatContentProps {
  messages: ChatMessageType[];
  isAgentTyping: boolean;
  statusLog: StatusEntry[];
  className?: string;
}

export function ChatContent({
  messages,
  isAgentTyping,
  statusLog,
  className,
}: ChatContentProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const statusScrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isAgentTyping, statusLog]);

  useEffect(() => {
    if (statusScrollRef.current) {
      statusScrollRef.current.scrollTop = statusScrollRef.current.scrollHeight;
    }
  }, [statusLog]);

  return (
    <div
      ref={scrollRef}
      className={cn(
        "flex-1 overflow-y-auto",
        className
      )}
    >
      <div className="max-w-3xl mx-auto px-4 py-6 space-y-4">
        {messages.length === 0 && !isAgentTyping && (
          <div className="flex flex-col items-center justify-center h-full text-center pt-20">
            <h2 className="text-xl font-semibold text-primary-900 mb-2">
              ברוכים הבאים לסידור משמרות
            </h2>
            <p className="text-primary-600 max-w-md">
              שלחו הודעה כדי להתחיל לתכנן את סידור המשמרות.
              <br />
              ספרו לי על העובדים והאילוצים שלהם.
            </p>
          </div>
        )}

        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}

        {/* Status log indicator */}
        {isAgentTyping && statusLog.length > 0 && (
          <div className="flex justify-start gap-3">
            <div className="shrink-0 h-8 w-8 rounded-full bg-primary-500 text-white flex items-center justify-center text-sm font-bold mt-1">
              N
            </div>
            <div
              ref={statusScrollRef}
              className={cn(
                "bg-white border border-primary-100 shadow-sm rounded-2xl rounded-es-md",
                "px-4 py-3 max-h-48 overflow-y-auto"
              )}
            >
              <div className="flex flex-col gap-1.5">
                {statusLog.map((entry, i) => {
                  const isLast = i === statusLog.length - 1;
                  return (
                    <div key={i} className="flex items-center gap-2">
                      {isLast ? (
                        <Loader2 className="h-3.5 w-3.5 animate-spin text-primary-500 shrink-0" />
                      ) : (
                        <Check className="h-3.5 w-3.5 text-green-600 shrink-0" />
                      )}
                      <span
                        className={cn(
                          "text-sm",
                          isLast
                            ? "text-primary-800"
                            : "text-primary-400"
                        )}
                      >
                        {entry.message}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
