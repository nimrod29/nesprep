"""Excel tools for shift planning agents."""

import json
import os
from datetime import date

from langchain_core.tools import tool

from app.config import settings
from app.utils.excel_helpers import (
    DAY_COLUMNS,
    HEBREW_DAYS,
    ShiftSlot,
    assign_employee_to_slot,
    find_week_start_row,
    get_assignments_for_week,
    get_sheet_for_month,
    get_week_structure,
    open_workbook,
    save_workbook,
)


class ExcelTools:
    """Tools for reading and writing Excel shift plans."""

    def __init__(
        self,
        template_path: str | None = None,
        output_dir: str | None = None,
        week_start: date | None = None,
    ):
        self.template_path = template_path
        self.output_dir = output_dir or settings.OUTPUT_DIR
        self.week_start = week_start
        self._workbook = None
        self._worksheet = None
        self._week_structure = None

    def get_tools(self) -> list:
        """Return the list of Excel tools."""
        tools_self = self

        @tool
        def read_template_structure() -> str:
            """Read the structure of the Excel template for the specified week.

            Returns information about:
            - Available shift slots (day, shift type, time range)
            - Current assignments if any exist
            - The week date range

            Returns:
                JSON string with template structure information.
            """
            if not tools_self.template_path:
                return json.dumps({"error": "No template path configured"})

            if not os.path.exists(tools_self.template_path):
                return json.dumps({"error": f"Template not found: {tools_self.template_path}"})

            try:
                wb = open_workbook(tools_self.template_path)
                tools_self._workbook = wb

                if tools_self.week_start:
                    ws = get_sheet_for_month(wb, tools_self.week_start.month, tools_self.week_start.year)
                else:
                    ws = wb.active

                if not ws:
                    return json.dumps({"error": "No worksheet found"})

                tools_self._worksheet = ws

                # Find week start row
                start_row = 6  # Default
                if tools_self.week_start:
                    found_row = find_week_start_row(ws, tools_self.week_start)
                    if found_row:
                        start_row = found_row

                week_structure = get_week_structure(ws, start_row)
                tools_self._week_structure = week_structure

                # Get current assignments
                assignments = get_assignments_for_week(ws, week_structure)

                return json.dumps(
                    {
                        "date_range": week_structure.date_range,
                        "days": HEBREW_DAYS,
                        "shift_types": ["בוקר", "צהריים", "ערב"],
                        "current_assignments": assignments,
                        "total_slots": len(week_structure.slots),
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            except Exception as e:
                return json.dumps({"error": str(e)})

        @tool
        def assign_shift(employee_name: str, day: str, shift_type: str) -> str:
            """Assign an employee to a specific shift.

            Args:
                employee_name: Name of the employee (in Hebrew).
                day: Day of the week in Hebrew (ראשון, שני, שלישי, רביעי, חמישי, שישי, שבת).
                shift_type: Type of shift (בוקר, צהריים, ערב).

            Returns:
                Confirmation message or error.
            """
            if not tools_self._worksheet or not tools_self._week_structure:
                return "Error: Template not loaded. Call read_template_structure first."

            if day not in HEBREW_DAYS:
                return f"Error: Invalid day '{day}'. Must be one of: {', '.join(HEBREW_DAYS)}"

            if shift_type not in ["בוקר", "צהריים", "ערב"]:
                return f"Error: Invalid shift type '{shift_type}'. Must be בוקר, צהריים, or ערב"

            # Find an available slot for this day and shift type
            for slot in tools_self._week_structure.slots:
                if slot.day == day and slot.shift_type == shift_type:
                    assign_employee_to_slot(tools_self._worksheet, slot, employee_name)
                    return f"Assigned {employee_name} to {day} {shift_type}"

            return f"Error: No slot found for {day} {shift_type}"

        @tool
        def get_employee_assignments(employee_name: str) -> str:
            """Get all current assignments for a specific employee.

            Args:
                employee_name: Name of the employee (in Hebrew).

            Returns:
                JSON string with the employee's assignments.
            """
            if not tools_self._worksheet or not tools_self._week_structure:
                return "Error: Template not loaded. Call read_template_structure first."

            assignments = get_assignments_for_week(tools_self._worksheet, tools_self._week_structure)

            employee_shifts = []
            for key, employees in assignments.items():
                if employee_name in employees:
                    day, shift_type, time_range = key.split("|")
                    employee_shifts.append(
                        {"day": day, "shift_type": shift_type, "time_range": time_range}
                    )

            return json.dumps(
                {"employee": employee_name, "shifts": employee_shifts, "total": len(employee_shifts)},
                ensure_ascii=False,
                indent=2,
            )

        @tool
        def get_shift_coverage() -> str:
            """Get coverage information for all shifts.

            Returns:
                JSON string with coverage per day and shift type.
            """
            if not tools_self._worksheet or not tools_self._week_structure:
                return "Error: Template not loaded. Call read_template_structure first."

            assignments = get_assignments_for_week(tools_self._worksheet, tools_self._week_structure)

            coverage: dict[str, dict[str, int]] = {}
            for day in HEBREW_DAYS:
                coverage[day] = {"בוקר": 0, "צהריים": 0, "ערב": 0}

            for key, employees in assignments.items():
                day, shift_type, _ = key.split("|")
                if day in coverage and shift_type in coverage[day]:
                    coverage[day][shift_type] += len(employees)

            return json.dumps(coverage, ensure_ascii=False, indent=2)

        @tool
        def save_plan(output_filename: str | None = None) -> str:
            """Save the current shift plan to an Excel file.

            Args:
                output_filename: Optional filename for the output. If not provided,
                                 generates a name based on the week start date.

            Returns:
                Path to the saved file or error message.
            """
            if not tools_self._workbook:
                return "Error: No workbook loaded. Call read_template_structure first."

            try:
                os.makedirs(tools_self.output_dir, exist_ok=True)

                if output_filename:
                    filename = output_filename
                elif tools_self.week_start:
                    filename = f"shift_plan_{tools_self.week_start.isoformat()}.xlsx"
                else:
                    filename = "shift_plan_output.xlsx"

                output_path = os.path.join(tools_self.output_dir, filename)
                save_workbook(tools_self._workbook, output_path)

                return f"Saved shift plan to: {output_path}"
            except Exception as e:
                return f"Error saving plan: {e}"

        return [
            read_template_structure,
            assign_shift,
            get_employee_assignments,
            get_shift_coverage,
            save_plan,
        ]
