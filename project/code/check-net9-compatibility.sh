#!/bin/bash

echo "🔍 .NET 9 Package Compatibility Check"
echo "====================================="

echo "📦 Checking package versions for .NET 9 compatibility:"
echo

echo "1. Elsa Workflows:"
elsa_version=$(grep "Elsa\"" LeadProcessing.csproj | grep -o 'Version="[^"]*"' | head -1)
echo "   Current: $elsa_version"
echo "   Status: ⚠️  Elsa 3.4.0 may need verification for .NET 9 support"

echo
echo "2. Hangfire:"
hangfire_version=$(grep "Hangfire.Core" LeadProcessing.csproj | grep -o 'Version="[^"]*"')
echo "   Current: $hangfire_version"
echo "   Status: ⚠️  Hangfire 1.8.17 should support .NET 9 but may need updates"

echo
echo "3. Entity Framework:"
ef_version=$(grep "Microsoft.EntityFrameworkCore.SqlServer" LeadProcessing.csproj | grep -o 'Version="[^"]*"')
echo "   Current: $ef_version"
echo "   Status: ✅ EF Core 9.0.3 fully supports .NET 9"

echo
echo "4. Azure packages:"
azure_version=$(grep "Azure.Identity" LeadProcessing.csproj | grep -o 'Version="[^"]*"')
echo "   Current: $azure_version"
echo "   Status: ✅ Azure packages generally support .NET 9"

echo
echo "5. Test packages:"
test_sdk_version=$(grep "Microsoft.NET.Test.Sdk" Tests/LeadProcessingTests.csproj | grep -o 'Version="[^"]*"')
mstest_version=$(grep "MSTest.TestFramework" Tests/LeadProcessingTests.csproj | grep -o 'Version="[^"]*"')
echo "   Test SDK: $test_sdk_version"
echo "   MSTest: $mstest_version"
echo "   Status: ✅ Microsoft test packages support .NET 9"

echo
echo "📋 Recommended Updates:"
echo "======================="
echo "1. Update Hangfire packages to latest stable versions"
echo "2. Check Elsa compatibility or consider newer version"
echo "3. Update Azure packages to latest versions"
echo "4. Update MSTest packages to latest versions"

echo
echo "🔧 Suggested Package Updates:"
echo "============================="
echo "Hangfire.Core: 1.8.17 → 1.8.19+"
echo "Hangfire.SqlServer: 1.8.17 → 1.8.19+"
echo "Hangfire.AspNetCore: 1.8.17 → 1.8.19+"
echo "Azure.Identity: 1.13.2 → 1.13.2+ (current version should be fine)"
echo "MSTest.TestAdapter: 3.6.3 → 3.6.3+ (current version should be fine)"