#!/bin/bash

echo "🔍 Lead Processing Application - Build Validation"
echo "================================================"

# Function to check if file exists
check_file() {
    if [ -f "$1" ]; then
        echo "✅ $1"
        return 0
    else
        echo "❌ Missing: $1"
        return 1
    fi
}

# Function to check if directory exists
check_directory() {
    if [ -d "$1" ]; then
        echo "✅ Directory: $1"
        return 0
    else
        echo "❌ Missing directory: $1"
        return 1
    fi
}

# Check project structure
echo
echo "📁 Project Structure:"
check_file "LeadProcessing.csproj"
check_file "Program.cs"
check_file "appsettings.json"
check_file "appsettings.Development.json"

echo
echo "📂 Core Directories:"
check_directory "Models"
check_directory "Data" 
check_directory "Services"
check_directory "Activities"
check_directory "Workflows"
check_directory "Jobs"
check_directory "Controllers"
check_directory "Views"
check_directory "Extensions"

echo
echo "🏗️ Model Files:"
check_file "Models/ApplicationUser.cs"
check_file "Models/Lead.cs"

echo
echo "💾 Data Layer:"
check_file "Data/ApplicationDbContext.cs"

echo
echo "⚙️ Services:"
check_file "Services/FakeDataGenerator.cs"
check_file "Services/GoogleLeadScraper.cs"
check_file "Services/YellowPagesLeadScraper.cs"
check_file "Services/LinkedInLeadScraper.cs"
check_file "Services/FacebookLeadScraper.cs"
check_file "Services/ILeadScraper.cs"

echo
echo "🔄 Workflow Activities:"
check_file "Activities/EnrichLeadActivity.cs"
check_file "Activities/VetLeadActivity.cs"
check_file "Activities/ScoreLeadActivity.cs"
check_file "Activities/ZohoUpsertActivity.cs"

echo
echo "📋 Workflow Definitions:"
check_file "Workflows/ProcessSingleLeadWorkflow.cs"

echo
echo "⏰ Background Jobs:"
check_file "Jobs/GoogleLeadJob.cs"
check_file "Jobs/YellowPagesLeadJob.cs"
check_file "Jobs/LinkedInLeadJob.cs"
check_file "Jobs/FacebookLeadJob.cs"

echo
echo "🌐 Controllers:"
check_file "Controllers/HomeController.cs"
check_file "Controllers/LeadsController.cs"

echo
echo "🎨 Views:"
check_directory "Views/Home"
check_directory "Views/Leads"
check_directory "Views/Shared"
check_file "Views/Home/Index.cshtml"
check_file "Views/Leads/Index.cshtml"
check_file "Views/Leads/Dashboard.cshtml"
check_file "Views/Leads/Details.cshtml"
check_file "Views/Shared/_Layout.cshtml"

echo
echo "🔧 Extensions:"
check_file "Extensions/DatabaseSeeder.cs"
check_file "Extensions/HangfireAuthorizationFilter.cs"

echo
echo "📝 Configuration Files:"
check_file "appsettings.json"
check_file "appsettings.Development.json"

echo
echo "🧪 Test Files:"
check_directory "Tests"
check_file "Tests/LeadProcessingTests.cs"

echo
echo "📦 Static Assets:"
check_directory "wwwroot"
check_directory "wwwroot/css"
check_directory "wwwroot/js"
check_directory "wwwroot/lib"

# Check critical configuration
echo
echo "⚙️ Configuration Check:"
if grep -q "DefaultConnection" appsettings.json; then
    echo "✅ Database connection string configured"
else
    echo "❌ Missing database connection string"
fi

if grep -q "Elsa" LeadProcessing.csproj; then
    echo "✅ Elsa Workflows dependency configured"
else
    echo "❌ Missing Elsa Workflows dependency"
fi

if grep -q "Hangfire" LeadProcessing.csproj; then
    echo "✅ Hangfire dependency configured"
else
    echo "❌ Missing Hangfire dependency"
fi

if grep -q "Microsoft.AspNetCore.Identity" LeadProcessing.csproj; then
    echo "✅ ASP.NET Core Identity configured"
else
    echo "❌ Missing ASP.NET Core Identity"
fi

echo
echo "🔍 Code Analysis:"

# Check for potential syntax issues in key files
echo "Checking Program.cs structure..."
if grep -q "builder.Services.AddElsa" Program.cs; then
    echo "✅ Elsa services configured"
else
    echo "⚠️  Elsa services configuration not found"
fi

if grep -q "builder.Services.AddHangfire" Program.cs; then
    echo "✅ Hangfire services configured"
else
    echo "⚠️  Hangfire services configuration not found"
fi

if grep -q "AddDefaultIdentity" Program.cs; then
    echo "✅ Identity services configured"
else
    echo "⚠️  Identity services configuration not found"
fi

echo
echo "📊 Summary:"
echo "=========="

# Count files
total_files=$(find . -name "*.cs" -o -name "*.cshtml" -o -name "*.json" -o -name "*.csproj" | wc -l)
echo "📄 Total source files: $total_files"

cs_files=$(find . -name "*.cs" | wc -l)
echo "🔧 C# source files: $cs_files"

view_files=$(find . -name "*.cshtml" | wc -l)
echo "🎨 Razor view files: $view_files"

echo
echo "✅ Build validation complete!"
echo "📋 Ready for: dotnet build && dotnet run"