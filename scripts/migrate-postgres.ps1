# PostgreSQL Migration Script for Windows (PowerShell)
# Usage: .\migrate-postgres.ps1 up|down|status

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('up', 'down', 'status')]
    [string]$Action = 'status'
)

# Configuration
$DB_HOST = "localhost"
$DB_PORT = "5432"
$DB_NAME = "localgrocery"
$DB_USER = "localgrocery"
$DB_PASSWORD = "dev_password_change_in_prod"
$MIGRATIONS_DIR = Join-Path $PSScriptRoot "..\backend\database\migrations"

# Set password environment variable for psql
$env:PGPASSWORD = $DB_PASSWORD

Write-Host "==================== PostgreSQL Migration Tool ====================" -ForegroundColor Cyan
Write-Host ("Database: {0}@{1}:{2}" -f $DB_NAME, $DB_HOST, $DB_PORT) -ForegroundColor Yellow
Write-Host "Action: $Action" -ForegroundColor Yellow
Write-Host ""

# Check if psql is available
if (-not (Get-Command psql -ErrorAction SilentlyContinue)) {
    Write-Host "Error: psql command not found. Please install PostgreSQL client tools." -ForegroundColor Red
    exit 1
}

# Check connection
Write-Host "Testing database connection..." -ForegroundColor Cyan
$testConnection = psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "SELECT 1;" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Cannot connect to PostgreSQL server." -ForegroundColor Red
    Write-Host $testConnection -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Database connection successful" -ForegroundColor Green
Write-Host ""

# Create database if not exists
Write-Host "Checking if database exists..." -ForegroundColor Cyan
$dbExists = psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME';"
if ([string]::IsNullOrWhiteSpace($dbExists)) {
    Write-Host "Creating database '$DB_NAME'..." -ForegroundColor Yellow
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "CREATE DATABASE $DB_NAME;"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Database created successfully" -ForegroundColor Green
    } else {
        Write-Host "Error: Failed to create database" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[OK] Database exists" -ForegroundColor Green
}
Write-Host ""

# Create schema_migrations table
Write-Host "Setting up migrations tracking table..." -ForegroundColor Cyan
$createTable = "CREATE TABLE IF NOT EXISTS schema_migrations (version VARCHAR(255) PRIMARY KEY, applied_at TIMESTAMP DEFAULT NOW());"

psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c $createTable 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Migrations tracking ready" -ForegroundColor Green
} else {
    Write-Host "Error: Failed to create schema_migrations table" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Get applied migrations
$appliedMigrations = psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -tAc "SELECT version FROM schema_migrations ORDER BY version;"

# Get migration files
if (-not (Test-Path $MIGRATIONS_DIR)) {
    Write-Host "Error: Migrations directory not found: $MIGRATIONS_DIR" -ForegroundColor Red
    exit 1
}

$migrationFiles = Get-ChildItem -Path $MIGRATIONS_DIR -Filter "*.sql" | Sort-Object Name

if ($Action -eq 'status') {
    Write-Host "==================== Migration Status ====================" -ForegroundColor Cyan
    Write-Host "Total migrations found: $($migrationFiles.Count)" -ForegroundColor Yellow
    Write-Host ""
    
    if ($migrationFiles.Count -eq 0) {
        Write-Host "No migration files found in $MIGRATIONS_DIR" -ForegroundColor Yellow
        exit 0
    }
    
    # Split applied migrations into array
    $appliedArray = @()
    if (-not [string]::IsNullOrWhiteSpace($appliedMigrations)) {
        $appliedArray = $appliedMigrations.Split([Environment]::NewLine) | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
    }
    
    foreach ($file in $migrationFiles) {
        $version = $file.BaseName
        if ($appliedArray -contains $version) {
            Write-Host "  [APPLIED] $version" -ForegroundColor Green
        } else {
            Write-Host "  [PENDING] $version" -ForegroundColor Yellow
        }
    }
    Write-Host ""
    exit 0
}

if ($Action -eq 'up') {
    Write-Host "==================== Running Migrations ====================" -ForegroundColor Cyan
    
    if ($migrationFiles.Count -eq 0) {
        Write-Host "No migration files found" -ForegroundColor Yellow
        exit 0
    }
    
    # Split applied migrations into array
    $appliedArray = @()
    if (-not [string]::IsNullOrWhiteSpace($appliedMigrations)) {
        $appliedArray = $appliedMigrations.Split([Environment]::NewLine) | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
    }
    
    $migrationsRun = 0
    foreach ($file in $migrationFiles) {
        $version = $file.BaseName
        
        if ($appliedArray -contains $version) {
            Write-Host "  [SKIP] $version (already applied)" -ForegroundColor Gray
            continue
        }
        
        Write-Host "  [RUN] Applying $version..." -ForegroundColor Cyan
        
        # Run migration
        $migrationPath = $file.FullName
        psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f $migrationPath
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  [FAIL] Migration $version failed" -ForegroundColor Red
            exit 1
        }
        
        # Record migration
        psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "INSERT INTO schema_migrations (version) VALUES ('$version');" | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [OK] $version completed" -ForegroundColor Green
            $migrationsRun++
        } else {
            Write-Host "  [FAIL] Failed to record migration" -ForegroundColor Red
            exit 1
        }
    }
    
    Write-Host ""
    if ($migrationsRun -eq 0) {
        Write-Host "All migrations up to date!" -ForegroundColor Green
    } else {
        Write-Host "Successfully applied $migrationsRun migration(s)" -ForegroundColor Green
    }
    Write-Host ""
    exit 0
}

if ($Action -eq 'down') {
    Write-Host "==================== Rolling Back Last Migration ====================" -ForegroundColor Cyan
    
    # Get last applied migration
    $lastMigration = psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -tAc "SELECT version FROM schema_migrations ORDER BY version DESC LIMIT 1;"
    
    if ([string]::IsNullOrWhiteSpace($lastMigration)) {
        Write-Host "No migrations to rollback" -ForegroundColor Yellow
        exit 0
    }
    
    $lastMigration = $lastMigration.Trim()
    Write-Host "Rolling back: $lastMigration" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "WARNING: Automatic rollback not implemented." -ForegroundColor Red
    Write-Host "Please manually rollback migration: $lastMigration" -ForegroundColor Yellow
    Write-Host ""
    $removeCmd = "DELETE FROM schema_migrations WHERE version='$lastMigration';"
    Write-Host "To remove from tracking: psql -d $DB_NAME -c `"$removeCmd`"" -ForegroundColor Cyan
    Write-Host ""
    exit 0
}
