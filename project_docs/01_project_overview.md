# Project Overview

## Introduction
VulnScan AI is an automated web vulnerability scanning system designed to detect security flaws in web applications. It specifically targets the **OWASP Top 10:2025** vulnerabilities, utilizing both traditional pattern matching and AI-powered analysis to predict severity and reduce false positives.

## Core Features
- **Automated Scanning**: Scans target URLs for common vulnerabilities.
- **AI-Powered Analysis**: Uses a machine learning model to predict the severity of found vulnerabilities.
- **OWASP Top 10 Coverage**: Specifically checks for high-impact security risks.
- **Reporting**: Generates detailed PDF reports of the scan results.
- **Modern Dashboard**: A clean, responsive React-based interface for managing scans.

## Technology Stack

### Frontend
- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS + Radix UI (shadcn/ui)
- **State Management**: React Hooks

### Backend
- **Framework**: Flask (Python)
- **Language**: Python 3.11+
- **Database**: PostgreSQL (Neon DB / Local)
- **ORM**: psycopg2 (No heavy ORM, utilizing raw SQL for performance/control)

### AI & Analysis
- **Model**: Scikit-learn (Severity Predictor)
- **Integration**: NVD (National Vulnerability Database) API

## System Architecture
The application follows a decoupled client-server architecture:
1.  **Frontend**: The Next.js app serves the UI and communicates with the Flask backend via REST APIs.
2.  **Backend**: The Flask API handles business logic, scanning operations, and database interactions.
3.  **Database**: PostgreSQL stores scan records, vulnerability findings, and user data.
4.  **Scanner Engine**: A modular Python component that performs the actual security checks and integrates with the AI model.
