import re
from agno.os import AgentOS
from agno.db.sqlite import AsyncSqliteDb
from agno.workflow import Workflow, Step, Parallel
from agno.workflow.types import StepInput, StepOutput

from paper2saas import (
    Paper2SaaSInput,
    create_paper_analyzer,
    market_researcher,
    idea_generator,
    validation_researcher,
    strategic_advisor,
    report_generator,
    combine_research,
    prepare_validation_context,
    filter_recommendations,
    workflow_agent,
)

# Preprocessing step to extract arxiv_id from user message
def extract_arxiv_id(step_input: StepInput) -> StepOutput:
    """Extract arxiv_id from user input (message or structured input)."""
    user_input = step_input.input
    
    # Handle structured input (dict with arxiv_id)
    if isinstance(user_input, dict) and "arxiv_id" in user_input:
        arxiv_id = user_input["arxiv_id"]
        additional_context = user_input.get("additional_context", "")
    # Handle string input (extract arxiv_id pattern)
    elif isinstance(user_input, str):
        # Match arxiv patterns like "2512.24991v1" or "2401.00001"
        match = re.search(r'(\d{4}\.\d{4,5}(?:v\d+)?)', user_input)
        arxiv_id = match.group(1) if match else user_input.strip()
        additional_context = user_input
    else:
        arxiv_id = str(user_input)
        additional_context = ""
    
    return StepOutput(
        step_name="extract_arxiv",
        content=f"Analyzing ArXiv paper: {arxiv_id}\nContext: {additional_context}",
        success=True,
        # Store arxiv_id for subsequent steps
        metadata={"arxiv_id": arxiv_id}
    )

# Dynamic paper analyzer step
def run_paper_analysis(step_input: StepInput) -> StepOutput:
    """Run paper analysis with extracted arxiv_id."""
    arxiv_id = step_input.get_step_metadata("extract_arxiv", {}).get("arxiv_id", "")
    analyzer = create_paper_analyzer(arxiv_id)
    response = analyzer.run(f"Analyze paper {arxiv_id}")
    
    return StepOutput(
        step_name="analyze_paper",
        content=response.content,
        success=True
    )

paper2saas_os = AgentOS(
    name="paper2saas-os",
    description="An intelligent system that transforms academic papers into validated SaaS opportunities",
    agents=[
        create_paper_analyzer("{arxiv_id}"),
        market_researcher,
        idea_generator,
        validation_researcher,
        strategic_advisor,
        report_generator,
    ],
    workflows=[paper2saas_workflow],
)

app = paper2saas_os.get_app()

if __name__ == "__main__":
    paper2saas_os.serve(app="my_os:app", reload=True)