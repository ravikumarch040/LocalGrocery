#!/bin/bash
#
# Master Test Runner for LocalGrocery Platform (Bash Wrapper)
# Usage: ./run_tests.sh [--service SERVICE] [--no-auto-start] [--output FILE] [--verbose]
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/run_all_tests.py"

# Parse arguments
SERVICE=""
NO_AUTO_START=""
OUTPUT=""
VERBOSE=""
HELP=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --service)
            SERVICE="$2"
            shift 2
            ;;
        --no-auto-start)
            NO_AUTO_START="--no-auto-start"
            shift
            ;;
        --output)
            OUTPUT="--output $2"
            shift 2
            ;;
        --verbose)
            VERBOSE="--verbose"
            shift
            ;;
        --help|-h)
            HELP=1
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Functions
print_header() {
    clear
    echo -e "${CYAN}${BOLD}"
    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║    LocalGrocery Platform - Master Test Runner (Linux/macOS)       ║"
    echo "╚════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_help() {
    echo -e "${BOLD}USAGE:${NC}"
    echo "  ./run_tests.sh [OPTIONS]"
    echo ""
    echo -e "${BOLD}OPTIONS:${NC}"
    echo "  --service <name>        Run only specific service (auth, inventory, etc.)"
    echo "  --no-auto-start         Don't automatically start services"
    echo "  --output <path>         Export results to JSON file"
    echo "  --verbose               Show verbose output"
    echo "  -h, --help              Show this help message"
    echo ""
    echo -e "${BOLD}EXAMPLES:${NC}"
    echo "  ./run_tests.sh                           # Run all tests"
    echo "  ./run_tests.sh --service inventory      # Test inventory only"
    echo "  ./run_tests.sh --output results.json    # Save results to file"
    echo ""
}

check_requirements() {
    echo -e "${YELLOW}Checking requirements...${NC}"
    
    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1)
        echo -e "${GREEN}  ✓ $PYTHON_VERSION${NC}"
    else
        echo -e "${RED}  ✗ Python 3 not found. Please install Python 3.11+${NC}"
        return 1
    fi
    
    # Check httpx
    if python3 -c "import httpx" 2>/dev/null; then
        echo -e "${GREEN}  ✓ httpx module installed${NC}"
    else
        echo -e "${YELLOW}  ⚠ httpx not installed. Installing...${NC}"
        python3 -m pip install httpx -q || true
    fi
    
    # Check test script
    if [[ -f "$PYTHON_SCRIPT" ]]; then
        echo -e "${GREEN}  ✓ Test script found${NC}"
    else
        echo -e "${RED}  ✗ Test script not found at $PYTHON_SCRIPT${NC}"
        return 1
    fi
    
    echo ""
    return 0
}

start_tests() {
    echo -e "${YELLOW}Starting test execution...${NC}"
    echo ""
    
    # Build command
    CMD="python3 $PYTHON_SCRIPT"
    
    [[ -n "$SERVICE" ]] && CMD="$CMD --service $SERVICE"
    [[ -n "$NO_AUTO_START" ]] && CMD="$CMD $NO_AUTO_START"
    [[ -n "$OUTPUT" ]] && CMD="$CMD $OUTPUT"
    [[ -n "$VERBOSE" ]] && CMD="$CMD $VERBOSE"
    
    # Run tests
    eval $CMD
    EXIT_CODE=$?
    
    echo ""
    if [[ $EXIT_CODE -eq 0 ]]; then
        echo -e "${GREEN}✓ All tests passed!${NC}"
    else
        echo -e "${RED}✗ Some tests failed (exit code: $EXIT_CODE)${NC}"
    fi
    
    return $EXIT_CODE
}

# Main
print_header

if [[ -n "$HELP" ]]; then
    print_help
    exit 0
fi

if ! check_requirements; then
    exit 1
fi

start_tests
exit $?
