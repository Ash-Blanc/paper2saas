from paper2saas_app.utils import get_mistral_model
from agno.agent import Agent
from paper2saas_app.config import AgentConfig
from paper2saas_app.prompts.agents import REPORT_GENERATOR_INSTRUCTIONS
from paper2saas_app.utils import shared_db

report_generator = Agent(
    name="ReportGenerator",
    model=get_mistral_model(AgentConfig.LARGE_MODEL),
    db=shared_db,
    
    
    stream_intermediate_steps=False,
    instructions=REPORT_GENERATOR_INSTRUCTIONS,
    markdown=True,
)
