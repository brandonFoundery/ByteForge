#!/bin/bash

echo "🔨 .NET 9 Compilation Check"
echo "==========================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📋 Checking project structure...${NC}"

# Check target frameworks
echo "Target Frameworks:"
echo "  Main Project: $(grep '<TargetFramework>' LeadProcessing.csproj | sed 's/.*<TargetFramework>\(.*\)<\/TargetFramework>.*/\1/')"
echo "  Test Project 1: $(grep '<TargetFramework>' LeadProcessing.Tests/LeadProcessing.Tests.csproj | sed 's/.*<TargetFramework>\(.*\)<\/TargetFramework>.*/\1/')"
echo "  Test Project 2: $(grep '<TargetFramework>' Tests/LeadProcessingTests.csproj | sed 's/.*<TargetFramework>\(.*\)<\/TargetFramework>.*/\1/')"

echo
echo -e "${BLUE}📦 Simulating: dotnet restore${NC}"
echo "  Determining projects to restore..."
echo "  - Checking LeadProcessing.csproj dependencies..."
echo "  - Checking LeadProcessing.Tests/LeadProcessing.Tests.csproj dependencies..."
echo "  - Checking Tests/LeadProcessingTests.csproj dependencies..."

echo
echo -e "${BLUE}🔨 Simulating: dotnet build${NC}"
echo "  Microsoft (R) Build Engine version 17.0.0 for .NET"
echo "  Determining projects to build..."

echo
echo -e "${YELLOW}⚠️  Potential .NET 9 Compatibility Issues:${NC}"

# Check for potential issues
echo "1. Package Compatibility:"
echo "   - Elsa 3.4.0 compatibility with .NET 9"
echo "   - Hangfire 1.8.17 compatibility with .NET 9"
echo "   - Azure packages compatibility"

echo
echo "2. Framework Misalignment:"
if [ "$(grep '<TargetFramework>' Tests/LeadProcessingTests.csproj | grep -c 'net8.0')" -gt 0 ]; then
    echo "   ❌ Tests/LeadProcessingTests.csproj still targets net8.0"
else
    echo "   ✅ Tests/LeadProcessingTests.csproj targets correct framework"
fi

echo
echo "3. API Changes in .NET 9:"
echo "   - Check for breaking changes in Entity Framework 9"
echo "   - Verify ASP.NET Core 9 compatibility"
echo "   - Review Identity framework changes"

echo
echo -e "${BLUE}🔍 Analyzing code for .NET 9 issues...${NC}"

# Check for common .NET 9 breaking changes
echo "Scanning for potential breaking changes..."

# Check for obsolete APIs
if grep -r "ConfigureServices\|UseStartup" --include="*.cs" . >/dev/null 2>&1; then
    echo "   ⚠️  Found potential obsolete hosting APIs"
fi

# Check for removed APIs
if grep -r "IHostingEnvironment\|IApplicationLifetime" --include="*.cs" . >/dev/null 2>&1; then
    echo "   ⚠️  Found deprecated hosting interfaces"
fi

echo
echo -e "${GREEN}📋 Next Steps:${NC}"
echo "1. Update test projects to .NET 9"
echo "2. Check package compatibility with .NET 9"
echo "3. Update any deprecated APIs"
echo "4. Test compilation and fix errors"
echo "5. Run tests to verify functionality"