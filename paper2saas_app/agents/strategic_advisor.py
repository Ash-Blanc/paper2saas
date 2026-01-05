from paper2saas_app.utils import get_mistral_model
from agno.agent import Agent
from agno.tools.reasoning import ReasoningTools

from paper2saas_app.config import AgentConfig
from paper2saas_app.prompts.agents import STRATEGIC_ADVISOR_INSTRUCTIONS
from paper2saas_app.utils import shared_db

strategic_advisor = Agent(
    name="StrategicAdvisor",
    model=get_mistral_model(AgentConfig.STRATEGIC_ADVISOR_MODEL),
    tools=[ReasoningTools()],
    db=shared_db,
    # reasoning=True,
    
    
    stream_intermediate_steps=False,
    instructions=STRATEGIC_ADVISOR_INSTRUCTIONS,
    markdown=True,
)
