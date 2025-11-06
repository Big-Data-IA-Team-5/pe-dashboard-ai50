#!/bin/bash

echo "🔍 QUICK STATUS CHECK"
echo "============================================================"

# Seed data
if [ -f "data/forbes_ai50_seed.json" ]; then
    SEED=$(cat data/forbes_ai50_seed.json | jq '. | length' 2>/dev/null || echo "error")
    echo "✅ Seed data: ${SEED} companies"
else
    echo "❌ Seed data: Not found"
fi

# Payloads
PAYLOADS=$(find data/payloads -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
echo "✅ Payloads: ${PAYLOADS} companies"

# Structured dashboards
STRUCT=$(find data/dashboards/structured -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
echo "📊 Structured dashboards: ${STRUCT}/48"

# RAG dashboards
RAG=$(find data/dashboards/rag -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
echo "📊 RAG dashboards: ${RAG}/48"

# Total
TOTAL=$((STRUCT + RAG))
echo "📊 Total dashboards: ${TOTAL}/96"

echo ""

# Check if batch is running
if pgrep -f "batch_dashboard_generator" > /dev/null; then
    PID=$(pgrep -f "batch_dashboard_generator")
    echo "✅ Batch generator: Running (PID: ${PID})"
else
    echo "⏸️  Batch generator: Not running"
fi

# Check log file
if [ -f "logs/dashboard_generation.log" ]; then
    LOG_SIZE=$(wc -l < logs/dashboard_generation.log)
    echo "📝 Log file: ${LOG_SIZE} lines"
else
    echo "📝 Log file: Not found"
fi

echo ""
echo "============================================================"

# Status message
if [ $TOTAL -ge 90 ]; then
    echo "🎉 ALMOST DONE! Ready for evaluation"
elif [ $TOTAL -ge 48 ]; then
    echo "🚀 HALFWAY THERE! Keep going..."
elif [ $TOTAL -ge 10 ]; then
    echo "✅ PROGRESSING WELL!"
else
    echo "⏳ JUST STARTED..."
fi
