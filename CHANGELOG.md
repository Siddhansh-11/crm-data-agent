# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Documentation structure with setup checkpoint and troubleshooting guides
- Test script for Firestore authentication verification
- CI/CD pipeline configuration (in progress)

### Changed
- Updated `run_local.sh` to automatically set `GOOGLE_APPLICATION_CREDENTIALS`
- Modified `.env` configuration to use asia-south1 region

### Fixed
- Google authentication error by properly setting credentials
- Firestore database connection using correct database name
- Application startup issues on localhost

## [0.1.0] - 2025-08-02

### Added
- Initial CRM Data Q&A Agent implementation using Google ADK
- Multi-agent architecture with specialized agents:
  - Root Agent for orchestration
  - Data Engineer for SQL generation
  - BI Engineer for Vega-Lite visualizations
  - CRM Business Analyst for insights
  - Chart Evaluator for validation
- Streamlit web interface for user interactions
- FastAPI backend for agent communication
- Firestore integration for session management
- BigQuery integration for Salesforce data queries
- Real-time stock ticker display in UI
- Interactive Vega-Lite chart generation
- Natural Language to SQL conversion capabilities

### Configuration
- Set up for Google Cloud Project: vital-domain-467705-i6
- Configured Firestore in asia-south1 (Mumbai) region
- Integrated with Vertex AI for Gemini 2.5 Pro model
- Established BigQuery connection for Salesforce data

### Security
- Implemented service account authentication
- Added proper credential management
- Secured API endpoints with authentication

[Unreleased]: https://github.com/Siddhansh-11/crm-data-agent/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Siddhansh-11/crm-data-agent/releases/tag/v0.1.0