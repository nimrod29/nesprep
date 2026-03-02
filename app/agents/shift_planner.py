"""Shift Planner agent: creates shift assignments based on constraints."""

import json
from collections.abc import Awaitable, Callable

from langchain_core.tools import tool

from app.agents.base_agent import BaseToolCallingAgent
from app.consts.models import ModelConsts
from app.dal import get_session
from app.prompts.shift_planner_prompts import SHIFT_PLANNER_SYSTEM_PROMPT
from app.tools.csv_tools import CSVTools
from app.tools.log_tools import LogTools


class ShiftPlannerAgent(BaseToolCallingAgent):
    """Agent that creates shift assignments based on constraints."""

    def __init__(
        self,
        shift_plan_id: int,
        manager_id: int,
        output_dir: str | None = None,
        model_name: str = ModelConsts.CLAUDE_SONNET_4_5,
        status_callback: Callable[[str], Awaitable[None]] | None = None,
        log_file_path: str | None = None,
    ):
        self.shift_plan_id = shift_plan_id
        self.manager_id = manager_id

        # Create tools
        log_tools = LogTools(log_file_path=log_file_path)
        csv_tools = CSVTools(
            shift_plan_id=shift_plan_id,
            output_dir=output_dir,
        )

        # Create constraint retrieval tool
        constraint_tool = self._create_constraint_tool(shift_plan_id)

        tools = log_tools.get_tools() + csv_tools.get_tools() + [constraint_tool]

        super().__init__(
            agent_name="ShiftPlanner",
            tools=tools,
            system_prompt=SHIFT_PLANNER_SYSTEM_PROMPT,
            model_name=model_name,
            status_callback=status_callback,
            max_iterations=50,
        )

    def _create_constraint_tool(self, shift_plan_id: int):
        """Create a tool to retrieve all constraints for this plan."""

        @tool
        def get_all_constraints() -> str:
            """Get all employee constraints for this shift plan.

            Returns:
                JSON string with all constraints including employee names,
                availability, unavailability, max shifts, preferences, etc.
            """
            from app.dal.models import Employee, EmployeeConstraint

            db = get_session()
            try:
                constraints = EmployeeConstraint.get_by_shift_plan(db, shift_plan_id)

                result = []
                for c in constraints:
                    employee = db.query(Employee).filter(Employee.id == c.employee_id).first()
                    if employee:
                        result.append(
                            {
                                "employee_name": employee.name,
                                "employee_id": c.employee_id,
                                "availability_days": c.get_availability_days_list(),
                                "unavailable_days": c.get_unavailable_days_list(),
                                "max_shifts_per_week": c.max_shifts_per_week,
                                "max_hours_per_week": c.max_hours_per_week,
                                "min_rest_hours": c.min_rest_hours,
                                "preferred_shift_types": c.get_preferred_shift_types_list(),
                                "notes": c.notes,
                            }
                        )

                return json.dumps(
                    {"constraints": result, "count": len(result)},
                    ensure_ascii=False,
                    indent=2,
                )
            finally:
                db.close()

        return get_all_constraints
