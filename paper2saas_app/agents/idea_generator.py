from agno.agent import Agent
from agno.tools.reasoning import ReasoningTools

from paper2saas_app.config import AgentConfig
from paper2saas_app.models_config import get_model, get_small_model
from paper2saas_app.models import IdeaGeneratorOutput
from paper2saas_app.prompts.agents import IDEA_GENERATOR_INSTRUCTIONS

idea_generator = Agent(
    name="IdeaGenerator",
    model=get_model(AgentConfig.SMALL_MODEL, get_small_model),
    tools=[ReasoningTools(add_instructions=True, enable_think=False, enable_analyze=False)],
    reasoning=False,
    reasoning_min_steps=3,
    reasoning_max_steps=10,
    output_schema=IdeaGeneratorOutput,
    instructions=IDEA_GENERATOR_INSTRUCTIONS,
    markdown=True,
)
