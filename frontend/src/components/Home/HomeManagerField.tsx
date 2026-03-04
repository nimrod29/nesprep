import type React from "react";
import { cn } from "@/shared/utils";

interface HomeManagerFieldProps {
  value: string;
  onChange: (value: string) => void;
  showRequired?: boolean;
}

export function HomeManagerField({
  value,
  onChange,
  showRequired,
}: HomeManagerFieldProps) {
  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    onChange(event.target.value);
  };

  return (
    <div className="flex flex-col items-center gap-2">
      <label
        htmlFor="manager-name"
        className="block text-xs sm:text-sm font-medium text-amber-900/90"
      >
        שם המנהל
      </label>
      <input
        id="manager-name"
        type="text"
        value={value}
        onChange={handleChange}
        placeholder="הקלד/י את שמך"
        className={cn(
          "w-[300px] max-w-full",
          "rounded-[14px]",
          "bg-amber-50",
          "border text-sm sm:text-base",
          "ps-4 pe-4 py-2.5",
          "shadow-sm shadow-amber-900/10",
          showRequired
            ? "border-red-300 focus:outline-none focus:border-red-400 focus:ring-1 focus:ring-red-300/70"
            : "border-amber-200/80 focus:outline-none focus:border-amber-400 focus:ring-1 focus:ring-amber-300/70",
          "placeholder:text-amber-800/60 text-amber-950"
        )}
        autoComplete="off"
      />
    </div>
  );
}

