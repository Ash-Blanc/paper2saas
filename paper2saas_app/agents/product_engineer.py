from agno.agent import Agent
from agno.tools.firecrawl import FirecrawlTools
from agno.tools.website import WebsiteTools
from agno.tools.baidusearch import BaiduSearchTools
from agno.tools.hackernews import HackerNewsTools
from agno.tools.reasoning import ReasoningTools

from paper2saas_app.config import AgentConfig
from paper2saas_app.models_config import get_model, get_large_model
from paper2saas_app.models import ProductEngineerOutput
from paper2saas_app.prompts.agents import PRODUCT_ENGINEER_INSTRUCTIONS

product_engineer = Agent(
    name="ProductEngineer",
    model=get_large_model(),  # ProductEngineer uses LARGE_MODEL by default
    tools=[
        FirecrawlTools(enable_search=True, enable_scrape=True),
        WebsiteTools(),
        BaiduSearchTools(),
        HackerNewsTools(),
        ReasoningTools(add_instructions=True),
    ],
    reasoning_min_steps=3,
    reasoning_max_steps=10,
    stream_intermediate_steps=False,
    output_schema=ProductEngineerOutput,
    instructions=PRODUCT_ENGINEER_INSTRUCTIONS,
    markdown=True,
)
