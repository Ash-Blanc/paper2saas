from agno.team import Team

from paper2saas_app.config import AgentConfig
from paper2saas_app.utils import shared_db, logger, run_team_with_error_handling, validate_arxiv_id
from paper2saas_app.prompts.agents import PAPER2SAAS_TEAM_INSTRUCTIONS

# Import agents
from paper2saas_app.agents.paper_analyzer import paper_analyzer
from paper2saas_app.agents.market_researcher import market_researcher
from paper2saas_app.agents.idea_generator import idea_generator
from paper2saas_app.agents.validation_researcher import validation_researcher
from paper2saas_app.agents.strategic_advisor import strategic_advisor
from paper2saas_app.agents.fact_checker import fact_checker
from paper2saas_app.agents.product_engineer import product_engineer
from paper2saas_app.agents.report_generator import report_generator

paper2saas_team = Team(
    name="Paper2SaaS",
    role="Transform arXiv papers into validated SaaS opportunities with evidence-based analysis",
    model="mistral:mistral-large-latest",
    stream_intermediate_steps=False,
    instructions=PAPER2SAAS_TEAM_INSTRUCTIONS,
    members=[
        paper_analyzer,
        market_researcher,
        fact_checker,
        idea_generator,
        validation_researcher,
        strategic_advisor,
        product_engineer,
        report_generator,
    ],
    db=shared_db,
    store_events=AgentConfig.STORE_EVENTS,
    markdown=AgentConfig.ENABLE_MARKDOWN,
    show_members_responses=AgentConfig.SHOW_MEMBER_RESPONSES,
    add_datetime_to_context=True,
)
logger.info("Initialized paper2saas_team with 8 agents (including ProductEngineer)")

def run_paper2saas(arxiv_id: str) -> dict:
    """
    Execute paper2saas_team with comprehensive error handling
    
    Args:
        arxiv_id: The arXiv paper ID to analyze
        
    Returns:
        dict with status, result/error, and metadata
    """
    # Validate input
    if not validate_arxiv_id(arxiv_id):
        logger.error(f"Invalid arXiv ID format: {arxiv_id}")
        return {
            "status": "error",
            "error": f"Invalid arXiv ID format: {arxiv_id}. Expected format: YYMM.NNNNN or YYMM.NNNNNvN",
            "arxiv_id": arxiv_id
        }
    
    result = run_team_with_error_handling(
        team=paper2saas_team,
        input_text=f"Analyze arXiv paper {arxiv_id} and generate SaaS opportunities",
        log_start_msg=f"Starting paper2saas analysis for arXiv ID: {arxiv_id}",
        log_success_msg=f"Successfully completed analysis for {arxiv_id}"
    )
    
    # Add arxiv_id to result
    result["arxiv_id"] = arxiv_id
    return result
