# Backend Guide

The backend is built with **Flask** and provides the REST API for the vulnerability scanner.

## Key Files
- `app.py`: Main entry point. Defines API routes and app configuration.
- `config.py`: (Assumed) Configuration settings.
- `requirements.txt`: Python dependencies.
- `scanners/`: Directory containing scanner logic (e.g., OWASP scanner).
- `ai_model/`: Directory for the AI severity prediction model.
- `integrations/`: Modules for external APIs (e.g., NVD).

## API Endpoints

### Health Check
- **GET** `/health`
- **Response**: `{ "status": "healthy", ... }`

### Scans
- **POST** `/api/scan/start`
    - Starts a new scan.
    - **Body**: `{ "scanId": 123, "url": "http://target.com" }`
    - **Returns**: JSON with initial scan results (vulnerabilities found, counts).

- **GET** `/api/scan/status/<scan_id>`
    - Gets current progress/results of a scan.
    - **Returns**: `{ "scan_status": "completed", "critical_count": 5, ... }`

### Reports
- **POST** `/api/generate-pdf`
    - Generates a PDF report.
    - **Body**: `{ "scan": {...}, "vulnerabilities": [...] }`
    - **Returns**: PDF file download.

## Database Schema
The system uses PostgreSQL. The main operations involve:
- **`scans` table**: Stores scan metadata (ID, URL, status, timestamps, counts).
- **`vulnerabilities` table**: Stores individual findings linked to a scan.
- **`cve_mappings` table**: Links vulnerabilities to real-world CVE data from NVD.

## AI Integration
The backend uses a `SeverityPredictor` class (`ai_model/severity_predictor.py`) to analyze found vulnerabilities. It predicts a severity score and confidence level to help prioritize fixes suited for the specific context.
