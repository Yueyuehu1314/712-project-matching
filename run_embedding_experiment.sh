#!/bin/bash

# Script to run embedding similarity comparison experiment
# This script ensures Ollama is running and executes the embedding analysis

echo "============================================"
echo "Embedding Similarity Comparison Experiment"
echo "============================================"
echo ""

# Check if Ollama is running
echo "[1/3] Checking Ollama service..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "ERROR: Ollama service is not running"
    echo "Please start Ollama with: ollama serve"
    exit 1
fi
echo "✓ Ollama is running"
echo ""

# Check if bge-m3 model is available
echo "[2/3] Checking bge-m3 model..."
if ! ollama list | grep -q "bge-m3"; then
    echo "WARNING: bge-m3 model not found"
    echo "Pulling bge-m3 model..."
    ollama pull bge-m3
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to pull bge-m3 model"
        exit 1
    fi
fi
echo "✓ bge-m3 model is available"
echo ""

# Run the experiment
echo "[3/3] Running embedding similarity comparison..."
python src/experiments/embedding_similarity_comparison.py

echo ""
echo "============================================"
echo "Experiment Complete"
echo "============================================"
echo ""
echo "Results saved to:"
echo "  • outputs/embeddings/project_profile_embeddings.json"
echo "  • outputs/embeddings/similarity_comparison_results.json"


