# Claude MCP Integration Setup

This guide shows how to connect your CRM Data Agent to Claude Desktop via MCP (Model Context Protocol).

## Overview

The MCP server exposes your existing CRM Data Agent functionality to Claude, allowing you to:
- Ask natural language questions about CRM data
- Get multi-agent analysis (Business Analyst + Data Engineer + BI Engineer)
- Generate SQL queries and execute them against BigQuery
- Create interactive Vega-Lite visualizations as Claude Artifacts
- Receive business insights and recommendations

## Prerequisites

1. **Claude Desktop** installed on your machine
2. **CRM Data Agent** running locally (as per main setup)
3. **Google Cloud credentials** properly configured

## Setup Steps

### 1. Install MCP Dependencies

The MCP dependencies have already been added to `requirements.txt`. If not installed:

```bash
cd /path/to/crm-data-agent
source .venv/bin/activate
pip install mcp httpx anyio
```

### 2. Configure Claude Desktop

Claude Desktop configuration is located at:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Add this configuration to your Claude Desktop config file:

```json
{
  "mcpServers": {
    "crm-data-agent": {
      "command": "python3",
      "args": [
        "/Users/siddhanshsarkar/Google ADK - Business Intelligence/crm-data-agent/src/mcp_server/run_server.py"
      ],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "/Users/siddhanshsarkar/Google ADK - Business Intelligence/crm-data-agent/service-account-key.json"
      }
    }
  }
}
```

**Important**: Update the paths to match your actual project location.

### 3. Test the Setup

1. **Restart Claude Desktop** after updating the config
2. **Open a new conversation** in Claude
3. **Test the connection** with a simple query:

```
Can you analyze our CRM data? Show me the top 5 customers by revenue.
```

Claude should:
- Connect to your MCP server
- Use the CRM Data Agent tools
- Return analysis with potential visualizations

## Available Tools

### `analyze_crm_data`
Analyze CRM data using natural language queries. Orchestrates the full multi-agent workflow.

**Example queries:**
- "What are the top 5 customers by revenue?"
- "Show me lead conversion trends by source"
- "Which regions have the highest sales performance?"
- "What's our customer acquisition cost by channel?"

### `get_crm_insights`
Get business insights and strategic recommendations.

**Example usage:**
- "Give me insights on sales performance"
- "What are the key trends in customer behavior?"
- "Provide recommendations for improving lead conversion"

## Expected Experience

When you ask Claude a CRM question:

1. **Claude calls the MCP tool** (`analyze_crm_data`)
2. **Your CRM agent orchestrates**:
   - CRM Business Analyst defines requirements
   - Data Engineer generates SQL queries
   - BI Engineer executes queries and creates visualizations
3. **Claude receives**:
   - Natural language analysis
   - Vega-Lite visualization JSON
   - Business insights and recommendations
4. **Claude renders**:
   - Text response with insights
   - Interactive charts as Artifacts (if visualizations generated)

## Troubleshooting

### Connection Issues
- Verify Claude Desktop config path is correct
- Check that Python path in config matches your Python installation
- Ensure service account file path is correct

### Authentication Errors
- Verify `GOOGLE_APPLICATION_CREDENTIALS` points to valid service account key
- Check that service account has necessary permissions (Firestore, BigQuery, Vertex AI)

### Tool Not Found
- Restart Claude Desktop after config changes
- Check logs in Claude Desktop for MCP server startup errors

### Data Access Issues
- Ensure your BigQuery dataset is accessible
- Verify Firestore database exists and is accessible
- Check that environment variables in `.env` are correct

## Advanced Configuration

### Custom Prompts
You can modify the system instructions in your agent to customize responses specifically for Claude users.

### Extended Tools
Add more MCP tools to expose additional functionality like:
- Data export capabilities
- Custom report generation
- Integration with other systems

## Benefits

Using Claude as your interface provides:
- **Superior UX**: Professional chat interface with no development needed
- **Artifacts**: Beautiful rendering of Vega-Lite charts
- **Context**: Claude's conversation memory and understanding
- **Multimodal**: Can handle text, images, and other content types
- **Sharing**: Easy sharing of conversations and insights