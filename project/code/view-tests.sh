#!/bin/bash

echo "🧪 Lead Processing System - Test Viewer"
echo "======================================="

echo "📋 Available Test Projects:"
echo "1. Tests/LeadProcessingTests.csproj - Core functionality tests"
echo "2. LeadProcessing.Tests/LeadProcessing.Tests.csproj - Comprehensive test suite"
echo

echo "🔍 Test Methods in Tests/LeadProcessingTests.cs:"
echo "==============================================="

# Extract test methods from the main test file
grep -n "\[TestMethod\]" Tests/LeadProcessingTests.cs -A 2 | while IFS= read -r line; do
    if [[ $line == *"[TestMethod]"* ]]; then
        echo -n "📝 "
    elif [[ $line == *"public"* ]] && [[ $line == *"void"* ]] && [[ $line == *"("* ]]; then
        # Extract method name
        method_name=$(echo "$line" | sed 's/.*public.*void \([^(]*\).*/\1/' | xargs)
        echo "Test: $method_name"
    fi
done

echo
echo "🔍 Test Methods in LeadProcessing.Tests/ directory:"
echo "=================================================="

# Find all test files in the comprehensive test suite
find LeadProcessing.Tests -name "*.cs" -type f | while read -r file; do
    if [[ -f "$file" ]]; then
        echo
        echo "📁 File: $file"
        echo "   Test Methods:"
        grep -n "\[Test\]" "$file" -A 1 2>/dev/null | while IFS= read -r line; do
            if [[ $line == *"public"* ]] && [[ $line == *"void"* ]] && [[ $line == *"("* ]]; then
                method_name=$(echo "$line" | sed 's/.*public.*void \([^(]*\).*/\1/' | xargs)
                echo "   ✅ $method_name"
            fi
        done
        
        # Also check for MSTest methods
        grep -n "\[TestMethod\]" "$file" -A 1 2>/dev/null | while IFS= read -r line; do
            if [[ $line == *"public"* ]] && [[ $line == *"void"* ]] && [[ $line == *"("* ]]; then
                method_name=$(echo "$line" | sed 's/.*public.*void \([^(]*\).*/\1/' | xargs)
                echo "   ✅ $method_name"
            fi
        done
    fi
done

echo
echo "📊 Test Categories and Coverage:"
echo "==============================="

echo "🔧 Unit Tests:"
echo "   - Lead model validation"
echo "   - FakeDataGenerator functionality"
echo "   - Lead scraper services (Google, LinkedIn, YellowPages, Facebook)"
echo "   - Email validation logic"
echo "   - Database operations"
echo "   - Lead scoring logic"

echo
echo "🧪 Integration Tests:"
echo "   - Database context operations"
echo "   - Service integration"
echo "   - Workflow activities"

echo
echo "🚀 How to Run Tests:"
echo "==================="
echo "1. With dotnet CLI:"
echo "   dotnet test                           # Run all tests"
echo "   dotnet test --logger console         # Detailed console output"
echo "   dotnet test --filter TestMethodName  # Run specific test"
echo
echo "2. With Visual Studio:"
echo "   - Open Test Explorer (Test > Test Explorer)"
echo "   - Build solution (Ctrl+Shift+B)"
echo "   - Run all tests (Ctrl+R, A)"
echo
echo "3. With VS Code:"
echo "   - Install .NET Test Explorer extension"
echo "   - Use Test Explorer panel"
echo "   - Run/debug individual tests"
echo
echo "4. With JetBrains Rider:"
echo "   - Unit Tests window (View > Tool Windows > Unit Tests)"
echo "   - Right-click test methods to run"
echo
echo "📈 Test Results Location:"
echo "========================"
echo "   - Console output: Real-time results"
echo "   - TestResults/: TRX files for detailed analysis"
echo "   - Coverage reports: If coverage tools are configured"
echo
echo "💡 Test Features:"
echo "================"
echo "   ✅ In-memory database for fast testing"
echo "   ✅ Dependency injection setup"
echo "   ✅ Mocked external services"
echo "   ✅ Data validation testing"
echo "   ✅ Business logic verification"
echo "   ✅ Integration testing"