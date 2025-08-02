#!/bin/bash
# Deployment script for CRM Data Agent

set -e

# Configuration
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-""}
REGION=${GOOGLE_CLOUD_LOCATION:-"asia-south1"}
SERVICE_NAME="crm-data-agent"
IMAGE_NAME="crm-data-agent"

# Parse command line arguments
ENVIRONMENT="staging"
VERSION="latest"
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -v|--version)
            VERSION="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -e, --environment    Deployment environment (staging|production) [default: staging]"
            echo "  -v, --version       Image version tag [default: latest]"
            echo "  --dry-run           Show commands without executing"
            echo "  -h, --help          Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "🚀 CRM Data Agent Deployment Script"
echo "Environment: $ENVIRONMENT"
echo "Version: $VERSION"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Validate environment
if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: GOOGLE_CLOUD_PROJECT environment variable not set"
    echo "Please set it in your .env file or export it"
    exit 1
fi

# Set service name based on environment
if [ "$ENVIRONMENT" = "production" ]; then
    FULL_SERVICE_NAME="${SERVICE_NAME}-prod"
    MIN_INSTANCES=1
    MAX_INSTANCES=10
    MEMORY="2Gi"
    CPU="2"
else
    FULL_SERVICE_NAME="${SERVICE_NAME}-staging"
    MIN_INSTANCES=0
    MAX_INSTANCES=5
    MEMORY="1Gi"
    CPU="1"
fi

# Build Docker image
echo "🔨 Building Docker image..."
BUILD_CMD="docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/crm-agent/$IMAGE_NAME:$VERSION ."

if [ "$DRY_RUN" = true ]; then
    echo "[DRY RUN] $BUILD_CMD"
else
    eval $BUILD_CMD
fi

# Push Docker image
echo "📤 Pushing Docker image..."
PUSH_CMD="docker push $REGION-docker.pkg.dev/$PROJECT_ID/crm-agent/$IMAGE_NAME:$VERSION"

if [ "$DRY_RUN" = true ]; then
    echo "[DRY RUN] $PUSH_CMD"
else
    eval $PUSH_CMD
fi

# Deploy to Cloud Run
echo "☁️ Deploying to Cloud Run..."
DEPLOY_CMD="gcloud run deploy $FULL_SERVICE_NAME \\
    --image $REGION-docker.pkg.dev/$PROJECT_ID/crm-agent/$IMAGE_NAME:$VERSION \\
    --platform managed \\
    --region $REGION \\
    --allow-unauthenticated \\
    --memory $MEMORY \\
    --cpu $CPU \\
    --min-instances $MIN_INSTANCES \\
    --max-instances $MAX_INSTANCES \\
    --set-env-vars AGENT_NAME=crm_data_agent,GOOGLE_GENAI_USE_VERTEXAI=1 \\
    --set-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID \\
    --set-env-vars GOOGLE_CLOUD_LOCATION=$REGION \\
    --tag $VERSION"

if [ "$DRY_RUN" = true ]; then
    echo "[DRY RUN] $DEPLOY_CMD"
else
    eval $DEPLOY_CMD
fi

# Get service URL
echo "🔗 Getting service URL..."
URL_CMD="gcloud run services describe $FULL_SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)'"

if [ "$DRY_RUN" = true ]; then
    echo "[DRY RUN] $URL_CMD"
    SERVICE_URL="https://example-service-url.a.run.app"
else
    SERVICE_URL=$(eval $URL_CMD)
fi

echo ""
echo "✅ Deployment completed successfully!"
echo "🔗 Service URL: $SERVICE_URL"
echo "📦 Image: $IMAGE_NAME:$VERSION"
echo "🏷️ Environment: $ENVIRONMENT"
echo ""

if [ "$ENVIRONMENT" = "production" ]; then
    echo "🎉 Production deployment live!"
    echo "🔒 Remember to configure authentication if needed"
else
    echo "🧪 Staging deployment ready for testing"
fi

# Basic health check
if [ "$DRY_RUN" = false ]; then
    echo "🏥 Running basic health check..."
    sleep 10
    if curl -f -s "$SERVICE_URL" > /dev/null; then
        echo "✅ Health check passed"
    else
        echo "⚠️ Health check failed - service may still be starting"
    fi
fi