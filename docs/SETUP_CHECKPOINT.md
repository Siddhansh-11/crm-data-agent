# Setup Checkpoint Documentation

## Current Status: ✅ Application Running Successfully

**Date**: August 2, 2025  
**Environment**: Local Development  
**Application URLs**:
- Streamlit UI: http://localhost:8080
- FastAPI Backend: http://localhost:8000

## Configuration Summary

### Google Cloud Configuration
- **Project ID**: `vital-domain-467705-i6`
- **Region**: `asia-south1` (Mumbai)
- **Service Account**: `crm-agent@vital-domain-467705-i6.iam.gserviceaccount.com`

### Firestore Configuration
- **Database Name**: `(default)`
- **Mode**: Firestore Native
- **Region**: `asia-south1` (Mumbai)
- **Status**: ✅ Connected and operational

### BigQuery Configuration
- **Location**: `US`
- **Salesforce Dataset**: `sfdc_data`

### Environment Variables
```bash
AGENT_NAME="crm_data_agent"
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT="vital-domain-467705-i6"
GOOGLE_CLOUD_LOCATION="asia-south1"
AI_STORAGE_BUCKET="my-crm-agent-assets-101"
BQ_LOCATION="US"
SFDC_BQ_DATASET="sfdc_data"
FIRESTORE_SESSION_DATABASE="(default)"
SFDC_METADATA_FILE="sfdc_metadata.json"
GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

## Service Account Setup

### Required Permissions
The service account `crm-agent@vital-domain-467705-i6.iam.gserviceaccount.com` has been configured with:
- Firestore access permissions
- BigQuery access permissions
- Vertex AI access permissions
- Cloud Storage access permissions

### Authentication Method
- Using service account key file: `service-account-key.json`
- Set via `GOOGLE_APPLICATION_CREDENTIALS` environment variable

## Application Components

### 1. FastAPI Backend (Port 8000)
- **Status**: Running
- **Process**: Uvicorn server
- **Endpoints**: 
  - `/api/agent` - Agent API endpoint
  - `/run_sse` - Server-sent events for streaming responses

### 2. Streamlit Frontend (Port 8080)
- **Status**: Running
- **Features**:
  - Interactive chat interface
  - Real-time stock ticker display
  - Session management via Firestore
  - Vega-Lite chart rendering

## Verification Tests Performed

### 1. Firestore Connection Test
```python
# Test script: test_firestore_auth.py
# Result: ✅ Successfully connected, wrote, read, and deleted test document
```

### 2. Application Startup
```bash
# Command: ./run_local.sh
# Result: ✅ Both FastAPI and Streamlit started successfully
```

### 3. HTTP Endpoint Tests
- FastAPI health: `curl http://localhost:8000` → 404 (expected for root)
- Streamlit UI: `curl -I http://localhost:8080` → 200 OK

## Next Steps

1. Deploy demo data to BigQuery using `utils/deploy_demo_data.py`
2. Test the agent with sample queries
3. Set up continuous deployment pipeline
4. Configure monitoring and logging

## Notes

- The application uses Gemini 2.5 Pro via Vertex AI
- Session data is stored in Firestore for persistence
- The agent can interpret business questions and generate SQL queries
- Interactive Vega-Lite charts are generated for data visualization