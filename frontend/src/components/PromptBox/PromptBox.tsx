/**
 * PromptBox - chat input styled to match the landing page prompt.
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
        "flex items-end gap-3 px-5 py-3",
        "rounded-2xl",
        "border border-primary-300/70",
        "bg-[rgba(255,248,240,0.85)]",
        "shadow-[0_8px_20px_rgba(0,0,0,0.06)]",
        "focus-within:border-primary-500",
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
          "text-primary-800",
          "placeholder:text-primary-600/50",
          "focus:outline-none",
          "disabled:opacity-50"
        )}
      />

      {isLoading && onStop ? (
        <button
          onClick={onStop}
          className={cn(
            "shrink-0 inline-flex items-center justify-center",
            "h-10 w-10 rounded-full",
            "bg-red-500 hover:bg-red-600 text-white",
            "transition-colors shadow-md"
          )}
          title="עצור"
        >
          <Square className="h-4 w-4" />
        </button>
      ) : (
        <button
          onClick={handleSubmit}
          disabled={!canSubmit}
          className={cn(
            "shrink-0 inline-flex items-center justify-center",
            "h-10 w-10 rounded-full",
            "transition-opacity shadow-md",
            "bg-primary-500 text-white",
            !canSubmit && "opacity-60 cursor-not-allowed"
          )}
          title="שלח"
        >
          <Send className="h-4 w-4 rtl:scale-x-[-1]" />
        </button>
      )}
    </div>
  );
}
