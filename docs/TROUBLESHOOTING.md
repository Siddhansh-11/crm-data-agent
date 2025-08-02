# Troubleshooting Guide

## Errors Encountered During Setup

### 1. Google Authentication Error

**Error Message**:
```
google.auth.exceptions.DefaultCredentialsError: Your default credentials were not found
```

**Root Cause**: 
The application couldn't find Google Cloud credentials because the `GOOGLE_APPLICATION_CREDENTIALS` environment variable wasn't set.

**Solution**:
1. Ensure service account key file exists: `service-account-key.json`
2. Set the environment variable:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
   ```
3. Updated `run_local.sh` to automatically set this variable

**Verification**:
```bash
python3 test_firestore_auth.py
```

### 2. Firestore Database Not Found

**Error Message**:
```
google.api_core.exceptions.NotFound: 404 The database crm-agent-sessions does not exist for project vital-domain-467705-i6
```

**Root Cause**: 
Mismatch between the Firestore database name in `.env-template` and the actual database name.

**Solution**:
1. Updated `.env` file to use the correct database name:
   ```
   FIRESTORE_SESSION_DATABASE="(default)"
   ```
2. Ensured the Firestore database was created in the correct region (asia-south1)

### 3. Region Configuration Mismatch

**Initial Configuration**:
- `.env` had `GOOGLE_CLOUD_LOCATION="us-central1"`
- Firestore was created in `asia-south1`

**Solution**:
Updated `.env` to match the Firestore region:
```
GOOGLE_CLOUD_LOCATION="asia-south1"
```

### 4. Application Not Accessible on Localhost

**Symptoms**:
- Application appeared to start but localhost URLs weren't working
- No processes found on ports 8000 or 8080

**Root Cause**: 
Application crashed due to authentication/configuration errors

**Solution**:
1. Fixed authentication by setting `GOOGLE_APPLICATION_CREDENTIALS`
2. Cleaned up stray processes:
   ```bash
   pkill -f "uvicorn.*fast_api_runner"
   pkill -f "streamlit run"
   pkill -f "python.*main.py"
   ```
3. Cleared log files and restarted with proper configuration

## Common Issues and Solutions

### Port Already in Use
```bash
# Find and kill processes on specific ports
lsof -i :8000 -i :8080
kill -9 <PID>
```

### Service Account Permissions
Ensure the service account has these roles:
- `roles/datastore.user` - For Firestore access
- `roles/bigquery.dataViewer` - For BigQuery read access
- `roles/bigquery.jobUser` - For running BigQuery jobs
- `roles/aiplatform.user` - For Vertex AI access
- `roles/storage.objectUser` - For Cloud Storage access

### Firestore Connection Test
Use the provided test script to verify Firestore connectivity:
```bash
python3 test_firestore_auth.py
```

Expected output:
```
✓ Successfully wrote test document
✓ Successfully read test document
✓ Successfully deleted test document
✅ Firestore authentication and connection successful!
```

### Browser Access Issues
If localhost URLs don't work in browser:
1. Try `http://127.0.0.1:8080` instead of `localhost:8080`
2. Clear browser cache and cookies
3. Try incognito/private browsing mode
4. Check for browser extensions blocking local connections
5. Ensure no VPN or proxy is interfering

### Log File Locations
- FastAPI logs: `fastapi.log`, `fastapi_startup.log`
- Streamlit logs: `streamlit.log`, `streamlit_startup.log`

### Environment Variable Issues
Always ensure `.env` file is in the `src/` directory, not the root directory.

## Debugging Commands

### Check Running Processes
```bash
ps aux | grep -E "(streamlit|uvicorn|python.*main\.py|fast_api)" | grep -v grep
```

### Check Port Status
```bash
lsof -i :8000 -i :8080
```

### View Recent Logs
```bash
tail -f streamlit.log
tail -f fastapi.log
```

### Test Individual Components
```bash
# Test FastAPI only
cd src && uvicorn --app-dir web fast_api_runner:api_app --port 8000

# Test Streamlit only
cd src && python3 web/main.py "agents/data_agent" "local"
```