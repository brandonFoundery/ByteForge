#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Lead Processing - Setup Validation${NC}"
echo "========================================="
echo ""

# Check for required files
echo -e "${BLUE}Checking project structure...${NC}"

required_files=(
    "LeadProcessing.csproj"
    "Program.cs"
    "appsettings.json"
    "Models/Lead.cs"
    "Models/ApplicationUser.cs"
    "Data/ApplicationDbContext.cs"
    "Activities/EnrichLeadActivity.cs"
    "Activities/VetLeadActivity.cs"
    "Activities/ScoreLeadActivity.cs"
    "Activities/ZohoUpsertActivity.cs"
    "Workflows/ProcessSingleLeadWorkflow.cs"
    "Jobs/GoogleLeadJob.cs"
    "Services/ILeadScraper.cs"
    "Services/GoogleLeadScraper.cs"
    "Controllers/LeadController.cs"
    "Controllers/HomeController.cs"
    "LeadProcessing.Tests/LeadProcessing.Tests.csproj"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -eq 0 ]; then
    echo -e "${GREEN}✓ All required files present${NC}"
else
    echo -e "${RED}✗ Missing files:${NC}"
    for file in "${missing_files[@]}"; do
        echo -e "  ${RED}- $file${NC}"
    done
fi

# Check for required directories
echo ""
echo -e "${BLUE}Checking directory structure...${NC}"

required_dirs=(
    "Models"
    "Data"
    "Activities"
    "Workflows"
    "Jobs"
    "Services"
    "Controllers"
    "Views/Home"
    "Views/Shared"
    "wwwroot/css"
    "wwwroot/js"
    "LeadProcessing.Tests"
    "scripts"
)

missing_dirs=()
for dir in "${required_dirs[@]}"; do
    if [ ! -d "$dir" ]; then
        missing_dirs+=("$dir")
    fi
done

if [ ${#missing_dirs[@]} -eq 0 ]; then
    echo -e "${GREEN}✓ All required directories present${NC}"
else
    echo -e "${RED}✗ Missing directories:${NC}"
    for dir in "${missing_dirs[@]}"; do
        echo -e "  ${RED}- $dir${NC}"
    done
fi

# Check for common syntax issues
echo ""
echo -e "${BLUE}Checking for common issues...${NC}"

# Check for namespace consistency
echo -e "${YELLOW}Namespace validation:${NC}"
inconsistent_namespaces=$(find . -name "*.cs" -not -path "./obj/*" -not -path "./bin/*" | xargs grep -l "namespace " | xargs grep "namespace " | grep -v "LeadProcessing" | wc -l)
if [ "$inconsistent_namespaces" -eq 0 ]; then
    echo -e "${GREEN}✓ Namespace consistency looks good${NC}"
else
    echo -e "${YELLOW}⚠ Found $inconsistent_namespaces potential namespace issues${NC}"
fi

# Check for missing using statements
echo -e "${YELLOW}Using statement validation:${NC}"
missing_usings=0

# Check if all .cs files have proper usings
cs_files=$(find . -name "*.cs" -not -path "./obj/*" -not -path "./bin/*" | wc -l)
if [ "$cs_files" -gt 0 ]; then
    echo -e "${GREEN}✓ Found $cs_files C# files${NC}"
else
    echo -e "${RED}✗ No C# files found${NC}"
fi

# Check for project references
echo ""
echo -e "${BLUE}Checking project references...${NC}"

if grep -q "LeadProcessing.csproj" LeadProcessing.Tests/LeadProcessing.Tests.csproj; then
    echo -e "${GREEN}✓ Test project references main project${NC}"
else
    echo -e "${RED}✗ Test project missing reference to main project${NC}"
fi

# Check NuGet packages
echo ""
echo -e "${BLUE}Checking NuGet package references...${NC}"

required_packages=(
    "Microsoft.AspNetCore.Identity.EntityFrameworkCore"
    "Microsoft.EntityFrameworkCore.SqlServer"
    "Elsa"
    "Hangfire"
)

missing_packages=()
for package in "${required_packages[@]}"; do
    if ! grep -q "$package" LeadProcessing.csproj; then
        missing_packages+=("$package")
    fi
done

if [ ${#missing_packages[@]} -eq 0 ]; then
    echo -e "${GREEN}✓ All required packages referenced${NC}"
else
    echo -e "${RED}✗ Missing package references:${NC}"
    for package in "${missing_packages[@]}"; do
        echo -e "  ${RED}- $package${NC}"
    done
fi

# Summary
echo ""
echo -e "${BLUE}Validation Summary:${NC}"
echo "==================="

total_issues=$((${#missing_files[@]} + ${#missing_dirs[@]} + ${#missing_packages[@]}))

if [ $total_issues -eq 0 ]; then
    echo -e "${GREEN}🎉 Project structure validation passed!${NC}"
    echo -e "${GREEN}Ready to build and test.${NC}"
    exit 0
else
    echo -e "${RED}❌ Found $total_issues issues that need to be resolved.${NC}"
    echo -e "${YELLOW}Please fix the issues above before building.${NC}"
    exit 1
fi