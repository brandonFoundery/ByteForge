#!/bin/bash

echo "🧪 Lead Processing System - Test Runner"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📦 Restoring test dependencies...${NC}"
dotnet restore

echo
echo -e "${BLUE}🔨 Building test projects...${NC}"
dotnet build --configuration Release

echo
echo -e "${BLUE}🧪 Running all tests with detailed output...${NC}"
echo "=================================================="

# Run main test project with verbose output
echo -e "${YELLOW}Running Tests/LeadProcessingTests.csproj:${NC}"
dotnet test Tests/LeadProcessingTests.csproj --logger "console;verbosity=detailed" --configuration Release

echo
echo -e "${YELLOW}Running LeadProcessing.Tests/LeadProcessing.Tests.csproj:${NC}"
dotnet test LeadProcessing.Tests/LeadProcessing.Tests.csproj --logger "console;verbosity=detailed" --configuration Release

echo
echo -e "${GREEN}✅ Test execution complete!${NC}"

# Generate test coverage report if available
echo
echo -e "${BLUE}📊 Generating test summary...${NC}"
dotnet test --logger "trx" --results-directory TestResults/

if [ -d "TestResults" ]; then
    echo -e "${GREEN}📄 Test results saved to TestResults/ directory${NC}"
fi

echo
echo -e "${YELLOW}💡 To run specific tests:${NC}"
echo "dotnet test --filter TestMethodName"
echo "dotnet test --filter ClassName"
echo "dotnet test --filter \"Category=Unit\""
echo
echo -e "${YELLOW}💡 To run tests in watch mode:${NC}"
echo "dotnet watch test"