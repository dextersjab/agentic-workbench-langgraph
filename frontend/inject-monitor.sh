#!/bin/bash

# This script injects our workflow monitor into OpenWebUI's loader.js

LOADER_PATH="/app/build/static/loader.js"
MONITOR_PATH="/workflow-monitor/workflow-monitor.js"

# Check if loader.js exists
if [ ! -f "$LOADER_PATH" ]; then
    echo "Error: loader.js not found at $LOADER_PATH"
    exit 1
fi

# Check if workflow-monitor.js exists
if [ ! -f "$MONITOR_PATH" ]; then
    echo "Error: workflow-monitor.js not found at $MONITOR_PATH"
    exit 1
fi

# Check if already injected
if grep -q "workflow-monitor" "$LOADER_PATH"; then
    echo "Removing old workflow monitor..."
    # Remove everything from the injection marker to the end
    sed -i '/\/\/ Injected Workflow Monitor/,$d' "$LOADER_PATH"
fi

echo "Injecting workflow monitor..."

# Append our script to loader.js
echo "" >> "$LOADER_PATH"
echo "// Injected Workflow Monitor" >> "$LOADER_PATH"
cat "$MONITOR_PATH" >> "$LOADER_PATH"

echo "Workflow monitor injected successfully"

# Execute the original command
exec "$@"