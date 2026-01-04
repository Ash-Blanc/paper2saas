from agno.agent import Agent
from agno.tools.reasoning import ReasoningTools

from paper2saas_app.config import AgentConfig
from paper2saas_app.prompts.agents import FACT_CHECKER_INSTRUCTIONS

fact_checker = Agent(
    name="FactChecker",
    model=AgentConfig.FACT_CHECKER_MODEL,
    tools=[ReasoningTools(add_instructions=True)],
    reasoning_min_steps=1,
    reasoning_max_steps=3,
    stream_intermediate_steps=False,
    instructions=FACT_CHECKER_INSTRUCTIONS,
    markdown=True,
)
