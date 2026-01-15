# 🚀 Quick Start Instructions

## Current Status
✅ **Python is installed** (found at: `C:\Users\khana\AppData\Local\Microsoft\WindowsApps\python.exe`)  
❌ **Node.js is NOT installed** (needs to be installed)

---

## Step 1: Install Node.js

**Download and Install:**
1. Go to: https://nodejs.org/
2. Download the **LTS version** (recommended)
3. Run the installer
4. **IMPORTANT:** Make sure to check "Automatically install the necessary tools" during installation
5. Restart your terminal/PowerShell after installation

**Verify Installation:**
```powershell
node --version
npm --version
```

**Alternative (if you have Chocolatey):**
```powershell
choco install nodejs-lts
```

---

## Step 2: Set Up Environment Variables

### Create `.env.local` in the project root:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/vulnscan
JWT_SECRET=your-random-32-character-secret-key-here-change-this
BACKEND_URL=http://localhost:5000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

**For JWT_SECRET, generate a random string:**
- Use: https://generate-secret.vercel.app/32
- Or run: `openssl rand -base64 32` (if you have OpenSSL)

### Create `backend/.env`:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/vulnscan
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000
```

**Note:** Replace `DATABASE_URL` with your actual database connection string:
- **Local PostgreSQL:** `postgresql://postgres:yourpassword@localhost:5432/vulnscan`
- **Neon Cloud:** `postgresql://user:pass@ep-xxx.neon.tech/neondb?sslmode=require`

---

## Step 3: Set Up Database

### Option A: Use Neon (Free Cloud Database - Recommended)

1. Go to https://neon.tech
2. Sign up (free)
3. Create a new project
4. Copy the connection string
5. Use it as `DATABASE_URL` in both `.env.local` and `backend/.env`
6. In Neon SQL Editor, run:
   - `scripts/001_create_schema.sql`
   - `scripts/003_add_email_verification.sql`

### Option B: Local PostgreSQL

1. Download from: https://www.postgresql.org/download/windows/
2. Install with default settings
3. Create database:
   ```powershell
   createdb vulnscan
   ```
4. Run migrations:
   ```powershell
   psql -U postgres -d vulnscan -f scripts/001_create_schema.sql
   psql -U postgres -d vulnscan -f scripts/003_add_email_verification.sql
   ```

---

## Step 4: Install Dependencies

### Frontend:
```powershell
npm install
```

### Backend:
```powershell
cd backend
python -m pip install -r requirements.txt
cd ..
```

---

## Step 5: Train AI Models (Optional)

```powershell
cd backend
python ai_model/train_models.py
cd ..
```

---

## Step 6: Start the Application

### Terminal 1 - Frontend:
```powershell
npm run dev
```
✅ Frontend will run at: **http://localhost:3000**

### Terminal 2 - Backend:
```powershell
cd backend
python app.py
```
✅ Backend will run at: **http://localhost:5000**

---

## Step 7: Test the Application

1. Open browser: **http://localhost:3000**
2. Click "Register" or "Get Started"
3. Create an account:
   - Name: Test User
   - Email: test@example.com
   - Password: testpass123
4. **Copy the verification URL** from the success message
5. Visit the verification URL to verify your email
6. Login with your credentials
7. On dashboard, enter a URL (e.g., `https://example.com`)
8. Click "Start Scan"
9. View the results!

---

## Troubleshooting

### "node is not recognized"
- **Restart your terminal** after installing Node.js
- Check PATH: `$env:PATH`
- Reinstall Node.js

### "python is not recognized"
- Use: `python` or `py` command
- Or use full path: `C:\Users\khana\AppData\Local\Microsoft\WindowsApps\python.exe`

### "Database connection failed"
- Check `DATABASE_URL` is correct
- For Neon: Make sure connection string includes `?sslmode=require`
- For local: Make sure PostgreSQL is running

### "Port 3000/5000 already in use"
```powershell
# Find process on port 3000
netstat -ano | findstr :3000
# Kill it (replace <PID> with actual process ID)
taskkill /PID <PID> /F
```

---

## Need Help?

See `SETUP_GUIDE.md` for detailed instructions.






