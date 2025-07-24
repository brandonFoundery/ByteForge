#!/bin/bash

echo "🔍 Package Version Verification"
echo "==============================="

echo "📦 Main Project (LeadProcessing.csproj):"
echo "========================================="
grep -E "Microsoft\.EntityFrameworkCore|Microsoft\.AspNetCore\.Identity\.EntityFrameworkCore" LeadProcessing.csproj | sed 's/^[ \t]*/  /'

echo
echo "📦 Test Project 1 (LeadProcessing.Tests/LeadProcessing.Tests.csproj):"
echo "===================================================================="
grep -E "Microsoft\.EntityFrameworkCore|Microsoft\.AspNetCore" LeadProcessing.Tests/LeadProcessing.Tests.csproj | sed 's/^[ \t]*/  /'

echo
echo "📦 Test Project 2 (Tests/LeadProcessingTests.csproj):"
echo "====================================================="
grep -E "Microsoft\.EntityFrameworkCore|Microsoft\.AspNetCore" Tests/LeadProcessingTests.csproj | sed 's/^[ \t]*/  /'

echo
echo "✅ Version Consistency Check:"
echo "=============================="

# Check for version conflicts
ef_versions=$(grep -h "Microsoft\.EntityFrameworkCore" LeadProcessing.csproj LeadProcessing.Tests/LeadProcessing.Tests.csproj Tests/LeadProcessingTests.csproj | grep -o 'Version="[^"]*"' | sort | uniq)
echo "EF Core versions found:"
echo "$ef_versions" | sed 's/^/  /'

identity_versions=$(grep -h "Microsoft\.AspNetCore\.Identity\.EntityFrameworkCore" LeadProcessing.csproj LeadProcessing.Tests/LeadProcessing.Tests.csproj | grep -o 'Version="[^"]*"' | sort | uniq)
echo
echo "Identity EF Core versions found:"
echo "$identity_versions" | sed 's/^/  /'

mvc_versions=$(grep -h "Microsoft\.AspNetCore\.Mvc\.Testing" LeadProcessing.Tests/LeadProcessing.Tests.csproj Tests/LeadProcessingTests.csproj | grep -o 'Version="[^"]*"' | sort | uniq)
echo
echo "MVC Testing versions found:"
echo "$mvc_versions" | sed 's/^/  /'

echo
echo "📋 Expected Results:"
echo "==================="
echo "  ✅ All EF Core packages should be version 9.0.3"
echo "  ✅ All Identity packages should be version 9.0.3"  
echo "  ✅ All MVC Testing packages should be version 9.0.3"
echo "  ✅ No version conflicts should exist"

echo
echo "🚀 Next Steps:"
echo "=============="
echo "  1. Run: dotnet restore"
echo "  2. Run: dotnet build"
echo "  3. Run: dotnet test"
echo "  4. Verify no NU1605 warnings appear"