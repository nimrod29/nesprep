"""Test the March 2026 shift plan with real constraints."""

import asyncio
from datetime import date

from langchain_core.messages import AIMessage, HumanMessage

from app.agents.planning_chat_agent import PlanningChatAgent
from app.dal import get_session
from app.dal.base import Base, engine
from app.dal.models import Employee, Manager, ShiftPlan


async def status_callback(message: str) -> None:
    """Print status updates."""
    print(f"  [STATUS] {message}")


async def run_march_plan_test() -> dict:
    """
    Run a full conversation to create the March 2026 shift plan.
    """
    print("=" * 70)
    print("NesPrep - March 2026 Shift Plan Test")
    print("=" * 70)
    print()

    Base.metadata.create_all(bind=engine)

    print("[Setup] Creating test data...")
    db = get_session()
    try:
        manager = Manager.get_by_email(db, "march_test@example.com")
        if not manager:
            manager = Manager.create(
                db, "march_test@example.com", "hashed_password", "March Test Manager"
            )
        manager_id = manager.id

        week_start = date(2026, 3, 1)
        shift_plan = ShiftPlan.create(
            db,
            manager_id=manager_id,
            week_start=week_start,
            title=f"March Plan {week_start.isoformat()}",
        )
        shift_plan_id = shift_plan.id

        print(f"      Manager ID: {manager_id}")
        print(f"      Shift Plan ID: {shift_plan_id}")
    finally:
        db.close()

    agent = PlanningChatAgent(
        shift_plan_id=shift_plan_id,
        manager_id=manager_id,
        status_callback=status_callback,
    )

    chat_history: list[HumanMessage | AIMessage] = []
    conversation_log: list[dict] = []

    async def send_message(user_message: str) -> str:
        """Send a message and get response."""
        print(f"\n{'='*70}")
        print(f"[User]: {user_message[:100]}..." if len(user_message) > 100 else f"[User]: {user_message}")
        print()

        response = await agent.run(user_message, chat_history)

        chat_history.append(HumanMessage(content=user_message))
        chat_history.append(AIMessage(content=response))

        conversation_log.append({"role": "user", "content": user_message})
        conversation_log.append({"role": "assistant", "content": response})

        print(f"[Agent]: {response}")
        return response

    print("\n" + "=" * 70)
    print("Starting Conversation")
    print("=" * 70)

    await send_message("היי, אני רוצה לתכנן את חודש מרץ 2026, מתחיל ב-1.3.2026")

    await send_message("""העובדים שלי הם:
דניאל
שני
שחר
תהל
שקד
עומר""")

    await send_message("""אילוצים של דניאל:
10.3 בוקר
8.3 בוקר
20.3 יום שישי לעבוד
28.3 מוצ״ש לעבוד
14.3 מוצ״ש לעבוד
1.3 ערב
23.3 לא לעבוד 
22.3 לא לעבוד
ימי שני וחמישי לא לעבוד""")

    await send_message("""אילוצים של תהל:
28.2-1.3 חופש אני באילת
2.3 משמרת ערב (אני חוזרת בבוקר מאילת)
4.3 יש לי טימס רווחה בעשר וחצי
5.3 בוקר עד ארבע (יורדת לאילת)
6.3 חופש
7.3 משמרת מוצ״ש (חוזרת באותו יום)
8.3 משמרת ערב
31.3 משמרת ערב
1-4.4 לרדת הביתה לחג""")

    await send_message("""אילוצים של שחר:
6.3 לא לעבוד
7.3 לא לעבוד
13.3 לעבוד
ימי שני רביעי וחמישי לימודים לא לעבוד""")

    await send_message("""אילוצים של שקד:
חופש עד ה-11.3 לא לעבוד
24.3 לא לעבוד""")

    await send_message("""אילוצים של שני:
1.3 ערב
3.3 בוקר
4.3 בוקר 
6.3 שישי
טיסה מה-8 עד 13.3 לא לעבוד 
14.3 מוצש
15.3 ערב 
17.3 בוקר/אמצע 
18.3 בוקר 
20.3 שישי 
22.3 ערב
24.3 בוקר 
25.3 אמצע
28.3 מוצש""")

    await send_message("""אילוצים של עומר:
פעמיים באמצע שבוע
ומוצ״ש כל החודש""")

    await send_message("מה הסטטוס? יש לך את כל מה שצריך?")

    await send_message("כן, אפשר ליצור את הסידור")

    print("\n" + "=" * 70)
    print("Conversation Summary")
    print("=" * 70)
    print(f"  Total messages: {len(conversation_log)}")
    print(f"  User messages: {len([m for m in conversation_log if m['role'] == 'user'])}")
    print(f"  Agent responses: {len([m for m in conversation_log if m['role'] == 'assistant'])}")

    return {
        "shift_plan_id": shift_plan_id,
        "manager_id": manager_id,
        "conversation": conversation_log,
        "chat_history_length": len(chat_history),
    }


async def main() -> None:
    """Run the March plan test."""
    result = await run_march_plan_test()

    print("\n" + "=" * 70)
    print("Test completed!")
    print(f"Shift Plan ID: {result['shift_plan_id']}")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
