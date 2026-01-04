from agno.agent import Agent
from paper2saas_app.config import AgentConfig
from paper2saas_app.prompts.agents import REPORT_GENERATOR_INSTRUCTIONS

report_generator = Agent(
    name="ReportGenerator",
    model=AgentConfig.LARGE_MODEL,
    reasoning_min_steps=1,
    reasoning_max_steps=4,
    stream_intermediate_steps=False,
    instructions=REPORT_GENERATOR_INSTRUCTIONS,
    markdown=True,
)
