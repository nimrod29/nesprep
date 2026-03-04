import type React from "react";
import { Send } from "lucide-react";
import { cn } from "@/shared/utils";

interface HomeMainPromptProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: (text: string) => void;
  disabled?: boolean;
}

export function HomeMainPrompt({
  value,
  onChange,
  onSubmit,
  disabled,
}: HomeMainPromptProps) {
  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter") {
      event.preventDefault();
      const trimmed = value.trim();
      if (!trimmed || disabled) {
        return;
      }
      onSubmit(trimmed);
    }
  };

  const handleClick = () => {
    const trimmed = value.trim();
    if (!trimmed || disabled) {
      return;
    }
    onSubmit(trimmed);
  };

  const isSendDisabled = disabled || !value.trim();

  return (
    <div className="w-full max-w-3xl sm:w-[92%]">
      <div
        className={cn(
          "flex items-center gap-2",
          "rounded-full border border-amber-200/80",
          "bg-amber-50/90 shadow-lg shadow-amber-900/10",
          "ps-5 pe-2 py-3"
        )}
      >
        <input
          type="text"
          value={value}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="לאיזה בוטיק ולאיזה חודש נבנה את סידור העבודה?"
          className={cn(
            "flex-1 bg-transparent border-0 outline-none",
            "text-sm sm:text-base text-amber-950 placeholder:text-amber-800/60"
          )}
        />
        <button
          type="button"
          onClick={handleClick}
          disabled={isSendDisabled}
          className={cn(
            "inline-flex items-center justify-center rounded-full",
            "h-9 w-9 sm:h-10 sm:w-10",
            "transition-colors duration-150",
            !isSendDisabled &&
              "bg-amber-800 hover:bg-amber-700 text-amber-50 shadow-md shadow-amber-900/30",
            isSendDisabled &&
              "bg-amber-200 text-amber-400 cursor-not-allowed"
          )}
          aria-label="שלח"
        >
          <Send className="h-4 w-4 rtl:scale-x-[-1]" />
        </button>
      </div>
    </div>
  );
}

