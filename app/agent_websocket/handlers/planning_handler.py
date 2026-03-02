"""Planning handler: orchestrates the 3 agents for shift planning."""

import logging
import os
from datetime import date

from fastapi import WebSocket

from app.agent_websocket.consts.events import EventTypes
from app.agent_websocket.events.event_emitter import emit_event
from app.agents.constraint_analyzer import ConstraintAnalyzerAgent
from app.agents.shift_planner import ShiftPlannerAgent
from app.agents.validator import ValidatorAgent
from app.config import settings
from app.dal import get_session
from app.dal.models import MessageRole, PlanningMessage, PlanStatus, ShiftPlan

logger = logging.getLogger(__name__)

MAX_VALIDATION_ITERATIONS = 3


async def handle_planning_request(
    websocket: WebSocket,
    session_id: str,
    shift_plan_id: int,
    manager_id: int,
    action: str,
    constraints_text: str | None = None,
    connection_state: dict | None = None,
) -> None:
    """Handle planning requests by orchestrating the agents.

    Args:
        websocket: The WebSocket connection.
        session_id: The session ID for events.
        shift_plan_id: The shift plan ID.
        manager_id: The manager ID.
        action: The action to perform ("analyze_constraints" or "generate").
        constraints_text: The constraints text (for analyze_constraints action).
        connection_state: Shared connection state.
    """
    connection_state = connection_state or {}

    async def status_callback(message: str) -> None:
        await emit_event(websocket, session_id, EventTypes.STATUS_UPDATE, {"message": message})

    if action == "analyze_constraints":
        await _handle_analyze_constraints(
            websocket=websocket,
            session_id=session_id,
            shift_plan_id=shift_plan_id,
            manager_id=manager_id,
            constraints_text=constraints_text or "",
            status_callback=status_callback,
        )

    elif action == "generate":
        await _handle_generate(
            websocket=websocket,
            session_id=session_id,
            shift_plan_id=shift_plan_id,
            manager_id=manager_id,
            status_callback=status_callback,
        )


async def _handle_analyze_constraints(
    websocket: WebSocket,
    session_id: str,
    shift_plan_id: int,
    manager_id: int,
    constraints_text: str,
    status_callback,
) -> None:
    """Handle constraint analysis."""
    db = get_session()
    try:
        # Update shift plan status
        shift_plan = ShiftPlan.get_by_id(db, shift_plan_id)
        if not shift_plan:
            await emit_event(
                websocket,
                session_id,
                EventTypes.ERROR,
                {"code": "plan_not_found", "message": "Shift plan not found"},
            )
            return

        shift_plan.update_status(db, PlanStatus.analyzing)

        # Save user message
        PlanningMessage.create(
            db,
            shift_plan_id=shift_plan_id,
            role=MessageRole.user,
            content=constraints_text,
        )

        await emit_event(
            websocket,
            session_id,
            EventTypes.PLANNING_ANALYZING,
            {"message": "Analyzing constraints..."},
        )

        # Create and run constraint analyzer agent
        analyzer = ConstraintAnalyzerAgent(
            shift_plan_id=shift_plan_id,
            manager_id=manager_id,
            status_callback=status_callback,
        )

        try:
            result = await analyzer.run(constraints_text)

            # Save assistant response
            PlanningMessage.create(
                db,
                shift_plan_id=shift_plan_id,
                role=MessageRole.assistant,
                content=result,
            )

            await emit_event(
                websocket,
                session_id,
                EventTypes.PLANNING_CONSTRAINTS_PARSED,
                {"result": result},
            )

        except Exception as e:
            logger.exception("Constraint analysis failed")
            shift_plan.update_status(db, PlanStatus.failed)
            await emit_event(
                websocket,
                session_id,
                EventTypes.ERROR,
                {"code": "analysis_failed", "message": str(e)},
            )

    finally:
        db.close()


async def _handle_generate(
    websocket: WebSocket,
    session_id: str,
    shift_plan_id: int,
    manager_id: int,
    status_callback,
) -> None:
    """Handle shift plan generation with validation loop."""
    db = get_session()
    try:
        # Get shift plan
        shift_plan = ShiftPlan.get_by_id(db, shift_plan_id)
        if not shift_plan:
            await emit_event(
                websocket,
                session_id,
                EventTypes.ERROR,
                {"code": "plan_not_found", "message": "Shift plan not found"},
            )
            return

        shift_plan.update_status(db, PlanStatus.planning)

        await emit_event(
            websocket,
            session_id,
            EventTypes.PLANNING_GENERATING,
            {"message": "Generating shift plan...", "progress": 0.1},
        )

        # Get template path and week start
        template_path = shift_plan.template_path
        week_start = shift_plan.week_start

        if not template_path or not os.path.exists(template_path):
            await emit_event(
                websocket,
                session_id,
                EventTypes.ERROR,
                {"code": "no_template", "message": "Template file not found"},
            )
            return

        # Create shift planner agent
        planner = ShiftPlannerAgent(
            shift_plan_id=shift_plan_id,
            manager_id=manager_id,
            template_path=template_path,
            week_start=week_start,
            output_dir=settings.OUTPUT_DIR,
            status_callback=status_callback,
        )

        # Create validator agent
        validator = ValidatorAgent(
            shift_plan_id=shift_plan_id,
            manager_id=manager_id,
            status_callback=status_callback,
        )

        # Generate initial plan
        try:
            plan_result = await planner.run(
                "Create a shift plan for this week based on the employee constraints. "
                "Read the template, get all constraints, and assign employees to shifts."
            )

            # Save planner response
            PlanningMessage.create(
                db,
                shift_plan_id=shift_plan_id,
                role=MessageRole.assistant,
                content=plan_result,
            )

        except Exception as e:
            logger.exception("Plan generation failed")
            shift_plan.update_status(db, PlanStatus.failed)
            await emit_event(
                websocket,
                session_id,
                EventTypes.ERROR,
                {"code": "generation_failed", "message": str(e)},
            )
            return

        # Validation loop
        output_path = os.path.join(
            settings.OUTPUT_DIR, f"shift_plan_{week_start.isoformat()}.xlsx"
        )

        for iteration in range(1, MAX_VALIDATION_ITERATIONS + 1):
            shift_plan.update_status(db, PlanStatus.validating)

            await emit_event(
                websocket,
                session_id,
                EventTypes.PLANNING_VALIDATING,
                {"iteration": iteration},
            )

            # Validate the plan
            validation_result = await validator.validate(output_path, week_start)

            if validation_result["valid"]:
                # Plan is valid!
                shift_plan.update_status(db, PlanStatus.completed)
                shift_plan.set_output_path(db, output_path)

                await emit_event(
                    websocket,
                    session_id,
                    EventTypes.PLANNING_COMPLETED,
                    {
                        "excel_path": output_path,
                        "summary": validation_result["summary"],
                        "iterations": iteration,
                    },
                )
                return

            # Plan has errors - send back to planner
            await emit_event(
                websocket,
                session_id,
                EventTypes.PLANNING_VALIDATION_ERRORS,
                {"errors": validation_result["errors"], "iteration": iteration},
            )

            if iteration < MAX_VALIDATION_ITERATIONS:
                # Try to fix errors
                error_summary = "\n".join(
                    f"- {e['message']}: {e['suggestion']}"
                    for e in validation_result["errors"]
                    if e["severity"] == "error"
                )

                try:
                    fix_result = await planner.run(
                        f"The plan has validation errors. Please fix them:\n{error_summary}"
                    )

                    PlanningMessage.create(
                        db,
                        shift_plan_id=shift_plan_id,
                        role=MessageRole.assistant,
                        content=fix_result,
                    )

                except Exception as e:
                    logger.exception("Error fixing plan")

        # Max iterations reached
        shift_plan.update_status(db, PlanStatus.completed)
        shift_plan.set_output_path(db, output_path)

        await emit_event(
            websocket,
            session_id,
            EventTypes.PLANNING_COMPLETED,
            {
                "excel_path": output_path,
                "summary": validation_result["summary"],
                "iterations": MAX_VALIDATION_ITERATIONS,
                "has_warnings": validation_result["summary"]["total_warnings"] > 0,
            },
        )

    finally:
        db.close()
