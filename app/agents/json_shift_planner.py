"""JSON Shift Planner agent: creates shift assignments as structured JSON."""

import json
import logging
from calendar import monthrange
from collections.abc import Awaitable, Callable
from datetime import date, timedelta

from langchain_core.tools import tool

from app.agents.base_agent import BaseToolCallingAgent
from app.agents.json_validator import JsonValidatorAgent
from app.consts.models import ModelConsts
from app.dal import get_session
from app.prompts.json_shift_planner_prompts import JSON_SHIFT_PLANNER_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

HEBREW_DAYS = ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת"]

HEBREW_MONTHS = {
    "ינואר": 1, "פברואר": 2, "מרץ": 3, "אפריל": 4,
    "מאי": 5, "יוני": 6, "יולי": 7, "אוגוסט": 8,
    "ספטמבר": 9, "אוקטובר": 10, "נובמבר": 11, "דצמבר": 12,
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
}

HEBREW_MONTH_NAMES = {
    1: "ינואר", 2: "פברואר", 3: "מרץ", 4: "אפריל",
    5: "מאי", 6: "יוני", 7: "יולי", 8: "אוגוסט",
    9: "ספטמבר", 10: "אוקטובר", 11: "נובמבר", 12: "דצמבר",
}


def _get_weeks_in_month(year: int, month: int) -> list[dict]:
    """Get all weeks (Sunday-Saturday) that overlap with the given month."""
    _, days_in_month = monthrange(year, month)
    first_day = date(year, month, 1)
    last_day = date(year, month, days_in_month)

    # Find the Sunday on or before the first day of the month
    days_since_sunday = (first_day.weekday() + 1) % 7
    first_sunday = first_day - timedelta(days=days_since_sunday)

    weeks = []
    current_sunday = first_sunday

    while True:
        current_saturday = current_sunday + timedelta(days=6)

        # Check if this week overlaps with the month
        week_overlaps = (
            (current_sunday.month == month and current_sunday.year == year) or
            (current_saturday.month == month and current_saturday.year == year) or
            (current_sunday <= first_day <= current_saturday) or
            (current_sunday <= last_day <= current_saturday)
        )

        if week_overlaps:
            days = []
            for i in range(7):
                day_date = current_sunday + timedelta(days=i)
                days.append({
                    "date": f"{day_date.day}.{day_date.month}",
                    "day_name": HEBREW_DAYS[i],
                    "full_date": day_date.isoformat(),
                })

            weeks.append({
                "start": f"{current_sunday.day}.{current_sunday.month}",
                "end": f"{current_saturday.day}.{current_saturday.month}",
                "days": days,
            })

        current_sunday = current_sunday + timedelta(days=7)

        if current_sunday > last_day and current_sunday.month != month:
            break

    return weeks


def _validate_week_structure(data: dict) -> list[str]:
    """Validate the structure of a week plan JSON. Returns list of errors."""
    errors = []

    if "week" not in data:
        errors.append("Missing 'week' field")

    if "days" not in data:
        errors.append("Missing 'days' field")
        return errors

    days = data.get("days", {})
    employee_shift_counts: dict[str, int] = {}

    for day_name in HEBREW_DAYS:
        if day_name not in days:
            errors.append(f"Missing day: {day_name}")
            continue

        day_data = days[day_name]

        if "date" not in day_data:
            errors.append(f"{day_name}: missing 'date' field")

        is_friday = day_name == "שישי"
        is_saturday = day_name == "שבת"

        if is_friday:
            if "morning" not in day_data or not isinstance(day_data.get("morning"), list):
                errors.append(f"{day_name}: missing 'morning' field")
            elif len(day_data["morning"]) != 4:
                errors.append(f"{day_name}: Friday morning must have exactly 4 employees, got {len(day_data['morning'])}")
            for shift in ["middle", "night"]:
                if shift in day_data and isinstance(day_data[shift], list) and len(day_data[shift]) > 0:
                    errors.append(f"{day_name}: Friday must NOT have {shift} shift")
        elif is_saturday:
            if "night" not in day_data or not isinstance(day_data.get("night"), list):
                errors.append(f"{day_name}: missing 'night' field")
            elif len(day_data["night"]) != 3:
                errors.append(f"{day_name}: Saturday night must have exactly 3 employees, got {len(day_data['night'])}")
            for shift in ["morning", "middle"]:
                if shift in day_data and isinstance(day_data[shift], list) and len(day_data[shift]) > 0:
                    errors.append(f"{day_name}: Saturday must NOT have {shift} shift")
        else:
            for shift in ["morning", "middle", "night"]:
                if shift not in day_data:
                    errors.append(f"{day_name}: missing '{shift}' field")
                elif not isinstance(day_data[shift], list):
                    errors.append(f"{day_name}: '{shift}' must be a list")

            if "morning" in day_data and isinstance(day_data["morning"], list):
                if len(day_data["morning"]) != 2:
                    errors.append(f"{day_name}: morning must have exactly 2 employees, got {len(day_data['morning'])}")
            if "middle" in day_data and isinstance(day_data["middle"], list):
                if len(day_data["middle"]) != 2:
                    errors.append(f"{day_name}: middle must have exactly 2 employees, got {len(day_data['middle'])}")
            if "night" in day_data and isinstance(day_data["night"], list):
                if len(day_data["night"]) != 1:
                    errors.append(f"{day_name}: night must have exactly 1 employee, got {len(day_data['night'])}")

        # Check for duplicate employees within the same day
        day_employees: list[str] = []
        for shift in ["morning", "middle", "night"]:
            if shift in day_data and isinstance(day_data[shift], list):
                day_employees.extend(day_data[shift])
        seen = set()
        for emp in day_employees:
            if emp in seen:
                errors.append(f"{day_name}: employee '{emp}' appears more than once in the same day")
            seen.add(emp)
            employee_shift_counts[emp] = employee_shift_counts.get(emp, 0) + 1

    # Check weekly shift limit (max 6 per employee)
    for emp, count in employee_shift_counts.items():
        if count > 6:
            errors.append(f"Employee '{emp}' has {count} shifts this week (maximum is 6)")

    return errors


class JsonShiftPlannerAgent(BaseToolCallingAgent):
    """Agent that creates shift assignments as structured JSON."""

    def __init__(
        self,
        shift_plan_id: int,
        manager_id: int,
        model_name: str = ModelConsts.CLAUDE_SONNET_4_5,
        status_callback: Callable[[str], Awaitable[None]] | None = None,
    ):
        self.shift_plan_id = shift_plan_id
        self.manager_id = manager_id
        self._constraints: dict | None = None
        self._week_plans: list[dict] = []
        self._validation_attempts: int = 0
        self._max_validation_attempts: int = 10
        self._validator = JsonValidatorAgent(
            model_name=model_name,
            status_callback=status_callback,
        )

        tools = self._create_tools()

        today = date.today()
        day_index = (today.weekday() + 1) % 7
        formatted_prompt = JSON_SHIFT_PLANNER_SYSTEM_PROMPT.format(
            current_date=today.strftime("%d/%m/%Y"),
            current_year=today.year,
            current_day_hebrew=HEBREW_DAYS[day_index],
        )

        super().__init__(
            agent_name="JsonShiftPlanner",
            tools=tools,
            system_prompt=formatted_prompt,
            model_name=model_name,
            status_callback=status_callback,
            max_iterations=100,
        )

    def _create_tools(self) -> list:
        """Create the tools for this agent."""
        tools_self = self

        async def _status(msg: str) -> None:
            """Emit status update via callback."""
            if tools_self.status_callback:
                await tools_self.status_callback(msg)

        @tool
        async def get_month_info(month_name: str) -> str:
            """Get month structure with weeks and dates.

            Args:
                month_name: Month name in Hebrew or English (e.g., "אפריל" or "april")

            Returns:
                JSON with year, month number, and all weeks with their dates.
            """
            await _status("מקבל מידע על החודש...")

            month_lower = month_name.lower().strip()
            month_num = HEBREW_MONTHS.get(month_lower)

            if month_num is None:
                return json.dumps({
                    "error": f"Unknown month: {month_name}. Use Hebrew (אפריל) or English (april)."
                }, ensure_ascii=False)

            # Determine year: current or next year (never past)
            today = date.today()
            year = today.year

            # If the month has already passed this year, use next year
            if month_num < today.month:
                year = today.year + 1
            elif month_num == today.month:
                # Current month is fine
                pass

            weeks = _get_weeks_in_month(year, month_num)
            month_name_hebrew = HEBREW_MONTH_NAMES[month_num]

            await _status(f"נמצאו {len(weeks)} שבועות בחודש {month_name_hebrew}")

            return json.dumps({
                "year": year,
                "month": month_num,
                "month_name": month_name_hebrew,
                "weeks_count": len(weeks),
                "weeks": weeks,
            }, ensure_ascii=False, indent=2)

        @tool
        async def get_all_constraints() -> str:
            """Get all employee constraints for this shift plan.

            Returns:
                JSON with all constraints including employee names,
                availability, unavailability, max shifts, preferences.
            """
            await _status("טוען אילוצי עובדים...")

            from app.dal.models import Employee, EmployeeConstraint

            db = get_session()
            try:
                constraints = EmployeeConstraint.get_by_shift_plan(db, tools_self.shift_plan_id)

                result = []
                for c in constraints:
                    employee = db.query(Employee).filter(Employee.id == c.employee_id).first()
                    if employee:
                        constraint_data = {
                            "employee_name": employee.name,
                            "availability_days": c.get_availability_days_list(),
                            "unavailable_days": c.get_unavailable_days_list(),
                            "max_shifts_per_week": c.max_shifts_per_week,
                            "preferred_shift_types": c.get_preferred_shift_types_list(),
                            "notes": c.notes,
                        }
                        result.append(constraint_data)

                # Store constraints for validation
                tools_self._constraints = {c["employee_name"]: c for c in result}

                await _status(f"נמצאו {len(result)} עובדים עם אילוצים")

                return json.dumps(
                    {"constraints": result, "count": len(result)},
                    ensure_ascii=False,
                    indent=2,
                )
            finally:
                db.close()

        @tool
        async def submit_week_plan(week_json: str) -> str:
            """Submit a week's plan for validation.

            Args:
                week_json: ONLY raw JSON of the week plan. No markdown, no backticks, no extra text.

            Returns:
                "Week plan accepted" if valid, or error messages to fix.
            """
            # Step 1: Parse JSON
            try:
                data = json.loads(week_json)
            except json.JSONDecodeError as e:
                logger.info("JSON parse error: %s", e.msg)
                return (
                    f"JSON parse error at position {e.pos}: {e.msg}. "
                    "Return ONLY valid JSON - no markdown code blocks, no backticks, no text before or after."
                )

            week_label = data.get("week", "unknown")
            await _status(f"בודק JSON לשבוע {week_label}...")

            tools_self._validation_attempts += 1

            # Accept after max attempts to avoid infinite loops
            if tools_self._validation_attempts > tools_self._max_validation_attempts:
                logger.info("Max validation attempts reached, accepting week %s", week_label)
                tools_self._week_plans.append(data)
                tools_self._validation_attempts = 0
                await _status(f"שבוע {week_label} אושר (מקסימום ניסיונות) - {len(tools_self._week_plans)} שבועות")
                return (
                    f"Week plan accepted (after max retries): {week_label}. "
                    f"Total weeks submitted: {len(tools_self._week_plans)}"
                )

            # Step 2: Validate structure with code
            await _status(f"מאמת מבנה שבוע {week_label}...")
            structure_errors = _validate_week_structure(data)
            if structure_errors:
                logger.info("Structure errors: %s", structure_errors)
                return f"Structure errors: {'; '.join(structure_errors)}"

            # Step 3: AI validation for constraints and balance
            if tools_self._constraints is None:
                return "Error: Call get_all_constraints first before submitting plans."

            logger.info(
                "Validation attempt %d for week %s",
                tools_self._validation_attempts,
                week_label,
            )

            await _status(
                f"מאמת אילוצים לשבוע {week_label} "
                f"(ניסיון {tools_self._validation_attempts}/{tools_self._max_validation_attempts})..."
            )

            validation_result = await tools_self._validator.validate(
                data,
                tools_self._constraints,
            )

            if not validation_result.get("valid", False):
                errors = validation_result.get("errors", [])
                suggestions = validation_result.get("suggestions", [])
                logger.info("Validation failed for week %s: %s", week_label, errors)
                await _status(f"שבוע {week_label} - נמצאו שגיאות, מתקן...")
                error_msg = "Validation errors:\n"
                for err in errors:
                    error_msg += f"- {err}\n"
                if suggestions:
                    error_msg += "\nSuggestions:\n"
                    for sug in suggestions:
                        error_msg += f"- {sug}\n"
                return error_msg

            # Success - store the week plan, reset attempt counter
            tools_self._week_plans.append(data)
            tools_self._validation_attempts = 0
            await _status(f"שבוע {week_label} אושר! ({len(tools_self._week_plans)} שבועות)")
            logger.info("Week %s accepted", week_label)
            return f"Week plan accepted: {week_label}. Total weeks submitted: {len(tools_self._week_plans)}"

        return [get_month_info, get_all_constraints, submit_week_plan]

    def get_week_plans(self) -> list[dict]:
        """Get all accepted week plans."""
        return self._week_plans.copy()
