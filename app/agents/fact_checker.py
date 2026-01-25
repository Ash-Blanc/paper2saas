from app.utils import get_mistral_model
from agno.agent import Agent

from app.config import AgentConfig
from app.prompts.agents import FACT_CHECKER_INSTRUCTIONS
from app.utils import shared_db

fact_checker = Agent(
    name="FactChecker",
    model=get_mistral_model(AgentConfig.FACT_CHECKER_MODEL),
    tools=[],
    db=shared_db,
    stream_intermediate_steps=False,
    instructions=FACT_CHECKER_INSTRUCTIONS,
    markdown=True,
)
