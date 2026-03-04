import { cn } from "@/shared/utils";

export function BrandPanel() {
  return (
    <div
      className={cn(
        "relative w-full max-w-xl rounded-3xl overflow-hidden",
        "bg-gradient-to-b from-zinc-900/80 via-amber-900/80 to-zinc-950/90",
        "border border-amber-800/60 shadow-2xl"
      )}
    >
      <div className="absolute inset-0 opacity-40 bg-[radial-gradient(circle_at_20%_0,rgba(255,255,255,0.08),transparent_55%),radial-gradient(circle_at_80%_100%,rgba(251,191,36,0.22),transparent_55%)]" />

      <div className="relative p-8 lg:p-10 flex flex-col gap-6">
        <div className="inline-flex items-center self-start rounded-full bg-amber-900/70 border border-amber-700/60 px-4 py-1.5 text-xs font-medium tracking-wide uppercase">
          <span className="h-2 w-2 rounded-full bg-amber-400 me-2" />
          מערכת סידורי משמרות ל‑Nespresso
        </div>

        <div>
          <h1 className="text-3xl lg:text-4xl font-semibold tracking-tight">
            NesPrep{" "}
            <span className="text-amber-300">
              for Nespresso
            </span>
          </h1>
          <p className="mt-3 text-sm lg:text-base text-amber-100/80 leading-relaxed">
            תנו ל‑AI להכין לכם סידור משמרות מדויק, מאוזן ואלגנטי – בזמן שאתם
            מתמקדים בלשים את האספרסו המושלם ללקוחות שלכם.
          </p>
        </div>

        <div className="mt-2 flex flex-wrap gap-3 text-xs text-amber-100/70">
          <span className="rounded-full bg-zinc-900/60 border border-amber-800/60 px-3 py-1">
            ⚙️ תכנון אוטומטי של משמרות
          </span>
          <span className="rounded-full bg-zinc-900/60 border border-amber-800/60 px-3 py-1">
            ☕ מותאם ל‑Nespresso
          </span>
          <span className="rounded-full bg-zinc-900/60 border border-amber-800/60 px-3 py-1">
            📅 קובצי Excel מעוצבים
          </span>
        </div>
      </div>
    </div>
  );
}

