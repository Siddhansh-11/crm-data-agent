#!/bin/bash
# Environment setup script for CRM Data Agent

set -e

echo "🚀 Setting up CRM Data Agent environment..."

# Check if we're in the right directory
if [ ! -f "CLAUDE.md" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.11 or higher is required. Found: $python_version"
    exit 1
fi

echo "✓ Python version check passed: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r src/requirements.txt

# Install development dependencies
echo "🔧 Installing development dependencies..."
pip install ruff pytest pytest-cov mypy types-requests bandit safety

# Check if .env file exists
if [ ! -f "src/.env" ]; then
    echo "⚠️ Warning: .env file not found. Creating from template..."
    cp src/.env-template src/.env
    echo "📝 Please edit src/.env with your configuration values"
else
    echo "✓ .env file exists"
fi

# Check if service account key exists
if [ ! -f "service-account-key.json" ]; then
    echo "⚠️ Warning: service-account-key.json not found"
    echo "📝 Please place your Google Cloud service account key file in the project root"
else
    echo "✓ Service account key file exists"
fi

# Set execute permissions for scripts
echo "🔧 Setting script permissions..."
chmod +x run_local.sh
chmod +x deploy_to_cloud_run.sh
chmod +x scripts/*.sh

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p data

echo ""
echo "✅ Environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit src/.env with your configuration values"
echo "2. Place your service-account-key.json in the project root"
echo "3. Run './run_local.sh' to start the application"
echo ""
echo "For troubleshooting, see docs/TROUBLESHOOTING.md"