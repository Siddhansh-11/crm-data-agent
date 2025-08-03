#!/usr/bin/env python3
"""
Script to run the CRM Data Agent MCP Server
"""

import os
import sys
from pathlib import Path
import asyncio
import logging

# Set up logging to stderr for Claude to see
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Set up environment
project_root = Path(__file__).parent.parent.parent
os.chdir(project_root)
logger.info(f"Project root: {project_root}")

# Set Google Application Credentials if not already set
if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
    service_account_path = project_root / "service-account-key.json"
    if service_account_path.exists():
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(service_account_path)
        logger.info(f"Set GOOGLE_APPLICATION_CREDENTIALS to: {service_account_path}")
    else:
        logger.error(f"Service account file not found at: {service_account_path}")
else:
    logger.info(f"Using existing GOOGLE_APPLICATION_CREDENTIALS: {os.environ['GOOGLE_APPLICATION_CREDENTIALS']}")

# Add project to Python path
sys.path.insert(0, str(project_root / "src"))

# Load .env file if it exists
env_file = project_root / "src" / ".env"
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(env_file)
    logger.info(f"Loaded environment variables from: {env_file}")
else:
    logger.warning(f".env file not found at: {env_file}")

# Log key environment variables for debugging
logger.info(f"GOOGLE_CLOUD_PROJECT: {os.environ.get('GOOGLE_CLOUD_PROJECT', 'NOT SET')}")
logger.info(f"FIRESTORE_SESSION_DATABASE: {os.environ.get('FIRESTORE_SESSION_DATABASE', 'NOT SET')}")

if __name__ == "__main__":
    try:
        from mcp_server.server import main
        logger.info("Starting MCP server...")
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}", exc_info=True)
        sys.exit(1)