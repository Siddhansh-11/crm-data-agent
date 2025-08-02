# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a CRM Data Q&A Agent built with Google's Agent Development Kit (ADK). It's a multi-agentic system that performs advanced RAG (Retrieval-Augmented Generation) with Natural Language to SQL over Salesforce data replicated to BigQuery. The agent interprets business questions, generates SQL queries, creates interactive Vega-Lite visualizations, and provides insights with recommended actions.

## Architecture

The system follows a multi-agent architecture:

- **Root Agent** (`src/agents/data_agent/agent.py`): Orchestrates the entire workflow using Gemini 2.5 Pro 
- **Data Engineer**: Handles SQL generation and database queries
- **BI Engineer**: Creates interactive Vega-Lite charts and visualizations
- **CRM Business Analyst**: Provides business context and insights
- **Chart Evaluator**: Validates and evaluates generated visualizations

## Key Dependencies

- **Google ADK** (`google-adk==1.3.*`): Core agent framework
- **Google Gemini** (`google-genai==1.20.*`): LLM capabilities
- **Streamlit**: Web UI framework
- **BigQuery**: Data warehouse for Salesforce data
- **Firestore**: Session management
- **Vertex AI**: Model hosting and AI services

## Development Commands

### Local Development
```bash
# Run locally (starts both FastAPI backend and Streamlit frontend)
./run_local.sh

# Or manually:
cd src
uvicorn --app-dir web fast_api_runner:api_app --port 8000 & python3 web/main.py "agents/data_agent" "local" & wait
```

### Deployment
```bash
# Deploy to Cloud Run
./deploy_to_cloud_run.sh

# Deploy demo data to BigQuery
python3 utils/deploy_demo_data.py
```

### Environment Setup
```bash
# Install dependencies
pip install -r src/requirements.txt

# Or with uv (recommended):
uv pip install -r src/requirements.txt

# Create virtual environment with uv:
uv venv .venv --python 3.11 && source .venv/bin/activate
```

## Configuration

The application requires a `src/.env` file with these variables:
- `GOOGLE_CLOUD_PROJECT`: GCP project ID for Vertex AI
- `GOOGLE_CLOUD_LOCATION`: GCP region for Vertex AI 
- `AI_STORAGE_BUCKET`: Cloud Storage bucket for ADK assets
- `BQ_LOCATION`: BigQuery location for Salesforce datasets
- `SFDC_BQ_DATASET`: Salesforce dataset name in BigQuery
- `FIRESTORE_SESSION_DATABASE`: Firestore database for session storage

Use `src/.env-template` as a starting point.

## Key Directories

- `src/agents/data_agent/`: Main agent implementation and prompts
- `src/agents/data_agent/tools/`: Agent tools (data_engineer, bi_engineer, etc.)
- `src/web/`: Web application (FastAPI backend, Streamlit frontend)
- `src/shared/`: Shared utilities (config, session management)
- `metadata/`: Salesforce metadata and loaders
- `utils/`: Deployment and utility scripts

## Agent Development

Agents are built using ADK's `LlmAgent` class with:
- System instructions in `src/agents/data_agent/prompts/`
- Tools in `src/agents/data_agent/tools/`
- Gemini 2.5 Pro as the primary model (`ROOT_AGENT_MODEL_ID`)

The root agent coordinates sub-agents through `AgentTool` instances and maintains state through ADK's callback system.

## Data Flow

1. User query → Root Agent → determines appropriate sub-agent
2. Data Engineer → generates SQL from natural language
3. BigQuery → executes SQL against Salesforce data
4. BI Engineer → creates Vega-Lite visualizations
5. Business Analyst → provides insights and recommendations
6. Results streamed back through FastAPI/Streamlit interface