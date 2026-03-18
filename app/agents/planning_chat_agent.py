"""Planning Chat Agent: conversational agent for shift planning."""

from collections.abc import Awaitable, Callable
from datetime import date

from app.agents.base_agent import BaseToolCallingAgent
from app.consts.models import ModelConsts
from app.prompts.planning_chat_prompts import PLANNING_CHAT_SYSTEM_PROMPT
from app.tools.log_tools import LogTools
from app.tools.planning_chat_tools import PlanningChatTools

HEBREW_DAYS = ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת"]


class PlanningChatAgent(BaseToolCallingAgent):
    """Conversational agent for shift planning.

    This agent handles natural conversation with managers, gathering information
    about employees and constraints, and triggering the planning pipeline when ready.
    """

    def __init__(
        self,
        shift_plan_id: int,
        manager_id: int,
        status_callback: Callable[[str], Awaitable[None]] | None = None,
        plan_callback: Callable[[list[dict]], Awaitable[None]] | None = None,
        model_name: str = ModelConsts.CLAUDE_SONNET_4_5,
    ):
        log_tools = LogTools()
        planning_tools = PlanningChatTools(
            shift_plan_id=shift_plan_id,
            manager_id=manager_id,
            status_callback=status_callback,
            plan_callback=plan_callback,
        )

        tools = log_tools.get_tools() + planning_tools.get_tools()

        today = date.today()
        day_index = (today.weekday() + 1) % 7
        formatted_prompt = PLANNING_CHAT_SYSTEM_PROMPT.format(
            current_date=today.strftime("%d/%m/%Y"),
            current_year=today.year,
            current_day_hebrew=HEBREW_DAYS[day_index],
        )

        super().__init__(
            agent_name="PlanningChatAgent",
            tools=tools,
            system_prompt=formatted_prompt,
            model_name=model_name,
            status_callback=status_callback,
            max_iterations=50,
        )

        self.shift_plan_id = shift_plan_id
        self.manager_id = manager_id
