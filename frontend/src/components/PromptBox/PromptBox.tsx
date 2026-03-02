/**
 * PromptBox - chat input component with send button.
 */

import { useState, useCallback, useRef, useEffect } from "react";
import { Send, Square } from "lucide-react";
import { cn } from "@/shared/utils";

interface PromptBoxProps {
  onSubmit: (text: string) => void;
  isLoading?: boolean;
  disabled?: boolean;
  placeholder?: string;
  onStop?: () => void;
  className?: string;
}

export function PromptBox({
  onSubmit,
  isLoading = false,
  disabled = false,
  placeholder = "הקלידו הודעה...",
  onStop,
  className,
}: PromptBoxProps) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
    }
  }, [value]);

  const handleSubmit = useCallback(() => {
    if (!value.trim() || isLoading || disabled) return;
    onSubmit(value.trim());
    setValue("");
  }, [value, isLoading, disabled, onSubmit]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSubmit();
      }
    },
    [handleSubmit]
  );

  const canSubmit = value.trim().length > 0 && !isLoading && !disabled;

  return (
    <div
      className={cn(
        "flex items-end gap-2 p-3 rounded-xl",
        "bg-gray-100 dark:bg-zinc-700",
        "border border-gray-200 dark:border-zinc-600",
        "focus-within:border-primary-500 dark:focus-within:border-primary-400",
        "transition-colors",
        className
      )}
    >
      <textarea
        ref={textareaRef}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled || isLoading}
        rows={1}
        className={cn(
          "flex-1 resize-none bg-transparent",
          "text-gray-900 dark:text-gray-100",
          "placeholder:text-gray-500 dark:placeholder:text-gray-400",
          "focus:outline-none",
          "disabled:opacity-50"
        )}
      />

      {isLoading && onStop ? (
        <button
          onClick={onStop}
          className={cn(
            "p-2 rounded-lg transition-colors",
            "bg-red-500 hover:bg-red-600",
            "text-white"
          )}
          title="עצור"
        >
          <Square className="h-5 w-5" />
        </button>
      ) : (
        <button
          onClick={handleSubmit}
          disabled={!canSubmit}
          className={cn(
            "p-2 rounded-lg transition-colors",
            canSubmit
              ? "bg-primary-500 hover:bg-primary-600 text-white"
              : "bg-gray-300 dark:bg-zinc-600 text-gray-500 dark:text-gray-400",
            "disabled:cursor-not-allowed"
          )}
          title="שלח"
        >
          <Send className="h-5 w-5 rtl:scale-x-[-1]" />
        </button>
      )}
    </div>
  );
}
