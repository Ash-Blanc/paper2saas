from agno.os import AgentOS

from paper2saas import (
    paper_analyzer,
    market_researcher,
    idea_generator,
    validation_researcher,
    strategic_advisor,
    report_generator,
    paper2saas_team,
)

paper2saas_os = AgentOS(
    name="paper2saas-os",
    description="Transforms academic papers into validated SaaS opportunities",
    agents=[
        paper_analyzer,
        market_researcher,
        idea_generator,
        validation_researcher,
        strategic_advisor,
        report_generator,
    ],
    teams=[paper2saas_team],
)

app = paper2saas_os.get_app()

if __name__ == "__main__":
    paper2saas_os.serve(app="__main__:app", reload=True)