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
from mcp.server.models import InitializationOptions
from mcp import types
from pydantic import BaseModel

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

# Import shared components
from shared.config_env import prepare_environment
from shared.firestore_session_service import FirestoreSessionService
from google.adk.sessions import Session
from google.adk.events import Event
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
initialized = False

# MCP Server instance
server = Server("crm-data-agent")

class CRMQueryRequest(BaseModel):
    """Request model for CRM data queries"""
    question: str
    session_id: str = None
    user_id: str = "claude-user"

class CRMQueryResponse(BaseModel):
    """Response model for CRM data queries"""
    answer: str
    sql_query: str = None
    visualization: dict = None
    insights: List[str] = []

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
    global session_service, initialized, root_agent
    if not initialized:
        # Import agent only when needed to avoid initialization issues
        from agents.data_agent.agent import root_agent as agent
        root_agent = agent
        
        session_service = FirestoreSessionService(
            database=os.environ.get("FIRESTORE_SESSION_DATABASE", "(default)"),
            project_id=os.environ.get("GOOGLE_CLOUD_PROJECT")
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
        session = await session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id
        )
        
        # Process the query through the existing agent
        result_events = []
        async for event in root_agent.run_iter(question, session):
            result_events.append(event)
            await session_service.append_event(session, event)
        
        # Extract response from events
        response_text = ""
        visualization_data = None
        sql_query = None
        
        for event in result_events:
            if event.message and event.message.content:
                for content in event.message.content:
                    if hasattr(content, 'text') and content.text:
                        response_text += content.text
            
            # Extract artifacts (charts, SQL)
            if event.actions and event.actions.artifact_delta:
                for filename, version in event.actions.artifact_delta.items():
                    if filename.endswith('.vg') or filename.endswith('.json'):
                        # This is likely a Vega-Lite chart
                        try:
                            from google.adk.artifacts import GcsArtifactService
                            artifact_service = GcsArtifactService()
                            artifact = await artifact_service.load_artifact(
                                app_name=app_name,
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
        
        # Format response for Claude
        response_parts = []
        
        # Add main analysis
        if response_text:
            response_parts.append(types.TextContent(
                type="text",
                text=f"## CRM Data Analysis\n\n{response_text}"
            ))
        
        # Add visualization if available
        if visualization_data:
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
    async with anyio.create_task_group() as tg:
        async with anyio.abc.AsyncResource.use(
            server.run(
                transport=anyio.lowlevel.FdTransport(sys.stdin, sys.stdout),
                initialization_options=InitializationOptions(
                    server_name="crm-data-agent",
                    server_version="1.0.0",
                    capabilities=server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities={}
                    )
                )
            )
        ):
            await anyio.sleep_forever()

if __name__ == "__main__":
    asyncio.run(main())