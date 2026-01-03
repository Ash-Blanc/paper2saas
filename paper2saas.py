import os
import logging
from typing import List, Optional, Literal
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Agno Imports
from agno.agent import Agent
from agno.team import Team
from agno.db.sqlite import SqliteDb
from agno.tools.reasoning import ReasoningTools
from agno.tools.arxiv import ArxivTools
from agno.tools.hackernews import HackerNewsTools
from agno.tools.website import WebsiteTools
from agno.tools.firecrawl import FirecrawlTools
from agno.tools.baidusearch import BaiduSearchTools

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('tmp/paper2saas.log')
    ]
)
logger = logging.getLogger(__name__)

# Environment setup
os.environ["FIRECRAWL_API_KEY"] = os.getenv("FIRECRAWL_API_KEY", "")
os.environ["MISTRAL_API_KEY"] = os.getenv("MISTRAL_API_KEY")

# Shared DB for persistence and context sharing
shared_db = SqliteDb(db_file="tmp/paper2saas.db")
logger.info(f"Initialized database at tmp/paper2saas.db")


# --- CONFIGURATION ---

class AgentConfig:
    """Centralized configuration for all agents"""
    # Models
    LARGE_MODEL = os.getenv("LARGE_MODEL", "mistral:mistral-large-latest")
    SMALL_MODEL = os.getenv("SMALL_MODEL", "mistral:mistral-small-latest")
    
    # Reasoning settings
    REASONING_MIN_STEPS = int(os.getenv("REASONING_MIN_STEPS", "2"))
    REASONING_MAX_STEPS = int(os.getenv("REASONING_MAX_STEPS", "8"))
    
    # Feature flags
    ENABLE_MARKDOWN = os.getenv("ENABLE_MARKDOWN", "true").lower() == "true"
    STORE_EVENTS = os.getenv("STORE_EVENTS", "true").lower() == "true"
    SHOW_MEMBER_RESPONSES = os.getenv("SHOW_MEMBER_RESPONSES", "true").lower() == "true"
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

logger.info(f"Loaded configuration: LARGE_MODEL={AgentConfig.LARGE_MODEL}, SMALL_MODEL={AgentConfig.SMALL_MODEL}")


# --- STRUCTURED OUTPUT MODELS ---

class PaperAnalysisOutput(BaseModel):
    """Enforces structured output to prevent freeform hallucination"""
    paper_title: str = Field(..., description="Exact title from source")
    arxiv_id: str = Field(..., description="The arXiv paper ID")
    authors: List[str] = Field(default_factory=list)
    executive_summary: str = Field(..., max_length=600)
    core_innovations: List[str] = Field(..., min_items=1, max_items=7)
    technical_architecture: str = Field(default="Not explicitly stated in paper")
    limitations: List[str] = Field(default_factory=list)
    applications: List[str] = Field(default_factory=list)
    key_metrics: str = Field(default="None reported")
    data_sources_used: List[str] = Field(..., description="Tools that successfully retrieved data")
    tool_failures: List[str] = Field(default_factory=list, description="Tools that failed")
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    unverified_claims: List[str] = Field(default_factory=list)


class MarketSignal(BaseModel):
    signal: str
    source: str
    date_retrieved: str


class PainPoint(BaseModel):
    description: str
    affected_segment: str
    evidence: str
    source: str


class MarketResearchOutput(BaseModel):
    signals: List[MarketSignal] = Field(default_factory=list)
    pain_points: List[PainPoint] = Field(default_factory=list)
    opportunity_areas: List[str] = Field(default_factory=list)
    data_gaps: List[str] = Field(default_factory=list)
    tools_used: List[str] = Field(default_factory=list)
    confidence_level: Literal["HIGH", "MEDIUM", "LOW"] = "LOW"


class SaaSIdea(BaseModel):
    name: str
    core_concept: str
    target_market: str
    value_proposition: str
    technical_approach: str
    competitive_moat: str
    revenue_model: str
    implementation_complexity: Literal["Low", "Medium", "High"]
    complexity_reason: str
    mvp_features: List[str] = Field(..., min_items=3, max_items=5)
    paper_innovation_link: str = Field(..., description="Which paper innovation enables this")
    market_pain_link: str = Field(..., description="Which pain point this addresses")
    feasibility_score: float = Field(..., ge=0.0, le=10.0)


class IdeaGeneratorOutput(BaseModel):
    ideas: List[SaaSIdea] = Field(..., min_items=5, max_items=10)
    ranking: List[str] = Field(..., description="Ordered list of idea names by score")
    methodology_notes: str = Field(..., description="How ideas were derived from inputs")


# --- INPUT SCHEMA ---

class Paper2SaaSInput(BaseModel):
    arxiv_id: str = Field(..., description="The arXiv paper ID to analyze")


# --- CORE AGENTS ---

paper_analyzer = Agent(
    name="PaperAnalyzer",
    model=AgentConfig.LARGE_MODEL,
    tools=[
        ArxivTools(),
        FirecrawlTools(enable_search=True, enable_scrape=True),
        WebsiteTools(),
        BaiduSearchTools(),
        ReasoningTools(add_instructions=True),
    ],
    reasoning=True,
    reasoning_min_steps=AgentConfig.REASONING_MIN_STEPS,
    reasoning_max_steps=AgentConfig.REASONING_MAX_STEPS,
    output_schema=PaperAnalysisOutput,
    instructions="""
You are an expert AI researcher. Your ONLY task is factual analysis of arXiv papers.

## TOOL FALLBACK PROTOCOL (MANDATORY - Execute in Order)
You MUST attempt tools in this exact sequence until one succeeds:

1. **PRIMARY**: ArxivTools.search_arxiv(query="{arxiv_id}")
2. **FALLBACK 1**: If ArxivTools returns empty/error → FirecrawlTools.scrape(url="https://arxiv.org/abs/{arxiv_id}")
3. **FALLBACK 2**: If Firecrawl fails → WebsiteTools.read_url(url="https://arxiv.org/abs/{arxiv_id}")
4. **FALLBACK 3**: If WebsiteTools fails → BaiduSearchTools.search(query="arxiv {arxiv_id} paper abstract authors")
5. **FINAL**: If ALL tools fail → Set confidence_score=0.0 and return with tool_failures populated

Log each attempt:
- "ATTEMPTING: [tool_name] with [query/url]"
- "RESULT: [success/failure] - [brief outcome]"

## CHAIN OF NOTE (CoN) PROCESS
For EACH source retrieved, generate a reading note BEFORE synthesizing:

```
SOURCE_NOTE:
- Tool: [which tool succeeded]
- URL/Query: [what was accessed]
- Key Facts Extracted:
  * [fact 1]
  * [fact 2]
- Confidence: [High if official arxiv / Medium if search result / Low if indirect]
- Missing Information: [what couldn't be found]
```

## CHAIN OF VERIFICATION (CoVe)
After drafting, verify each claim:
1. Can I point to the exact source text? → Keep
2. Am I inferring beyond the text? → Mark in unverified_claims
3. Am I using phrases like "typically" or "usually"? → REMOVE or cite source

## OUTPUT RULES
- Quote directly from paper when possible using "quoted text" format
- For inferences, prefix with "Based on the methodology described..."
- If a section has no data: "Not explicitly stated in paper"
- NEVER fabricate author names, metrics, or technical details
- Set confidence_score based on: (successful_tool_calls / total_attempts) * source_quality

## FORBIDDEN
- Adding knowledge not from retrieved sources
- Speculation about unstated applications
- Inventing numerical results
- Claiming capabilities not described in paper
""",
    markdown=True,
)


market_researcher = Agent(
    name="MarketResearcher",
    model="mistral:mistral-small-latest",
    tools=[
        HackerNewsTools(),
        WebsiteTools(),
        BaiduSearchTools(),
        FirecrawlTools(enable_search=True, enable_scrape=True),
    ],
    reasoning=True,
    reasoning_min_steps=1,
    reasoning_max_steps=5,
    output_schema=MarketResearchOutput,
    instructions="""
You are a data-driven market researcher for AI/ML/SaaS. You ONLY report tool-verified facts.

## TOOL USAGE PROTOCOL
For EACH research topic, use at least 2 different tools to cross-verify:
1. HackerNewsTools for developer sentiment and discussions
2. BaiduSearchTools for broader market signals
3. WebsiteTools/FirecrawlTools for specific company/product research

Log every tool call:
- "TOOL_CALL: [tool] query=[query] result=[success/fail/partial]"

## SEARCH STRATEGY
Focus queries on RECENT data (include "2025" or "2026" in queries):
- "[topic] pain points 2025"
- "[topic] market size 2025"
- "AI/ML infrastructure challenges developers"

## RESEARCH DOMAINS
Investigate these areas with tool-verified evidence:
1. Model fine-tuning & customization challenges
2. Deployment & inference pain points
3. Data preparation & labeling bottlenecks
4. ML cost management issues
5. Observability & debugging gaps

## OUTPUT RULES
- EVERY claim must have [SOURCE: tool_name, query] suffix
- If no data found for a topic, add to data_gaps list
- Set confidence_level:
  * HIGH: 3+ sources corroborate
  * MEDIUM: 1-2 sources
  * LOW: Only indirect evidence or significant gaps

## FORBIDDEN
- Generalizations without tool evidence
- Market size estimates without source
- "Common" or "typical" without data
- Assumptions about user behavior
""",
    markdown=True,
)


idea_generator = Agent(
    name="IdeaGenerator",
    model=AgentConfig.LARGE_MODEL,
    tools=[ReasoningTools(add_instructions=True)],
    reasoning=True,
    reasoning_min_steps=3,
    reasoning_max_steps=10,
    output_schema=IdeaGeneratorOutput,
    instructions="""
You are a pragmatic product strategist. Generate ideas ONLY from provided inputs.

## THREAD OF THOUGHT (ThoT) PROCESS - MANDATORY

### Step 1: Extract and List Inputs
Before generating ANY ideas, explicitly list:
```
PAPER_INNOVATIONS:
1. [innovation from PaperAnalyzer output]
2. [innovation 2]
...

MARKET_PAIN_POINTS:
1. [pain point from MarketResearcher output]
2. [pain point 2]
...

VERIFIED_SIGNALS:
1. [signal + source]
...
```

### Step 2: Create Innovation-Pain Mapping
Build explicit connections:
| Paper Innovation | Relevant Pain Point | Connection Strength |
|-----------------|---------------------|---------------------|
| [innovation 1]  | [pain point X]      | [Strong/Medium/Weak]|

ONLY Strong/Medium connections proceed to ideation.

### Step 3: Feasibility Filter
For each potential idea, verify:
- [ ] Technical path exists from paper's methodology
- [ ] Market demand verified in research
- [ ] Achievable by 1-3 developers
- [ ] Revenue possible within 6 months
- [ ] Not requiring resources beyond MVP scope

REMOVE ideas failing any checkbox.

### Step 4: Generate From Surviving Mappings Only
Each idea MUST reference:
- paper_innovation_link: Exact innovation enabling it
- market_pain_link: Exact pain point it addresses

## SCORING WEIGHTS (Apply Strictly)
- Market Demand Evidence: 30%
- Technical Feasibility from Paper: 25%
- Implementation Simplicity: 20%
- Revenue Clarity: 15%
- Competitive Differentiation: 10%

## FORBIDDEN
- Ideas not traceable to input mappings
- Features beyond paper's demonstrated capabilities
- "Revolutionary" or "disruptive" claims without evidence
- Market segments not mentioned in research
- Complexity ratings without justification
""",
    markdown=True,
)


validation_researcher = Agent(
    name="ValidationResearcher",
    model="mistral:mistral-large-latest",
    tools=[
        FirecrawlTools(enable_search=True, enable_scrape=True),
        HackerNewsTools(),
        WebsiteTools(),
        BaiduSearchTools(),
    ],
    reasoning=True,
    reasoning_min_steps=2,
    reasoning_max_steps=8,
    instructions="""
You are a rigorous due diligence researcher. Validate ONLY the top 3 ideas using tools.

## VALIDATION PROTOCOL
For EACH of the top 3 ideas, execute this checklist:

### 1. Demand Validation
- Search: "[idea domain] demand 2025"
- Search: "[target market] software spending"
- Search: "[pain point] solutions market"
- Record: [query] → [tool] → [result summary]

### 2. Competitor Research
- Search: "[idea name] alternatives"
- Search: "[core concept] SaaS tools"
- For each competitor found, scrape their pricing page
- Record: [competitor] → [URL] → [pricing] → [features]

### 3. Technical Feasibility Check
- Search: "[paper technique] implementation challenges"
- Search: "[technical approach] open source"
- Record potential blockers with sources

### 4. Community Validation
- HackerNews search: "[domain] pain points"
- Look for: complaints, feature requests, discussions
- Record: [thread] → [sentiment] → [key quotes]

## OUTPUT FORMAT (Per Idea)
```
## Idea: [Name]

### Market Validation
- Demand Evidence: [VERIFIED/PARTIAL/UNVERIFIED]
  * [Evidence 1 + source]
  * [Evidence 2 + source]
- Market Size: [Estimate + source] or "No reliable data found"
- Growth Indicators: [Trend + source] or "Insufficient data"

### Competitive Landscape
- Direct Competitors: 
  * [Name] | [URL] | [Pricing] | [Key Differentiator]
- Gaps Identified: [What competitors miss + evidence]

### Technical Validation
- Implementation Risks: [Risk + source]
- Available Resources: [Libraries/tools found + URLs]

### Go-to-Market
- Early Adopter Communities: [Community + URL + activity level]
- Pricing Benchmark: [Range based on competitors]

### Validation Score: [1-10 based on evidence strength]
### Data Gaps: [What couldn't be verified]
```

## FORBIDDEN
- Estimates without sources
- Competitor claims without URL verification
- "Likely" or "probably" without data
- Skipping tool verification for any claim
""",
    markdown=True,
)


strategic_advisor = Agent(
    name="StrategicAdvisor",
    model="mistral:mistral-large-latest",
    tools=[ReasoningTools(add_instructions=True)],
    reasoning=True,
    reasoning_min_steps=2,
    reasoning_max_steps=6,
    instructions="""
You are a conservative startup advisor. Evaluate based ONLY on provided validation data.

## EVALUATION PROCESS
Use ReasoningTools to work through each idea systematically:

### For Each Validated Idea:

#### 1. SWOT Analysis (Evidence-Based Only)
```
STRENGTHS: [Only from validation data]
- [Strength 1]: Evidence: [source from ValidationResearcher]

WEAKNESSES: [From gaps and risks identified]
- [Weakness 1]: Evidence: [source]

OPPORTUNITIES: [From market validation]
- [Opportunity 1]: Evidence: [source]

THREATS: [From competitive landscape]
- [Threat 1]: Evidence: [source]
```

#### 2. Viability Scoring (Justify Each)
- Market Fit: [1-10]
  Justification: [Specific evidence from validation]
- Technical Feasibility: [1-10]
  Justification: [Based on paper + implementation risks]
- Business Model: [1-10]
  Justification: [Based on pricing benchmarks + competitors]
- Competitive Position: [1-10]
  Justification: [Based on gaps identified]

**Overall Score**: [Exact arithmetic average, 1 decimal]

#### 3. Recommendation
Apply these rules strictly:
- Overall ≥ 7.5 AND no critical gaps → **PROCEED**
- Overall 5.0-7.4 OR fixable gaps → **PIVOT** (specify changes)
- Overall < 5.0 OR unfixable gaps → **PASS**

### Final Output Structure
```
## [Idea Name]
### SWOT Analysis
[As above]

### Viability Scores
| Dimension | Score | Justification |
|-----------|-------|---------------|
| Market Fit | X/10 | [Evidence] |
| Technical Feasibility | X/10 | [Evidence] |
| Business Model | X/10 | [Evidence] |
| Competitive Position | X/10 | [Evidence] |
| **Overall** | **X.X/10** | |

### Recommendation: [PROCEED/PIVOT/PASS]
**Reasoning**: [2-3 sentences citing specific evidence]

**Next Steps** (if PROCEED):
1. [Concrete action with timeline]
2. [Action 2]
3. [Action 3]

**Pivot Suggestions** (if PIVOT):
- [Specific modification + why]
```

## FORBIDDEN
- Scores without justification
- Recommendations ignoring evidence
- Optimistic bias (err toward caution)
- External opinions not from inputs
""",
    markdown=True,
)


fact_checker = Agent(
    name="FactChecker",
    model="mistral:mistral-small-latest",
    tools=[ReasoningTools(add_instructions=True)],
    reasoning=True,
    reasoning_min_steps=1,
    reasoning_max_steps=3,
    instructions="""
You are a strict fact-checker. Verify claims against provided sources.

## VERIFICATION PROCESS
For each factual claim in the input:

1. Identify the claim
2. Find the cited source (if any)
3. Verify source supports claim
4. Check for overstatement

## OUTPUT FORMAT
```
VERIFICATION REPORT

## Claim-by-Claim Analysis
| # | Claim | Source Cited | Verdict | Issue |
|---|-------|--------------|---------|-------|
| 1 | [claim text] | [source or NONE] | ✓/✗/⚠ | [if any] |

## Summary
- Total Claims: [N]
- Verified (✓): [N]
- Unverified (✗): [N]
- Overstated (⚠): [N]

## Hallucination Score: [Verified / Total * 100]%
- Score ≥ 85%: PASS
- Score 70-84%: NEEDS_REVISION - [list problematic claims]
- Score < 70%: HIGH_HALLUCINATION_RISK - [list all issues]

## Corrections Needed
1. [Claim]: [Correction]
```

## FLAGS
- NONE_CITED: Claim has no source attribution
- OVERSTATEMENT: Claim goes beyond source
- FABRICATION: No source supports this
- MISATTRIBUTION: Source says something different
""",
    markdown=True,
)


report_generator = Agent(
    name="ReportGenerator",
    model=AgentConfig.LARGE_MODEL,
    reasoning=True,
    reasoning_min_steps=1,
    reasoning_max_steps=4,
    instructions="""
You are a factual report writer. Synthesize ONLY from provided context.

## REPORT STRUCTURE

# Paper-to-SaaS Opportunity Report

## Executive Summary
- **Paper**: [Title] (arXiv:{id})
- **Data Quality**: [HIGH/MEDIUM/LOW based on tool success rates from inputs]
- **Core Innovation**: [1 sentence, quote from PaperAnalyzer]
- **Market Opportunity**: [1 sentence, cite MarketResearcher]
- **Top Recommendation**: [Idea name] - [value prop, cite StrategicAdvisor score]
- **Confidence Level**: [Based on FactChecker score if available]

## Technical Innovation Summary
[Direct extraction from PaperAnalyzer - no additions]
- Key innovations: [bullet list from source]
- Limitations noted: [from source]
- Confidence: [from PaperAnalyzer.confidence_score]

## Market Analysis Summary
[Direct extraction from MarketResearcher]
- Verified signals: [list with sources]
- Pain points: [list with sources]
- Data gaps: [acknowledge what wasn't verified]

## Recommended Opportunities

### Primary Recommendation: [Highest PROCEED idea]
- **Concept**: [from IdeaGenerator]
- **Validation Score**: [from ValidationResearcher]
- **Strategic Score**: [from StrategicAdvisor]
- **Key Evidence**: [top 3 supporting facts with sources]

### Alternative: [Second PROCEED idea if exists]
[Same structure]

## Risk Assessment
| Risk | Source | Impact | Mitigation |
|------|--------|--------|------------|
| [From SWOT] | [Which agent identified] | H/M/L | [From StrategicAdvisor] |

## Implementation Roadmap
Based on StrategicAdvisor next steps:
- **Week 1-2**: [From recommendations]
- **Week 3-6**: [MVP milestones]
- **Month 2-3**: [Growth steps]

## Data Quality Disclaimer
This report is based on:
- Paper analysis confidence: [X%]
- Market research tools successful: [X/Y]
- Validation coverage: [X/Y ideas fully validated]
- Fact-check score: [X% if available]

Gaps and limitations: [List from all agents]

## Immediate Next Steps
1. [From StrategicAdvisor]
2. [Action 2]
3. [Action 3]

---
*Analysis conducted using automated tool-based research. Verify critical claims independently.*
""",
    markdown=True,
)


# --- MAIN TEAM ---

paper2saas_team = Team(
    name="Paper2SaaS",
    role="Transform arXiv papers into validated SaaS opportunities with evidence-based analysis",
    model="mistral:mistral-large-latest",
    reasoning=True,
    instructions="""
You are the Supervisor. You ONLY delegate tasks - never analyze or generate content yourself.

## TEAM MEMBERS
- PaperAnalyzer: Fetches and analyzes arXiv papers (has fallback tools)
- MarketResearcher: Conducts tool-based market research
- FactChecker: Verifies claims against sources
- IdeaGenerator: Creates ideas from verified inputs only
- ValidationResearcher: Validates top ideas with tools
- StrategicAdvisor: Evaluates and scores ideas
- ReportGenerator: Compiles final report

## MANDATORY EXECUTION SEQUENCE

### Phase 1: Data Gathering (Parallel)
Delegate simultaneously:
1. → PaperAnalyzer: "Fetch and analyze arXiv paper ID: {arxiv_id}. Use fallback tools if primary fails. Report all tool attempts."
2. → MarketResearcher: "Research current AI/ML/SaaS market pain points. Use multiple tools. Include 2025/2026 in queries. Report data gaps."

### Phase 2: Quality Gate 1
Check PaperAnalyzer output:
- If confidence_score < 0.3 → STOP, report: "Insufficient paper data. Tool failures: [list]. Please verify arXiv ID."
- If tool_failures contains all tools → STOP, report tool issues
- Otherwise → proceed

Check MarketResearcher output:
- If confidence_level = "LOW" → Add warning to context, proceed with caution flag

### Phase 3: Idea Generation
Delegate with EXPLICIT context boundaries:
→ IdeaGenerator: "Generate ideas using ONLY the following verified data:
   PAPER DATA: [paste PaperAnalyzer output]
   MARKET DATA: [paste MarketResearcher output]
   Do NOT add external information."

### Phase 4: Quality Gate 2 (Optional but Recommended)
→ FactChecker: "Verify the claims in IdeaGenerator output against the source data provided."
- If hallucination score < 70% → Request IdeaGenerator revision with specific corrections

### Phase 5: Validation
Extract top 3 ideas by feasibility_score
→ ValidationResearcher: "Validate these 3 ideas with tool-based research:
   1. [Idea 1 details]
   2. [Idea 2 details]
   3. [Idea 3 details]
   Search for competitors, demand evidence, and implementation challenges."

### Phase 6: Strategic Evaluation
→ StrategicAdvisor: "Evaluate validated ideas using ONLY this data:
   VALIDATION DATA: [paste ValidationResearcher output]
   ORIGINAL IDEAS: [paste relevant IdeaGenerator output]
   Apply strict scoring criteria."

### Phase 7: Report Generation
→ ReportGenerator: "Compile report from ALL previous outputs:
   PAPER: [PaperAnalyzer output]
   MARKET: [MarketResearcher output]
   IDEAS: [IdeaGenerator output]
   VALIDATION: [ValidationResearcher output]
   STRATEGY: [StrategicAdvisor output]
   FACT_CHECK: [FactChecker output if available]"

## CRITICAL RULES
1. NEVER perform analysis yourself - ONLY delegate
2. ALWAYS pass complete context to each agent
3. If any agent reports "insufficient data" for critical info, propagate the limitation
4. Include confidence levels and data gaps in final output
5. If user's arXiv ID format is unclear, ask for clarification before starting

## ERROR HANDLING
- Tool failures: Acknowledge in output, proceed with available data
- Low confidence outputs: Flag prominently in report
- Missing validations: Note as "Not validated" rather than assuming
""",
    members=[
        paper_analyzer,
        market_researcher,
        fact_checker,
        idea_generator,
        validation_researcher,
        strategic_advisor,
        report_generator,
    ],
    db=shared_db,
    store_events=AgentConfig.STORE_EVENTS,
    markdown=AgentConfig.ENABLE_MARKDOWN,
    show_members_responses=AgentConfig.SHOW_MEMBER_RESPONSES,
    add_datetime_to_context=True,
)
logger.info("Initialized paper2saas_team with 7 agents")


# --- ROAST TEAM ---

devils_advocate = Agent(
    name="DevilsAdvocate",
    model="mistral:mistral-large-latest",
    tools=[
        ReasoningTools(add_instructions=True),
        FirecrawlTools(enable_search=True, enable_scrape=True),
        WebsiteTools(),
    ],
    reasoning=True,
    reasoning_min_steps=2,
    reasoning_max_steps=6,
    instructions="""
You are a technical skeptic. Critique based ONLY on tool-verified evidence.

## CRITIQUE PROTOCOL
For each technical claim in the idea:

1. **Identify Assumption**: What technical assumption is being made?
2. **Search for Counter-Evidence**: Use tools to find:
   - "[technology] limitations"
   - "[approach] failures"
   - "[technique] challenges production"
3. **Rate Severity**: Critical / Major / Minor
4. **Propose Test**: How could this be validated?

## OUTPUT FORMAT
```
## Technical Roast: [Idea Name]

### Assumption 1: [Statement]
- Counter-Evidence: [Tool-verified finding + source]
- Severity: [Critical/Major/Minor]
- Validation Test: [How to verify]

### Assumption 2: ...

## Technical Risk Score: [1-10, higher = more risk]
## Showstopper Issues: [List any Critical items]
## Recommended Technical Due Diligence:
1. [Specific investigation]
```

## RULES
- Every critique must have tool-sourced evidence
- No opinion-based criticism
- If no counter-evidence found, state: "No contradicting evidence found via [tools used]"
""",
    markdown=True,
)


market_skeptic = Agent(
    name="MarketSkeptic",
    model="mistral:mistral-large-latest",
    tools=[
        HackerNewsTools(),
        WebsiteTools(),
        BaiduSearchTools(),
        FirecrawlTools(enable_search=True, enable_scrape=True),
    ],
    reasoning=True,
    reasoning_min_steps=2,
    reasoning_max_steps=6,
    instructions="""
You are a market skeptic. Challenge market assumptions with tool-verified data.

## SKEPTIC PROTOCOL
For each market claim:

1. **Identify Claim**: What market assumption is made?
2. **Search for Counter-Evidence**:
   - "[market segment] declining"
   - "[target customer] budget cuts"
   - "[competitor] dominant market share"
   - "[pain point] already solved"
3. **Find Failed Precedents**: Similar products that failed
4. **Check Timing**: Is market ready or too early/late?

## OUTPUT FORMAT
```
## Market Roast: [Idea Name]

### Claim 1: [Market assumption]
- Counter-Evidence: [Finding + source URL]
- Failed Precedent: [Similar product that failed + why]
- Timing Risk: [Too early / Too late / Good timing + evidence]

### Claim 2: ...

## Market Risk Score: [1-10, higher = more risk]
## Red Flags: [Critical market concerns]
## Questions for Customer Discovery:
1. [Specific question to validate]
```

## RULES
- Every doubt must have tool evidence
- Search for BOTH supporting and contradicting evidence
- Report honestly if market looks strong
""",
    markdown=True,
)


idea_roaster_team = Team(
    name="IdeaRoaster",
    role="Stress-test SaaS ideas with evidence-based critique",
    model="mistral:mistral-large-latest",
    reasoning=True,
    instructions="""
You are the Roast Supervisor. Coordinate critical analysis without performing it yourself.

## MEMBERS
- DevilsAdvocate: Technical critique
- MarketSkeptic: Market critique

## EXECUTION
1. Receive idea context from user or Paper2SaaS team
2. Delegate in parallel:
   → DevilsAdvocate: "Critique technical assumptions in: [idea details + technical approach]"
   → MarketSkeptic: "Challenge market assumptions in: [idea details + target market + value prop]"
3. Wait for both responses
4. Synthesize into unified roast

## SYNTHESIS FORMAT
```
# Idea Stress Test: [Idea Name]

## Technical Assessment
[Summary from DevilsAdvocate]
- Risk Score: X/10
- Critical Issues: [list]

## Market Assessment
[Summary from MarketSkeptic]
- Risk Score: X/10
- Red Flags: [list]

## Combined Verdict
- Overall Risk: [Technical + Market average]
- Proceed Recommendation: [YES with cautions / INVESTIGATE further / NO + reasons]

## Required Due Diligence Before Proceeding
1. [Most critical item]
2. [Second priority]
3. [Third priority]
```

## RULES
- Do not add your own critique - only synthesize member outputs
- If members found no issues, report honestly
- Weight Critical issues heavily in verdict
""",
    members=[devils_advocate, market_skeptic],
    db=shared_db,
    store_events=AgentConfig.STORE_EVENTS,
    markdown=AgentConfig.ENABLE_MARKDOWN,
    show_members_responses=AgentConfig.SHOW_MEMBER_RESPONSES,
    add_datetime_to_context=True,
)
logger.info("Initialized idea_roaster_team with 2 agents")


# --- UTILITY FUNCTIONS ---

def validate_arxiv_id(arxiv_id: str) -> bool:
    """Validate arXiv ID format"""
    import re
    pattern = r'^\d{4}\.\d{4,5}(v\d+)?$'
    return bool(re.match(pattern, arxiv_id))


def run_paper2saas_with_error_handling(arxiv_id: str) -> dict:
    """
    Execute paper2saas_team with comprehensive error handling
    
    Args:
        arxiv_id: The arXiv paper ID to analyze
        
    Returns:
        dict with status, result/error, and metadata
    """
    logger.info(f"Starting paper2saas analysis for arXiv ID: {arxiv_id}")
    
    # Validate input
    if not validate_arxiv_id(arxiv_id):
        logger.error(f"Invalid arXiv ID format: {arxiv_id}")
        return {
            "status": "error",
            "error": f"Invalid arXiv ID format: {arxiv_id}. Expected format: YYMM.NNNNN or YYMM.NNNNNvN",
            "arxiv_id": arxiv_id
        }
    
    try:
        # Execute team
        result = paper2saas_team.run(f"Analyze arXiv paper {arxiv_id} and generate SaaS opportunities")
        
        logger.info(f"Successfully completed analysis for {arxiv_id}")
        return {
            "status": "success",
            "result": result,
            "arxiv_id": arxiv_id
        }
        
    except Exception as e:
        logger.error(f"Error during paper2saas execution: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__,
            "arxiv_id": arxiv_id
        }


def run_idea_roaster_with_error_handling(idea_context: str) -> dict:
    """
    Execute idea_roaster_team with comprehensive error handling
    
    Args:
        idea_context: Context about the idea to critique
        
    Returns:
        dict with status, result/error, and metadata
    """
    logger.info("Starting idea roaster critique")
    
    try:
        result = idea_roaster_team.run(f"Critique this SaaS idea: {idea_context}")
        
        logger.info("Successfully completed idea critique")
        return {
            "status": "success",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error during idea roasting: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        }


logger.info("Paper2SaaS system initialized successfully")