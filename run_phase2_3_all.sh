#!/bin/bash
# Phase 2+3 Autonomous Benchmark Runner
# Runs Phase 2 (3 runs) and Phase 3 (3 runs) sequentially within each phase,
# but both phases can be launched in parallel by the caller.
#
# Usage:
#   ./run_phase2_3_all.sh phase2    # Run Phase 2 x3
#   ./run_phase2_3_all.sh phase3    # Run Phase 3 x3

set -e
cd /home/agent/neuromem
source .venv/bin/activate

PHASE="$1"

if [ "$PHASE" = "phase2" ]; then
    echo "=========================================="
    echo "PHASE 2 — GPU Offloading Verification"
    echo "=========================================="
    for RUN in 1 2 3; do
        echo ""
        echo ">>> Starting Phase 2 Run $RUN at $(date)"
        python3 /home/agent/neuromem/run_phase2_benchmark.py --run $RUN
        echo ">>> Finished Phase 2 Run $RUN at $(date)"
        echo ""
        # Brief pause between runs
        sleep 10
    done
    echo "=========================================="
    echo "ALL PHASE 2 RUNS COMPLETE"
    echo "=========================================="

elif [ "$PHASE" = "phase3" ]; then
    echo "=========================================="
    echo "PHASE 3 — Local HyDE LLM (Ollama)"
    echo "=========================================="
    # Verify Ollama is running
    if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "ERROR: Ollama not running. Starting..."
        nohup ollama serve > /tmp/ollama.log 2>&1 &
        sleep 3
    fi
    for RUN in 1 2 3; do
        echo ""
        echo ">>> Starting Phase 3 Run $RUN at $(date)"
        python3 /home/agent/neuromem/run_phase3_benchmark.py --run $RUN
        echo ">>> Finished Phase 3 Run $RUN at $(date)"
        echo ""
        sleep 10
    done
    echo "=========================================="
    echo "ALL PHASE 3 RUNS COMPLETE"
    echo "=========================================="

else
    echo "Usage: $0 [phase2|phase3]"
    exit 1
fi
