#!/usr/bin/env powershell
<#
.SYNOPSIS
    Master Test Runner for LocalGrocery Platform (Windows PowerShell Wrapper)
    
.DESCRIPTION
    Wrapper script for run_all_tests.py that provides Windows-friendly interface
    
.EXAMPLE
    .\run_tests.ps1                    # Run all tests
    .\run_tests.ps1 -Service inventory # Test only inventory service
    .\run_tests.ps1 -NoAutoStart       # Don't start services automatically
    
#>

param(
    [string]$Service,
    [switch]$NoAutoStart,
    [string]$Output,
    [switch]$Verbose,
    [switch]$Help
)

# Script configuration
$BackendDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonScript = Join-Path $BackendDir "run_all_tests.py"

# Helper functions
function Write-Header {
    Write-Host "`n" -ForegroundColor White
    Write-Host "╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║    LocalGrocery Platform - Master Test Runner (Windows)           ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Help {
    Write-Host "USAGE:"
    Write-Host "  .\run_tests.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "OPTIONS:"
    Write-Host "  -Service <name>        Run only specific service (auth, inventory, etc.)"
    Write-Host "  -NoAutoStart           Don't automatically start services"
    Write-Host "  -Output <path>         Export results to JSON file"
    Write-Host "  -Verbose               Show verbose output"
    Write-Host "  -Help                  Show this help message"
    Write-Host ""
    Write-Host "EXAMPLES:"
    Write-Host "  .\run_tests.ps1                           # Run all tests"
    Write-Host "  .\run_tests.ps1 -Service inventory       # Test inventory only"
    Write-Host "  .\run_tests.ps1 -Output results.json     # Save results to file"
    Write-Host ""
}

function Check-Requirements {
    Write-Host "Checking requirements..." -ForegroundColor Yellow
    
    # Check Python
    try {
        $python = (python --version 2>&1)
        Write-Host "  ✓ Python: $python" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Python not found. Please install Python 3.11+" -ForegroundColor Red
        return $false
    }
    
    # Check httpx
    try {
        python -c "import httpx" -ErrorAction Stop
        Write-Host "  ✓ httpx module installed" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ httpx not installed. Installing..." -ForegroundColor Yellow
        python -m pip install httpx -q
    }
    
    # Check test script exists
    if (Test-Path $PythonScript) {
        Write-Host "  ✓ Test script found" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Test script not found at $PythonScript" -ForegroundColor Red
        return $false
    }
    
    Write-Host ""
    return $true
}

function Start-Tests {
    Write-Host "Starting test execution..." -ForegroundColor Yellow
    Write-Host ""
    
    # Build arguments
    $args = @()
    if ($Service) {
        $args += "--service", $Service
    }
    if ($NoAutoStart) {
        $args += "--no-auto-start"
    }
    if ($Output) {
        $args += "--output", $Output
    }
    if ($Verbose) {
        $args += "--verbose"
    }
    
    # Run tests
    & python $PythonScript @args
    $exitCode = $LASTEXITCODE
    
    if ($exitCode -eq 0) {
        Write-Host "✓ All tests passed!" -ForegroundColor Green
    } else {
        Write-Host "✗ Some tests failed (exit code: $exitCode)" -ForegroundColor Red
    }
    
    return $exitCode
}

# Main script logic
Clear-Host
Write-Header

if ($Help) {
    Write-Help
    exit 0
}

# Check requirements
if (-not (Check-Requirements)) {
    exit 1
}

# Run tests
$exitCode = Start-Tests

exit $exitCode
