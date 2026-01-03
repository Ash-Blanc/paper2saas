# paper2saas_agent_fixed_v2.py
import os
# from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Agno SDK Imports
from agno.workflow.types import StepInput, StepOutput
# from agno.run.workflow import WorkflowRunOutput
from agno.agent import Agent
from agno.tools.reasoning import ReasoningTools
from agno.tools.workflow import WorkflowTools

load_dotenv()

# Environment setup
os.environ["FIRECRAWL_API_KEY"] = os.getenv("FIRECRAWL_API_KEY", "")
os.environ["MISTRAL_API_KEY"] = os.getenv("MISTRAL_API_KEY")

# --- INPUT SCHEMA ---
class Paper2SaaSInput(BaseModel):
    """Input schema for the Paper2SaaS workflow."""
    arxiv_id: str = Field(..., description="The arXiv paper ID to analyze (e.g., '2401.00001')")

# Tool Imports
from agno.tools.arxiv import ArxivTools
from agno.tools.hackernews import HackerNewsTools
from agno.tools.website import WebsiteTools
from agno.tools.firecrawl import FirecrawlTools
from agno.tools.baidusearch import BaiduSearchTools

# 1. Paper Analyzer - Fixed to use specific arxiv_id
paper_analyzer = Agent(
        name="PaperAnalyzer",
        model="mistral:mistral-large-latest",
        tools=[ArxivTools(), ReasoningTools(add_instructions=True)],
        instructions=f"""
        You are an expert AI researcher. Your ONLY task is to analyze the paper with a given ArXiv ID
        
        CRITICAL: You MUST use ArxivTools.search_arxiv() with the appropriate query to fetch THE SPECIFIC paper.
        Do NOT hallucinate or analyze any other paper.
        
        Steps:
        1. Use ArxivTools to search for arxiv_id
        2. Read and analyze the actual paper content
        3. Provide a structured analysis with:
           
           ## Paper Title & ID
           - Title: [Actual title from the fetched paper]
           - ArXiv ID: [provided arxiv_id]
           - Authors: [List authors]
           
           ## Executive Summary
           [2-3 sentences about what this paper actually does]
           
           ## Core Technical Innovations
           - [Innovation 1 from the paper]
           - [Innovation 2 from the paper]
           - [Innovation 3 from the paper]
           
           ## Technical Architecture
           [Key technical details and methods]
           
           ## Limitations & Constraints
           - [Limitation 1]
           - [Limitation 2]
           
           ## Potential Real-World Applications
           - [Application 1]
           - [Application 2]
           - [Application 3]
           
           ## Key Results/Metrics
           [Performance metrics if available]
        
        Remember: ONLY analyze paper with given arxiv id. If you cannot find it, report that clearly.
        """,
        markdown=True,
    )

# 2. Market Researcher - Without DuckDuckGo to avoid errors
market_researcher = Agent(
    name="MarketResearcher", 
    model="mistral:mistral-small-latest",
    tools=[
        HackerNewsTools(),
        WebsiteTools(),
        BaiduSearchTools(),
    ],
    instructions="""
    You are a market research expert focusing on AI/ML/SaaS markets.
    
    Your tasks:
    1. Search HackerNews for recent discussions about:
       - AI tool needs and frustrations
       - Fine-tuning challenges
       - Model deployment issues
       - Data annotation problems
       - ML infrastructure pain points
    
    2. Look for:
       - Specific problems developers are facing
       - Emerging needs in AI/ML space
       - Gaps in current solutions
       - Pricing complaints about existing tools
    
    Output format:
    ## Market Signals
    - **Signal 1**: [Description and HN source/link]
    - **Signal 2**: [Description and HN source/link]
    - **Signal 3**: [Description and HN source/link]
    
    ## Key Pain Points
    - **Pain Point 1**: [Who has it, why it matters, evidence]
    - **Pain Point 2**: [Who has it, why it matters, evidence]
    
    ## Opportunity Areas
    - **Area 1**: [Description and market indicators]
    - **Area 2**: [Description and market indicators]
    
    Focus on RECENT discussions (last 30 days if possible).
    """,
    markdown=True,
)

# 3. Idea Generator - Enhanced with specific paper context
idea_generator = Agent(
    name="IdeaGenerator",
    model="mistral:mistral-large-latest",
    tools=[ReasoningTools(add_instructions=True)],
    instructions="""
    You are a product strategist. Based on the paper analysis and market research provided:
    
    1. Identify connections between the paper's innovations and market needs
    2. Generate 7-10 SaaS ideas that:
       - DIRECTLY use the paper's technical contributions
       - Address SPECIFIC pain points from the market research
       - Can generate revenue within 6 months
       - Are technically feasible for a small team
    
    For EACH idea, provide ALL of these details:
    
    ### Idea #X: [Catchy Name]
    **Core Concept**: [1-2 sentence description]
    **Target Market**: [Specific user segment with size estimate]
    **Value Proposition**: [Why users would pay - be specific]
    **Technical Approach**: [How the paper's tech specifically enables this]
    **Competitive Moat**: [What makes this defensible]
    **Revenue Model**: [Pricing strategy: subscription/usage/enterprise]
    **Implementation Complexity**: [Low/Medium/High] - [Justification]
    **MVP Features**: [3-4 core features for launch]
    
    Rank ideas 1-10 by combining:
    - Market demand evidence (40%)
    - Technical feasibility (30%)
    - Revenue potential (30%)
    """,
    markdown=True,
)

# 4. Validation Researcher - More robust search handling
validation_researcher = Agent(
    name="ValidationResearcher",
    model="mistral:mistral-large-latest",
    tools=[
        FirecrawlTools(enable_search=True, enable_scrape=True),
        HackerNewsTools(),
        WebsiteTools()
    ],
    instructions="""
    You are a due diligence expert. Take the TOP 3 ideas and validate them thoroughly.
    
    For EACH of the 3 ideas:
    
    1. Search for competitors using generic terms (don't use exact product names that don't exist yet)
    2. Look for evidence of market demand
    3. Find similar tools and their pricing
    
    ## Idea: [Restate the idea name and concept]
    
    ### Market Validation
    - **Demand Evidence**: [Real searches, discussions, or requests found]
    - **Market Size**: [Estimates based on similar tools]
    - **Growth Indicators**: [Trends showing increasing need]
    
    ### Competitive Landscape
    - **Direct Competitors**: [Name, URL, key features, pricing]
    - **Indirect Solutions**: [Alternatives users currently use]
    - **Market Gaps**: [What competitors miss]
    
    ### Technical Validation
    - **Implementation Examples**: [Similar technical implementations]
    - **Technical Risks**: [Potential challenges]
    - **Required Expertise**: [Skills needed]
    
    ### Go-to-Market
    - **Early Adopters**: [Specific communities or companies]
    - **Distribution Channels**: [How to reach users]
    - **Pricing Benchmark**: [What similar tools charge]
    
    ### Risk Assessment
    - **Primary Risk**: [Biggest challenge]
    - **Mitigation Strategy**: [How to address it]
    
    If search fails for a specific query, note it and continue with other validation methods.
    """,
    markdown=True,
)

# 5. Strategic Advisor
strategic_advisor = Agent(
    name="StrategicAdvisor",
    model="mistral:mistral-large-latest",
    tools=[ReasoningTools(add_instructions=True)],
    instructions="""
    You are a seasoned startup advisor. Evaluate each validated idea critically:
    
    For each idea, provide:
    
    ## Idea: [Name]
    
    ### SWOT Analysis
    **Strengths**: 
    - [What's genuinely compelling]
    
    **Weaknesses**: 
    - [Critical flaws or challenges]
    
    **Opportunities**: 
    - [Growth and expansion potential]
    
    **Threats**: 
    - [What could kill this]
    
    ### Viability Score
    - Market Fit: [1-10]
    - Technical Feasibility: [1-10]
    - Business Model: [1-10]
    - Overall: [Average]
    
    ### Recommendation
    **[PROCEED / PIVOT / PASS]**
    
    **Reasoning**: [Detailed explanation]
    
    **If PROCEED**: Next 3 immediate steps
    **If PIVOT**: Suggested changes
    **If PASS**: Why it won't work
    
    Only mark PROCEED if overall score is 7+ and no critical blockers exist.
    """,
    markdown=True
)

# 6. Executive Report Generator
report_generator = Agent(
    name="ReportGenerator",
    model="mistral:mistral-large-latest",
    instructions="""
    Create a professional executive report synthesizing all findings:
    
    # Paper-to-SaaS Opportunity Report
    
    ## Executive Summary
    **Paper**: [Title and ArXiv ID]
    **Key Innovation**: [1 sentence on what's new]
    **Market Opportunity**: [1 sentence on market need]
    **Top Recommendation**: [Best SaaS idea in 1 sentence]
    **Investment Required**: [Time and resources]
    **Confidence Level**: [High/Medium/Low]
    
    ## Technical Innovation Summary
    - **Core Technology**: [What the paper introduces]
    - **Practical Applications**: [How it can be used]
    - **Implementation Readiness**: [How mature the tech is]
    
    ## Market Analysis Summary
    - **Validated Demand**: [Evidence of market need]
    - **Competition Gap**: [What's missing in current solutions]
    - **Revenue Potential**: [Market size estimate]
    
    ## Top SaaS Recommendations
    
    ### 🥇 Primary: [Name]
    **Value Proposition**: [2 sentences on what and why]
    **Target Customers**: [Specific segment]
    **Revenue Model**: [Pricing strategy]
    **MVP Timeline**: [Weeks to launch]
    **First Year Revenue Potential**: [Estimate]
    
    ### 🥈 Alternative: [Name]
    [Shorter version of above]
    
    ## Implementation Roadmap
    
    ### Week 1-2: Foundation
    - [ ] [Specific task]
    - [ ] [Specific task]
    
    ### Week 3-4: Core Development
    - [ ] [Specific task]
    - [ ] [Specific task]
    
    ### Week 5-6: MVP Launch
    - [ ] [Specific task]
    - [ ] [Specific task]
    
    ## Success Metrics
    - **Month 1**: [Target]
    - **Month 3**: [Target]
    - **Month 6**: [Target]
    
    ## Risk Mitigation
    | Risk | Impact | Mitigation |
    |------|--------|------------|
    | [Risk 1] | [H/M/L] | [Strategy] |
    | [Risk 2] | [H/M/L] | [Strategy] |
    
    ## Immediate Next Steps
    1. [Action item with owner]
    2. [Action item with owner]
    3. [Action item with owner]
    
    ---
    *Generated from ArXiv Paper Analysis | Confidence: [Level] | Date: [Today]*
    """,
    markdown=True,
)

# Create the workflow
paper2saas_workflow = Workflow(
    id="paper2saas",
    name="Paper2SaaS Discovery Engine",
    description="Enter an ArXiv ID (e.g., '2512.24991v1') to analyze for SaaS opportunities",
    input_schema=Paper2SaaSInput,  # Validates structured input
    db=AsyncSqliteDb(db_file="tmp/paper2saas.db"),
    steps=[
        Step(name="extract_arxiv", executor=extract_arxiv_id),
        Parallel(
            Step(name="analyze_paper", executor=run_paper_analysis),
            Step(name="research_market", agent=market_researcher),
            name="initial_research"
        ),
        Step(name="combine_research", executor=combine_research),
        Step(name="generate_ideas", agent=idea_generator),
        Step(name="prepare_validation", executor=prepare_validation_context),
        Step(name="validate_ideas", agent=validation_researcher),
        Step(name="advise", agent=strategic_advisor),
        Step(name="filter_recommendations", executor=filter_recommendations),
        Step(name="generate_report", agent=report_generator),
    ],
    store_events=True,
)

# 7. Workflow Agent
workflow_agent = Agent(
    name="Paper2SaaS",
    model="mistral:mistral-large-latest",  # Set the model that should be used
    tools=[WorkflowTools(
        workflow=paper2saas_workflow
    )],
)

# --- WORKFLOW FUNCTIONS ---

def combine_research(step_input: StepInput) -> StepOutput:
    """Combines paper analysis and market research."""
    paper_analysis = step_input.get_step_content("analyze_paper") or "No paper analysis available"
    market_research = step_input.get_step_content("research_market") or "No market research available"
    
    combined = f"""
# Combined Research Context

## 📄 Paper Analysis
{paper_analysis}

## 📊 Market Research
{market_research}

## 🎯 Synthesis Goal
Create SaaS ideas that leverage the paper's technical innovations to solve the market problems identified above.
"""
    
    return StepOutput(
        step_name="combine_research",
        content=combined,
        success=True
    )

def prepare_validation_context(step_input: StepInput) -> StepOutput:
    """Prepares ideas with full context for validation."""
    ideas = step_input.get_step_content("generate_ideas") or ""
    
    formatted = f"""
# Ideas Ready for Validation

{ideas}

## Validation Instructions
For the TOP 3 ideas above (based on ranking), perform thorough market validation.
When searching, use generic terms related to the problem space, not the specific product names.
"""
    
    return StepOutput(
        step_name="prepare_validation",
        content=formatted,
        success=True
    )

def filter_recommendations(step_input: StepInput) -> StepOutput:
    """Filters and prioritizes final recommendations."""
    advisory = step_input.get_step_content("advise") or ""
    
    if "PROCEED" not in advisory:
        output = """
# ⚠️ Pivot Recommended

No ideas met the viability criteria for immediate development.

## Analysis Summary
""" + advisory + """

## Suggested Next Steps
1. Consider adjacent problem spaces
2. Explore different applications of the technology
3. Gather more market validation data
"""
    else:
        output = f"""
# ✅ Validated Opportunities

{advisory}

## Priority Order
Focus on ideas marked PROCEED, starting with highest viability scores.
"""
    
    return StepOutput(
        step_name="filter_recommendations",
        content=output,
        success=True
    )

# --- WORKFLOW DEFINITION ---

# def create_workflow(arxiv_id: str) -> Workflow:
#     """Creates workflow with specific arxiv_id context."""
#     return Workflow(
#         name="Paper2SaaS Discovery Engine",
#         description=f"Analyzing ArXiv paper {arxiv_id} for SaaS opportunities",
#         input_schema=Paper2SaaSInput,
#         steps=[
#             # Phase 1: Parallel Research
#             Parallel(
#                 Step(name="analyze_paper", agent=create_paper_analyzer(arxiv_id)),
#                 Step(name="research_market", agent=market_researcher),
#                 name="initial_research"
#             ),
            
#             # Phase 2: Synthesis
#             Step(name="combine_research", executor=combine_research),
#             Step(name="generate_ideas", agent=idea_generator),
            
#             # Phase 3: Validation Preparation
#             Step(name="prepare_validation", executor=prepare_validation_context),
#             Step(name="validate_ideas", agent=validation_researcher),
            
#             # Phase 4: Strategic Review
#             Step(name="advise", agent=strategic_advisor),
#             Step(name="filter_recommendations", executor=filter_recommendations),
            
#             # Phase 5: Final Report
#             Step(name="generate_report", agent=report_generator),
#         ],
#         store_events=True,
#     )

# def run_paper2saas(arxiv_id: str, debug: bool = False):
    """
    Run the Paper2SaaS workflow with proper arxiv_id handling.
    
    Args:
        arxiv_id: ArXiv paper ID to analyze
        debug: Whether to show detailed execution steps
    """
    print(f"\n{'='*60}")
    print(f"🚀 Paper2SaaS Discovery Engine")
    print(f"📄 Analyzing: arxiv.org/abs/{arxiv_id}")
    print(f"{'='*60}\n")
    
    try:
        # Create workflow with specific arxiv_id
        workflow = create_workflow(arxiv_id)
        workflow_input = Paper2SaaSInput(arxiv_id=arxiv_id)
        
        print("🔍 Phase 1: Fetching paper and researching market...")
        
        if debug:
            response = workflow.run(
                input=workflow_input,
                stream=True,
                markdown=True
            )
            
            for event in response:
                if hasattr(event, 'event'):
                    print(f"  ▶ {event.event}")
        else:
            response = workflow.run(
                input=workflow_input,
                markdown=True
            )
        
        print("\n" + "="*60)
        print("📊 FINAL REPORT")
        print("="*60)
        print(response.content)
        print("\n" + "="*60)
        
        # Save report to file
        with open(f"paper2saas_report_{arxiv_id.replace('.', '_')}.md", "w") as f:
            f.write(response.content)
            print(f"\n📁 Report saved to: paper2saas_report_{arxiv_id.replace('.', '_')}.md")
        
        return response
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print(f"\nTroubleshooting:")
        print(f"1. Verify ArXiv ID '{arxiv_id}' is valid")
        print(f"2. Check your API keys are set correctly")
        print(f"3. Ensure you have internet connection")
        return None