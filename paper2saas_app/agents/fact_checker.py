from paper2saas_app.utils import get_mistral_model
from agno.agent import Agent

from paper2saas_app.config import AgentConfig
from paper2saas_app.prompts.agents import FACT_CHECKER_INSTRUCTIONS
from paper2saas_app.utils import shared_db

fact_checker = Agent(
    name="FactChecker",
    model=get_mistral_model(AgentConfig.FACT_CHECKER_MODEL),
    tools=[],
    db=shared_db,
    stream_intermediate_steps=False,
    instructions=FACT_CHECKER_INSTRUCTIONS,
    markdown=True,
)
