#!/bin/bash

echo "🔍 Real Build Analysis (Without dotnet CLI)"
echo "============================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}📋 Project Structure Verification:${NC}"
echo "===================================="

# Check all project files exist and are valid
echo "1. Project Files:"
for proj in LeadProcessing.csproj LeadProcessing.Tests/LeadProcessing.Tests.csproj Tests/LeadProcessingTests.csproj; do
    if [ -f "$proj" ]; then
        echo -e "   ${GREEN}✅ $proj${NC}"
        
        # Check for basic XML validity
        if grep -q "<Project" "$proj" && grep -q "</Project>" "$proj"; then
            echo "      - Valid XML structure"
        else
            echo -e "      ${RED}- Invalid XML structure${NC}"
        fi
        
        # Check target framework
        target=$(grep -o '<TargetFramework>[^<]*</TargetFramework>' "$proj" | sed 's/<[^>]*>//g')
        echo "      - Target Framework: $target"
    else
        echo -e "   ${RED}❌ $proj (missing)${NC}"
    fi
done

echo
echo "2. Solution File:"
if [ -f "LeadProcessing.sln" ]; then
    echo -e "   ${GREEN}✅ LeadProcessing.sln${NC}"
    project_count=$(grep -c "Project(" LeadProcessing.sln)
    echo "      - Projects included: $project_count"
else
    echo -e "   ${RED}❌ LeadProcessing.sln (missing)${NC}"
fi

echo
echo -e "${BLUE}🔍 Source Code Analysis:${NC}"
echo "========================="

# Check for common compilation issues
echo "1. Namespace and Using Statement Analysis:"

# Check for missing using statements
echo "   Checking critical using statements..."

critical_usings=(
    "using Microsoft.AspNetCore"
    "using Microsoft.EntityFrameworkCore"
    "using Elsa"
    "using Hangfire"
)

for using in "${critical_usings[@]}"; do
    count=$(find . -name "*.cs" -exec grep -l "$using" {} \; 2>/dev/null | wc -l)
    if [ $count -gt 0 ]; then
        echo -e "   ${GREEN}✅ $using found in $count files${NC}"
    else
        echo -e "   ${YELLOW}⚠️  $using not found${NC}"
    fi
done

echo
echo "2. Class Definition Analysis:"

# Check for duplicate class names in the same namespace
echo "   Checking for duplicate class definitions..."

find . -name "*.cs" -type f | while read file; do
    # Extract class names and namespaces
    if grep -q "public class\|public partial class" "$file"; then
        namespace=$(grep "namespace" "$file" | head -1 | sed 's/.*namespace \([^;{]*\).*/\1/' | tr -d ' ')
        classes=$(grep "public class\|public partial class" "$file" | sed 's/.*public.*class \([^ {<]*\).*/\1/' | sort | uniq)
        
        if [ ! -z "$classes" ]; then
            echo "   📁 $file"
            echo "      Namespace: $namespace"
            echo "$classes" | while read class; do
                if [ ! -z "$class" ]; then
                    echo "      Class: $class"
                fi
            done
        fi
    fi
done | head -20  # Limit output

echo
echo "3. Method Signature Analysis:"

# Check for common method signature issues
echo "   Checking for async/await patterns..."

async_issues=0
find . -name "*.cs" -type f -exec grep -l "async.*Task" {} \; | while read file; do
    # Check for async methods without await
    if grep -q "async.*Task" "$file" && ! grep -q "await" "$file"; then
        echo -e "   ${YELLOW}⚠️  $file: async method without await${NC}"
        async_issues=$((async_issues + 1))
    fi
done

echo
echo "4. Elsa Workflow API Analysis:"

# Check Elsa-specific issues
echo "   Checking Elsa workflow configurations..."

elsa_files=$(find . -name "*.cs" -exec grep -l "Elsa\|Activity\|Workflow" {} \; 2>/dev/null)

if [ ! -z "$elsa_files" ]; then
    echo "$elsa_files" | head -5 | while read file; do
        echo "   📄 $file:"
        
        # Check for CodeActivity usage
        if grep -q "CodeActivity" "$file"; then
            echo "      - Uses CodeActivity pattern"
            
            # Check for ExecuteAsync method
            if grep -q "ExecuteAsync" "$file"; then
                echo "      - Has ExecuteAsync method"
            else
                echo -e "      ${RED}- Missing ExecuteAsync method${NC}"
            fi
        fi
        
        # Check for Input/Output properties
        if grep -q "Input<" "$file"; then
            echo "      - Uses Input<T> properties"
        fi
        
        if grep -q "Output<" "$file"; then
            echo "      - Uses Output<T> properties"
        fi
    done
else
    echo -e "   ${RED}❌ No Elsa-related files found${NC}"
fi

echo
echo -e "${BLUE}📦 Package Reference Analysis:${NC}"
echo "=============================="

# Check package references
echo "1. Package Version Consistency:"

packages=(
    "Microsoft.EntityFrameworkCore"
    "Elsa"
    "Hangfire"
    "Microsoft.AspNetCore"
)

for package in "${packages[@]}"; do
    echo "   $package versions:"
    find . -name "*.csproj" -exec grep "$package" {} \; | grep -o 'Version="[^"]*"' | sort | uniq | while read version; do
        echo "      $version"
    done
done

echo
echo "2. Missing Package References:"

# Check if required packages are referenced
required_packages=(
    "Microsoft.AspNetCore.Identity.EntityFrameworkCore"
    "Microsoft.EntityFrameworkCore.SqlServer"
    "Elsa"
    "Hangfire.Core"
)

for package in "${required_packages[@]}"; do
    if grep -r "$package" *.csproj */*.csproj 2>/dev/null | grep -q "PackageReference"; then
        echo -e "   ${GREEN}✅ $package${NC}"
    else
        echo -e "   ${RED}❌ $package (missing)${NC}"
    fi
done

echo
echo -e "${BLUE}🔧 Potential Issues Identified:${NC}"
echo "==============================="

issues_found=0

# Check for common issues
echo "1. File Missing Issues:"
critical_files=(
    "Program.cs"
    "Models/Lead.cs"
    "Models/ApplicationUser.cs"
    "Data/ApplicationDbContext.cs"
)

for file in "${critical_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "   ${RED}❌ Missing: $file${NC}"
        issues_found=$((issues_found + 1))
    fi
done

echo
echo "2. Configuration Issues:"

if [ -f "Program.cs" ]; then
    # Check Program.cs for common configuration issues
    if ! grep -q "builder.Services.AddElsa" Program.cs; then
        echo -e "   ${RED}❌ Elsa not configured in Program.cs${NC}"
        issues_found=$((issues_found + 1))
    fi
    
    if ! grep -q "builder.Services.AddHangfire" Program.cs; then
        echo -e "   ${RED}❌ Hangfire not configured in Program.cs${NC}"
        issues_found=$((issues_found + 1))
    fi
    
    if ! grep -q "AddDbContext" Program.cs; then
        echo -e "   ${RED}❌ DbContext not configured in Program.cs${NC}"
        issues_found=$((issues_found + 1))
    fi
fi

echo
if [ $issues_found -eq 0 ]; then
    echo -e "${GREEN}🎉 No major structural issues detected!${NC}"
    echo "The compilation errors are likely due to:"
    echo "1. API changes in Elsa 3.3.5"
    echo "2. Missing method implementations"
    echo "3. Incorrect method signatures"
    echo "4. Type resolution issues"
else
    echo -e "${RED}⚠️  Found $issues_found critical issues that need fixing${NC}"
fi

echo
echo -e "${BLUE}📋 Recommended Investigation:${NC}"
echo "============================="
echo "1. Check Elsa 3.3.5 API documentation for breaking changes"
echo "2. Verify all Activity base class implementations"
echo "3. Check Input/Output property syntax"
echo "4. Validate async/await patterns"
echo "5. Review namespace imports"