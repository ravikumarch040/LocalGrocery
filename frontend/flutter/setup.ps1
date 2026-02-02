# LocalGrocery Flutter Setup Script
# This script initializes the Flutter monorepo structure

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "LocalGrocery Flutter Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if Flutter is installed
Write-Host "Checking Flutter installation..." -ForegroundColor Yellow
$flutterVersion = flutter --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Flutter is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Flutter from https://flutter.dev/docs/get-started/install" -ForegroundColor Red
    exit 1
}

Write-Host "Flutter is installed!" -ForegroundColor Green
Write-Host ""

# Navigate to flutter directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "Current directory: $(Get-Location)" -ForegroundColor Cyan
Write-Host ""

# Create directory structure
Write-Host "Creating project structure..." -ForegroundColor Yellow

$directories = @(
    "apps/customer_app",
    "apps/retailer_app",
    "apps/delivery_app",
    "packages/api_client/lib/src",
    "packages/ui_components/lib/src",
    "packages/local_storage/lib/src",
    "docs"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "Created: $dir" -ForegroundColor Green
    } else {
        Write-Host "Exists: $dir" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "Project structure created!" -ForegroundColor Green
Write-Host ""

# Install melos (if not installed)
Write-Host "Checking for Melos..." -ForegroundColor Yellow
$melosCheck = dart pub global list | Select-String "melos"
if (-not $melosCheck) {
    Write-Host "Installing Melos..." -ForegroundColor Yellow
    dart pub global activate melos
    Write-Host "Melos installed!" -ForegroundColor Green
} else {
    Write-Host "Melos is already installed!" -ForegroundColor Green
}

Write-Host ""

# Get dependencies for core package
Write-Host "Installing dependencies for 'core' package..." -ForegroundColor Yellow
Set-Location packages/core
flutter pub get
Set-Location ../..
Write-Host "Core package dependencies installed!" -ForegroundColor Green
Write-Host ""

# Get dependencies for models package
Write-Host "Installing dependencies for 'models' package..." -ForegroundColor Yellow
Set-Location packages/models
flutter pub get
Set-Location ../..
Write-Host "Models package dependencies installed!" -ForegroundColor Green
Write-Host ""

# Create .env template files
Write-Host "Creating environment template files..." -ForegroundColor Yellow

$envTemplate = @"
# LocalGrocery Environment Configuration

# API Configuration
API_BASE_URL=http://localhost:8000/v1

# Payment Gateway
RAZORPAY_KEY=rzp_test_xxxxx
CASHFREE_KEY=xxxxx

# Maps
GOOGLE_MAPS_API_KEY=xxxxx

# Firebase
FIREBASE_API_KEY=xxxxx
FIREBASE_PROJECT_ID=localgrocery

# Feature Flags
ENABLE_ANALYTICS=true
ENABLE_CRASH_REPORTING=false
"@

if (-not (Test-Path ".env.dev")) {
    $envTemplate | Out-File -FilePath ".env.dev" -Encoding UTF8
    Write-Host "Created: .env.dev" -ForegroundColor Green
}

if (-not (Test-Path ".env.staging")) {
    $envTemplate -replace "localhost:8000", "staging-api.localgrocery.com" | Out-File -FilePath ".env.staging" -Encoding UTF8
    Write-Host "Created: .env.staging" -ForegroundColor Green
}

if (-not (Test-Path ".env.production")) {
    $envTemplate -replace "localhost:8000", "api.localgrocery.com" -replace "rzp_test", "rzp_live" | Out-File -FilePath ".env.production" -Encoding UTF8
    Write-Host "Created: .env.production" -ForegroundColor Green
}

Write-Host ""

# Summary
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Update .env files with your API keys" -ForegroundColor White
Write-Host "2. Create Flutter apps in apps/ directory:" -ForegroundColor White
Write-Host "   cd apps" -ForegroundColor Gray
Write-Host "   flutter create customer_app" -ForegroundColor Gray
Write-Host "   flutter create retailer_app" -ForegroundColor Gray
Write-Host "   flutter create delivery_app" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Run code generation for models package:" -ForegroundColor White
Write-Host "   cd packages/models" -ForegroundColor Gray
Write-Host "   flutter pub run build_runner build --delete-conflicting-outputs" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Start developing! Check README.md for more details" -ForegroundColor White
Write-Host ""
