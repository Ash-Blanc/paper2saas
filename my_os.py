from agno.os import AgentOS

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

p2s_os = AgentOS(
    name="p2s-os",
    description="Turns academic papers into battle-tested SaaS opportunities",
    agents=[
        paper_analyzer,
        market_researcher,
        idea_generator,
        validation_researcher,
        strategic_advisor,
        report_generator,
        product_engineer,
        fact_checker,
        devils_advocate,
        market_skeptic
    ],
    teams=[
        paper2saas_team,     # Main flow
        idea_roaster_team,   # Brutal critique
    ],
    tracing=False,
)

app = p2s_os.get_app()

if __name__ == "__main__":
    p2s_os.serve(app="__main__:app", reload=True)
