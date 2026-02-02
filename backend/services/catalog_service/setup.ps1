# Catalog Service Setup Script
# Run this from PowerShell in the catalog_service directory

Write-Host "=== Catalog Service Setup ===" -ForegroundColor Cyan

# 1. Create virtual environment
Write-Host "`n[1/5] Creating virtual environment..." -ForegroundColor Yellow
if (!(Test-Path "venv")) {
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}

# 2. Activate virtual environment and install dependencies
Write-Host "`n[2/5] Installing dependencies..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
Write-Host "✓ Dependencies installed" -ForegroundColor Green

# 3. Create .env file if not exists
Write-Host "`n[3/5] Setting up environment configuration..." -ForegroundColor Yellow
if (!(Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "✓ .env file created from template" -ForegroundColor Green
    Write-Host "  ⚠ Please update .env with your actual configuration" -ForegroundColor Yellow
} else {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}

# 4. Run database migration
Write-Host "`n[4/5] Running database migration..." -ForegroundColor Yellow
Write-Host "  Execute the following SQL migration:" -ForegroundColor Cyan
Write-Host "  psql -h localhost -U localgrocery -d localgrocery -f migrations/001_create_catalog_tables.sql" -ForegroundColor Cyan
Write-Host "  Or manually run the migration script in your PostgreSQL client" -ForegroundColor Cyan

# 5. Instructions to run service
Write-Host "`n[5/5] Setup complete!" -ForegroundColor Green
Write-Host "`nTo run the Catalog Service:" -ForegroundColor Cyan
Write-Host "  1. Ensure PostgreSQL is running" -ForegroundColor White
Write-Host "  2. Run migration: psql -h localhost -U localgrocery -d localgrocery -f migrations/001_create_catalog_tables.sql" -ForegroundColor White
Write-Host "  3. Activate venv: .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  4. Start service: python -m uvicorn app.main:app --reload --port 8002" -ForegroundColor White
Write-Host "  5. Access docs: http://localhost:8002/docs" -ForegroundColor White
Write-Host "`nTo run tests:" -ForegroundColor Cyan
Write-Host "  pytest -v" -ForegroundColor White
Write-Host "  pytest --cov=app tests/" -ForegroundColor White

Write-Host "`n=== Setup Complete ===" -ForegroundColor Green
