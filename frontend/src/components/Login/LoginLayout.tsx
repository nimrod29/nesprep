import type { ReactNode } from "react";
import { cn } from "@/shared/utils";

interface LoginLayoutProps {
  children: ReactNode;
  className?: string;
}

export function LoginLayout({ children, className }: LoginLayoutProps) {
  return (
    <div
      dir="ltr"
      className={cn(
        "min-h-screen w-full flex flex-col text-start",
        // Soft warm cream → caramel gradient, slightly warmer bottom-right
        "bg-[radial-gradient(circle_at_top_left,#F5EFE6_0%,#F5EFE6_25%,#EAD9C2_55%,#E6B873_100%)]"
      )}
    >
      <main className="flex min-h-screen items-center justify-center px-4">
        <div
          className={cn(
            "w-full max-w-[520px]",
            "bg-[#F9F3E8]",
            "rounded-2xl border border-[#E4D3BD]/70",
            "shadow-xl shadow-black/10",
            "ps-8 pe-8 pt-10 pb-12 sm:ps-10 sm:pe-10 sm:pt-12 sm:pb-12",
            "flex flex-col gap-10",
            className
          )}
        >
          {children}
        </div>
      </main>
    </div>
  );
}

