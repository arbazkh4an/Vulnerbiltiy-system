# PowerShell Script to Start the Application Locally
# Run this script to start both frontend and backend
$env:Path = "C:\Users\khana\AppData\Local\Programs\Python\Python311;C:\Users\khana\AppData\Local\Programs\Python\Python311\Scripts;" + $env:Path

Write-Host "🚀 Starting VulnScan AI Application..." -ForegroundColor Green
Write-Host ""

# Check if Node.js is installed
Write-Host "Checking Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
}
catch {
    Write-Host "❌ Node.js not found! Please install Node.js from https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# Check if Python is installed
Write-Host "Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "❌ Python not found! Please install Python from https://www.python.org/" -ForegroundColor Red
    exit 1
}

# Check if .env.local exists
Write-Host "Checking environment files..." -ForegroundColor Yellow
if (-not (Test-Path ".env.local")) {
    Write-Host "⚠️  .env.local not found! Creating from example..." -ForegroundColor Yellow
    Copy-Item ".env.local.example" ".env.local" -ErrorAction SilentlyContinue
    Write-Host "⚠️  Please edit .env.local and add your DATABASE_URL and JWT_SECRET" -ForegroundColor Yellow
}

if (-not (Test-Path "backend\.env")) {
    Write-Host "⚠️  backend/.env not found! Creating from example..." -ForegroundColor Yellow
    Copy-Item "backend\.env.example" "backend\.env" -ErrorAction SilentlyContinue
    Write-Host "⚠️  Please edit backend/.env and add your DATABASE_URL" -ForegroundColor Yellow
}

# Check if node_modules exists
Write-Host "Checking dependencies..." -ForegroundColor Yellow
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Installing frontend dependencies..." -ForegroundColor Yellow
    npm.cmd install
}

# Check if backend dependencies are installed
if (-not (Test-Path "backend\venv")) {
    Write-Host "📦 Installing backend dependencies..." -ForegroundColor Yellow
    Set-Location backend
    python -m pip install -r requirements.txt
    Set-Location ..
}

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Starting servers..." -ForegroundColor Yellow
Write-Host ""
Write-Host "📝 IMPORTANT: You need TWO terminal windows:" -ForegroundColor Cyan
Write-Host "   1. Frontend: npm run dev (runs on http://localhost:3000)" -ForegroundColor Cyan
Write-Host "   2. Backend:  cd backend and python app.py (runs on http://localhost:5000)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Opening new terminal windows..." -ForegroundColor Yellow

# Start frontend in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; npm.cmd run dev"

# Wait a bit
Start-Sleep -Seconds 2

# Start backend in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; python app.py"

Write-Host ""
Write-Host "✅ Both servers should be starting in separate windows!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "🔧 Backend:  http://localhost:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit this window..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")






