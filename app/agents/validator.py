"""Validator agent: validates shift plans against business rules."""

import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import date

from app.agents.base_agent import BaseAgent
from app.consts.models import ModelConsts
from app.dal import get_session
from app.utils.excel_helpers import (
    HEBREW_DAYS,
    get_assignments_for_week,
    get_sheet_for_month,
    get_week_structure,
    open_workbook,
)
from langchain_core.prompts import ChatPromptTemplate


@dataclass
class ValidationError:
    """Represents a validation error or warning."""

    type: str
    severity: str  # "error" or "warning"
    employee: str | None
    day: str | None
    shift: str | None
    message: str
    suggestion: str


class ValidatorAgent(BaseAgent):
    """Agent that validates shift plans against business rules.

    This agent doesn't use tools - it performs validation directly and returns structured results.
    """

    def __init__(
        self,
        shift_plan_id: int,
        manager_id: int,
        model_name: str = ModelConsts.CLAUDE_SONNET_4_5,
        status_callback: Callable[[str], Awaitable[None]] | None = None,
    ):
        super().__init__(
            agent_name="Validator",
            model_name=model_name,
            status_callback=status_callback,
        )
        self.shift_plan_id = shift_plan_id
        self.manager_id = manager_id

    async def validate(
        self,
        excel_path: str,
        week_start: date,
    ) -> dict:
        """Validate a shift plan.

        Args:
            excel_path: Path to the Excel file with the shift plan.
            week_start: Start date of the week being validated.

        Returns:
            Validation result dictionary with errors and summary.
        """
        await self.emit_status("Validating shift plan...")

        errors: list[ValidationError] = []

        # Load the Excel file
        try:
            wb = open_workbook(excel_path)
            ws = get_sheet_for_month(wb, week_start.month, week_start.year)
            if not ws:
                return self._create_error_result("Could not find worksheet for the specified month")

            week_structure = get_week_structure(ws, 6)  # Default start row
            assignments = get_assignments_for_week(ws, week_structure)
        except Exception as e:
            return self._create_error_result(f"Error reading Excel file: {e}")

        # Load constraints from database
        constraints = self._load_constraints()

        # Run all validations
        errors.extend(self._check_availability(assignments, constraints))
        errors.extend(self._check_unavailability(assignments, constraints))
        errors.extend(self._check_max_shifts(assignments, constraints))
        errors.extend(self._check_max_hours(assignments, constraints))
        errors.extend(self._check_coverage(assignments))
        errors.extend(self._check_preferences(assignments, constraints))

        # Build result
        error_count = sum(1 for e in errors if e.severity == "error")
        warning_count = sum(1 for e in errors if e.severity == "warning")

        employees_with_issues = list(set(e.employee for e in errors if e.employee))
        days_with_issues = list(set(e.day for e in errors if e.day))

        return {
            "valid": error_count == 0,
            "errors": [
                {
                    "type": e.type,
                    "severity": e.severity,
                    "employee": e.employee,
                    "day": e.day,
                    "shift": e.shift,
                    "message": e.message,
                    "suggestion": e.suggestion,
                }
                for e in errors
            ],
            "summary": {
                "total_errors": error_count,
                "total_warnings": warning_count,
                "employees_with_issues": employees_with_issues,
                "days_with_issues": days_with_issues,
            },
        }

    def _load_constraints(self) -> dict[str, dict]:
        """Load all constraints from the database."""
        from app.dal.models import Employee, EmployeeConstraint

        db = get_session()
        try:
            constraints_list = EmployeeConstraint.get_by_shift_plan(db, self.shift_plan_id)
            result = {}

            for c in constraints_list:
                employee = db.query(Employee).filter(Employee.id == c.employee_id).first()
                if employee:
                    result[employee.name] = {
                        "availability_days": c.get_availability_days_list(),
                        "unavailable_days": c.get_unavailable_days_list(),
                        "max_shifts_per_week": c.max_shifts_per_week,
                        "max_hours_per_week": c.max_hours_per_week,
                        "min_rest_hours": c.min_rest_hours or 11,
                        "preferred_shift_types": c.get_preferred_shift_types_list(),
                    }

            return result
        finally:
            db.close()

    def _get_employee_shifts(self, assignments: dict[str, list[str]]) -> dict[str, list[dict]]:
        """Get all shifts for each employee."""
        employee_shifts: dict[str, list[dict]] = {}

        for key, employees in assignments.items():
            day, shift_type, time_range = key.split("|")
            for emp in employees:
                if emp not in employee_shifts:
                    employee_shifts[emp] = []
                employee_shifts[emp].append(
                    {"day": day, "shift_type": shift_type, "time_range": time_range}
                )

        return employee_shifts

    def _check_availability(
        self, assignments: dict[str, list[str]], constraints: dict[str, dict]
    ) -> list[ValidationError]:
        """Check that employees only work on available days."""
        errors = []
        employee_shifts = self._get_employee_shifts(assignments)

        for emp_name, shifts in employee_shifts.items():
            if emp_name not in constraints:
                continue

            availability = constraints[emp_name].get("availability_days", [])
            if not availability:  # No restriction
                continue

            for shift in shifts:
                if shift["day"] not in availability:
                    errors.append(
                        ValidationError(
                            type="availability",
                            severity="error",
                            employee=emp_name,
                            day=shift["day"],
                            shift=shift["shift_type"],
                            message=f"{emp_name} is not available on {shift['day']}",
                            suggestion=f"Remove {emp_name} from {shift['day']} or update their availability",
                        )
                    )

        return errors

    def _check_unavailability(
        self, assignments: dict[str, list[str]], constraints: dict[str, dict]
    ) -> list[ValidationError]:
        """Check that employees don't work on unavailable days."""
        errors = []
        employee_shifts = self._get_employee_shifts(assignments)

        for emp_name, shifts in employee_shifts.items():
            if emp_name not in constraints:
                continue

            unavailable = constraints[emp_name].get("unavailable_days", [])
            if not unavailable:
                continue

            for shift in shifts:
                if shift["day"] in unavailable:
                    errors.append(
                        ValidationError(
                            type="unavailability",
                            severity="error",
                            employee=emp_name,
                            day=shift["day"],
                            shift=shift["shift_type"],
                            message=f"{emp_name} cannot work on {shift['day']}",
                            suggestion=f"Remove {emp_name} from {shift['day']}",
                        )
                    )

        return errors

    def _check_max_shifts(
        self, assignments: dict[str, list[str]], constraints: dict[str, dict]
    ) -> list[ValidationError]:
        """Check that employees don't exceed max shifts per week."""
        errors = []
        employee_shifts = self._get_employee_shifts(assignments)

        for emp_name, shifts in employee_shifts.items():
            if emp_name not in constraints:
                continue

            max_shifts = constraints[emp_name].get("max_shifts_per_week")
            if max_shifts is None:
                continue

            if len(shifts) > max_shifts:
                errors.append(
                    ValidationError(
                        type="max_shifts",
                        severity="error",
                        employee=emp_name,
                        day=None,
                        shift=None,
                        message=f"{emp_name} has {len(shifts)} shifts but max is {max_shifts}",
                        suggestion=f"Remove {len(shifts) - max_shifts} shift(s) from {emp_name}",
                    )
                )

        return errors

    def _check_max_hours(
        self, assignments: dict[str, list[str]], constraints: dict[str, dict]
    ) -> list[ValidationError]:
        """Check that employees don't exceed max hours per week."""
        errors = []
        employee_shifts = self._get_employee_shifts(assignments)
        hours_per_shift = 9  # Approximate hours per shift

        for emp_name, shifts in employee_shifts.items():
            if emp_name not in constraints:
                continue

            max_hours = constraints[emp_name].get("max_hours_per_week")
            if max_hours is None:
                continue

            total_hours = len(shifts) * hours_per_shift
            if total_hours > max_hours:
                errors.append(
                    ValidationError(
                        type="max_hours",
                        severity="error",
                        employee=emp_name,
                        day=None,
                        shift=None,
                        message=f"{emp_name} has ~{total_hours} hours but max is {max_hours}",
                        suggestion=f"Reduce shifts for {emp_name} to stay under {max_hours} hours",
                    )
                )

        return errors

    def _check_coverage(self, assignments: dict[str, list[str]]) -> list[ValidationError]:
        """Check that each shift has minimum coverage."""
        errors = []

        # Group by day and shift type
        coverage: dict[str, dict[str, int]] = {}
        for day in HEBREW_DAYS:
            coverage[day] = {"בוקר": 0, "צהריים": 0, "ערב": 0}

        for key, employees in assignments.items():
            day, shift_type, _ = key.split("|")
            if day in coverage and shift_type in coverage[day]:
                coverage[day][shift_type] += len(employees)

        # Check for zero coverage
        for day, shifts in coverage.items():
            for shift_type, count in shifts.items():
                if count == 0:
                    errors.append(
                        ValidationError(
                            type="coverage",
                            severity="warning",
                            employee=None,
                            day=day,
                            shift=shift_type,
                            message=f"No employees assigned to {day} {shift_type}",
                            suggestion=f"Assign at least one employee to {day} {shift_type}",
                        )
                    )

        return errors

    def _check_preferences(
        self, assignments: dict[str, list[str]], constraints: dict[str, dict]
    ) -> list[ValidationError]:
        """Check if employees are working their preferred shifts (soft constraint)."""
        errors = []
        employee_shifts = self._get_employee_shifts(assignments)

        for emp_name, shifts in employee_shifts.items():
            if emp_name not in constraints:
                continue

            preferred = constraints[emp_name].get("preferred_shift_types", [])
            if not preferred:
                continue

            non_preferred_count = 0
            for shift in shifts:
                if shift["shift_type"] not in preferred:
                    non_preferred_count += 1

            if non_preferred_count > 0:
                errors.append(
                    ValidationError(
                        type="preference",
                        severity="warning",
                        employee=emp_name,
                        day=None,
                        shift=None,
                        message=f"{emp_name} has {non_preferred_count} shifts outside their preference ({', '.join(preferred)})",
                        suggestion=f"Consider moving {emp_name} to their preferred shifts if possible",
                    )
                )

        return errors

    def _create_error_result(self, message: str) -> dict:
        """Create an error result for validation failures."""
        return {
            "valid": False,
            "errors": [
                {
                    "type": "system",
                    "severity": "error",
                    "employee": None,
                    "day": None,
                    "shift": None,
                    "message": message,
                    "suggestion": "Fix the issue and try again",
                }
            ],
            "summary": {
                "total_errors": 1,
                "total_warnings": 0,
                "employees_with_issues": [],
                "days_with_issues": [],
            },
        }
