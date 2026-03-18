#!/bin/bash
# V3 Benchmark — Run all systems
# Usage: ./run_all.sh [--smoke-test]

VENV="/Users/j/Desktop/neuromem/.venv_v3/bin/python"
DIR="/Users/j/Desktop/neuromem/v3_benchmark"

SMOKE=""
if [ "$1" = "--smoke-test" ]; then
    SMOKE="--smoke-test"
    echo "=== SMOKE TEST MODE ==="
fi

echo "============================================"
echo "V3 BENCHMARK — Run All Systems"
echo "============================================"

# Baselines (no API key needed)
echo ""
echo "--- BASELINES ---"
echo "[1/16] FTS5..."
$VENV $DIR/benchmark_runner.py --adapter fts5 $SMOKE 2>&1 | tail -5

echo "[2/16] ChromaDB..."
$VENV $DIR/benchmark_runner.py --adapter chromadb $SMOKE 2>&1 | tail -5

# Neuromem (our system, no API key needed)
echo ""
echo "--- NEUROMEM (OUR SYSTEM) ---"
echo "[3/16] Neuromem (6-layer)..."
$VENV $DIR/benchmark_runner.py --adapter neuromem $SMOKE 2>&1 | tail -5

# No API key needed
echo ""
echo "--- NO API KEY NEEDED ---"
echo "[4/16] OpenMemory..."
$VENV $DIR/benchmark_runner.py --adapter openmemory $SMOKE 2>&1 | tail -5

# Need ANTHROPIC_API_KEY
echo ""
echo "--- NEED ANTHROPIC_API_KEY ---"
echo "[4/15] Mem0..."
$VENV $DIR/benchmark_runner.py --adapter mem0 $SMOKE 2>&1 | tail -5

echo "[5/15] LangMem..."
$VENV $DIR/benchmark_runner.py --adapter langmem $SMOKE 2>&1 | tail -5

echo "[6/15] Cognee..."
$VENV $DIR/benchmark_runner.py --adapter cognee $SMOKE 2>&1 | tail -5

# Need specific services or API keys
echo ""
echo "--- NEED SERVICES/KEYS ---"
echo "[7/15] Graphiti (needs Neo4j Docker)..."
$VENV $DIR/benchmark_runner.py --adapter graphiti $SMOKE 2>&1 | tail -5

echo "[8/15] Letta (needs letta server)..."
$VENV $DIR/benchmark_runner.py --adapter letta $SMOKE 2>&1 | tail -5

echo "[9/15] EverMemOS (needs EVERMEMOS_API_KEY)..."
$VENV $DIR/benchmark_runner.py --adapter evermemos $SMOKE 2>&1 | tail -5

echo "[10/15] SimpleMem (needs OPENAI_API_KEY)..."
$VENV $DIR/benchmark_runner.py --adapter simplemem $SMOKE 2>&1 | tail -5

# Likely to fail
echo ""
echo "--- MAY FAIL ---"
echo "[11/15] LightMem (stub package)..."
$VENV $DIR/benchmark_runner.py --adapter lightmem $SMOKE 2>&1 | tail -5

echo "[12/15] MemMachine (not on PyPI)..."
$VENV $DIR/benchmark_runner.py --adapter memmachine $SMOKE 2>&1 | tail -5

echo "[13/15] Hindsight (build error)..."
$VENV $DIR/benchmark_runner.py --adapter hindsight $SMOKE 2>&1 | tail -5

echo "[14/15] A-MEM (GitHub only)..."
$VENV $DIR/benchmark_runner.py --adapter amem $SMOKE 2>&1 | tail -5

echo "[15/15] Memary (Python 3.11 only)..."
$VENV $DIR/benchmark_runner.py --adapter memary $SMOKE 2>&1 | tail -5

echo ""
echo "============================================"
echo "ALL SYSTEMS DONE — Run scorer next:"
echo "  $VENV $DIR/scorer.py --all"
echo "============================================"
