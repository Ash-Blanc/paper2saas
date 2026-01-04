from paper2saas_app.utils import get_mistral_model
from agno.agent import Agent
from agno.tools.firecrawl import FirecrawlTools
from agno.tools.website import WebsiteTools

from paper2saas_app.config import AgentConfig
from paper2saas_app.prompts.agents import DEVILS_ADVOCATE_INSTRUCTIONS

devils_advocate = Agent(
    name="DevilsAdvocate",
    model=get_mistral_model(AgentConfig.DEVILS_ADVOCATE_MODEL),
    tools=[
        FirecrawlTools(enable_search=True, enable_scrape=True),
        WebsiteTools(),
    ],
    # 
    
    
    stream_intermediate_steps=False,
    instructions=DEVILS_ADVOCATE_INSTRUCTIONS,
    markdown=True,
)
