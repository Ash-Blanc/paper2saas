from paper2saas_app.utils import get_mistral_model
from agno.agent import Agent

from paper2saas_app.config import AgentConfig
from paper2saas_app.prompts.agents import STRATEGIC_ADVISOR_INSTRUCTIONS

strategic_advisor = Agent(
    name="StrategicAdvisor",
    model=get_mistral_model(AgentConfig.STRATEGIC_ADVISOR_MODEL),
    
    
    stream_intermediate_steps=False,
    instructions=STRATEGIC_ADVISOR_INSTRUCTIONS,
    markdown=True,
)
