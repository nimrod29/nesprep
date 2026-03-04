import type { ReactNode } from "react";
import { cn } from "@/shared/utils";

interface HomeLayoutProps {
  header?: ReactNode;
  children: ReactNode;
  className?: string;
}

export function HomeLayout({ header, children, className }: HomeLayoutProps) {
  return (
    <div
      className={cn(
        "min-h-screen flex flex-col",
        // Warm vertical gradient: #F5EFE6 → #EAD9C2 → #E6B873
        "bg-[linear-gradient(to_bottom,#F5EFE6_0%,#EAD9C2_40%,#E6B873_100%)]"
      )}
    >
      <header className="pt-[28px] ps-8 pe-8">
        {header}
      </header>
      <main className="flex-1 flex justify-center">
        <div
          className={cn(
            "w-full max-w-3xl",
            "px-6 sm:px-8",
            "flex flex-col items-center",
            className
          )}
        >
          {children}
        </div>
      </main>
    </div>
  );
}

