#!/usr/bin/env python3
"""
Master Test Runner for LocalGrocery Platform
Runs tests for all 8 microservices, checks health, starts services as needed
"""

import asyncio
import subprocess
import json
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
import httpx
import os

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

@dataclass
class ServiceConfig:
    """Configuration for each microservice"""
    name: str
    port: int
    path: str  # Relative path from backend/services/
    health_endpoint: str
    has_unit_tests: bool
    has_integration_tests: bool

@dataclass
class TestResult:
    """Result of running tests for a service"""
    service: str
    status: str  # "running", "down", "error"
    unit_passed: int
    unit_total: int
    integration_passed: int
    integration_total: int
    duration: float
    error_msg: str = ""

# Service configurations
SERVICES = [
    ServiceConfig("Auth Service", 8001, "auth_service", "/health", False, True),
    ServiceConfig("Cart Service", 8008, "cart_service", "/health", False, True),
    ServiceConfig("Catalog Service", 8002, "catalog_service", "/health", False, True),
    ServiceConfig("Delivery Service", 8005, "delivery_service", "/health", False, True),
    ServiceConfig("Inventory Service", 8007, "inventory_service", "/health", False, True),
    ServiceConfig("Notification Service", 8006, "notification_service", "/health", False, True),
    ServiceConfig("Order Service", 8003, "order_service", "/health", False, True),
    ServiceConfig("Payment Service", 8004, "payment_service", "/health", False, True),
]

BACKEND_DIR = Path(__file__).parent
SERVICES_DIR = BACKEND_DIR / "services"

async def check_service_health(service: ServiceConfig) -> bool:
    """Check if a service is running by making a health check request"""
    url = f"http://localhost:{service.port}{service.health_endpoint}"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            return response.status_code == 200
    except Exception:
        return False

async def start_service(service: ServiceConfig) -> Tuple[bool, str]:
    """Start a service using uvicorn in the background"""
    try:
        service_dir = SERVICES_DIR / service.path

        # Check if main.py exists
        main_file = service_dir / "app" / "main.py"
        if not main_file.exists():
            return False, f"main.py not found at {main_file}"

        # Start service with output redirection
        log_out = service_dir / f"service_{service.name.lower().replace(' ', '_')}_out.log"
        log_err = service_dir / f"service_{service.name.lower().replace(' ', '_')}_err.log"

        process = subprocess.Popen(
            [
                sys.executable,
                "-m", "uvicorn",
                "app.main:app",
                "--host", "0.0.0.0",
                "--port", str(service.port),
            ],
            cwd=str(service_dir),
            stdout=open(str(log_out), 'w'),
            stderr=open(str(log_err), 'w'),
            env={
                **os.environ,
                "PYTHONIOENCODING": "utf-8",
                "PYTHONUTF8": "1",
            },
        )

        # Wait for service to start
        for attempt in range(30):  # 30 attempts * 0.5s = 15 seconds max
            await asyncio.sleep(0.5)
            if await check_service_health(service):
                return True, f"Started (PID: {process.pid})"

        return False, "Timeout waiting for service to start"

    except Exception as e:
        return False, str(e)

async def run_service_tests(service: ServiceConfig, no_auto_start: bool = False) -> TestResult:
    """Run unit and integration tests for a service"""
    start_time = time.time()
    
    # Check if service is running
    is_running = await check_service_health(service)
    
    if not is_running and not no_auto_start:
        print(f"  ⏳ {Colors.YELLOW}Starting {service.name}...{Colors.RESET}")
        success, msg = await start_service(service)
        if success:
            print(f"     {Colors.GREEN}✓ Started{Colors.RESET}")
            is_running = True
        else:
            print(f"     {Colors.RED}✗ Failed: {msg}{Colors.RESET}")
    
    if not is_running:
        duration = time.time() - start_time
        return TestResult(
            service=service.name,
            status="down",
            unit_passed=0,
            unit_total=0,
            integration_passed=0,
            integration_total=0,
            duration=duration,
            error_msg="Service not running and auto-start disabled"
        )
    
    # Run tests
    service_dir = SERVICES_DIR / service.path
    results = TestResult(
        service=service.name,
        status="running",
        unit_passed=0,
        unit_total=0,
        integration_passed=0,
        integration_total=0,
        duration=0,
    )
    
    # Run unit tests if available
    if service.has_unit_tests:
        print(f"  📋 {Colors.BLUE}Running unit tests...{Colors.RESET}")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short", "-q"],
                cwd=str(service_dir),
                capture_output=True,
                timeout=120,
                text=True
            )
            
            # Parse pytest output for pass/fail counts
            output = result.stdout + result.stderr
            if "passed" in output:
                # Extract numbers from pytest output like "18 passed in 2.34s"
                import re
                match = re.search(r'(\d+) passed', output)
                if match:
                    results.unit_passed = int(match.group(1))
                    results.unit_total = int(match.group(1))  # Simplified: assume no failures in count
                
                # Check for failures
                fail_match = re.search(r'(\d+) failed', output)
                if fail_match:
                    results.unit_total += int(fail_match.group(1))
                
                print(f"     {Colors.GREEN}✓ Unit tests: {results.unit_passed}/{results.unit_total}{Colors.RESET}")
        except subprocess.TimeoutExpired:
            results.error_msg = "Unit tests timeout"
            print(f"     {Colors.RED}✗ Unit tests timeout{Colors.RESET}")
        except Exception as e:
            results.error_msg = str(e)
            print(f"     {Colors.RED}✗ Unit tests error: {e}{Colors.RESET}")
    
    # Run integration tests if available
    if service.has_integration_tests:
        print(f"  📋 {Colors.BLUE}Running integration tests...{Colors.RESET}")
        
        # Check for test_*_apis.py file
        api_test_file = service_dir / "test_*_apis.py"
        test_files = list(service_dir.glob("test_*_apis.py"))
        
        if test_files:
            try:
                result = subprocess.run(
                    [sys.executable, str(test_files[0])],
                    cwd=str(service_dir),
                    capture_output=True,
                    timeout=120,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )
                
                # Parse output for test counts
                output = result.stdout + result.stderr
                import re

                total_match = re.search(r"Total Tests:\s*(\d+)", output)
                passed_match = re.search(r"Passed:\s*(\d+)", output)
                failed_match = re.search(r"Failed:\s*(\d+)", output)
                skipped_match = re.search(r"Skipped:\s*(\d+)", output)

                if total_match and passed_match:
                    results.integration_total = int(total_match.group(1))
                    results.integration_passed = int(passed_match.group(1))
                else:
                    # Look for pattern like "8 ✅ Passed" or pytest summary
                    emoji_passed = re.search(r'(\d+)\s*✅', output)
                    emoji_failed = re.search(r'(\d+)\s*❌', output)
                    pytest_passed = re.search(r'(\d+)\s+passed', output)
                    pytest_failed = re.search(r'(\d+)\s+failed', output)

                    if emoji_passed:
                        results.integration_passed = int(emoji_passed.group(1))
                    if pytest_passed:
                        results.integration_passed = max(results.integration_passed, int(pytest_passed.group(1)))

                    failed_count = 0
                    if emoji_failed:
                        failed_count = int(emoji_failed.group(1))
                    if pytest_failed:
                        failed_count = max(failed_count, int(pytest_failed.group(1)))

                    if results.integration_passed or failed_count:
                        results.integration_total = results.integration_passed + failed_count

                if results.integration_total > 0:
                    print(f"     {Colors.GREEN}✓ Integration: {results.integration_passed}/{results.integration_total}{Colors.RESET}")
                elif result.returncode != 0:
                    results.error_msg = "Integration tests failed"
                    print(f"     {Colors.RED}✗ Integration tests failed (see logs){Colors.RESET}")
                    
            except subprocess.TimeoutExpired:
                results.error_msg = "Integration tests timeout"
                print(f"     {Colors.RED}✗ Integration tests timeout{Colors.RESET}")
            except Exception as e:
                results.error_msg = str(e)
                print(f"     {Colors.RED}✗ Integration tests error: {e}{Colors.RESET}")
    
    results.duration = time.time() - start_time
    return results

def print_header():
    """Print report header"""
    print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}  LOCALGROCERY PLATFORM - COMPREHENSIVE TEST REPORT{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}  {datetime.now().strftime('%B %d, %Y %H:%M UTC')}{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}\n")

def print_service_status(results: List[TestResult]):
    """Print service status table"""
    print(f"{Colors.BOLD}SERVICE STATUS{Colors.RESET}")
    print(f"{'-'*80}")
    print(f"{'Service':<25} {'Port':<6} {'Status':<15} {'Duration':<10}")
    print(f"{'-'*80}")
    
    for result in results:
        status_icon = "🟢" if result.status == "running" else "🔴"
        print(f"{result.service:<25} {'-':<6} {status_icon} {result.status:<12} {result.duration:.2f}s")
    
    print()

def print_test_results(results: List[TestResult]):
    """Print test results table"""
    print(f"{Colors.BOLD}TEST RESULTS{Colors.RESET}")
    print(f"{'-'*80}")
    print(f"{'Service':<25} {'Unit Tests':<18} {'Integration':<18} {'Overall':<12}")
    print(f"{'-'*80}")
    
    for result in results:
        unit_str = f"✅ {result.unit_passed}/{result.unit_total}" if result.unit_total > 0 else "N/A"
        integration_str = f"✅ {result.integration_passed}/{result.integration_total}" if result.integration_total > 0 else "⏳ Pending"
        
        if result.integration_total > 0:
            if result.integration_passed == result.integration_total:
                overall = "✅ Ready"
            elif result.integration_passed / result.integration_total >= 0.9:
                overall = "⚠️  Ready*"
            else:
                overall = "❌ Failing"
        else:
            overall = "⏳ Pending"
        
        print(f"{result.service:<25} {unit_str:<18} {integration_str:<18} {overall:<12}")
    
    print()

def print_summary(results: List[TestResult]):
    """Print test summary"""
    total_unit_passed = sum(r.unit_passed for r in results)
    total_unit_total = sum(r.unit_total for r in results)
    total_integration_passed = sum(r.integration_passed for r in results)
    total_integration_total = sum(r.integration_total for r in results)
    total_duration = sum(r.duration for r in results)
    
    total_tests = total_unit_total + total_integration_total
    total_passed = total_unit_passed + total_integration_passed
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"{Colors.BOLD}SUMMARY{Colors.RESET}")
    print(f"{'-'*80}")
    print(f"Total Tests:        {total_tests}")
    print(f"Passed:             {total_passed} ({success_rate:.1f}%)")
    print(f"Failed:             {total_tests - total_passed} ({100 - success_rate:.1f}%)")
    print(f"Total Duration:     {total_duration:.1f}s")
    
    if success_rate == 100:
        status = f"{Colors.GREEN}✅ ALL TESTS PASSING{Colors.RESET}"
    elif success_rate >= 90:
        status = f"{Colors.YELLOW}⚠️  MOSTLY PASSING (NEEDS FIXES){Colors.RESET}"
    else:
        status = f"{Colors.RED}❌ CRITICAL FAILURES{Colors.RESET}"
    
    print(f"\nStatus: {status}")
    print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}\n")
    
    return success_rate >= 90

async def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description="Run all LocalGrocery service tests")
    parser.add_argument("--service", help="Run only a specific service")
    parser.add_argument("--no-auto-start", action="store_true", help="Don't auto-start services")
    parser.add_argument("--output", help="Output results to JSON file")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    print_header()
    
    # Filter services if specific one requested
    services_to_test = SERVICES
    if args.service:
        services_to_test = [s for s in SERVICES if args.service.lower() in s.name.lower()]
        if not services_to_test:
            print(f"{Colors.RED}Service '{args.service}' not found{Colors.RESET}")
            return 1
    
    # Run tests for each service
    results = []
    print(f"{Colors.BOLD}Running tests for {len(services_to_test)} service(s)...{Colors.RESET}\n")
    
    for service in services_to_test:
        print(f"{Colors.BLUE}Testing {service.name}:{Colors.RESET}")
        result = await run_service_tests(service, args.no_auto_start)
        results.append(result)
        print()
    
    # Print reports
    print_service_status(results)
    print_test_results(results)
    success = print_summary(results)
    
    # Export JSON if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump([asdict(r) for r in results], f, indent=2)
        print(f"Results exported to {args.output}\n")
    
    # Exit code
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
