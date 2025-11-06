#!/bin/bash

echo "📊 BATCH GENERATION MONITOR"
echo "Checking every 60 seconds (Press Ctrl+C to stop)"
echo ""

while true; do
    clear
    echo "⏰ Current Time: $(date '+%I:%M:%S %p')"
    echo "=" * 60
    echo ""
    
    # Count generated dashboards
    STRUCT=$(find data/dashboards/structured -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    RAG=$(find data/dashboards/rag -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    TOTAL=$((STRUCT + RAG))
    
    echo "📈 Dashboard Progress:"
    echo "   Structured: ${STRUCT}/48"
    echo "   RAG:        ${RAG}/48"
    echo "   Total:      ${TOTAL}/96"
    echo ""
    
    # Progress bar
    PERCENT=$((TOTAL * 100 / 96))
    BAR_LENGTH=40
    FILLED=$((PERCENT * BAR_LENGTH / 100))
    
    echo -n "   Progress: ["
    for ((i=0; i<BAR_LENGTH; i++)); do
        if [ $i -lt $FILLED ]; then
            echo -n "█"
        else
            echo -n "░"
        fi
    done
    echo "] ${PERCENT}%"
    echo ""
    
    # Check if process is running
    if pgrep -f "batch_dashboard_generator" > /dev/null; then
        echo "✅ Status: Running"
        
        # Show latest from log if exists
        if [ -f "logs/dashboard_generation.log" ]; then
            echo ""
            echo "📝 Latest activity:"
            tail -3 logs/dashboard_generation.log | sed 's/^/   /'
        fi
    else
        echo "⚠️  Status: Not running"
        
        if [ $TOTAL -ge 90 ]; then
            echo "   🎉 Looks complete!"
        else
            echo "   ⚠️  Process may have stopped"
        fi
    fi
    
    # Completion check
    if [ $TOTAL -ge 96 ]; then
        echo ""
        echo "=" * 60
        echo "🎉 BATCH GENERATION COMPLETE!"
        echo "=" * 60
        echo ""
        echo "Next: Run evaluation"
        echo "  python scripts/batch_evaluator.py"
        break
    fi
    
    echo ""
    echo "Press Ctrl+C to stop monitoring"
    sleep 60
done
