from app.utils import get_mistral_model
from agno.agent import Agent
from agno.tools.reasoning import ReasoningTools
from agno.tools.arxiv import ArxivTools
from agno.tools.website import WebsiteTools
from agno.tools.firecrawl import FirecrawlTools
from agno.tools.baidusearch import BaiduSearchTools

from app.config import AgentConfig
from app.models import PaperAnalysisOutput
from app.prompts.agents import PAPER_ANALYZER_INSTRUCTIONS
from app.utils import shared_db

paper_analyzer = Agent(
    name="PaperAnalyzer",
    model=get_mistral_model(AgentConfig.LARGE_MODEL),
    tools=[
        ArxivTools(),
        FirecrawlTools(enable_search=True, enable_scrape=True),
        WebsiteTools(),
        BaiduSearchTools(),
        # ReasoningTools(add_instructions=True),
    ],
    db=shared_db,
    reasoning=False,
    # reasoning_max_steps=AgentConfig.REASONING_MAX_STEPS,
    # output_schema=PaperAnalysisOutput,
    stream_intermediate_steps=False,
    instructions=PAPER_ANALYZER_INSTRUCTIONS,
    markdown=True,
    tool_call_limit=4,
)
