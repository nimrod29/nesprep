/**
 * ShiftPlanTable - renders week plans as Hebrew RTL shift tables.
 */

import { cn } from "@/shared/utils";
import type { WeekPlan } from "@/shared/websocket";

const HEBREW_DAYS = [
  "ראשון",
  "שני",
  "שלישי",
  "רביעי",
  "חמישי",
  "שישי",
  "שבת",
] as const;

const SHIFT_LABELS = [
  { key: "morning", label: "בוקר" },
  { key: "middle", label: "צהריים" },
  { key: "night", label: "ערב" },
] as const;

interface ShiftPlanTableProps {
  weekPlans: WeekPlan[];
  className?: string;
}

export function ShiftPlanTable({ weekPlans, className }: ShiftPlanTableProps) {
  if (!weekPlans.length) return null;

  return (
    <div className={cn("flex flex-col gap-6 w-full max-w-4xl", className)}>
      {weekPlans.map((week) => (
        <WeekTable key={week.week} week={week} />
      ))}
    </div>
  );
}

interface WeekTableProps {
  week: WeekPlan;
}

function WeekTable({ week }: WeekTableProps) {
  return (
    <div className="overflow-x-auto rounded-xl border border-primary-200">
      <div className="bg-primary-500 text-white px-4 py-2 text-sm font-semibold">
        שבוע {week.week}
      </div>
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="bg-primary-50">
            <th className="border-b border-e border-primary-200 px-3 py-2 text-start font-medium text-primary-800 w-20">
              משמרת
            </th>
            {HEBREW_DAYS.map((day) => {
              const dayData = week.days[day];
              return (
                <th
                  key={day}
                  className="border-b border-e border-primary-200 px-2 py-2 text-center font-medium text-primary-900 last:border-e-0"
                >
                  <div>{day}</div>
                  {dayData && (
                    <div className="text-xs text-primary-400 font-normal">
                      {dayData.date}
                    </div>
                  )}
                </th>
              );
            })}
          </tr>
        </thead>
        <tbody>
          {SHIFT_LABELS.map(({ key, label }, rowIdx) => (
            <tr
              key={key}
              className={rowIdx % 2 === 0 ? "bg-white" : "bg-primary-50/30"}
            >
              <td className="border-b border-e border-primary-200 px-3 py-2 font-medium text-primary-800">
                {label}
              </td>
              {HEBREW_DAYS.map((day) => {
                const dayData = week.days[day];
                const employees =
                  dayData?.[key as keyof typeof dayData] as string[] | undefined;

                return (
                  <td
                    key={day}
                    className="border-b border-e border-primary-200 px-2 py-2 text-center text-primary-900 last:border-e-0"
                  >
                    {employees?.length ? (
                      <div className="flex flex-col gap-0.5">
                        {employees.map((name) => (
                          <span key={name} className="text-xs leading-tight">
                            {name}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <span className="text-primary-200">—</span>
                    )}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
