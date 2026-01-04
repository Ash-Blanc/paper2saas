from agno.agent import Agent
from agno.tools.reasoning import ReasoningTools

from paper2saas_app.config import AgentConfig
from paper2saas_app.prompts.agents import STRATEGIC_ADVISOR_INSTRUCTIONS

strategic_advisor = Agent(
    name="StrategicAdvisor",
    model=AgentConfig.STRATEGIC_ADVISOR_MODEL,
    tools=[ReasoningTools(add_instructions=True)],
    reasoning_min_steps=2,
    reasoning_max_steps=6,
    stream_intermediate_steps=False,
    instructions=STRATEGIC_ADVISOR_INSTRUCTIONS,
    markdown=True,
)
