#!/bin/bash
# MCP Server Runner for CRM Data Agent

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Set up environment
export GOOGLE_APPLICATION_CREDENTIALS="${SCRIPT_DIR}/service-account-key.json"

# Change to project directory
cd "${SCRIPT_DIR}"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run the MCP server
exec python3 "${SCRIPT_DIR}/src/mcp_server/run_server.py"