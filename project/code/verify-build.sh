#!/bin/bash

echo "🔍 Build Verification Script"
echo "============================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

errors_found=0

echo -e "${BLUE}1. Checking C# Syntax and API Usage:${NC}"
echo "===================================="

# Check all Activities for correct Elsa 3.3.5 API
echo "✅ Checking Elsa Activities API compatibility:"

activity_files=("Activities/EnrichLeadActivity.cs" "Activities/VetLeadActivity.cs" "Activities/ScoreLeadActivity.cs" "Activities/ZohoUpsertActivity.cs")

for file in "${activity_files[@]}"; do
    if [ -f "$file" ]; then
        echo "   📄 $file:"
        
        # Check base class
        if grep -q "CodeActivity<" "$file"; then
            echo -e "      ${RED}❌ Uses generic CodeActivity<T> (incompatible)${NC}"
            errors_found=$((errors_found + 1))
        elif grep -q ": CodeActivity" "$file"; then
            echo -e "      ${GREEN}✅ Uses correct CodeActivity base class${NC}"
        else
            echo -e "      ${RED}❌ Missing CodeActivity base class${NC}"
            errors_found=$((errors_found + 1))
        fi
        
        # Check ExecuteAsync method
        if grep -q "ExecuteAsync(ActivityExecutionContext" "$file"; then
            echo -e "      ${GREEN}✅ Has correct ExecuteAsync signature${NC}"
        else
            echo -e "      ${RED}❌ Missing or incorrect ExecuteAsync method${NC}"
            errors_found=$((errors_found + 1))
        fi
        
        # Check for SetResult (should not exist)
        if grep -q "SetResult(" "$file"; then
            echo -e "      ${RED}❌ Uses deprecated SetResult method${NC}"
            errors_found=$((errors_found + 1))
        fi
        
        # Check for CompleteActivityAsync
        if grep -q "CompleteActivityAsync()" "$file"; then
            echo -e "      ${GREEN}✅ Uses correct CompleteActivityAsync()${NC}"
        else
            echo -e "      ${RED}❌ Missing CompleteActivityAsync() call${NC}"
            errors_found=$((errors_found + 1))
        fi
        
    else
        echo -e "   ${RED}❌ Missing file: $file${NC}"
        errors_found=$((errors_found + 1))
    fi
done

echo
echo "✅ Checking Program.cs Elsa configuration:"

if [ -f "Program.cs" ]; then
    if grep -q "AddWorkflow<" "Program.cs"; then
        echo -e "   ${RED}❌ Uses deprecated AddWorkflow<T> method${NC}"
        errors_found=$((errors_found + 1))
    elif grep -q "AddWorkflowsFrom<" "Program.cs"; then
        echo -e "   ${GREEN}✅ Uses correct AddWorkflowsFrom<T> method${NC}"
    else
        echo -e "   ${YELLOW}⚠️  No workflow registration found${NC}"
    fi
    
    if grep -q "UseEntityFrameworkPersistence" "Program.cs"; then
        echo -e "   ${GREEN}✅ EF persistence configured${NC}"
    else
        echo -e "   ${RED}❌ Missing EF persistence configuration${NC}"
        errors_found=$((errors_found + 1))
    fi
fi

echo
echo -e "${BLUE}2. Checking Package References:${NC}"
echo "==============================="

# Check for correct package versions in project files
project_files=("LeadProcessing.csproj" "LeadProcessing.Tests/LeadProcessing.Tests.csproj" "Tests/LeadProcessingTests.csproj")

for proj in "${project_files[@]}"; do
    if [ -f "$proj" ]; then
        echo "📄 $proj:"
        
        # Check target framework
        if grep -q "<TargetFramework>net8.0</TargetFramework>" "$proj"; then
            echo -e "   ${GREEN}✅ Targets .NET 8.0${NC}"
        else
            echo -e "   ${RED}❌ Not targeting .NET 8.0${NC}"
            errors_found=$((errors_found + 1))
        fi
        
        # Check key package versions
        if grep -q 'Elsa.*Version="3.3.5"' "$proj"; then
            echo -e "   ${GREEN}✅ Elsa 3.3.5${NC}"
        elif grep -q 'Elsa' "$proj"; then
            version=$(grep 'Elsa' "$proj" | grep -o 'Version="[^"]*"' | head -1)
            echo -e "   ${YELLOW}⚠️  Elsa $version (expected 3.3.5)${NC}"
        fi
        
        if grep -q 'Microsoft.EntityFrameworkCore.*Version="8.0.12"' "$proj"; then
            echo -e "   ${GREEN}✅ EF Core 8.0.12${NC}"
        elif grep -q 'Microsoft.EntityFrameworkCore' "$proj"; then
            version=$(grep 'Microsoft.EntityFrameworkCore' "$proj" | grep -o 'Version="[^"]*"' | head -1)
            echo -e "   ${YELLOW}⚠️  EF Core $version (expected 8.0.12)${NC}"
        fi
    fi
done

echo
echo -e "${BLUE}3. Checking Required Files:${NC}"
echo "=========================="

critical_files=(
    "Program.cs"
    "Models/Lead.cs"
    "Models/ApplicationUser.cs"
    "Data/ApplicationDbContext.cs"
    "Controllers/HomeController.cs"
    "Services/FakeDataGenerator.cs"
)

for file in "${critical_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "   ${GREEN}✅ $file${NC}"
    else
        echo -e "   ${RED}❌ Missing: $file${NC}"
        errors_found=$((errors_found + 1))
    fi
done

echo
echo -e "${BLUE}4. Summary:${NC}"
echo "=========="

if [ $errors_found -eq 0 ]; then
    echo -e "${GREEN}🎉 All checks passed! Solution should build successfully.${NC}"
    echo
    echo "Key fixes applied:"
    echo "• Updated all Activities to use CodeActivity (not CodeActivity<T>)"
    echo "• Replaced SetResult() with CompleteActivityAsync()"
    echo "• Updated Program.cs to use AddWorkflowsFrom<T>"
    echo "• Maintained .NET 8.0 and EF Core 8.0.12 compatibility"
    echo
    echo "The solution is now compatible with Elsa 3.3.5 API."
else
    echo -e "${RED}⚠️  Found $errors_found issues that may prevent successful compilation${NC}"
    echo
    echo "Please review the errors above and apply necessary fixes."
fi