#!/bin/bash

echo "🔍 Build Error Diagnosis"
echo "========================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}📋 Project Structure Analysis:${NC}"
echo "============================="

echo "1. Solution File Projects:"
grep "Project(" LeadProcessing.sln | while read line; do
    project_name=$(echo "$line" | sed 's/.*= "\([^"]*\)".*/\1/')
    project_path=$(echo "$line" | sed 's/.*", "\([^"]*\)".*/\1/')
    echo "   - $project_name: $project_path"
    
    # Check if project file exists
    if [ -f "$project_path" ]; then
        echo -e "     ${GREEN}✅ File exists${NC}"
    else
        echo -e "     ${RED}❌ File missing${NC}"
    fi
done

echo
echo "2. Actual Project Files:"
find . -name "*.csproj" -type f | while read project; do
    project_name=$(basename "$project" .csproj)
    echo "   - $project_name: $project"
done

echo
echo -e "${BLUE}🔍 Potential Conflicts:${NC}"
echo "======================="

echo "1. Duplicate Class Names:"
# Check for duplicate class names
find . -name "*.cs" -type f -exec basename {} .cs \; | sort | uniq -d | while read duplicate; do
    echo -e "   ${YELLOW}⚠️  Duplicate class name: $duplicate${NC}"
    find . -name "$duplicate.cs" -type f | while read file; do
        namespace=$(grep "namespace" "$file" | head -1 | sed 's/.*namespace \([^;]*\).*/\1/')
        echo "     - $file (namespace: $namespace)"
    done
done

echo
echo "2. Missing Namespace References:"
# Check for common missing references
missing_refs=0

if ! grep -q "using Elsa.Workflows;" Activities/*.cs 2>/dev/null; then
    echo -e "   ${RED}❌ Missing Elsa.Workflows using statements${NC}"
    missing_refs=$((missing_refs + 1))
fi

if ! grep -q "Microsoft.Extensions.DependencyInjection" Program.cs; then
    echo -e "   ${RED}❌ Missing DependencyInjection reference${NC}"
    missing_refs=$((missing_refs + 1))
fi

echo
echo "3. File Existence Check:"
# Check for referenced files that might not exist
critical_files=(
    "Models/Lead.cs"
    "Models/ApplicationUser.cs"
    "Data/ApplicationDbContext.cs"
    "Activities/EnrichLeadActivity.cs"
    "Workflows/ProcessSingleLeadWorkflow.cs"
    "Extensions/HangfireAuthorizationFilter.cs"
)

for file in "${critical_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "   ${GREEN}✅ $file${NC}"
    else
        echo -e "   ${RED}❌ Missing: $file${NC}"
    fi
done

echo
echo -e "${BLUE}🔧 Elsa Workflow API Check:${NC}"
echo "==========================="

# Check for potential Elsa API issues
if grep -q "CodeActivity<" Activities/*.cs 2>/dev/null; then
    echo -e "   ${GREEN}✅ CodeActivity usage found${NC}"
    
    # Check for correct base class usage
    if grep -q "protected override.*ExecuteAsync" Activities/*.cs 2>/dev/null; then
        echo -e "   ${GREEN}✅ ExecuteAsync method found${NC}"
    else
        echo -e "   ${RED}❌ ExecuteAsync method missing or incorrect${NC}"
    fi
else
    echo -e "   ${RED}❌ No CodeActivity usage found${NC}"
fi

echo
echo -e "${BLUE}📦 Package Compatibility:${NC}"
echo "========================="

# Check for Elsa version compatibility
elsa_version=$(grep 'Elsa"' LeadProcessing.csproj | grep -o 'Version="[^"]*"' | head -1)
echo "Elsa Version: $elsa_version"

if [[ "$elsa_version" == *"3.4.0"* ]]; then
    echo -e "   ${YELLOW}⚠️  Elsa 3.4.0 may have API changes incompatible with .NET 9${NC}"
    echo "   Consider checking Elsa documentation for .NET 9 compatibility"
fi

echo
echo -e "${BLUE}🚨 Critical Issues Summary:${NC}"
echo "=========================="

critical_issues=0

# Check for solution file issues
if [ $(grep -c "Project(" LeadProcessing.sln) -ne 3 ]; then
    echo -e "   ${RED}❌ Solution file doesn't include all 3 projects${NC}"
    critical_issues=$((critical_issues + 1))
fi

# Check for duplicate files
if [ -f "Services/HangfireAuthorizationFilter.cs" ] && [ -f "Extensions/HangfireAuthorizationFilter.cs" ]; then
    echo -e "   ${RED}❌ Duplicate HangfireAuthorizationFilter files${NC}"
    critical_issues=$((critical_issues + 1))
fi

echo
echo -e "${BLUE}📋 Recommended Fixes:${NC}"
echo "===================="
echo "1. Ensure solution file includes all 3 projects"
echo "2. Remove duplicate HangfireAuthorizationFilter from Services"
echo "3. Check Elsa 3.4.0 API compatibility with .NET 9"
echo "4. Verify all using statements are correct"
echo "5. Check for namespace conflicts"
echo "6. Validate all referenced packages are .NET 9 compatible"

if [ $critical_issues -eq 0 ]; then
    echo -e "${GREEN}🎉 No critical issues detected!${NC}"
else
    echo -e "${RED}⚠️  Found $critical_issues critical issues that need fixing${NC}"
fi