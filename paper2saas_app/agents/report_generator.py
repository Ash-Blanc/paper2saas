from agno.agent import Agent
from paper2saas_app.config import AgentConfig
from paper2saas_app.models_config import get_model, get_large_model
from paper2saas_app.prompts.agents import REPORT_GENERATOR_INSTRUCTIONS

report_generator = Agent(
    name="ReportGenerator",
    model=get_large_model(),
    reasoning_min_steps=1,
    reasoning_max_steps=4,
    stream_intermediate_steps=False,
    instructions=REPORT_GENERATOR_INSTRUCTIONS,
    markdown=True,
)
