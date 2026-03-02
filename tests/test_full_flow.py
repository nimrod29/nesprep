"""Full flow test - runs the complete shift planning pipeline."""

import asyncio
import os
from datetime import date

from app.agents.constraint_analyzer import ConstraintAnalyzerAgent
from app.agents.shift_planner import ShiftPlannerAgent
from app.agents.validator import ValidatorAgent
from app.config import settings
from app.dal import get_session
from app.dal.base import Base, engine
from app.dal.models import Employee, Manager, ShiftPlan, PlanStatus


async def status_callback(message: str) -> None:
    """Print status updates."""
    print(f"  [STATUS] {message}")


async def run_full_flow(template_path: str, week_start: date) -> dict:
    """
    Run the complete shift planning flow:
    1. Setup test data (manager + employees)
    2. Create a shift plan
    3. Run Constraint Analyzer on sample constraints
    4. Run Shift Planner to create assignments
    5. Run Validator to check the plan
    6. If errors, loop back to planner (up to 3 iterations)
    7. Return final result

    Args:
        template_path: Path to the Excel template file
        week_start: Start date of the week to plan

    Returns:
        Dict with success status, output path, and validation summary
    """
    print("=" * 70)
    print("NesPrep - Full Flow Test")
    print("=" * 70)
    print()

    # Initialize database
    Base.metadata.create_all(bind=engine)

    # Step 1: Setup test data
    print("[1/6] Setting up test data...")
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

        manager_id = manager.id
        print(f"      Manager ID: {manager_id}")
        print(f"      Employees: {', '.join(test_employees)}")
    finally:
        db.close()

    # Step 2: Create shift plan
    print("\n[2/6] Creating shift plan...")
    db = get_session()
    try:
        shift_plan = ShiftPlan.create(
            db,
            manager_id=manager_id,
            week_start=week_start,
            title=f"Test Plan {week_start.isoformat()}",
            template_path=template_path,
        )
        shift_plan_id = shift_plan.id
        print(f"      Shift Plan ID: {shift_plan_id}")
        print(f"      Week Start: {week_start}")
    finally:
        db.close()

    # Step 3: Run Constraint Analyzer
    print("\n[3/6] Running Constraint Analyzer...")
    constraints_text = """
    שקד יכולה לעבוד רק בימים א-ג, עד 6 משמרות בשבוע.
    דניאל לא יכול לעבוד בשישי.
    תהל מעדיפה משמרות בוקר.
    שחר יכול לעבוד כל יום חוץ משבת.
    עומר מוגבל ל-40 שעות בשבוע.
    קורין יכולה לעבוד רק בערב.
    שני זמינה כל השבוע.
    """
    print(f"      Constraints:\n{constraints_text}")

    analyzer = ConstraintAnalyzerAgent(
        shift_plan_id=shift_plan_id,
        manager_id=manager_id,
        status_callback=status_callback,
    )

    db = get_session()
    try:
        shift_plan = ShiftPlan.get_by_id(db, shift_plan_id)
        if shift_plan:
            shift_plan.update_status(db, PlanStatus.analyzing)
    finally:
        db.close()

    analyzer_result = await analyzer.run(constraints_text)
    print(f"\n      Analyzer Result: {analyzer_result[:200]}...")

    # Step 4: Run Shift Planner
    print("\n[4/6] Running Shift Planner...")

    db = get_session()
    try:
        shift_plan = ShiftPlan.get_by_id(db, shift_plan_id)
        if shift_plan:
            shift_plan.update_status(db, PlanStatus.planning)
    finally:
        db.close()

    planner = ShiftPlannerAgent(
        shift_plan_id=shift_plan_id,
        manager_id=manager_id,
        template_path=template_path,
        week_start=week_start,
        output_dir=settings.OUTPUT_DIR,
        status_callback=status_callback,
    )

    planner_result = await planner.run(
        "Create a shift plan for this week. Read the template, get all constraints, "
        "and assign employees to shifts while respecting their constraints. "
        "Make sure to save the plan when done."
    )
    print(f"\n      Planner Result: {planner_result[:200]}...")

    output_path = os.path.join(settings.OUTPUT_DIR, f"shift_plan_{week_start.isoformat()}.xlsx")

    # Step 5 & 6: Validation loop
    print("\n[5/6] Running Validator...")
    max_iterations = 3
    final_result = None

    validator = ValidatorAgent(
        shift_plan_id=shift_plan_id,
        manager_id=manager_id,
        status_callback=status_callback,
    )

    for iteration in range(1, max_iterations + 1):
        print(f"\n      Validation iteration {iteration}...")

        db = get_session()
        try:
            shift_plan = ShiftPlan.get_by_id(db, shift_plan_id)
            if shift_plan:
                shift_plan.update_status(db, PlanStatus.validating)
        finally:
            db.close()

        if not os.path.exists(output_path):
            print(f"      WARNING: Output file not found at {output_path}")
            final_result = {
                "valid": False,
                "errors": [{"message": "Output file not created", "severity": "error"}],
                "summary": {"total_errors": 1, "total_warnings": 0},
            }
            break

        validation_result = await validator.validate(output_path, week_start)
        final_result = validation_result

        print(f"      Valid: {validation_result['valid']}")
        print(f"      Errors: {validation_result['summary']['total_errors']}")
        print(f"      Warnings: {validation_result['summary']['total_warnings']}")

        if validation_result["valid"]:
            print("      ✓ Plan is valid!")
            break

        if iteration < max_iterations:
            # Try to fix errors
            error_summary = "\n".join(
                f"- {e['message']}: {e['suggestion']}"
                for e in validation_result["errors"]
                if e["severity"] == "error"
            )
            print(f"\n      Errors to fix:\n{error_summary}")
            print("\n      Asking planner to fix errors...")

            fix_result = await planner.run(
                f"The plan has validation errors. Please fix them:\n{error_summary}"
            )
            print(f"      Fix result: {fix_result[:100]}...")

    # Step 6: Final status
    print("\n[6/6] Finalizing...")
    db = get_session()
    try:
        shift_plan = ShiftPlan.get_by_id(db, shift_plan_id)
        if shift_plan:
            if final_result and final_result["valid"]:
                shift_plan.update_status(db, PlanStatus.completed)
                shift_plan.set_output_path(db, output_path)
            else:
                shift_plan.update_status(db, PlanStatus.completed)  # Still save even with warnings
                shift_plan.set_output_path(db, output_path)
    finally:
        db.close()

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Shift Plan ID: {shift_plan_id}")
    print(f"  Output Path: {output_path}")
    print(f"  File Exists: {os.path.exists(output_path)}")
    if final_result:
        print(f"  Valid: {final_result['valid']}")
        print(f"  Total Errors: {final_result['summary']['total_errors']}")
        print(f"  Total Warnings: {final_result['summary']['total_warnings']}")

        if final_result["errors"]:
            print("\n  Issues:")
            for error in final_result["errors"][:5]:  # Show first 5
                severity = "ERROR" if error["severity"] == "error" else "WARNING"
                print(f"    [{severity}] {error['message']}")

    print("=" * 70)

    return {
        "success": final_result["valid"] if final_result else False,
        "shift_plan_id": shift_plan_id,
        "output_path": output_path,
        "validation": final_result,
    }


async def main() -> None:
    """Run the full flow test."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m tests.test_full_flow <template_path> [week_start]")
        print("Example: python -m tests.test_full_flow /path/to/template.xlsx 2026-02-01")
        sys.exit(1)

    template_path = sys.argv[1]
    if not os.path.exists(template_path):
        print(f"Error: Template file not found: {template_path}")
        sys.exit(1)

    week_start = date(2026, 2, 1)
    if len(sys.argv) >= 3:
        try:
            week_start = date.fromisoformat(sys.argv[2])
        except ValueError:
            print(f"Error: Invalid date format: {sys.argv[2]}")
            sys.exit(1)

    result = await run_full_flow(template_path, week_start)

    if result["success"]:
        print("\n✓ Full flow completed successfully!")
    else:
        print("\n✗ Full flow completed with issues.")


if __name__ == "__main__":
    asyncio.run(main())
