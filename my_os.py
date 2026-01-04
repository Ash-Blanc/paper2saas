from agno.os import AgentOS

from paper2saas import (
    paper_analyzer,
    market_researcher,
    idea_generator,
    validation_researcher,
    strategic_advisor,
    report_generator,
    product_engineer,
    fact_checker,
    devils_advocate,
    market_skeptic,
    paper2saas_team,
    idea_roaster_team,
)

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