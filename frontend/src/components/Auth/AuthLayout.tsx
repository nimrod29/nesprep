import type { ReactNode } from "react";
import { cn } from "@/shared/utils";

interface AuthLayoutProps {
  brand: ReactNode;
  content: ReactNode;
  className?: string;
}

export function AuthLayout({ brand, content, className }: AuthLayoutProps) {
  return (
    <div
      className={cn(
        "min-h-screen flex flex-col lg:flex-row",
        "bg-gradient-to-br from-zinc-950 via-amber-950 to-zinc-900",
        "text-white",
        className
      )}
    >
      <div className="w-full lg:w-1/2 flex items-center justify-center ps-6 pe-6 pt-10 pb-8 lg:ps-16 lg:pe-10">
        {brand}
      </div>
      <div className="w-full lg:w-1/2 flex items-center justify-center ps-6 pe-6 pb-12 lg:ps-10 lg:pe-16 lg:pb-0">
        {content}
      </div>
    </div>
  );
}

