#!/bin/bash

# Quick test runner - runs tests without full output
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🚀 Quick Test Run"
echo "=================="

cd "$PROJECT_DIR" || exit 1

# Run tests quietly and show just the summary
dotnet test --configuration Debug --verbosity quiet --no-build --logger "console;verbosity=minimal" 2>/dev/null

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Some tests failed. Run './scripts/run-tests.sh -v' for details."
fi

exit $EXIT_CODE