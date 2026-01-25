from app.utils import get_mistral_model
from agno.agent import Agent
from agno.tools.hackernews import HackerNewsTools
from agno.tools.website import WebsiteTools
from agno.tools.baidusearch import BaiduSearchTools
from agno.tools.firecrawl import FirecrawlTools

from app.config import AgentConfig
from app.prompts.agents import MARKET_SKEPTIC_INSTRUCTIONS

market_skeptic = Agent(
    name="MarketSkeptic",
    model=get_mistral_model(AgentConfig.MARKET_SKEPTIC_MODEL),
    tools=[
        HackerNewsTools(),
        WebsiteTools(),
        BaiduSearchTools(),
        FirecrawlTools(enable_search=True, enable_scrape=True),
    ],
    # 
    
    
    stream_intermediate_steps=False,
    instructions=MARKET_SKEPTIC_INSTRUCTIONS,
    markdown=True,
)
