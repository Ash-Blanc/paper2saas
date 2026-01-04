from agno.agent import Agent
from agno.tools.hackernews import HackerNewsTools
from agno.tools.website import WebsiteTools
from agno.tools.baidusearch import BaiduSearchTools
from agno.tools.firecrawl import FirecrawlTools

from paper2saas_app.config import AgentConfig
from paper2saas_app.models_config import get_model, get_small_model
from paper2saas_app.models import MarketResearchOutput
from paper2saas_app.prompts.agents import MARKET_RESEARCHER_INSTRUCTIONS

market_researcher = Agent(
    name="MarketResearcher",
    model=get_model(AgentConfig.MARKET_RESEARCHER_MODEL, get_small_model),
    tools=[
        HackerNewsTools(),
        WebsiteTools(),
        BaiduSearchTools(),
        FirecrawlTools(enable_search=True, enable_scrape=True),
    ],
    reasoning_min_steps=1,
    reasoning_max_steps=5,
    output_schema=MarketResearchOutput,
    stream_intermediate_steps=False,
    instructions=MARKET_RESEARCHER_INSTRUCTIONS,
    markdown=True,
)
