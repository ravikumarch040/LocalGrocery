#!/usr/bin/env powershell
# LocalGrocery - Start All Microservices

Write-Host "LocalGrocery Microservices Startup Script" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Services to start
$services = @(
    @{ name = "Auth Service"; port = 8001; path = "backend\services\auth_service" },
    @{ name = "Catalog Service"; port = 8002; path = "backend\services\catalog_service" },
    @{ name = "Order Service"; port = 8003; path = "backend\services\order_service" },
    @{ name = "Payment Service"; port = 8004; path = "backend\services\payment_service" },
    @{ name = "Delivery Service"; port = 8005; path = "backend\services\delivery_service" },
    @{ name = "Notification Service"; port = 8006; path = "backend\services\notification_service" },
    @{ name = "Inventory Service"; port = 8007; path = "backend\services\inventory_service" },
    @{ name = "Cart Service"; port = 8008; path = "backend\services\cart_service" }
)

# Function to start service
function Start-Service {
    param([string]$Name, [int]$Port, [string]$Path)

    Write-Host "Starting $Name on port $Port..." -ForegroundColor Yellow

    $rootDir = Get-Location
    $fullPath = Join-Path $rootDir $Path
    $venvActivate = Join-Path $fullPath "venv\Scripts\Activate.ps1"
    
    # Check if venv exists
    if (-not (Test-Path $venvActivate)) {
        Write-Host "ERROR: venv not found for $Name at $venvActivate" -ForegroundColor Red
        Write-Host "Please create venv: cd $Path && python -m venv venv && pip install -r requirements.txt" -ForegroundColor Yellow
        return
    }
    
    $cmd = "& '$venvActivate'; python -m uvicorn app.main:app --reload --port $Port"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmd -WorkingDirectory $fullPath

    Write-Host "$Name started (PID in new window)" -ForegroundColor Green
}

# Start all services
foreach ($service in $services) {
    Start-Service -Name $service.name -Port $service.port -Path $service.path
    Start-Sleep -Seconds 2
}

Write-Host ""
Write-Host "✅ All services started!" -ForegroundColor Green
Write-Host ""
Write-Host "Service URLs:" -ForegroundColor Cyan
Write-Host "  Auth:         http://localhost:8001/docs" -ForegroundColor White
Write-Host "  Catalog:      http://localhost:8002/docs" -ForegroundColor White
Write-Host "  Order:        http://localhost:8003/docs" -ForegroundColor White
Write-Host "  Payment:      http://localhost:8004/docs" -ForegroundColor White
Write-Host "  Delivery:     http://localhost:8005/docs" -ForegroundColor White
Write-Host "  Notification: http://localhost:8006/docs" -ForegroundColor White
Write-Host "  Inventory:    http://localhost:8007/docs" -ForegroundColor White
Write-Host "  Cart:         http://localhost:8008/docs" -ForegroundColor White
Write-Host ""
Write-Host "Health Check:" -ForegroundColor Cyan
Write-Host "  All services: http://localhost:{8001-8008}/health" -ForegroundColor White
Write-Host ""
Write-Host "Note: Services are running in new PowerShell windows." -ForegroundColor Yellow
Write-Host "      Close any window to stop that service." -ForegroundColor Yellow
