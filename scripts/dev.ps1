# VeritasAI One-Click Local Development Launcher for Windows 11 PowerShell
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Starting VeritasAI Platform (FastAPI Backend + React Frontend)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# Verify Python
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "Error: Python is not found in PATH." -ForegroundColor Red
    Exit 1
}

# Verify Node
$nodeCmd = Get-Command node -ErrorAction SilentlyContinue
if (-not $nodeCmd) {
    Write-Host "Error: Node.js is not found in PATH." -ForegroundColor Red
    Exit 1
}

# Ensure Database & Evidence Seeded
Write-Host "`n[1/3] Checking Evidence Index and Database..." -ForegroundColor Yellow
python scripts/seed_evidence.py

# Launch FastAPI in a separate process
Write-Host "`n[2/3] Starting FastAPI Backend on http://localhost:8000..." -ForegroundColor Green
$backendJob = Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload" -PassThru

# Start Vite Frontend
Write-Host "`n[3/3] Starting Vite React Frontend on http://localhost:5173..." -ForegroundColor Green
Set-Location frontend
npm run dev
