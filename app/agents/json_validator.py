"""JSON Validator agent: validates shift plan JSON against constraints using AI."""

import json
from collections.abc import Awaitable, Callable

from langchain_core.prompts import ChatPromptTemplate

from app.agents.base_agent import BaseAgent
from app.consts.models import ModelConsts


JSON_VALIDATOR_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a shift plan validator. Analyze the week plan JSON and constraints to find issues.

# VALIDATION RULES

1. **Coverage**: Each day MUST have exactly 2 morning, 2 middle, 1 night
2. **Unavailability**: Employees MUST NOT be assigned to days in their unavailable_days
3. **Availability**: If availability_days is set, employees can ONLY work those days
4. **Max shifts**: Employees MUST NOT exceed their max_shifts_per_week
5. **Balance**: Shifts should be distributed fairly (warn if imbalanced)

# OUTPUT FORMAT

Return ONLY valid JSON in this exact format:

If valid:
{{"valid": true}}

If invalid:
{{"valid": false, "errors": ["error 1", "error 2"], "suggestions": ["fix 1", "fix 2"]}}

Do NOT include any text outside the JSON. No explanations, no markdown."""),
    ("human", """Week Plan:
{week_json}

Employee Constraints:
{constraints_json}

Validate and return JSON result:""")
])


class JsonValidatorAgent(BaseAgent):
    """Agent that validates shift plan JSON against constraints using AI reasoning."""

    def __init__(
        self,
        model_name: str = ModelConsts.CLAUDE_SONNET_4_5,
        status_callback: Callable[[str], Awaitable[None]] | None = None,
    ):
        super().__init__(
            agent_name="JsonValidator",
            model_name=model_name,
            status_callback=status_callback,
        )

    async def validate(
        self,
        week_data: dict,
        constraints: dict,
    ) -> dict:
        """Validate a week plan against constraints.

        Args:
            week_data: Parsed week plan dictionary
            constraints: Employee constraints dictionary

        Returns:
            Validation result: {"valid": true} or {"valid": false, "errors": [...], "suggestions": [...]}
        """
        await self.emit_status("Validating week plan with AI...")

        week_json = json.dumps(week_data, ensure_ascii=False, indent=2)
        constraints_json = json.dumps(constraints, ensure_ascii=False, indent=2)

        response = await self.send_prompt(
            JSON_VALIDATOR_PROMPT,
            week_json=week_json,
            constraints_json=constraints_json,
        )

        # Parse the AI response as JSON
        try:
            # Strip any markdown formatting the AI might have added
            clean_response = response.strip()
            if clean_response.startswith("```"):
                clean_response = clean_response.split("```")[1]
                if clean_response.startswith("json"):
                    clean_response = clean_response[4:]
                clean_response = clean_response.strip()

            result = json.loads(clean_response)
            return result
        except json.JSONDecodeError:
            # If AI response isn't valid JSON, treat as error
            return {
                "valid": False,
                "errors": [f"Validator returned invalid JSON: {response[:200]}"],
                "suggestions": ["Internal error - please retry"],
            }
