# Docker Setup for CRM Data Agent

This document provides instructions for running the CRM Data Agent using Docker on any device, including your Mac Mini.

## Prerequisites

1. **Docker and Docker Compose**: Install Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop/)
2. **Google Cloud Credentials**: Ensure you have a `service-account-key.json` file in the root directory
3. **Environment Configuration**: Set up your `.env` file in the `src/` directory (use `src/.env-template` as reference)

## Quick Start

### 1. Basic Web Interface

Run the CRM Data Agent with Streamlit web interface:

```bash
# Build and start the service
docker-compose up --build crm-data-agent

# Or run in detached mode
docker-compose up -d crm-data-agent
```

Access the application at: http://localhost:8000

### 2. MCP Server (Claude Desktop Integration)

Run the MCP server for Claude Desktop integration:

```bash
# Start MCP server
docker-compose --profile mcp up --build mcp-server
```

The MCP server will be available at port 8080.

### 3. Development Mode

For development with hot reload:

```bash
# Start development service with volume mounting
docker-compose --profile dev up --build crm-data-agent-dev
```

Access at: http://localhost:8001

## Configuration

### Environment Variables

Create a `src/.env` file with these required variables:

```bash
AGENT_NAME="crm_data_agent"
GOOGLE_GENAI_USE_VERTEXAI=1

# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT="your-project-id"
GOOGLE_CLOUD_LOCATION="us-central1"
AI_STORAGE_BUCKET="your-bucket-name"

# BigQuery Configuration
BQ_LOCATION="US"
SFDC_BQ_DATASET="sfdc_data"

# Firestore Configuration
FIRESTORE_SESSION_DATABASE="crm-agent-sessions"

# Metadata
SFDC_METADATA_FILE="sfdc_metadata.json"
GOOGLE_API_KEY="your-api-key"
```

### Service Account Key

Place your Google Cloud service account key file as `service-account-key.json` in the root directory.

## Docker Commands Reference

### Building

```bash
# Build the image
docker-compose build

# Build with no cache
docker-compose build --no-cache
```

### Running Services

```bash
# Start main web interface
docker-compose up crm-data-agent

# Start MCP server
docker-compose --profile mcp up mcp-server

# Start development mode
docker-compose --profile dev up crm-data-agent-dev

# Run all profiles
docker-compose --profile mcp --profile dev up

# Run in background
docker-compose up -d crm-data-agent
```

### Management

```bash
# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# View logs
docker-compose logs crm-data-agent

# Follow logs
docker-compose logs -f crm-data-agent

# Execute commands in running container
docker-compose exec crm-data-agent bash
```

## Direct Docker Commands

If you prefer using Docker directly instead of Docker Compose:

### Build Image

```bash
cd src
docker build -t crm-data-agent .
```

### Run Container

```bash
# Web interface
docker run -p 8000:8000 \
  --env-file src/.env \
  -v $(pwd)/service-account-key.json:/app/service-account-key.json:ro \
  -v $(pwd)/src/.env:/app/.env:ro \
  crm-data-agent

# MCP server
docker run -p 8080:8080 \
  --env-file src/.env \
  -v $(pwd)/service-account-key.json:/app/service-account-key.json:ro \
  -v $(pwd)/src/.env:/app/.env:ro \
  crm-data-agent python3 mcp_server/run_server.py
```

## Service Endpoints

- **Web Interface**: http://localhost:8000
- **FastAPI Backend**: http://localhost:8000/docs (API documentation)
- **MCP Server**: http://localhost:8080
- **Development**: http://localhost:8001

## Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   # Stop conflicting services
   docker-compose down
   # Or use different ports by modifying docker-compose.yml
   ```

2. **Permission denied for service account**:
   ```bash
   # Ensure service-account-key.json has correct permissions
   chmod 600 service-account-key.json
   ```

3. **Environment variables not loaded**:
   ```bash
   # Check .env file exists and has correct values
   cat src/.env
   ```

4. **Health check failures**:
   ```bash
   # Check application logs
   docker-compose logs crm-data-agent
   ```

### Debug Mode

Run with debug output:

```bash
docker-compose up --build crm-data-agent | tee docker-debug.log
```

### Container Shell Access

```bash
# Access running container
docker-compose exec crm-data-agent bash

# Or start a temporary container
docker run -it --entrypoint bash crm-data-agent
```

## Performance Considerations

### Mac Mini Specific

- **Memory**: The application uses ~2-4GB RAM. Ensure Docker has sufficient memory allocated.
- **CPU**: Multi-core processing is utilized. Consider adjusting worker count in production.
- **Storage**: Container images are ~2-3GB. Ensure adequate disk space.

### Production Optimizations

1. **Multi-stage builds**: Already implemented in Dockerfile
2. **Layer caching**: Dependencies installed before code copy
3. **Non-root user**: Security best practice implemented
4. **Health checks**: Built-in health monitoring

## Integration with Existing Scripts

The Docker setup maintains compatibility with existing scripts:

- `run_local.sh` equivalent: `docker-compose up crm-data-agent`
- `run_mcp_server.sh` equivalent: `docker-compose --profile mcp up mcp-server`

## Next Steps

1. Test the setup: `docker-compose up --build crm-data-agent`
2. Verify web interface at http://localhost:8000
3. Test MCP integration with Claude Desktop
4. Consider setting up automated deployments for production use

For more detailed information, refer to the main project documentation in `CLAUDE.md` and `README.md`.