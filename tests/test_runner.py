"""Interactive test runner for agents (no WebSocket, direct testing)."""

import asyncio
import os
from datetime import date

from langchain_core.messages import AIMessage, HumanMessage

from app.agents.constraint_analyzer import ConstraintAnalyzerAgent
from app.agents.planning_chat_agent import PlanningChatAgent
from app.agents.shift_planner import ShiftPlannerAgent
from app.agents.validator import ValidatorAgent
from app.dal import get_session
from app.dal.base import Base, engine
from app.dal.models import Employee, Manager, ShiftPlan


async def _status_callback(message: str) -> None:
    print(f"  [status] {message}")


def setup_test_data() -> tuple[int, int]:
    """Create test manager and employees."""
    db = get_session()
    try:
        manager = Manager.get_by_email(db, "test@example.com")
        if not manager:
            manager = Manager.create(db, "test@example.com", "hashed_password", "Test Manager")

        test_employees = ["שקד", "דניאל", "תהל", "שחר", "עומר", "קורין", "שני"]
        for name in test_employees:
            existing = Employee.get_by_name_and_manager(db, manager.id, name)
            if not existing:
                Employee.create(db, manager.id, name)

        return manager.id, manager.id
    finally:
        db.close()


async def test_planning_chat_agent(manager_id: int, shift_plan_id: int) -> None:
    """Test the planning chat agent interactively."""
    print("\n" + "=" * 60)
    print("Testing Planning Chat Agent")
    print("=" * 60)
    print()
    print("This is the main conversational agent for shift planning.")
    print("Type your messages in Hebrew or English.")
    print("Type 'quit' to exit.")
    print()

    agent = PlanningChatAgent(
        shift_plan_id=shift_plan_id,
        manager_id=manager_id,
        status_callback=_status_callback,
    )

    chat_history: list[HumanMessage | AIMessage] = []

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not user_input:
            continue

        if user_input.lower() == "quit":
            break

        print("\nAgent thinking...")
        response = await agent.run(user_input, chat_history)

        chat_history.append(HumanMessage(content=user_input))
        chat_history.append(AIMessage(content=response))

        print(f"\nAgent: {response}")


async def test_constraint_analyzer(manager_id: int, shift_plan_id: int) -> None:
    """Test the constraint analyzer agent."""
    print("\n" + "=" * 60)
    print("Testing Constraint Analyzer Agent")
    print("=" * 60)

    agent = ConstraintAnalyzerAgent(
        shift_plan_id=shift_plan_id,
        manager_id=manager_id,
        status_callback=_status_callback,
    )

    test_input = """
    שקד יכולה לעבוד רק בימים א-ג, עד 6 משמרות בשבוע.
    דניאל לא יכול לעבוד בשישי.
    תהל מעדיפה משמרות בוקר.
    שחר יכול לעבוד כל יום חוץ משבת.
    עומר מוגבל ל-40 שעות בשבוע.
    """

    print(f"\nInput:\n{test_input}")
    print("\nProcessing...")

    result = await agent.run(test_input)
    print(f"\nResult:\n{result}")


async def test_shift_planner(
    manager_id: int, shift_plan_id: int, template_path: str, week_start: date
) -> str:
    """Test the shift planner agent."""
    print("\n" + "=" * 60)
    print("Testing Shift Planner Agent")
    print("=" * 60)

    agent = ShiftPlannerAgent(
        shift_plan_id=shift_plan_id,
        manager_id=manager_id,
        template_path=template_path,
        week_start=week_start,
        status_callback=_status_callback,
    )

    print("\nGenerating shift plan...")

    result = await agent.run(
        "Create a shift plan for this week. Read the template, get all constraints, "
        "and assign employees to shifts while respecting their constraints."
    )

    print(f"\nResult:\n{result}")

    return os.path.join("./output", f"shift_plan_{week_start.isoformat()}.xlsx")


async def test_validator(
    manager_id: int, shift_plan_id: int, excel_path: str, week_start: date
) -> None:
    """Test the validator agent."""
    print("\n" + "=" * 60)
    print("Testing Validator Agent")
    print("=" * 60)

    agent = ValidatorAgent(
        shift_plan_id=shift_plan_id,
        manager_id=manager_id,
        status_callback=_status_callback,
    )

    print(f"\nValidating: {excel_path}")

    result = await agent.validate(excel_path, week_start)

    print(f"\nValid: {result['valid']}")
    print(f"Errors: {result['summary']['total_errors']}")
    print(f"Warnings: {result['summary']['total_warnings']}")

    if result["errors"]:
        print("\nIssues found:")
        for error in result["errors"]:
            severity = "ERROR" if error["severity"] == "error" else "WARNING"
            print(f"  [{severity}] {error['message']}")
            print(f"           Suggestion: {error['suggestion']}")


async def main() -> None:
    """Interactive test runner."""
    print("=" * 60)
    print("NesPrep - Shift Planning Agent Test Runner")
    print("=" * 60)
    print()

    Base.metadata.create_all(bind=engine)

    manager_id, _ = setup_test_data()

    db = get_session()
    try:
        week_start = date(2026, 2, 1)
        shift_plan = ShiftPlan.create(
            db,
            manager_id=manager_id,
            week_start=week_start,
            title="Test Shift Plan",
        )
        shift_plan_id = shift_plan.id
    finally:
        db.close()

    print(f"Created test shift plan ID: {shift_plan_id}")
    print(f"Manager ID: {manager_id}")
    print()

    print("Commands:")
    print("  0 - Test Planning Chat Agent (interactive conversation)")
    print("  1 - Test Constraint Analyzer")
    print("  2 - Test Shift Planner (requires template path)")
    print("  3 - Test Validator (requires Excel path)")
    print("  q - Quit")
    print()

    while True:
        try:
            cmd = input("> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break

        if cmd == "q":
            break

        elif cmd == "0":
            await test_planning_chat_agent(manager_id, shift_plan_id)

        elif cmd == "1":
            await test_constraint_analyzer(manager_id, shift_plan_id)

        elif cmd == "2":
            template_path = input("Template path: ").strip()
            if not template_path:
                print("Template path required")
                continue
            if not os.path.exists(template_path):
                print(f"File not found: {template_path}")
                continue
            await test_shift_planner(manager_id, shift_plan_id, template_path, week_start)

        elif cmd == "3":
            excel_path = input("Excel path: ").strip()
            if not excel_path:
                print("Excel path required")
                continue
            if not os.path.exists(excel_path):
                print(f"File not found: {excel_path}")
                continue
            await test_validator(manager_id, shift_plan_id, excel_path, week_start)

        else:
            print(f"Unknown command: {cmd}")


def main_sync() -> None:
    """Entry point for the nesprep script."""
    asyncio.run(main())


if __name__ == "__main__":
    main_sync()
