# Deployment Guide - VulnScan AI

## Overview
This guide covers deploying the full-stack vulnerability scanning system to production.

## Architecture
- **Frontend**: Next.js on Vercel
- **Backend**: Python Flask on Render/Railway/Heroku
- **Database**: PostgreSQL on Neon

## Frontend Deployment (Vercel)

### Prerequisites
- GitHub account
- Vercel account (free tier available)

### Steps

1. **Push code to GitHub**
   \`\`\`bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/vulnscan-ai.git
   git push -u origin main
   \`\`\`

2. **Deploy to Vercel**
   - Go to https://vercel.com/new
   - Import your GitHub repository
   - Vercel will auto-detect Next.js
   - Add environment variables:
     - `DATABASE_URL` (from Neon)
     - `JWT_SECRET` (generate a random 32+ character string)
     - `BACKEND_URL` (your Python backend URL)

3. **Deploy**
   - Click "Deploy"
   - Vercel will build and deploy your app
   - Your app will be live at: https://your-project.vercel.app

## Backend Deployment (Render)

### Prerequisites
- GitHub account
- Render account (free tier available)

### Steps

1. **Prepare backend code**
   - Ensure `backend/` directory has:
     - `app.py`
     - `requirements.txt`
     - `runtime.txt`

2. **Deploy to Render**
   - Go to https://render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: vulnscan-backend
     - **Root Directory**: backend
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app`
     - **Environment**: Python 3.11

3. **Add Environment Variables**
   - `DATABASE_URL` (from Neon)
   - `NVD_API_KEY` (optional, for NVD API)

4. **Deploy**
   - Click "Create Web Service"
   - Your backend will be live at: https://vulnscan-backend.onrender.com

## Alternative Backend Deployment

### Railway

1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway auto-detects Python and uses Dockerfile
5. Add `DATABASE_URL` environment variable
6. Deploy

### Heroku

\`\`\`bash
# Install Heroku CLI
heroku login
cd backend
heroku create vulnscan-backend
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
\`\`\`

## Database Setup (Neon)

1. **Create Neon Project**
   - Go to https://neon.tech
   - Create a new project
   - Copy the connection string

2. **Run Database Migrations**
   - In Vercel dashboard, go to your project
   - Navigate to Storage → Neon
   - Run the SQL scripts from `scripts/` folder:
     - `001_create_schema.sql`
     - `002_seed_sample_data.sql`

## Environment Variables

### Frontend (Vercel)
\`\`\`
DATABASE_URL=postgresql://user:pass@host/db
JWT_SECRET=your-32-character-secret-key
BACKEND_URL=https://vulnscan-backend.onrender.com
\`\`\`

### Backend (Render/Railway/Heroku)
\`\`\`
DATABASE_URL=postgresql://user:pass@host/db
NVD_API_KEY=your-nvd-api-key (optional)
\`\`\`

## Post-Deployment

### 1. Test the Application
- Visit your Vercel URL
- Register a new account
- Start a test scan
- Verify results display correctly
- Download PDF report

### 2. Configure CORS
Update `backend/app.py`:
\`\`\`python
CORS(app, origins=["https://your-project.vercel.app"])
\`\`\`

### 3. Train AI Models
\`\`\`bash
cd backend
python ai_model/train_models.py
\`\`\`
Commit the generated model files.

### 4. Monitor
- Set up error tracking (e.g., Sentry)
- Monitor API usage and rate limits
- Check database connection pool

## Security Checklist

- [ ] Use HTTPS everywhere
- [ ] Set strong JWT_SECRET
- [ ] Configure CORS properly
- [ ] Use environment variables (never commit secrets)
- [ ] Enable Neon database connection pooling
- [ ] Set up rate limiting
- [ ] Regular dependency updates

## Troubleshooting

### Frontend Issues
- Check Vercel build logs
- Verify environment variables are set
- Check Next.js error logs in browser console

### Backend Issues
- Check Render/Railway logs
- Verify DATABASE_URL connection
- Test endpoints with curl/Postman
- Check Python version compatibility

### Database Issues
- Verify Neon connection string
- Check if migrations ran successfully
- Monitor connection pool usage

## Support

For issues during deployment:
- Check logs in respective platforms
- Verify all environment variables
- Test database connectivity
- Review API endpoint responses

## Performance Optimization

1. **Frontend**
   - Enable Vercel Edge caching
   - Optimize images with Next.js Image component
   - Use React Server Components where possible

2. **Backend**
   - Increase gunicorn workers
   - Enable connection pooling
   - Cache NVD API responses
   - Use async scanning for large jobs

## Scaling Considerations

- Use Vercel Pro for higher limits
- Upgrade Render/Railway plan for more resources
- Neon: Enable autoscaling
- Consider Redis for session storage
- Implement queue system for scan jobs
