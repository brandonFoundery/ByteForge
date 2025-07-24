#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "${MAGENTA}========================================${NC}"
    echo -e "${MAGENTA}$1${NC}"
    echo -e "${MAGENTA}========================================${NC}"
}

print_section() {
    echo -e "\n${CYAN}>>> $1${NC}"
}

print_status() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${CYAN}ℹ${NC} $1"
}

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

print_header "Lead Processing Test Runner"
echo ""

print_status "Project directory: $PROJECT_DIR"
print_status "Test execution started at: $(date)"
echo ""

# Change to project directory
cd "$PROJECT_DIR" || {
    print_error "Failed to change to project directory: $PROJECT_DIR"
    exit 1
}

# Parse command line arguments
VERBOSE=false
COVERAGE=false
FILTER=""
CONFIG="Debug"

while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -f|--filter)
            FILTER="$2"
            shift 2
            ;;
        --release)
            CONFIG="Release"
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -v, --verbose     Enable verbose output"
            echo "  -c, --coverage    Collect code coverage"
            echo "  -f, --filter      Filter tests (e.g., 'Category=Unit')"
            echo "  --release         Use Release configuration"
            echo "  -h, --help        Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Run all tests"
            echo "  $0 -v                 # Run tests with verbose output"
            echo "  $0 -c                 # Run tests with coverage"
            echo "  $0 -f 'Name~Lead'     # Run tests with 'Lead' in the name"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Clean previous test results
print_section "Cleaning previous test results"
rm -rf TestResults/ 2>/dev/null || true
rm -rf LeadProcessing.Tests/TestResults/ 2>/dev/null || true
print_success "Test results cleaned"

# Build the solution
print_section "Building solution"
print_status "Building in $CONFIG configuration..."
if dotnet build --configuration $CONFIG --verbosity minimal --no-restore; then
    print_success "Build completed successfully"
else
    print_error "Build failed!"
    exit 1
fi

# Restore packages if needed
print_section "Restoring NuGet packages"
if dotnet restore --verbosity minimal; then
    print_success "Package restore completed"
else
    print_warning "Package restore had issues"
fi

# Prepare test command
TEST_CMD="dotnet test"
TEST_CMD="$TEST_CMD --configuration $CONFIG"
TEST_CMD="$TEST_CMD --no-build"
TEST_CMD="$TEST_CMD --logger 'console;verbosity=normal'"

if [ "$VERBOSE" = true ]; then
    TEST_CMD="$TEST_CMD --verbosity normal"
else
    TEST_CMD="$TEST_CMD --verbosity minimal"
fi

if [ "$COVERAGE" = true ]; then
    TEST_CMD="$TEST_CMD --collect:'XPlat Code Coverage'"
    TEST_CMD="$TEST_CMD --results-directory ./TestResults"
fi

if [ ! -z "$FILTER" ]; then
    TEST_CMD="$TEST_CMD --filter '$FILTER'"
fi

# Run tests
print_section "Running tests"
print_status "Test command: $TEST_CMD"
print_status "Starting test execution..."
echo ""

# Create a temporary file to capture test output
TEMP_OUTPUT=$(mktemp)

# Execute tests and capture output
if eval $TEST_CMD | tee "$TEMP_OUTPUT"; then
    TEST_EXIT_CODE=0
else
    TEST_EXIT_CODE=$?
fi

echo ""

# Parse test results
print_section "Test Results Summary"

# Extract key information from test output
TOTAL_TESTS=$(grep -o "Total tests: [0-9]*" "$TEMP_OUTPUT" | grep -o "[0-9]*" || echo "0")
PASSED_TESTS=$(grep -o "Passed: [0-9]*" "$TEMP_OUTPUT" | grep -o "[0-9]*" || echo "0")
FAILED_TESTS=$(grep -o "Failed: [0-9]*" "$TEMP_OUTPUT" | grep -o "[0-9]*" || echo "0")
SKIPPED_TESTS=$(grep -o "Skipped: [0-9]*" "$TEMP_OUTPUT" | grep -o "[0-9]*" || echo "0")

# Calculate execution time
if grep -q "Total time:" "$TEMP_OUTPUT"; then
    EXECUTION_TIME=$(grep "Total time:" "$TEMP_OUTPUT" | awk '{print $3}')
else
    EXECUTION_TIME="N/A"
fi

# Display summary
echo -e "${BLUE}┌─────────────────────────────────────┐${NC}"
echo -e "${BLUE}│           TEST SUMMARY              │${NC}"
echo -e "${BLUE}├─────────────────────────────────────┤${NC}"
printf "${BLUE}│${NC} %-15s ${GREEN}%15s${NC} ${BLUE}│${NC}\n" "Total Tests:" "$TOTAL_TESTS"
printf "${BLUE}│${NC} %-15s ${GREEN}%15s${NC} ${BLUE}│${NC}\n" "Passed:" "$PASSED_TESTS"

if [ "$FAILED_TESTS" -gt 0 ]; then
    printf "${BLUE}│${NC} %-15s ${RED}%15s${NC} ${BLUE}│${NC}\n" "Failed:" "$FAILED_TESTS"
else
    printf "${BLUE}│${NC} %-15s ${GREEN}%15s${NC} ${BLUE}│${NC}\n" "Failed:" "$FAILED_TESTS"
fi

if [ "$SKIPPED_TESTS" -gt 0 ]; then
    printf "${BLUE}│${NC} %-15s ${YELLOW}%15s${NC} ${BLUE}│${NC}\n" "Skipped:" "$SKIPPED_TESTS"
else
    printf "${BLUE}│${NC} %-15s ${GREEN}%15s${NC} ${BLUE}│${NC}\n" "Skipped:" "$SKIPPED_TESTS"
fi

printf "${BLUE}│${NC} %-15s ${CYAN}%15s${NC} ${BLUE}│${NC}\n" "Execution Time:" "$EXECUTION_TIME"
echo -e "${BLUE}└─────────────────────────────────────┘${NC}"

# Show pass rate
if [ "$TOTAL_TESTS" -gt 0 ]; then
    PASS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    if [ "$PASS_RATE" -eq 100 ]; then
        echo -e "\n${GREEN}🎉 All tests passed! (${PASS_RATE}%)${NC}"
    elif [ "$PASS_RATE" -ge 90 ]; then
        echo -e "\n${YELLOW}😐 Most tests passed (${PASS_RATE}%)${NC}"
    else
        echo -e "\n${RED}😞 Many tests failed (${PASS_RATE}%)${NC}"
    fi
fi

# Show failed test details if any
if [ "$FAILED_TESTS" -gt 0 ]; then
    print_section "Failed Test Details"
    grep -A 5 -B 1 "Failed.*\[" "$TEMP_OUTPUT" || print_info "Failed test details not available in this format"
fi

# Coverage report
if [ "$COVERAGE" = true ]; then
    print_section "Code Coverage"
    if [ -d "TestResults" ]; then
        COVERAGE_FILE=$(find TestResults -name "coverage.cobertura.xml" | head -1)
        if [ ! -z "$COVERAGE_FILE" ]; then
            print_success "Coverage report generated: $COVERAGE_FILE"
            
            # Try to extract coverage percentage if available
            if command -v xmllint >/dev/null 2>&1; then
                COVERAGE_PERCENT=$(xmllint --xpath "string(//coverage/@line-rate)" "$COVERAGE_FILE" 2>/dev/null || true)
                if [ ! -z "$COVERAGE_PERCENT" ]; then
                    COVERAGE_PERCENT=$(echo "$COVERAGE_PERCENT * 100" | bc -l 2>/dev/null | cut -d. -f1 || echo "N/A")
                    print_info "Line Coverage: ${COVERAGE_PERCENT}%"
                fi
            fi
        else
            print_warning "Coverage file not found"
        fi
    else
        print_warning "TestResults directory not found"
    fi
fi

# Final status
echo ""
print_section "Final Status"
if [ $TEST_EXIT_CODE -eq 0 ]; then
    print_success "Test execution completed successfully!"
    if [ "$FAILED_TESTS" -eq 0 ]; then
        echo -e "${GREEN}🚀 Ready for deployment!${NC}"
    fi
else
    print_error "Test execution failed!"
    echo -e "${RED}🔥 Fix failing tests before deployment!${NC}"
fi

# Cleanup
rm -f "$TEMP_OUTPUT"

print_status "Test execution finished at: $(date)"
exit $TEST_EXIT_CODE