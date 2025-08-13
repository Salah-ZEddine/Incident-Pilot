#!/bin/bash
# Test Log Generator for Incident Pilot
# This script runs the Python log generator with default settings

echo "🚀 Incident Pilot - Log Generator Test Script"
echo "==============================================="
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python is not installed or not in PATH"
    echo "Please install Python 3.7+ and try again"
    read -p "Press any key to exit..."
    exit 1
fi

echo "✅ Python found"
echo

# Run the log generator
echo "📝 Starting log generation..."
python3 test.py --count 3 --delay 1.5 --output ~/test-logs.log

if [ $? -eq 0 ]; then
    echo
    echo "✅ Log generation completed successfully!"
    echo "📁 Logs saved to: ~/test-logs.log"
    echo
    echo "📋 You can now:"
    echo "  1. Check the generated logs: cat ~/test-logs.log"
    echo "  2. Start your log processor service"
    echo "  3. Start your anomaly detector service"
    echo "  4. Feed these logs into your pipeline"
else
    echo
    echo "❌ Log generation failed"
fi

echo
read -p "Press any key to continue..." -n1 -s
echo