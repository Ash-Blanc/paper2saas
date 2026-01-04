from paper2saas_app.utils import get_mistral_model
from agno.agent import Agent
from agno.tools.hackernews import HackerNewsTools
from agno.tools.website import WebsiteTools
from agno.tools.baidusearch import BaiduSearchTools
from agno.tools.firecrawl import FirecrawlTools

from paper2saas_app.config import AgentConfig
from paper2saas_app.models import MarketResearchOutput
from paper2saas_app.prompts.agents import MARKET_RESEARCHER_INSTRUCTIONS

market_researcher = Agent(
    name="MarketResearcher",
    model=get_mistral_model(AgentConfig.MARKET_RESEARCHER_MODEL),
    tools=[
        HackerNewsTools(),
        WebsiteTools(),
        BaiduSearchTools(),
        FirecrawlTools(enable_search=True, enable_scrape=True),
    ],
    output_schema=MarketResearchOutput,
    stream_intermediate_steps=False,
    instructions=MARKET_RESEARCHER_INSTRUCTIONS,
    markdown=True,
)
