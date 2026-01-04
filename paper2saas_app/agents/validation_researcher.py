from agno.agent import Agent
from agno.tools.firecrawl import FirecrawlTools
from agno.tools.hackernews import HackerNewsTools
from agno.tools.website import WebsiteTools
from agno.tools.baidusearch import BaiduSearchTools

from paper2saas_app.config import AgentConfig
from paper2saas_app.prompts.agents import VALIDATION_RESEARCHER_INSTRUCTIONS

validation_researcher = Agent(
    name="ValidationResearcher",
    model=AgentConfig.VALIDATION_RESEARCHER_MODEL,
    tools=[
        FirecrawlTools(enable_search=True, enable_scrape=True),
        HackerNewsTools(),
        WebsiteTools(),
        BaiduSearchTools(),
    ],
    reasoning_min_steps=2,
    reasoning_max_steps=8,
    stream_intermediate_steps=False,
    instructions=VALIDATION_RESEARCHER_INSTRUCTIONS,
    markdown=True,
)
