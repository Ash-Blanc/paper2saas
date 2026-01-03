from agno.os import AgentOS

from paper2saas import (
    paper_analyzer,
    market_researcher,
    idea_generator,
    validation_researcher,
    strategic_advisor,
    report_generator,
    paper2saas_team,
    idea_roaster_team,  # New roast team
)

paper2saas_os = AgentOS(
    name="paper2saas-os",
    description="Turns academic papers into battle-tested SaaS opportunities",
    agents=[
        paper_analyzer,
        market_researcher,
        idea_generator,
        validation_researcher,
        strategic_advisor,
        report_generator,
    ],
    teams=[
        paper2saas_team,     # Main flow
        idea_roaster_team,   # Brutal critique
    ],
)

app = paper2saas_os.get_app()

if __name__ == "__main__":
    paper2saas_os.serve(app="__main__:app", reload=True)