from paper2saas_app.utils import get_mistral_model
from agno.agent import Agent
from agno.tools.firecrawl import FirecrawlTools
from agno.tools.website import WebsiteTools
from agno.tools.baidusearch import BaiduSearchTools
from agno.tools.hackernews import HackerNewsTools

from paper2saas_app.config import AgentConfig
from paper2saas_app.models import ProductEngineerOutput
from paper2saas_app.prompts.agents import PRODUCT_ENGINEER_INSTRUCTIONS

product_engineer = Agent(
    name="ProductEngineer",
    model=get_mistral_model(AgentConfig.LARGE_MODEL),
    tools=[
        FirecrawlTools(enable_search=True, enable_scrape=True),
        WebsiteTools(),
        BaiduSearchTools(),
        HackerNewsTools(),
    ],
    
    
    stream_intermediate_steps=False,
    output_schema=ProductEngineerOutput,
    instructions=PRODUCT_ENGINEER_INSTRUCTIONS,
    markdown=True,
)
