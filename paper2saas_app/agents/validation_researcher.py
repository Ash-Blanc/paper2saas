from paper2saas_app.utils import get_mistral_model
from agno.agent import Agent
from agno.tools.firecrawl import FirecrawlTools
from agno.tools.hackernews import HackerNewsTools
from agno.tools.website import WebsiteTools
from agno.tools.baidusearch import BaiduSearchTools

from paper2saas_app.config import AgentConfig
from paper2saas_app.prompts.agents import VALIDATION_RESEARCHER_INSTRUCTIONS
from paper2saas_app.utils import shared_db

validation_researcher = Agent(
    name="ValidationResearcher",
    model=get_mistral_model(AgentConfig.VALIDATION_RESEARCHER_MODEL),
    tools=[
        FirecrawlTools(enable_search=True, enable_scrape=True),
        WebsiteTools(),
        BaiduSearchTools(),
        HackerNewsTools(),
    ],
    db=shared_db,
    
    
    stream_intermediate_steps=False,
    instructions=VALIDATION_RESEARCHER_INSTRUCTIONS,
    markdown=True,
)
