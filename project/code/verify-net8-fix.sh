#!/bin/bash

echo "✅ .NET 8 Downgrade Verification"
echo "================================"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}📋 Framework Verification:${NC}"
echo "=========================="

echo "Target Frameworks:"
main_fw=$(grep '<TargetFramework>' LeadProcessing.csproj | sed 's/.*<TargetFramework>\(.*\)<\/TargetFramework>.*/\1/')
test1_fw=$(grep '<TargetFramework>' LeadProcessing.Tests/LeadProcessing.Tests.csproj | sed 's/.*<TargetFramework>\(.*\)<\/TargetFramework>.*/\1/')
test2_fw=$(grep '<TargetFramework>' Tests/LeadProcessingTests.csproj | sed 's/.*<TargetFramework>\(.*\)<\/TargetFramework>.*/\1/')

echo "  Main Project: $main_fw"
echo "  Test Project 1: $test1_fw"  
echo "  Test Project 2: $test2_fw"

if [ "$main_fw" = "net8.0" ] && [ "$test1_fw" = "net8.0" ] && [ "$test2_fw" = "net8.0" ]; then
    echo -e "  ${GREEN}✅ All projects now target .NET 8.0${NC}"
else
    echo -e "  ❌ Framework mismatch still exists${NC}"
fi

echo
echo -e "${BLUE}📦 Package Version Verification:${NC}"
echo "==============================="

echo "Entity Framework Core:"
ef_main=$(grep 'Microsoft.EntityFrameworkCore.SqlServer' LeadProcessing.csproj | grep -o 'Version="[^"]*"')
ef_test1=$(grep 'Microsoft.EntityFrameworkCore.InMemory' LeadProcessing.Tests/LeadProcessing.Tests.csproj | grep -o 'Version="[^"]*"')
ef_test2=$(grep 'Microsoft.EntityFrameworkCore.InMemory' Tests/LeadProcessingTests.csproj | grep -o 'Version="[^"]*"')

echo "  Main Project: $ef_main"
echo "  Test Project 1: $ef_test1"
echo "  Test Project 2: $ef_test2"

if [[ "$ef_main" == *"8.0.10"* ]] && [[ "$ef_test1" == *"8.0.10"* ]] && [[ "$ef_test2" == *"8.0.10"* ]]; then
    echo -e "  ${GREEN}✅ All EF Core packages downgraded to 8.0.10${NC}"
else
    echo -e "  ❌ EF Core version mismatch${NC}"
fi

echo
echo "Elsa Workflows:"
elsa_version=$(grep 'Elsa"' LeadProcessing.csproj | grep -o 'Version="[^"]*"' | head -1)
elsa_ef_version=$(grep 'Elsa.EntityFrameworkCore.SqlServer' LeadProcessing.csproj | grep -o 'Version="[^"]*"')

echo "  Elsa Core: $elsa_version"
echo "  Elsa EF: $elsa_ef_version"

if [[ "$elsa_version" == *"3.4.2"* ]] && [[ "$elsa_ef_version" == *"3.4.2"* ]]; then
    echo -e "  ${GREEN}✅ Elsa updated to latest stable 3.4.2${NC}"
else
    echo -e "  ❌ Elsa version issue${NC}"
fi

echo
echo -e "${BLUE}🔧 Solution File Check:${NC}"
echo "======================"

project_count=$(grep -c "Project(" LeadProcessing.sln)
echo "Projects in solution: $project_count"

if [ $project_count -eq 3 ]; then
    echo -e "  ${GREEN}✅ Solution includes all 3 projects${NC}"
    
    # Check if paths are correct
    if grep -q "LeadProcessing.Tests/LeadProcessing.Tests.csproj" LeadProcessing.sln && grep -q "Tests/LeadProcessingTests.csproj" LeadProcessing.sln; then
        echo -e "  ${GREEN}✅ Project paths are correct${NC}"
    else
        echo -e "  ❌ Project paths need fixing${NC}"
    fi
else
    echo -e "  ❌ Solution missing projects${NC}"
fi

echo
echo -e "${BLUE}🔍 Duplicate File Check:${NC}"
echo "======================="

if [ ! -f "Services/HangfireAuthorizationFilter.cs" ]; then
    echo -e "  ${GREEN}✅ Duplicate HangfireAuthorizationFilter removed${NC}"
else
    echo -e "  ❌ Duplicate file still exists${NC}"
fi

echo
echo -e "${BLUE}📊 Compatibility Assessment:${NC}"
echo "============================"

compatibility_score=0
total_checks=5

# Check frameworks
if [ "$main_fw" = "net8.0" ] && [ "$test1_fw" = "net8.0" ] && [ "$test2_fw" = "net8.0" ]; then
    echo -e "  ${GREEN}✅ Framework Compatibility: PASS${NC}"
    compatibility_score=$((compatibility_score + 1))
fi

# Check EF Core
if [[ "$ef_main" == *"8.0.10"* ]]; then
    echo -e "  ${GREEN}✅ EF Core Compatibility: PASS${NC}"
    compatibility_score=$((compatibility_score + 1))
fi

# Check Elsa
if [[ "$elsa_version" == *"3.4.2"* ]]; then
    echo -e "  ${GREEN}✅ Elsa Compatibility: PASS${NC}"
    compatibility_score=$((compatibility_score + 1))
fi

# Check solution
if [ $project_count -eq 3 ]; then
    echo -e "  ${GREEN}✅ Solution Structure: PASS${NC}"
    compatibility_score=$((compatibility_score + 1))
fi

# Check duplicates
if [ ! -f "Services/HangfireAuthorizationFilter.cs" ]; then
    echo -e "  ${GREEN}✅ No Duplicates: PASS${NC}"
    compatibility_score=$((compatibility_score + 1))
fi

echo
echo -e "${BLUE}📊 Fix Success Rate: ${compatibility_score}/${total_checks}${NC}"

if [ $compatibility_score -eq $total_checks ]; then
    echo -e "${GREEN}🎉 All build errors should now be resolved!${NC}"
    echo
    echo -e "${YELLOW}🚀 Ready to build:${NC}"
    echo "  1. dotnet restore"
    echo "  2. dotnet build"
    echo "  3. dotnet test"
    echo
    echo -e "${YELLOW}🔮 Future .NET 9 Migration:${NC}"
    echo "  Monitor Elsa GitHub for .NET 9 support"
    echo "  When available, upgrade back to .NET 9"
elif [ $compatibility_score -ge 3 ]; then
    echo -e "${YELLOW}⚠️  Most issues fixed, minor problems remain${NC}"
else
    echo -e "❌ Significant issues still need addressing${NC}"
fi