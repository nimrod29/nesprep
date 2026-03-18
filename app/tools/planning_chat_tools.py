"""Planning chat tools for the conversational planning agent."""

import json
import logging
import os
from calendar import monthrange
from collections.abc import Awaitable, Callable
from datetime import date, timedelta
from typing import TYPE_CHECKING

from langchain_core.tools import tool

from app.config import settings
from app.utils.csv_template_generator import HEBREW_DAYS

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

HEBREW_MONTH_NAMES = {
    1: "ינואר", 2: "פברואר", 3: "מרץ", 4: "אפריל",
    5: "מאי", 6: "יוני", 7: "יולי", 8: "אוגוסט",
    9: "ספטמבר", 10: "אוקטובר", 11: "נובמבר", 12: "דצמבר",
}


class PlanningChatTools:
    """Tools for the conversational planning chat agent."""

    def __init__(
        self,
        shift_plan_id: int,
        manager_id: int,
        status_callback: Callable[[str], Awaitable[None]] | None = None,
        plan_callback: Callable[[list[dict]], Awaitable[None]] | None = None,
    ):
        self.shift_plan_id = shift_plan_id
        self.manager_id = manager_id
        self.status_callback = status_callback
        self.plan_callback = plan_callback

    def get_tools(self) -> list:
        """Return the list of planning chat tools."""
        tools_self = self

        @tool
        def get_current_date() -> str:
            """Get today's date and day of week for planning context.

            Returns:
                JSON with date, day_name (Hebrew), and day_index (0=Sunday).
            """
            today = date.today()
            # Python weekday: Monday=0, Sunday=6
            # Convert to Sunday=0, Saturday=6
            day_index = (today.weekday() + 1) % 7
            day_name = HEBREW_DAYS[day_index]

            return json.dumps(
                {
                    "date": today.isoformat(),
                    "day": today.day,
                    "month": today.month,
                    "year": today.year,
                    "day_name": day_name,
                    "day_index": day_index,
                },
                ensure_ascii=False,
            )

        @tool
        def get_employees() -> str:
            """Get the list of employees for this manager.

            Returns:
                JSON string with employee names and IDs.
            """
            from app.dal import get_session
            from app.dal.models import Employee

            db: Session = get_session()
            try:
                employees = Employee.get_by_manager(db, tools_self.manager_id)
                if not employees:
                    return json.dumps(
                        {"employees": [], "count": 0, "message": "No employees found"},
                        ensure_ascii=False,
                    )

                employee_list = [{"id": e.id, "name": e.name} for e in employees]
                return json.dumps(
                    {"employees": employee_list, "count": len(employee_list)},
                    ensure_ascii=False,
                    indent=2,
                )
            finally:
                db.close()

        @tool
        def add_employee(name: str, phone: str | None = None, notes: str | None = None) -> str:
            """Add a new employee for this manager.

            Args:
                name: The employee's name.
                phone: Optional phone number.
                notes: Optional notes about the employee.

            Returns:
                Confirmation message or error.
            """
            from app.dal import get_session
            from app.dal.models import Employee

            db: Session = get_session()
            try:
                existing = Employee.get_by_name_and_manager(db, tools_self.manager_id, name)
                if existing:
                    return f"Employee '{name}' already exists."

                employee = Employee.create(
                    db,
                    manager_id=tools_self.manager_id,
                    name=name,
                    phone=phone,
                    notes=notes,
                )
                return f"Added employee: {employee.name} (ID: {employee.id})"
            except Exception as e:
                return f"Error adding employee: {e}"
            finally:
                db.close()

        @tool
        def remove_employee(name: str) -> str:
            """Remove an employee by name.

            Args:
                name: The employee's name to remove.

            Returns:
                Confirmation message or error.
            """
            from app.dal import get_session
            from app.dal.models import Employee

            db: Session = get_session()
            try:
                employee = Employee.get_by_name_and_manager(db, tools_self.manager_id, name)
                if not employee:
                    return f"Employee '{name}' not found."

                db.delete(employee)
                db.commit()
                return f"Removed employee: {name}"
            except Exception as e:
                return f"Error removing employee: {e}"
            finally:
                db.close()

        @tool
        def set_employee_constraint(
            name: str,
            availability_days: list[str] | None = None,
            unavailable_days: list[str] | None = None,
            max_shifts_per_week: int | None = None,
            max_hours_per_week: int | None = None,
            preferred_shift_types: list[str] | None = None,
            notes: str | None = None,
        ) -> str:
            """Save a constraint for an employee.

            Use full Hebrew day names: ראשון, שני, שלישי, רביעי, חמישי, שישי, שבת

            Args:
                name: Employee name (in Hebrew).
                availability_days: Days the employee CAN work (e.g., ["ראשון", "שני"]).
                unavailable_days: Days the employee CANNOT work (e.g., ["שישי"]).
                max_shifts_per_week: Maximum number of shifts per week.
                max_hours_per_week: Maximum hours per week.
                preferred_shift_types: Preferred shift types (e.g., ["בוקר", "ערב"]).
                notes: Additional notes about this constraint.

            Returns:
                Confirmation message or error.
            """
            from app.dal import get_session
            from app.dal.models import Employee, EmployeeConstraint

            db: Session = get_session()
            try:
                employee = Employee.get_by_name_and_manager(db, tools_self.manager_id, name)
                if not employee:
                    return f"Error: Employee '{name}' not found. Add them first with add_employee."

                existing = EmployeeConstraint.get_by_employee_and_plan(
                    db, tools_self.shift_plan_id, employee.id
                )

                if existing:
                    existing.update(
                        db,
                        availability_days=availability_days,
                        unavailable_days=unavailable_days,
                        max_shifts_per_week=max_shifts_per_week,
                        max_hours_per_week=max_hours_per_week,
                        preferred_shift_types=preferred_shift_types,
                        notes=notes,
                    )
                    action = "Updated"
                else:
                    EmployeeConstraint.create(
                        db,
                        shift_plan_id=tools_self.shift_plan_id,
                        employee_id=employee.id,
                        availability_days=availability_days,
                        unavailable_days=unavailable_days,
                        max_shifts_per_week=max_shifts_per_week,
                        max_hours_per_week=max_hours_per_week,
                        preferred_shift_types=preferred_shift_types,
                        notes=notes,
                    )
                    action = "Created"

                return f"{action} constraint for {name}"
            except Exception as e:
                return f"Error saving constraint: {e}"
            finally:
                db.close()

        @tool
        def get_constraints_summary() -> str:
            """Get a summary of all constraints for this shift plan.

            Returns:
                JSON summary of all employee constraints.
            """
            from app.dal import get_session
            from app.dal.models import Employee, EmployeeConstraint

            db: Session = get_session()
            try:
                constraints = EmployeeConstraint.get_by_shift_plan(db, tools_self.shift_plan_id)

                if not constraints:
                    return json.dumps(
                        {"constraints": [], "count": 0, "message": "No constraints set yet"},
                        ensure_ascii=False,
                    )

                summary = []
                for c in constraints:
                    employee = Employee.get_by_id(db, c.employee_id)
                    summary.append(
                        {
                            "employee": employee.name if employee else "Unknown",
                            "availability_days": c.get_availability_days_list(),
                            "unavailable_days": c.get_unavailable_days_list(),
                            "max_shifts_per_week": c.max_shifts_per_week,
                            "max_hours_per_week": c.max_hours_per_week,
                            "preferred_shift_types": c.get_preferred_shift_types_list(),
                            "notes": c.notes,
                        }
                    )

                return json.dumps(
                    {"constraints": summary, "count": len(summary)},
                    ensure_ascii=False,
                    indent=2,
                )
            finally:
                db.close()

        @tool
        def get_planning_status() -> str:
            """Check what information is still needed before creating a plan.

            Returns:
                JSON status with what's ready and what's missing.
            """
            from app.dal import get_session
            from app.dal.models import Employee, EmployeeConstraint, ShiftPlan

            db: Session = get_session()
            try:
                shift_plan = ShiftPlan.get_by_id(db, tools_self.shift_plan_id)
                employees = Employee.get_by_manager(db, tools_self.manager_id)
                constraints = EmployeeConstraint.get_by_shift_plan(db, tools_self.shift_plan_id)

                status = {
                    "ready": True,
                    "missing": [],
                    "info": {},
                }

                if not shift_plan:
                    status["ready"] = False
                    status["missing"].append("shift_plan not found")
                    return json.dumps(status, ensure_ascii=False, indent=2)

                status["info"]["week_start"] = (
                    shift_plan.week_start.isoformat() if shift_plan.week_start else None
                )
                status["info"]["template_path"] = shift_plan.template_path or settings.get_template_path()
                status["info"]["employee_count"] = len(employees)
                status["info"]["constraint_count"] = len(constraints)

                if not shift_plan.week_start:
                    status["ready"] = False
                    status["missing"].append("week_start - which week to plan?")

                if not employees:
                    status["ready"] = False
                    status["missing"].append("employees - who needs to be scheduled?")

                employees_without_constraints = []
                employee_ids_with_constraints = {c.employee_id for c in constraints}
                for emp in employees:
                    if emp.id not in employee_ids_with_constraints:
                        employees_without_constraints.append(emp.name)

                if employees_without_constraints:
                    status["info"]["employees_without_constraints"] = employees_without_constraints

                return json.dumps(status, ensure_ascii=False, indent=2)
            finally:
                db.close()

        @tool
        def set_target_month(year: int, month: int) -> str:
            """Set the target month for this shift plan.

            Args:
                year: The year (e.g., 2025)
                month: The month (1-12)

            Returns:
                Confirmation message or error.
            """
            from app.dal import get_session
            from app.dal.models import ShiftPlan

            db: Session = get_session()
            try:
                shift_plan = ShiftPlan.get_by_id(db, tools_self.shift_plan_id)
                if not shift_plan:
                    return "Error: Shift plan not found"

                if month < 1 or month > 12:
                    return f"Error: Invalid month {month}. Must be 1-12."

                # Store as first day of month for compatibility
                target_date = date(year, month, 1)
                shift_plan.week_start = target_date
                db.add(shift_plan)
                db.commit()

                hebrew_months = {
                    1: "ינואר", 2: "פברואר", 3: "מרץ", 4: "אפריל",
                    5: "מאי", 6: "יוני", 7: "יולי", 8: "אוגוסט",
                    9: "ספטמבר", 10: "אוקטובר", 11: "נובמבר", 12: "דצמבר"
                }
                month_name = hebrew_months.get(month, str(month))

                return f"Set target month to {month_name} {year}"
            except Exception as e:
                return f"Error setting target month: {e}"
            finally:
                db.close()

        @tool
        def set_week_start(week_start: str) -> str:
            """Set the week start date for this shift plan.

            Args:
                week_start: The start date in YYYY-MM-DD format.

            Returns:
                Confirmation message or error.
            """
            from app.dal import get_session
            from app.dal.models import ShiftPlan

            db: Session = get_session()
            try:
                shift_plan = ShiftPlan.get_by_id(db, tools_self.shift_plan_id)
                if not shift_plan:
                    return "Error: Shift plan not found"

                parsed_date = date.fromisoformat(week_start)
                shift_plan.week_start = parsed_date
                db.add(shift_plan)
                db.commit()

                return f"Set week start to {week_start}"
            except ValueError:
                return f"Error: Invalid date format '{week_start}'. Use YYYY-MM-DD."
            except Exception as e:
                return f"Error setting week start: {e}"
            finally:
                db.close()

        @tool
        def set_template_path(template_path: str) -> str:
            """Set the Excel template path for this shift plan.

            Args:
                template_path: Path to the Excel template file.

            Returns:
                Confirmation message or error.
            """
            from app.dal import get_session
            from app.dal.models import ShiftPlan

            db: Session = get_session()
            try:
                if not os.path.exists(template_path):
                    return f"Error: Template file not found at '{template_path}'"

                shift_plan = ShiftPlan.get_by_id(db, tools_self.shift_plan_id)
                if not shift_plan:
                    return "Error: Shift plan not found"

                shift_plan.template_path = template_path
                db.add(shift_plan)
                db.commit()

                return f"Set template path to {template_path}"
            except Exception as e:
                return f"Error setting template path: {e}"
            finally:
                db.close()

        @tool
        async def create_shift_plan() -> str:
            """Create the shift plan using the JSON-based planning agent.

            Only call this when you have:
            - Employees added
            - Constraints set (or confirmed none needed)
            - Target month set (use set_target_month)

            This triggers the JsonShiftPlannerAgent which creates validated JSON plans.

            Returns:
                Result of the planning process with accepted week plans.
            """
            from app.agents.json_shift_planner import JsonShiftPlannerAgent
            from app.dal import get_session
            from app.dal.models import PlanStatus, ShiftPlan

            db: Session = get_session()
            try:
                shift_plan = ShiftPlan.get_by_id(db, tools_self.shift_plan_id)
                if not shift_plan:
                    return "Error: Shift plan not found"

                if not shift_plan.week_start:
                    return "Error: Target month not set. Use set_target_month first."

                target_year = shift_plan.week_start.year
                target_month = shift_plan.week_start.month

                shift_plan.update_status(db, PlanStatus.planning)
            finally:
                db.close()

            if tools_self.status_callback:
                await tools_self.status_callback("Starting JSON shift plan generation...")
            # region agent log
            import time as _t; open("/Users/nmrwdsny/projects/nesprep/.cursor/debug-4fbabf.log", "a").write('{"sessionId":"4fbabf","location":"planning_chat_tools.py:create_shift_plan","message":"create_shift_plan_entered","data":{"shift_plan_id":' + str(tools_self.shift_plan_id) + ',"target_month":' + str(target_month) + '},"timestamp":' + str(int(_t.time()*1000)) + ',"hypothesisId":"E"}\n')
            # endregion

            hebrew_months = {
                1: "ינואר", 2: "פברואר", 3: "מרץ", 4: "אפריל",
                5: "מאי", 6: "יוני", 7: "יולי", 8: "אוגוסט",
                9: "ספטמבר", 10: "אוקטובר", 11: "נובמבר", 12: "דצמבר"
            }
            month_name = hebrew_months.get(target_month, str(target_month))

            planner = JsonShiftPlannerAgent(
                shift_plan_id=tools_self.shift_plan_id,
                manager_id=tools_self.manager_id,
                status_callback=tools_self.status_callback,
            )

            try:
                if tools_self.status_callback:
                    await tools_self.status_callback("Running JSON shift planner agent...")

                await planner.run(f"צור לי משמרות ל{month_name}")

                week_plans = planner.get_week_plans()

                db = get_session()
                try:
                    shift_plan = ShiftPlan.get_by_id(db, tools_self.shift_plan_id)
                    if shift_plan:
                        shift_plan.update_status(db, PlanStatus.completed)
                        if week_plans:
                            shift_plan.set_plan_data(db, week_plans)
                finally:
                    db.close()

                if not week_plans:
                    return "Planning completed but no week plans were accepted. Check constraints."

                if tools_self.plan_callback:
                    await tools_self.plan_callback(week_plans)

                result = (
                    f"Plan created successfully!\n"
                    f"Month: {month_name} {target_year}\n"
                    f"Weeks planned: {len(week_plans)}\n\n"
                    "Week summaries:\n"
                )

                for plan in week_plans:
                    result += f"- {plan.get('week', 'unknown')}\n"

                return result

            except Exception as e:
                logger.exception("Plan creation failed")
                db = get_session()
                try:
                    shift_plan = ShiftPlan.get_by_id(db, tools_self.shift_plan_id)
                    if shift_plan:
                        shift_plan.update_status(db, PlanStatus.failed)
                finally:
                    db.close()

                return f"Error creating plan: {e}"

        @tool
        def get_current_plan() -> str:
            """Get the current shift plan if one exists.

            Call this before making any edits, or when the user asks about the current plan.

            Returns:
                A formatted text view of the plan, or a message if no plan exists.
            """
            from app.dal import get_session
            from app.dal.models import ShiftPlan

            db: Session = get_session()
            try:
                shift_plan = ShiftPlan.get_by_id(db, tools_self.shift_plan_id)
                if not shift_plan:
                    return "Error: Shift plan not found"

                week_plans = shift_plan.get_plan_data()
                if not week_plans:
                    return "No plan exists yet. Use create_shift_plan to generate one."

                shift_labels = {"morning": "בוקר", "middle": "צהריים", "night": "ערב"}
                lines = [f"Current plan ({len(week_plans)} weeks):\n"]

                for wp in week_plans:
                    lines.append(f"=== שבוע {wp.get('week', '?')} ===")
                    days = wp.get("days", {})
                    for day_name in HEBREW_DAYS:
                        day = days.get(day_name)
                        if not day:
                            continue
                        lines.append(f"  {day_name} ({day.get('date', '')}):")
                        for shift_key, label in shift_labels.items():
                            employees = day.get(shift_key, [])
                            names = ", ".join(employees) if employees else "—"
                            lines.append(f"    {label}: {names}")
                    lines.append("")

                return "\n".join(lines)
            finally:
                db.close()

        @tool
        async def update_shift_plan(changes_json: str) -> str:
            """Update the current shift plan with changes.

            Args:
                changes_json: JSON string describing the changes. Format:
                    {"changes": [
                        {"action": "replace", "week": "2.3-8.3", "day": "שני",
                         "shift": "morning", "old_employee": "דניאל", "new_employee": "שחר"},
                        {"action": "add", "week": "2.3-8.3", "day": "שני",
                         "shift": "morning", "employee": "עומר"},
                        {"action": "remove", "week": "2.3-8.3", "day": "שני",
                         "shift": "morning", "employee": "דניאל"}
                    ]}

            Returns:
                Summary of changes applied, or error message.
            """
            from app.dal import get_session
            from app.dal.models import ShiftPlan

            db: Session = get_session()
            try:
                shift_plan = ShiftPlan.get_by_id(db, tools_self.shift_plan_id)
                if not shift_plan:
                    return "Error: Shift plan not found"

                week_plans = shift_plan.get_plan_data()
                if not week_plans:
                    return "Error: No plan exists yet. Use create_shift_plan first."

                try:
                    payload = json.loads(changes_json)
                except json.JSONDecodeError as e:
                    return f"Error: Invalid JSON — {e}"

                changes = payload.get("changes", [])
                if not changes:
                    return "Error: No changes provided."

                week_index = {wp.get("week"): wp for wp in week_plans}
                applied = []
                errors = []

                for change in changes:
                    action = change.get("action")
                    week_key = change.get("week")
                    day_name = change.get("day")
                    shift_key = change.get("shift")

                    wp = week_index.get(week_key)
                    if not wp:
                        errors.append(f"Week '{week_key}' not found")
                        continue

                    day_data = wp.get("days", {}).get(day_name)
                    if not day_data:
                        errors.append(f"Day '{day_name}' not found in week '{week_key}'")
                        continue

                    if shift_key not in day_data:
                        errors.append(f"Shift '{shift_key}' not found in {day_name}")
                        continue

                    roster = day_data[shift_key]

                    if action == "replace":
                        old_emp = change.get("old_employee")
                        new_emp = change.get("new_employee")
                        if old_emp in roster:
                            idx = roster.index(old_emp)
                            roster[idx] = new_emp
                            applied.append(
                                f"Replaced {old_emp} → {new_emp} ({day_name} {shift_key})"
                            )
                        else:
                            errors.append(f"{old_emp} not in {day_name} {shift_key}")

                    elif action == "add":
                        emp = change.get("employee")
                        if emp not in roster:
                            roster.append(emp)
                            applied.append(f"Added {emp} to {day_name} {shift_key}")
                        else:
                            errors.append(f"{emp} already in {day_name} {shift_key}")

                    elif action == "remove":
                        emp = change.get("employee")
                        if emp in roster:
                            roster.remove(emp)
                            applied.append(f"Removed {emp} from {day_name} {shift_key}")
                        else:
                            errors.append(f"{emp} not in {day_name} {shift_key}")

                    else:
                        errors.append(f"Unknown action: {action}")

                shift_plan.set_plan_data(db, week_plans)

                if tools_self.plan_callback:
                    await tools_self.plan_callback(week_plans)

                parts = []
                if applied:
                    parts.append("Changes applied:\n" + "\n".join(f"  ✓ {a}" for a in applied))
                if errors:
                    parts.append("Errors:\n" + "\n".join(f"  ✗ {e}" for e in errors))
                return "\n".join(parts) if parts else "No changes were made."
            except Exception as e:
                return f"Error updating plan: {e}"
            finally:
                db.close()

        @tool
        def get_month_calendar(month: int, year: int) -> str:
            """Get all dates in a month with their corresponding Hebrew day names.

            Args:
                month: Month number (1-12).
                year: Year (e.g. 2026).

            Returns:
                JSON with every date in the month and its Hebrew day name.
            """
            if month < 1 or month > 12:
                return json.dumps({"error": f"Invalid month {month}. Must be 1-12."}, ensure_ascii=False)

            _, days_in_month = monthrange(year, month)
            month_name = HEBREW_MONTH_NAMES.get(month, str(month))

            days = []
            for day_num in range(1, days_in_month + 1):
                d = date(year, month, day_num)
                day_index = (d.weekday() + 1) % 7
                days.append({
                    "date": f"{d.day}.{d.month}",
                    "day_name": HEBREW_DAYS[day_index],
                    "full_date": d.isoformat(),
                })

            return json.dumps(
                {"month": month, "year": year, "month_name": month_name, "days": days},
                ensure_ascii=False,
                indent=2,
            )

        return [
            get_current_date,
            get_employees,
            add_employee,
            remove_employee,
            set_employee_constraint,
            get_constraints_summary,
            get_planning_status,
            set_target_month,
            set_week_start,
            set_template_path,
            create_shift_plan,
            get_current_plan,
            update_shift_plan,
            get_month_calendar,
        ]
