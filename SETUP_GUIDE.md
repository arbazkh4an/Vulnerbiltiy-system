# Local Setup Guide - Step by Step

## Prerequisites Installation

### 1. Install Node.js (v18 or higher)

**Windows:**
1. Download from: https://nodejs.org/
2. Install the LTS version
3. Verify installation:
   ```powershell
   node --version
   npm --version
   ```

**Or use Chocolatey:**
```powershell
choco install nodejs-lts
```

### 2. Install Python (v3.11 or higher)

**Windows:**
1. Download from: https://www.python.org/downloads/
2. **IMPORTANT:** Check "Add Python to PATH" during installation
3. Verify installation:
   ```powershell
   python --version
   pip --version
   ```

**Or use Microsoft Store:**
- Search for "Python 3.11" in Microsoft Store
- Install it

### 3. Install PostgreSQL (or use Neon Cloud Database)

**Option A: Local PostgreSQL**
1. Download from: https://www.postgresql.org/download/windows/
2. Install with default settings
3. Remember the password you set for the `postgres` user

**Option B: Neon Cloud Database (Recommended - Free)**
1. Go to https://neon.tech
2. Sign up for free account
3. Create a new project
4. Copy the connection string (you'll use this as DATABASE_URL)

---

## Application Setup Steps

### Step 1: Install Frontend Dependencies

```powershell
# Make sure you're in the project root
cd C:\Users\khana\Downloads\vulnerability-scanning-system

# Install Node.js dependencies
npm install
```

**If npm is not found:**
- Restart your terminal/PowerShell after installing Node.js
- Or use full path: `C:\Program Files\nodejs\npm.cmd install`

### Step 2: Install Backend Dependencies

```powershell
# Navigate to backend folder
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Go back to root
cd ..
```

**If pip is not found:**
- Make sure Python is added to PATH
- Or use: `python -m pip install -r requirements.txt`

### Step 3: Set Up Environment Variables

**Frontend (.env.local):**
```powershell
# Create .env.local file in the root directory
# Copy from .env.local.example and update values
```

Create `.env.local` with:
```
DATABASE_URL=your-database-connection-string
JWT_SECRET=generate-a-random-32-character-secret-key-here
BACKEND_URL=http://localhost:5000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

**Backend (backend/.env):**
```powershell
# Create .env file in backend directory
# Copy from backend/.env.example and update values
```

Create `backend/.env` with:
```
DATABASE_URL=your-database-connection-string
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000
```

### Step 4: Set Up Database

**If using Neon (Cloud):**
1. Go to your Neon dashboard
2. Open SQL Editor
3. Run the SQL from `scripts/001_create_schema.sql`
4. Run the SQL from `scripts/003_add_email_verification.sql`
5. (Optional) Run `scripts/002_seed_sample_data.sql` for demo data

**If using Local PostgreSQL:**
```powershell
# Create database
createdb vulnscan

# Run migrations (replace with your PostgreSQL connection details)
psql -U postgres -d vulnscan -f scripts/001_create_schema.sql
psql -U postgres -d vulnscan -f scripts/003_add_email_verification.sql
```

### Step 5: Train AI Models (Optional but Recommended)

```powershell
cd backend
python ai_model/train_models.py
cd ..
```

This creates the ML models for severity prediction.

---

## Running the Application

### Terminal 1: Start Frontend

```powershell
# In project root
npm run dev
```

Frontend will be available at: **http://localhost:3000**

### Terminal 2: Start Backend

```powershell
# Navigate to backend
cd backend

# Start Flask server
python app.py
```

Backend will be available at: **http://localhost:5000**

---

## Quick Test

1. Open browser: http://localhost:3000
2. Click "Register" or "Get Started"
3. Create an account:
   - Name: Test User
   - Email: test@example.com
   - Password: testpass123 (min 8 characters)
4. Copy the verification URL from the console/response
5. Visit the verification URL to verify email
6. Login with your credentials
7. On dashboard, enter a test URL (e.g., `https://example.com`)
8. Click "Start Scan"
9. View results!

---

## Troubleshooting

### "node is not recognized"
- Restart terminal after installing Node.js
- Check Node.js is in PATH: `$env:PATH`
- Reinstall Node.js and check "Add to PATH"

### "python is not recognized"
- Reinstall Python and check "Add Python to PATH"
- Or use: `py` instead of `python` on Windows

### "Database connection failed"
- Check DATABASE_URL is correct
- For Neon: Make sure connection string includes `?sslmode=require`
- For local: Make sure PostgreSQL is running

### "Port 3000 already in use"
```powershell
# Find and kill process on port 3000
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### "Port 5000 already in use"
```powershell
# Find and kill process on port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### "Module not found" errors
```powershell
# Frontend
rm -r node_modules
npm install

# Backend
pip install -r backend/requirements.txt --force-reinstall
```

---

## Next Steps

Once running:
- ✅ Frontend: http://localhost:3000
- ✅ Backend: http://localhost:5000
- ✅ Database: Connected

You can now scan websites!


