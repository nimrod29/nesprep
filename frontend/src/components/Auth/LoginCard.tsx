import type React from "react";
import { cn } from "@/shared/utils";

interface LoginCardProps {
  name: string;
  onNameChange: (value: string) => void;
  onSubmit: (event: React.FormEvent) => void;
  isSubmitDisabled: boolean;
}

export function LoginCard({
  name,
  onNameChange,
  onSubmit,
  isSubmitDisabled,
}: LoginCardProps) {
  return (
    <div className="w-full max-w-md">
      <div
        className={cn(
          "rounded-3xl bg-zinc-950/80 border border-amber-900/70 shadow-2xl",
          "backdrop-blur-sm px-6 py-7 sm:px-8 sm:py-8"
        )}
      >
        <div className="mb-6">
          <h2 className="text-xl sm:text-2xl font-semibold text-amber-50">
            התחברות למנהל הסניף
          </h2>
          <p className="mt-2 text-sm text-amber-100/70">
            הזינו את שמכם כדי להתחיל לבנות סידור משמרות מותאם לצוות שלכם.
          </p>
        </div>

        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <label
              htmlFor="manager-name"
              className="block text-sm font-medium text-amber-100 mb-1"
            >
              שם המנהל
            </label>
            <input
              id="manager-name"
              type="text"
              value={name}
              onChange={(event) => onNameChange(event.target.value)}
              placeholder="לדוגמה: דניאל לוי"
              className={cn(
                "w-full rounded-2xl border text-sm sm:text-base",
                "bg-zinc-900/60 border-amber-800/70",
                "text-amber-50 placeholder:text-amber-200/50",
                "ps-4 pe-4 py-3",
                "focus:outline-none focus:border-amber-400 focus:ring-2 focus:ring-amber-500/40"
              )}
              autoComplete="off"
              autoFocus
            />
          </div>

          <button
            type="submit"
            disabled={isSubmitDisabled}
            className={cn(
              "w-full inline-flex items-center justify-center rounded-2xl",
              "py-3 ps-4 pe-4 text-sm sm:text-base font-medium tracking-wide",
              "transition-colors duration-150",
              !isSubmitDisabled &&
                "bg-amber-500 hover:bg-amber-400 text-zinc-950 shadow-lg shadow-amber-900/40",
              isSubmitDisabled &&
                "bg-zinc-800 text-amber-200/40 cursor-not-allowed border border-zinc-700"
            )}
          >
            התחל סידור משמרות
          </button>
        </form>

        <p className="mt-4 text-[11px] sm:text-xs text-amber-100/60 leading-relaxed">
          על־ידי התחברות אתם מאפשרים למערכת NesPrep לנהל עבורכם את שיחות
          התכנון והפקת קובצי הסידור – בלי לשנות שום דבר ב‑Nespresso עצמה.
        </p>
      </div>
    </div>
  );
}

