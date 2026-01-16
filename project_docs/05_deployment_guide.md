# Deployment Guide

This guide outlines the general steps to deploy VulnScan AI to production.

## Database
1.  **Provision**: Set up a PostgreSQL database (e.g., Neon, Railway, AWS RDS).
2.  **Schema**: Execute the database migration or initialization scripts (check `scripts/` or `backend/` for SQL files).
3.  **Connection String**: Obtain the `DATABASE_URL`.

## Frontend (Vercel)
The easiest way to deploy the Next.js frontend is via Vercel.
1.  **Connect Repo**: Import your GitHub repository to Vercel.
2.  **Environment Variables**:
    - `NEXT_PUBLIC_API_URL`: The URL of your deployed backend (e.g., `https://my-backend.onrender.com/api`).
    - `DATABASE_URL`: Your PostgreSQL connection string.
    - `JWT_SECRET`: A secure random string.
3.  **Build Command**: `next build` (Default)
4.  **Deploy**: Click deploy.

## Backend (Render / Railway)
The Python Flask backend is best hosted on a platform like Render or Railway.
1.  **Connect Repo**: Link your repository.
2.  **Build Command**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Start Command**:
    ```bash
    gunicorn app:app
    ```
    *(Note: You may need to add `gunicorn` to `requirements.txt` if not present, though it is standard for Flask production).*
4.  **Environment Variables**:
    - `DATABASE_URL`: Must match the one used by the frontend.
    - `FLASK_ENV`: `production`

## Post-Deployment Checks
1.  Visit the frontend URL.
2.  Test the health check endpoint on the backend URL.
3.  Run a test scan to verify the backend can talk to the database and external APIs.
