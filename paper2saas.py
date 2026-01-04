# Facade for backward compatibility
from paper2saas_app.config import AgentConfig
from paper2saas_app.utils import validate_arxiv_id
from paper2saas_app.teams.paper2saas import run_paper2saas as run_paper2saas_with_error_handling
from paper2saas_app.teams.roaster import run_idea_roaster as run_idea_roaster_with_error_handling

# Re-export agents if needed, but primarily used for the helper functions
# If scripts import agents directly from here, I should add them too.
from paper2saas_app.agents.paper_analyzer import paper_analyzer
from paper2saas_app.agents.market_researcher import market_researcher
from paper2saas_app.agents.idea_generator import idea_generator
from paper2saas_app.agents.validation_researcher import validation_researcher
from paper2saas_app.agents.strategic_advisor import strategic_advisor
from paper2saas_app.agents.report_generator import report_generator
from paper2saas_app.agents.product_engineer import product_engineer
from paper2saas_app.agents.fact_checker import fact_checker
from paper2saas_app.agents.devils_advocate import devils_advocate
from paper2saas_app.agents.market_skeptic import market_skeptic
from paper2saas_app.teams.paper2saas import paper2saas_team
from paper2saas_app.teams.roaster import idea_roaster_team
