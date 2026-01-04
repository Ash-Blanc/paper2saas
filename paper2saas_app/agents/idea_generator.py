from paper2saas_app.utils import get_mistral_model
from agno.agent import Agent

from paper2saas_app.config import AgentConfig
from paper2saas_app.models import IdeaGeneratorOutput
from paper2saas_app.prompts.agents import IDEA_GENERATOR_INSTRUCTIONS

idea_generator = Agent(
    name="IdeaGenerator",
    model=get_mistral_model(AgentConfig.SMALL_MODEL),
    tools=[],
    output_schema=IdeaGeneratorOutput,
    instructions=IDEA_GENERATOR_INSTRUCTIONS,
    markdown=True,
)
