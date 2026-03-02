"""Constraint tools for parsing and saving employee constraints."""

import json
from typing import TYPE_CHECKING

from langchain_core.tools import tool

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class ConstraintTools:
    """Tools for parsing and saving employee constraints."""

    def __init__(
        self,
        shift_plan_id: int,
        manager_id: int,
        db_session_factory,
    ):
        self.shift_plan_id = shift_plan_id
        self.manager_id = manager_id
        self.db_session_factory = db_session_factory
        self._parsed_constraints: list[dict] = []

    def get_tools(self) -> list:
        """Return the list of constraint tools."""
        tools_self = self

        @tool
        def get_employee_list() -> str:
            """Get the list of employees for this manager.

            Returns:
                JSON string with employee names and IDs.
            """
            from app.dal.models import Employee

            db: Session = tools_self.db_session_factory()
            try:
                employees = Employee.get_by_manager(db, tools_self.manager_id)
                employee_list = [{"id": e.id, "name": e.name} for e in employees]
                return json.dumps(
                    {"employees": employee_list, "count": len(employee_list)},
                    ensure_ascii=False,
                    indent=2,
                )
            finally:
                db.close()

        @tool
        def save_employee_constraint(
            employee_name: str,
            availability_days: list[str] | None = None,
            unavailable_days: list[str] | None = None,
            max_shifts_per_week: int | None = None,
            max_hours_per_week: int | None = None,
            min_rest_hours: int | None = None,
            preferred_shift_types: list[str] | None = None,
            notes: str | None = None,
        ) -> str:
            """Save a constraint for an employee.

            Args:
                employee_name: Name of the employee (in Hebrew).
                availability_days: Days the employee CAN work (e.g., ["ראשון", "שני"]).
                unavailable_days: Days the employee CANNOT work (e.g., ["שישי"]).
                max_shifts_per_week: Maximum number of shifts per week.
                max_hours_per_week: Maximum hours per week.
                min_rest_hours: Minimum rest hours between shifts (default 11).
                preferred_shift_types: Preferred shift types (e.g., ["בוקר", "ערב"]).
                notes: Additional notes about this constraint.

            Returns:
                Confirmation message or error.
            """
            from app.dal.models import Employee, EmployeeConstraint

            db: Session = tools_self.db_session_factory()
            try:
                # Find employee by name
                employee = Employee.get_by_name_and_manager(
                    db, tools_self.manager_id, employee_name
                )

                if not employee:
                    return f"Error: Employee '{employee_name}' not found for this manager."

                # Check if constraint already exists
                existing = EmployeeConstraint.get_by_employee_and_plan(
                    db, tools_self.shift_plan_id, employee.id
                )

                if existing:
                    # Update existing constraint
                    existing.update(
                        db,
                        availability_days=availability_days,
                        unavailable_days=unavailable_days,
                        max_shifts_per_week=max_shifts_per_week,
                        max_hours_per_week=max_hours_per_week,
                        min_rest_hours=min_rest_hours,
                        preferred_shift_types=preferred_shift_types,
                        notes=notes,
                    )
                    action = "Updated"
                else:
                    # Create new constraint
                    EmployeeConstraint.create(
                        db,
                        shift_plan_id=tools_self.shift_plan_id,
                        employee_id=employee.id,
                        availability_days=availability_days,
                        unavailable_days=unavailable_days,
                        max_shifts_per_week=max_shifts_per_week,
                        max_hours_per_week=max_hours_per_week,
                        min_rest_hours=min_rest_hours or 11,
                        preferred_shift_types=preferred_shift_types,
                        notes=notes,
                    )
                    action = "Created"

                # Track parsed constraint
                tools_self._parsed_constraints.append(
                    {
                        "employee": employee_name,
                        "availability_days": availability_days,
                        "unavailable_days": unavailable_days,
                        "max_shifts_per_week": max_shifts_per_week,
                        "max_hours_per_week": max_hours_per_week,
                        "preferred_shift_types": preferred_shift_types,
                        "notes": notes,
                    }
                )

                return f"{action} constraint for {employee_name}"
            except Exception as e:
                return f"Error saving constraint: {e}"
            finally:
                db.close()

        @tool
        def finalize_constraints() -> str:
            """Finalize constraint parsing and return a summary.

            Call this when you have finished parsing all constraints.

            Returns:
                JSON summary of all parsed constraints.
            """
            return json.dumps(
                {
                    "status": "completed",
                    "constraints_parsed": len(tools_self._parsed_constraints),
                    "constraints": tools_self._parsed_constraints,
                },
                ensure_ascii=False,
                indent=2,
            )

        return [get_employee_list, save_employee_constraint, finalize_constraints]
