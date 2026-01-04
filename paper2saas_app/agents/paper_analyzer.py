from agno.agent import Agent
from agno.tools.reasoning import ReasoningTools
from agno.tools.arxiv import ArxivTools
from agno.tools.website import WebsiteTools
from agno.tools.firecrawl import FirecrawlTools
from agno.tools.baidusearch import BaiduSearchTools

from paper2saas_app.config import AgentConfig
from paper2saas_app.models import PaperAnalysisOutput
from paper2saas_app.prompts.agents import PAPER_ANALYZER_INSTRUCTIONS

paper_analyzer = Agent(
    name="PaperAnalyzer",
    model=AgentConfig.LARGE_MODEL,
    tools=[
        ArxivTools(),
        FirecrawlTools(enable_search=True, enable_scrape=True),
        WebsiteTools(),
        BaiduSearchTools(),
        ReasoningTools(add_instructions=True, enable_think=False, enable_analyze=False),
    ],
    reasoning=True,
    reasoning_min_steps=AgentConfig.REASONING_MIN_STEPS,
    reasoning_max_steps=AgentConfig.REASONING_MAX_STEPS,
    output_schema=PaperAnalysisOutput,
    stream_intermediate_steps=False,
    instructions=PAPER_ANALYZER_INSTRUCTIONS,
    markdown=True,
)
