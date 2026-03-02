#!/usr/bin/env python3
"""Test script for the JSON Shift Planner agent.

Usage:
    python scripts/test_json_planner.py

Seeds the database with sample data and runs the planner.
Edit the PROMPT variable below to test different scenarios.
"""

import asyncio
import json
import logging
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(message)s",
    datefmt="%H:%M:%S",
)

from app.dal.base import Base, engine, get_session
from app.dal.models import Employee, EmployeeConstraint, Manager, ShiftPlan

PROMPT = """
צור לי משמרות למרץ 2026
"""

EMPLOYEES_AND_CONSTRAINTS = {
    "דניאל": {
        "unavailable_days": ["שני", "חמישי"],
        "notes": (
            "10.3 בוקר\n"
            "8.3 בוקר\n"
            "20.3 יום שישי לעבוד\n"
            "28.3 מוצ״ש לעבוד\n"
            "14.3 מוצ״ש לעבוד\n"
            "1.3 ערב\n"
            "23.3 לא לעבוד\n"
            "22.3 לא לעבוד\n"
            "ימי שני וחמישי לא לעבוד"
        ),
    },
    "תהל": {
        "notes": (
            "28.2-1.3 חופש אני באילת\n"
            "2.3 משמרת ערב (אני חוזרת בבוקר מאילת)\n"
            "4.3 יש לי טימס רווחה בעשר וחצי\n"
            "5.3 בוקר עד ארבע (יורדת לאילת)\n"
            "6.3 חופש\n"
            "7.3 משמרת מוצ״ש (חוזרת באותו יום)\n"
            "8.3 משמרת ערב\n"
            "31.3 משמרת ערב\n"
            "1-4.4 לרדת הביתה לחג"
        ),
    },
    "שחר": {
        "unavailable_days": ["שני", "רביעי", "חמישי"],
        "notes": (
            "6.3 לא לעבוד\n"
            "7.3 לא לעבוד\n"
            "13.3 לעבוד\n"
            "ימי שני רביעי וחמישי לימודים לא לעבוד"
        ),
    },
    "שקד": {
        "notes": (
            "חופש עד ה-11.3 לא לעבוד\n"
            "24.3 לא לעבוד"
        ),
    },
    "שני": {
        "notes": (
            "1.3 ערב\n"
            "3.3 בוקר\n"
            "4.3 בוקר\n"
            "6.3 שישי\n"
            "טיסה מה-8-13.3 לא לעבוד\n"
            "14.3 מוצש\n"
            "15.3 ערב\n"
            "17.3 בוקר/אמצע\n"
            "18.3 בוקר\n"
            "20.3 שישי\n"
            "22.3 ערב\n"
            "24.3 בוקר\n"
            "25.3 אמצע\n"
            "28.3 מוצש"
        ),
    },
    "עומר": {
        "notes": (
            "פעמיים באמצע השבוע\n"
            "ומוצ״ש כל החודש"
        ),
    },
}


def seed_database():
    """Create tables and seed with test data. Returns (shift_plan_id, manager_id)."""
    Base.metadata.create_all(bind=engine)

    db = get_session()
    try:
        existing_manager = Manager.get_by_email(db, "test@nesprep.com")
        if existing_manager:
            for plan in ShiftPlan.get_by_manager(db, existing_manager.id):
                plan.delete(db)
            for emp in Employee.get_by_manager(db, existing_manager.id):
                db.delete(emp)
            db.commit()
            db.delete(existing_manager)
            db.commit()

        manager = Manager.create(db, email="test@nesprep.com", hashed_password="test", name="מנהל בדיקות")

        shift_plan = ShiftPlan.create(
            db,
            manager_id=manager.id,
            week_start=date(2026, 3, 1),
            title="משמרות מרץ 2026",
        )

        for emp_name, constraint_data in EMPLOYEES_AND_CONSTRAINTS.items():
            employee = Employee.create(db, manager_id=manager.id, name=emp_name)

            EmployeeConstraint.create(
                db,
                shift_plan_id=shift_plan.id,
                employee_id=employee.id,
                unavailable_days=constraint_data.get("unavailable_days"),
                availability_days=constraint_data.get("availability_days"),
                max_shifts_per_week=constraint_data.get("max_shifts_per_week"),
                preferred_shift_types=constraint_data.get("preferred_shift_types"),
                notes=constraint_data.get("notes"),
            )

        print(f"Seeded: manager={manager.id}, shift_plan={shift_plan.id}, employees={len(EMPLOYEES_AND_CONSTRAINTS)}")
        return shift_plan.id, manager.id
    finally:
        db.close()


async def main():
    """Seed database and run the JSON shift planner."""
    from app.agents.json_shift_planner import JsonShiftPlannerAgent

    shift_plan_id, manager_id = seed_database()

    prompt = PROMPT.strip()
    if not prompt:
        print("Error: PROMPT is empty.")
        return

    print("=" * 60)
    print("JSON Shift Planner Test")
    print("=" * 60)
    print(f"Prompt: {prompt}")
    print("-" * 60)

    async def status_callback(status: str):
        print(f"  [Status] {status}")

    agent = JsonShiftPlannerAgent(
        shift_plan_id=shift_plan_id,
        manager_id=manager_id,
        status_callback=status_callback,
    )

    try:
        result = await agent.run(prompt)

        print("\n" + "=" * 60)
        print("AGENT RESULT")
        print("=" * 60)
        print(result)

        week_plans = agent.get_week_plans()
        if week_plans:
            print("\n" + "=" * 60)
            print(f"ACCEPTED WEEK PLANS ({len(week_plans)})")
            print("=" * 60)
            for i, plan in enumerate(week_plans, 1):
                print(f"\n--- Week {i}: {plan.get('week', '?')} ---")
                print(json.dumps(plan, ensure_ascii=False, indent=2))
        else:
            print("\nNo week plans were accepted.")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
