# Update all service dependencies for Python 3.13 compatibility
# Run this script from the backend directory

Write-Host "Updating dependencies for Python 3.13 compatibility..." -ForegroundColor Cyan

$services = @(
    "auth_service",
    "catalog_service",
    "order_service",
    "payment_service",
    "delivery_service",
    "notification_service",
    "inventory_service",
    "cart_service"
)

$commonUpdates = @{
    "sqlalchemy==2.0.23" = "sqlalchemy==2.0.36"
    "sqlalchemy==2.0.35" = "sqlalchemy==2.0.36"
    "asyncpg==0.29.0" = "asyncpg==0.30.0"
    "asyncpg==0.31.0" = "asyncpg==0.30.0"
    "pydantic==2.5.0" = "pydantic==2.10.4"
    "pydantic==2.5.2" = "pydantic==2.10.4"
    "pydantic==2.9.0" = "pydantic==2.10.4"
    "passlib[bcrypt]" = "passlib"
    "bcrypt==" = "# bcrypt removed - requires Rust on Python 3.13"
}

foreach ($service in $services) {
    $servicePath = "services\$service"
    $reqFile = "$servicePath\requirements.txt"
    
    if (Test-Path $reqFile) {
        Write-Host "`nProcessing $service..." -ForegroundColor Yellow
        
        $content = Get-Content $reqFile -Raw
        $updated = $false
        
        foreach ($old in $commonUpdates.Keys) {
            if ($content -match [regex]::Escape($old)) {
                $new = $commonUpdates[$old]
                $content = $content -replace [regex]::Escape($old), $new
                $updated = $true
                Write-Host "  Updated: $old -> $new" -ForegroundColor Green
            }
        }
        
        if ($updated) {
            Set-Content -Path $reqFile -Value $content -NoNewline
            Write-Host "  Saved updates to $reqFile" -ForegroundColor Green
        } else {
            Write-Host "  No updates needed" -ForegroundColor Gray
        }
    } else {
        Write-Host "`nSkipping $service - requirements.txt not found" -ForegroundColor Red
    }
}

Write-Host "`nDependency update complete!" -ForegroundColor Cyan
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Navigate to each service directory" -ForegroundColor White
Write-Host "2. Activate venv: .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "3. Install: pip install -r requirements.txt --force-reinstall" -ForegroundColor White
