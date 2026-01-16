# Getting Started Guide

This guide will help you set up the VulnScan AI environment on your local machine.

## Prerequisites
Ensure you have the following installed:
1.  **Node.js** (v18 or higher) - [Download](https://nodejs.org/)
2.  **Python** (v3.11 or higher) - [Download](https://python.org/)
3.  **PostgreSQL** (Optional if using a cloud DB like Neon)

## Installation

### 1. Clone the Repository
```bash
git clone <repository_url>
cd vulnerability-scanning-system
```

### 2. Environment Setup
The project requires two environment files.

#### Frontend (`.env.local`)
Create a `.env.local` file in the root directory:
```env
NEXT_PUBLIC_API_URL=http://localhost:5000/api
DATABASE_URL="postgresql://user:password@host:port/dbname"
JWT_SECRET="your-super-secret-key"
```

#### Backend (`backend/.env`)
Create a `.env` file in the `backend/` directory:
```env
DATABASE_URL="postgresql://user:password@host:port/dbname"
FLASK_ENV=development
PORT=5000
```

### 3. Dependencies
You can install dependencies manually or let the start script handle it.

**Manual Installation:**
```bash
# Frontend
npm install

# Backend
cd backend
python -m venv venv
# Windows
.\venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

## Running the Application
We have provided a one-click PowerShell script for Windows users.

### Quick Start (Windows)
Run the `start-local.ps1` script from PowerShell:
```powershell
.\start-local.ps1
```
This script will:
1.  Check for Node.js and Python.
2.  Install missing dependencies.
3.  Launch the Frontend (http://localhost:3000) and Backend (http://localhost:5000) in separate windows.

### Manual Start
**Terminal 1 (Frontend):**
```bash
npm run dev
```

**Terminal 2 (Backend):**
```bash
cd backend
# Activate venv if needed
python app.py
```

## Verify Installation
- Open http://localhost:3000 in your browser.
- You should see the VulnScan AI landing page.
- Check the backend health at http://localhost:5000/health.
