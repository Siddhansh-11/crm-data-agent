#!/usr/bin/env python3
"""
MCP Server for CRM Data Agent

This server exposes the existing CRM Data Agent functionality through MCP protocol,
allowing Claude to interact with the multi-agent system for business intelligence queries.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

import anyio
from mcp.server import Server
from mcp import types

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

# Import shared components
from shared.config_env import prepare_environment
from shared.firestore_session_service import FirestoreSessionService
from google.adk.sessions import Session
from google.adk.events import Event
from google.adk.runners import Runner
from google.adk.artifacts import GcsArtifactService
from google.adk.memory import InMemoryMemoryService
from google.genai.types import Content, Part
import uuid
import os

# Agent will be imported lazily
root_agent = None

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize environment
prepare_environment()

# Global variables that will be initialized when server starts
session_service = None
artifact_service = None
memory_service = None
runner = None
initialized = False

# MCP Server instance
server = Server("crm-data-agent")

def format_agent_workflow(question: str, function_calls: list, function_responses: list, final_response: str) -> str:
    """Format the multi-agent workflow into a rich, demo-ready response for Claude"""
    
    workflow_content = f"# 🤖 Multi-Agent CRM Analysis Workflow\n\n"
    workflow_content += f"**Question**: {question}\n\n"
    workflow_content += "---\n\n"
    
    # Process function calls and responses in order
    agent_steps = {}
    
    # Map function calls to their responses
    for fc in function_calls:
        agent_name = fc.name
        if agent_name not in agent_steps:
            agent_steps[agent_name] = {'call': fc, 'response': None}
    
    for fr in function_responses:
        agent_name = fr.name
        if agent_name in agent_steps:
            agent_steps[agent_name]['response'] = fr
    
    # Format each agent step
    agent_icons = {
        'crm_business_analyst': '📊 **Business Analyst**',
        'data_engineer': '⚡ **Data Engineer**', 
        'bi_engineer_tool': '📈 **BI Engineer**'
    }
    
    step_num = 1
    for agent_name, step_data in agent_steps.items():
        agent_title = agent_icons.get(agent_name, f"🔧 **{agent_name}**")
        workflow_content += f"## Step {step_num}: {agent_title}\n\n"
        
        # Show agent input/request
        if step_data['call'] and hasattr(step_data['call'], 'args'):
            workflow_content += "### 📥 Input:\n"
            args = step_data['call'].args
            if isinstance(args, dict):
                for key, value in args.items():
                    # Truncate very long values for readability
                    if isinstance(value, str) and len(value) > 200:
                        value = value[:200] + "..."
                    workflow_content += f"- **{key}**: {value}\n"
            else:
                workflow_content += f"```\n{args}\n```\n"
            workflow_content += "\n"
        
        # Show agent response/output
        if step_data['response'] and hasattr(step_data['response'], 'response'):
            workflow_content += "### 📤 Output:\n"
            response_data = step_data['response'].response
            
            # Handle different response formats
            if isinstance(response_data, dict):
                # Pretty format structured responses (like from data_engineer)
                if 'sql_code' in response_data:
                    workflow_content += "**SQL Query Generated:**\n"
                    workflow_content += f"```sql\n{response_data['sql_code']}\n```\n\n"
                if 'sql_code_file_name' in response_data:
                    workflow_content += f"**File**: `{response_data['sql_code_file_name']}`\n\n"
                if 'result' in response_data:
                    workflow_content += "**Analysis Result:**\n"
                    result_text = response_data['result']
                    if len(result_text) > 500:
                        result_text = result_text[:500] + "...\n\n*[Truncated for readability]*"
                    workflow_content += f"{result_text}\n\n"
            elif isinstance(response_data, str):
                # Handle text responses (like from business analyst)
                if len(response_data) > 500:
                    response_data = response_data[:500] + "...\n\n*[Truncated for readability]*"
                workflow_content += f"{response_data}\n\n"
            else:
                workflow_content += f"```\n{response_data}\n```\n\n"
        
        workflow_content += "---\n\n"
        step_num += 1
    
    # Add final integrated analysis
    if final_response:
        workflow_content += f"## 🎯 Final Integrated Analysis\n\n{final_response}\n\n"
        workflow_content += "---\n\n"
    
    workflow_content += "## 💡 Workflow Summary\n\n"
    workflow_content += "This analysis demonstrates our sophisticated **multi-agent architecture**:\n\n"
    workflow_content += "1. 📊 **Business Analyst** interpreted your question and defined the analytical approach\n"
    workflow_content += "2. ⚡ **Data Engineer** generated optimized SQL queries and executed them against BigQuery\n"
    workflow_content += "3. 📈 **BI Engineer** processed the data and created visualizations\n"
    workflow_content += "4. 🤖 **Root Agent** synthesized all inputs into actionable business insights\n\n"
    workflow_content += "*Each agent specializes in their domain, ensuring expert-level analysis at every step.*"
    
    return workflow_content


@server.list_tools()
async def list_tools() -> List[types.Tool]:
    """List available tools for the CRM Data Agent"""
    return [
        types.Tool(
            name="analyze_crm_data",
            description="""
            Analyze CRM data using natural language queries. This tool orchestrates a team of specialized AI agents:
            - CRM Business Analyst: Defines metrics and data requirements
            - Data Engineer: Generates SQL queries for BigQuery
            - BI Engineer: Executes queries and creates Vega-Lite visualizations
            
            Capabilities:
            - Answer questions about customers, leads, opportunities, and sales performance
            - Generate interactive charts and visualizations
            - Provide business insights and recommendations
            - Handle complex multi-dimensional analysis
            
            Examples:
            - "What are the top 5 customers by revenue?"
            - "Show me lead conversion trends by source"
            - "Which regions have the highest sales performance?"
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Natural language question about CRM data"
                    }
                },
                "required": ["question"]
            }
        ),
        types.Tool(
            name="get_crm_insights",
            description="""
            Get business insights and recommendations based on CRM data analysis.
            This tool provides executive-level summaries and actionable recommendations.
            
            Use this tool to:
            - Summarize key business metrics
            - Identify trends and patterns
            - Get strategic recommendations
            - Understand business performance drivers
            """,
            inputSchema={
                "type": "object", 
                "properties": {
                    "focus_area": {
                        "type": "string",
                        "description": "Area to focus insights on (e.g., 'sales performance', 'customer analysis', 'lead conversion')",
                        "default": "overall business performance"
                    }
                },
                "required": []
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool calls from Claude"""
    try:
        if name == "analyze_crm_data":
            return await handle_crm_analysis(arguments)
        elif name == "get_crm_insights":
            return await handle_crm_insights(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        logger.error(f"Error in tool call {name}: {str(e)}")
        return [types.TextContent(
            type="text",
            text=f"Error processing request: {str(e)}"
        )]

async def initialize_services():
    """Initialize services when needed"""
    global session_service, artifact_service, memory_service, runner, initialized, root_agent
    if not initialized:
        # Import agent only when needed to avoid initialization issues
        from agents.data_agent.agent import root_agent as agent
        root_agent = agent
        
        # Initialize services
        session_service = FirestoreSessionService(
            database=os.environ.get("FIRESTORE_SESSION_DATABASE", "(default)"),
            project_id=os.environ.get("GOOGLE_CLOUD_PROJECT")
        )
        
        artifact_service = GcsArtifactService(
            bucket_name=os.environ.get("AI_STORAGE_BUCKET", "my-crm-agent-assets-101")
        )
        
        memory_service = InMemoryMemoryService()
        
        # Create runner
        runner = Runner(
            app_name="crm_data_agent",
            agent=root_agent,
            artifact_service=artifact_service,
            session_service=session_service,
            memory_service=memory_service
        )
        
        initialized = True

async def handle_crm_analysis(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle CRM data analysis requests"""
    await initialize_services()
    
    question = arguments.get("question", "")
    
    if not question:
        return [types.TextContent(
            type="text", 
            text="Please provide a question about CRM data to analyze."
        )]
    
    # Create or get session
    session_id = str(uuid.uuid4())
    user_id = "claude-user"
    app_name = "crm_data_agent"
    
    try:
        # Create session first
        session = await session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id
        )
        
        # Create Content object for the message
        content = Content(
            parts=[Part.from_text(text=question)],
            role="user"
        )
        
        # Set MCP caller flag for BI Engineer
        os.environ["CALLER_SOURCE"] = "mcp_claude"
        
        # Process the query through the runner
        result_events = []
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        ):
            result_events.append(event)
        
        # Extract response from events with detailed workflow tracking
        response_text = ""
        visualization_data = None
        recharts_component = None
        sql_query = None
        workflow_steps = []
        function_calls = []
        function_responses = []
        
        for event in result_events:
            # Process events with content (following Streamlit pattern)
            if event.content and event.content.parts:
                # Only process model responses, skip user events
                if event.content.role == "model":
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            response_text += part.text
                        
                        # Extract function calls and responses (like Streamlit)
                        if hasattr(part, 'function_call') and part.function_call:
                            function_calls.append(part.function_call)
                        elif hasattr(part, 'function_response') and part.function_response:
                            function_responses.append(part.function_response)
            
            # Extract artifacts (charts, SQL)
            if event.actions and event.actions.artifact_delta:
                for filename, version in event.actions.artifact_delta.items():
                    if filename.endswith('.recharts.jsx'):
                        # Recharts component for Claude
                        try:
                            artifact = await artifact_service.load_artifact(
                                app_name="crm_data_agent",
                                user_id=user_id,
                                session_id=session_id,
                                filename=filename,
                                version=version
                            )
                            if artifact.inline_data:
                                recharts_component = artifact.inline_data.data.decode('utf-8')
                        except Exception as e:
                            logger.warning(f"Could not load Recharts artifact {filename}: {e}")
                    elif filename.endswith('.vg') or filename.endswith('.json'):
                        # This is likely a Vega-Lite chart
                        try:
                            artifact = await artifact_service.load_artifact(
                                app_name="crm_data_agent",
                                user_id=user_id,
                                session_id=session_id,
                                filename=filename,
                                version=version
                            )
                            if artifact.inline_data:
                                viz_text = artifact.inline_data.data.decode('utf-8')
                                try:
                                    visualization_data = json.loads(viz_text)
                                except json.JSONDecodeError:
                                    pass
                        except Exception as e:
                            logger.warning(f"Could not load artifact {filename}: {e}")
        
        # Format rich workflow response for Claude
        response_parts = []
        
        # Add detailed workflow if we have function calls/responses
        if function_calls or function_responses:
            workflow_content = format_agent_workflow(
                question, function_calls, function_responses, response_text
            )
            response_parts.append(types.TextContent(
                type="text",
                text=workflow_content
            ))
        elif response_text:
            # Fallback to basic response if no workflow details
            response_parts.append(types.TextContent(
                type="text",
                text=f"## CRM Data Analysis\n\n{response_text}"
            ))
        
        # Add visualization - prioritize Recharts for Claude
        if recharts_component:
            response_parts.append(types.TextContent(
                type="text",
                text=f"## 📊 Interactive Visualization\n\nCreate a React artifact with this code:\n\n```jsx\n{recharts_component}\n```"
            ))
        elif visualization_data:
            response_parts.append(types.TextContent(
                type="text", 
                text=f"## Interactive Visualization\n\n```json\n{json.dumps(visualization_data, indent=2)}\n```\n\n*This Vega-Lite specification can be rendered as an interactive chart.*"
            ))
        
        if not response_parts:
            response_parts.append(types.TextContent(
                type="text",
                text="Analysis completed, but no response was generated. Please try rephrasing your question."
            ))
            
        return response_parts
        
    except Exception as e:
        logger.error(f"Error processing CRM analysis: {str(e)}")
        return [types.TextContent(
            type="text",
            text=f"Error analyzing CRM data: {str(e)}. Please check your question and try again."
        )]
    finally:
        # Clean up environment variable
        if "CALLER_SOURCE" in os.environ:
            del os.environ["CALLER_SOURCE"]

async def handle_crm_insights(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle CRM insights requests"""
    await initialize_services()
    
    focus_area = arguments.get("focus_area", "overall business performance")
    
    insight_question = f"Provide key business insights and recommendations focusing on {focus_area}. Include top metrics, trends, and actionable recommendations."
    
    # Reuse the analysis handler
    return await handle_crm_analysis({"question": insight_question})

async def main():
    """Main entry point for the MCP server"""
    # Use stdio transport for Claude Desktop integration
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())