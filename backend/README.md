# VulnScan AI - Python Backend

## Overview
Flask-based vulnerability scanning backend targeting OWASP Top 10:2025 vulnerabilities.

## Features
- Automated vulnerability detection
- AI-powered severity prediction
- NVD API integration for CVE/CWE data
- PostgreSQL database integration
- RESTful API design

## Setup Instructions

### Local Development

1. Install dependencies:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

2. Set environment variables:
\`\`\`bash
export DATABASE_URL="your-postgresql-connection-string"
\`\`\`

3. Run the server:
\`\`\`bash
python app.py
\`\`\`

### Deployment on Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `gunicorn app:app`
5. Add environment variable: `DATABASE_URL`

### Deployment on Railway

1. Create a new project on Railway
2. Connect your GitHub repository
3. Railway will auto-detect Python and use the Dockerfile
4. Add environment variable: `DATABASE_URL`

### Deployment on Heroku

1. Install Heroku CLI
2. Create a new app:
\`\`\`bash
heroku create vulnscan-backend
\`\`\`

3. Add PostgreSQL addon:
\`\`\`bash
heroku addons:create heroku-postgresql:hobby-dev
\`\`\`

4. Deploy:
\`\`\`bash
git push heroku main
\`\`\`

## API Endpoints

### Health Check
\`\`\`
GET /health
\`\`\`

### Start Scan
\`\`\`
POST /api/scan/start
Body: { "scanId": 123, "url": "https://example.com" }
\`\`\`

### Get Scan Status
\`\`\`
GET /api/scan/status/<scan_id>
\`\`\`

## Security Notes
- Always use HTTPS in production
- Configure CORS appropriately
- Keep dependencies updated
- Use environment variables for sensitive data
