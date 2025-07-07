#!/bin/bash
# Monitor Claude execution logs in real-time

echo "🔍 Monitoring Claude Code execution logs..."
echo "Press Ctrl+C to stop"
echo ""

# Monitor all phase1 logs
tail -f logs/*_phase1_claude_execution.log 2>/dev/null | while read line; do
    # Color code based on content
    if [[ "$line" == *"SUCCESS"* ]]; then
        echo -e "\033[32m$line\033[0m"  # Green for success
    elif [[ "$line" == *"FAILED"* ]]; then
        echo -e "\033[31m$line\033[0m"  # Red for failure
    elif [[ "$line" == *"Starting Claude Code"* ]]; then
        echo -e "\033[36m$line\033[0m"  # Cyan for start
    else
        echo "$line"
    fi
done