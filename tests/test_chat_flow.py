"""Chat flow test - tests the conversational planning agent."""

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


async def run_chat_flow(template_path: str | None = None) -> dict:
    """
    Run a simulated conversation with the planning chat agent.

    This demonstrates the conversational flow:
    1. Greeting and asking about the week
    2. Adding employees
    3. Setting constraints
    4. Creating the plan

    Args:
        template_path: Optional path to Excel template

    Returns:
        Dict with conversation history and final result
    """
    print("=" * 70)
    print("NesPrep - Chat Flow Test")
    print("=" * 70)
    print()

    Base.metadata.create_all(bind=engine)

    print("[Setup] Creating test data...")
    db = get_session()
    try:
        manager = Manager.get_by_email(db, "chat_test@example.com")
        if not manager:
            manager = Manager.create(
                db, "chat_test@example.com", "hashed_password", "Chat Test Manager"
            )
        manager_id = manager.id

        week_start = date(2026, 2, 1)
        shift_plan = ShiftPlan.create(
            db,
            manager_id=manager_id,
            week_start=week_start,
            title=f"Chat Test Plan {week_start.isoformat()}",
            template_path=template_path,
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
        print(f"\n[User]: {user_message}")
        print("\n[Agent thinking...]")

        response = await agent.run(user_message, chat_history)

        chat_history.append(HumanMessage(content=user_message))
        chat_history.append(AIMessage(content=response))

        conversation_log.append({"role": "user", "content": user_message})
        conversation_log.append({"role": "assistant", "content": response})

        print(f"\n[Agent]: {response}")
        return response

    print("\n" + "=" * 70)
    print("Starting Conversation")
    print("=" * 70)

    await send_message("היי, אני רוצה לתכנן את השבוע של 1-7 בפברואר")

    await send_message("העובדים שלי הם: שקד, דניאל, תהל, שחר, עומר")

    await send_message(
        "שקד יכולה לעבוד רק בימים א-ג. "
        "דניאל לא יכול בשישי. "
        "תהל מעדיפה בוקר."
    )

    await send_message("שחר ועומר זמינים כל השבוע")

    await send_message("מה הסטטוס? יש לך את כל מה שצריך?")

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
    """Run the chat flow test."""
    import sys

    template_path = None
    if len(sys.argv) >= 2:
        template_path = sys.argv[1]
        print(f"Using template: {template_path}")

    result = await run_chat_flow(template_path)

    print("\n" + "=" * 70)
    print("Test completed!")
    print(f"Shift Plan ID: {result['shift_plan_id']}")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
