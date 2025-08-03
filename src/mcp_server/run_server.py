#!/usr/bin/env python3
"""
Script to run the CRM Data Agent MCP Server
"""

import os
import sys
from pathlib import Path
import asyncio

# Set up environment
project_root = Path(__file__).parent.parent.parent
os.chdir(project_root)

# Set Google Application Credentials
service_account_path = project_root / "service-account-key.json"
if service_account_path.exists():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(service_account_path)

# Add project to Python path
sys.path.insert(0, str(project_root / "src"))

if __name__ == "__main__":
    from mcp_server.server import main
    asyncio.run(main())