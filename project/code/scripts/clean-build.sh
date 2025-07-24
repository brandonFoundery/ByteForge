#!/bin/bash

# Clean and rebuild the entire solution
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🧹 Clean Build"
echo "=============="

cd "$PROJECT_DIR" || exit 1

echo "Cleaning solution..."
dotnet clean --verbosity minimal

echo "Restoring packages..."
dotnet restore --verbosity minimal

echo "Building solution..."
dotnet build --configuration Debug --verbosity minimal

if [ $? -eq 0 ]; then
    echo "✅ Clean build completed successfully!"
else
    echo "❌ Build failed!"
    exit 1
fi