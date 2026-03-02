"""Constraint Analyzer agent: parses natural language constraints into structured format."""

from collections.abc import Awaitable, Callable

from app.agents.base_agent import BaseToolCallingAgent
from app.consts.models import ModelConsts
from app.dal import get_session
from app.prompts.constraint_analyzer_prompts import CONSTRAINT_ANALYZER_SYSTEM_PROMPT
from app.tools.constraint_tools import ConstraintTools
from app.tools.log_tools import LogTools


class ConstraintAnalyzerAgent(BaseToolCallingAgent):
    """Agent that parses natural language constraints into structured format."""

    def __init__(
        self,
        shift_plan_id: int,
        manager_id: int,
        model_name: str = ModelConsts.CLAUDE_SONNET_4_5,
        status_callback: Callable[[str], Awaitable[None]] | None = None,
        log_file_path: str | None = None,
    ):
        self.shift_plan_id = shift_plan_id
        self.manager_id = manager_id

        # Create tools
        log_tools = LogTools(log_file_path=log_file_path)
        constraint_tools = ConstraintTools(
            shift_plan_id=shift_plan_id,
            manager_id=manager_id,
            db_session_factory=get_session,
        )

        tools = log_tools.get_tools() + constraint_tools.get_tools()

        super().__init__(
            agent_name="ConstraintAnalyzer",
            tools=tools,
            system_prompt=CONSTRAINT_ANALYZER_SYSTEM_PROMPT,
            model_name=model_name,
            status_callback=status_callback,
            max_iterations=15,
        )
