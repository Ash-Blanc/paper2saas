# Paper2SaaS

Multi-agent AI system that transforms academic arXiv papers into validated SaaS business opportunities.

## Overview

Paper2SaaS uses a team of specialized AI agents to:
1. Analyze academic papers from arXiv
2. Research market opportunities and pain points
3. Generate SaaS ideas based on paper innovations
4. Validate ideas with market research
5. Provide strategic recommendations
6. Produce comprehensive opportunity reports

## Tech Stack

- **Python**: 3.12+
- **Framework**: [Agno](https://github.com/agnohq/agno) - Multi-agent orchestration
- **LLM**: Mistral AI (mistral-large, mistral-small)
- **API**: FastAPI
- **Database**: SQLite (agent event persistence)
- **Tools**: ArxivTools, FirecrawlTools, WebsiteTools, BaiduSearchTools, HackerNewsTools

## Architecture

### Main Team: paper2saas_team (7 agents)

Sequential workflow:
1. **PaperAnalyzer** - Fetches and analyzes arXiv papers with fallback protocol
2. **MarketResearcher** - Conducts tool-based market research
3. **IdeaGenerator** - Creates SaaS ideas from verified inputs
4. **ValidationResearcher** - Validates top ideas with external research
5. **StrategicAdvisor** - Evaluates and scores ideas
6. **FactChecker** - Verifies claims against sources
7. **ReportGenerator** - Compiles comprehensive final report

### Critique Team: idea_roaster_team (2 agents)

Parallel critique for stress-testing:
- **DevilsAdvocate** - Technical critique with tool-verified evidence
- **MarketSkeptic** - Market assumptions challenge

## Key Features

- **Structured Outputs**: Pydantic models prevent hallucination
- **Chain-of-Note (CoN)**: Systematic source tracking
- **Chain-of-Verification (CoVe)**: Claim verification protocol
- **Multi-Tool Fallback**: ArxivTools → FirecrawlTools → WebsiteTools → BaiduSearchTools
- **Reasoning**: All agents have configurable reasoning steps
- **Event Persistence**: SQLite storage for debugging and analysis

## Setup

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

```bash
# Clone repo
git clone <repo-url>
cd paper2saas

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Environment Variables

Required:
- `MISTRAL_API_KEY` - Your Mistral AI API key
- `FIRECRAWL_API_KEY` - Your Firecrawl API key

Optional:
- `LARGE_MODEL` - Default: mistral:mistral-large-latest
- `SMALL_MODEL` - Default: mistral:mistral-small-latest
- `REASONING_MIN_STEPS` - Default: 2
- `REASONING_MAX_STEPS` - Default: 8
- `ENABLE_MARKDOWN` - Default: true
- `STORE_EVENTS` - Default: true
- `SHOW_MEMBER_RESPONSES` - Default: true
- `LOG_LEVEL` - Default: INFO

## Usage

### Start the API Server

```bash
# Development mode with auto-reload
uv run uvicorn my_os:app --reload

# Or using Python directly
python my_os.py
```

API will be available at `http://localhost:8000`

### API Endpoints

- `GET /` - Health check
- `POST /paper2saas/run` - Analyze paper and generate opportunities
  ```json
  {
    "arxiv_id": "2512.24991v1"
  }
  ```

### Example Usage

```python
import requests

response = requests.post(
    "http://localhost:8000/paper2saas/run",
    json={"arxiv_id": "2512.24991v1"}
)

print(response.json())
```

## Project Structure

```
paper2saas/
├── paper2saas.py      # Main agent definitions and teams
├── my_os.py           # AgentOS setup and FastAPI app
├── pyproject.toml     # Dependencies
├── .env               # Environment variables (not in git)
├── tmp/
│   ├── paper2saas.db  # SQLite event storage
│   └── paper2saas.log # Application logs
└── README.md
```

## Development

### Logging

Logs are written to:
- Console (stdout)
- `tmp/paper2saas.log`

Configure log level with `LOG_LEVEL` environment variable.

### Database

Agent events are stored in `tmp/paper2saas.db` for:
- Debugging agent interactions
- Analyzing workflow performance
- Context sharing between agents

### Adding New Agents

1. Define Pydantic output schema
2. Create Agent with tools and instructions
3. Add to appropriate team
4. Update team workflow in instructions

## Methodology

### Anti-Hallucination Measures

1. **Structured Outputs**: All agents use Pydantic schemas
2. **Source Attribution**: Every claim must cite tool/source
3. **Chain-of-Note**: Systematic reading notes before synthesis
4. **Chain-of-Verification**: Post-draft claim verification
5. **Fact Checking**: Dedicated agent verifies claims
6. **Data Quality Metrics**: Confidence scores, tool success rates

### Tool Usage Protocol

- Primary tool attempts first
- Automatic fallback chain on failure
- All attempts logged
- Confidence scoring based on source quality

## Troubleshooting

### Common Issues

**Error: Missing API keys**
- Ensure `.env` file exists with valid keys
- Check `MISTRAL_API_KEY` and `FIRECRAWL_API_KEY`

**Error: Database locked**
- Only one process can write to SQLite at a time
- Restart the server

**Low confidence scores**
- Verify arXiv ID is correct
- Check if paper is accessible
- Review logs in `tmp/paper2saas.log`

## Contributing

Currently in active development. Main contributor: ash_blanc

## License

[Add license information]
