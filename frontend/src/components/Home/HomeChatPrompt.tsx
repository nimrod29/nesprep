import type React from "react";
import { useEffect, useState } from "react";
import { Send } from "lucide-react";
import { cn } from "@/shared/utils";

interface HomeChatPromptProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: (text: string) => void;
}

export function HomeChatPrompt({
  value,
  onChange,
  onSubmit,
}: HomeChatPromptProps) {
  const [hasInteracted, setHasInteracted] = useState(false);
  const [typedText, setTypedText] = useState("");

  const displayTyping = !hasInteracted && !value;

  useEffect(() => {
    if (!displayTyping) {
      setTypedText("");
      return;
    }

    const fullText = "לאיזה בוטיק ולאיזה חודש נבנה סידור עבודה?";
    let index = 0;
    let isAdding = true;
    let timeoutId: number;

    const step = () => {
      if (!isAdding) {
        setTypedText("");
        index = 0;
        isAdding = true;
        timeoutId = window.setTimeout(step, 400);
        return;
      }

      setTypedText(fullText.slice(0, index + 1));
      index += 1;

      if (index === fullText.length) {
        isAdding = false;
        timeoutId = window.setTimeout(step, 1400);
        return;
      }

      timeoutId = window.setTimeout(step, 110);
    };

    timeoutId = window.setTimeout(step, 250);

    return () => {
      window.clearTimeout(timeoutId);
    };
  }, [displayTyping]);

  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter") {
      event.preventDefault();
      const trimmed = value.trim();
      if (!trimmed) return;
      onSubmit(trimmed);
    }
  };

  const handleClick = () => {
    setHasInteracted(true);
    const trimmed = value.trim();
    if (!trimmed) return;
    onSubmit(trimmed);
  };

  const handleFocus = () => {
    setHasInteracted(true);
  };

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!hasInteracted) {
      setHasInteracted(true);
    }
    onChange(event.target.value);
  };

  const isDisabled = !value.trim();

  return (
    <div className="w-[92vw] sm:w-[88vw] max-w-[980px] mx-auto sm:px-0">
      <div
        className={cn(
          "flex items-center gap-4",
          "h-[66px] sm:h-[72px]",
          "rounded-full",
          "border border-[#E4D3BD]/70",
          "bg-[rgba(255,248,240,0.85)]",
          "shadow-[0_12px_24px_rgba(0,0,0,0.08)]",
          "ps-6 pe-6"
        )}
      >
        <div className="relative flex-1 h-full flex items-center">
          <input
            type="text"
            value={value}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            onFocus={handleFocus}
            dir="rtl"
            className={cn(
              "w-full bg-transparent border-0 outline-none",
              "text-[16px] text-[#6E5B47]",
              "text-end"
            )}
          />
          {displayTyping && (
            <span
              className={cn(
                "pointer-events-none absolute inset-y-0 start-0 end-0",
                "flex items-center justify-end",
                "pe-1 text-[16px] text-[#6E5B47]/80"
              )}
            >
              <span dir="rtl">{typedText}</span>
              {typedText && <span className="typewriter-caret" />}
            </span>
          )}
        </div>
        <button
          type="button"
          onClick={handleClick}
          disabled={isDisabled}
          className={cn(
            "inline-flex items-center justify-center rounded-full",
            "h-10 w-10",
            "transition-opacity",
            "bg-[#E2A94B] text-white",
            "shadow-[0_4px_8px_rgba(0,0,0,0.12)]",
            isDisabled && "opacity-60 cursor-not-allowed"
          )}
          aria-label="שלח"
        >
          <Send className="h-4 w-4 rtl:scale-x-[-1]" />
        </button>
      </div>
    </div>
  );
}

