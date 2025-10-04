#!/bin/bash

# Comprehensive script to run the complete embedding similarity analysis
# Including embedding generation, similarity comparison, and visualization

echo "============================================"
echo "COMPLETE EMBEDDING SIMILARITY ANALYSIS"
echo "============================================"
echo ""
echo "This script will:"
echo "  1. Generate embeddings for all projects and profiles"
echo "  2. Compare similarities (matched vs unmatched)"
echo "  3. Create visualizations"
echo ""

# Check if Ollama is running
echo "[Step 1/4] Checking prerequisites..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "ERROR: Ollama service is not running"
    echo "Please start Ollama with: ollama serve"
    exit 1
fi
echo "✓ Ollama is running"

# Check if bge-m3 model is available
if ! ollama list | grep -q "bge-m3"; then
    echo "WARNING: bge-m3 model not found"
    echo "Pulling bge-m3 model (this may take a few minutes)..."
    ollama pull bge-m3
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to pull bge-m3 model"
        exit 1
    fi
fi
echo "✓ bge-m3 model is available"
echo ""

# Run embedding generation and comparison
echo "[Step 2/4] Generating embeddings and computing similarities..."
echo "This may take 15-30 minutes depending on your hardware..."
echo ""
python src/experiments/embedding_similarity_comparison.py

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Embedding analysis failed"
    exit 1
fi

echo ""
echo "[Step 3/4] Creating visualizations..."
python src/experiments/visualize_similarity_results.py

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Visualization failed"
    exit 1
fi

echo ""
echo "[Step 4/4] Generating summary report..."

# Create a simple text summary
RESULTS_FILE="outputs/embeddings/similarity_comparison_results.json"
if [ -f "$RESULTS_FILE" ]; then
    python -c "
import json
with open('$RESULTS_FILE', 'r') as f:
    data = json.load(f)
    
print('\n=== ANALYSIS SUMMARY ===\n')
print('Matched Pairs (Student_A generated for Project_A):')
print(f\"  Count: {data['analysis']['matched_pairs']['count']}\")
print(f\"  Mean Similarity: {data['analysis']['matched_pairs']['mean']:.4f}\")
print(f\"  Std Dev: {data['analysis']['matched_pairs']['std']:.4f}\")
print()
print('Unmatched Pairs (Student_not_A vs Project_A):')
print(f\"  Count: {data['analysis']['unmatched_pairs']['count']}\")
print(f\"  Mean Similarity: {data['analysis']['unmatched_pairs']['mean']:.4f}\")
print(f\"  Std Dev: {data['analysis']['unmatched_pairs']['std']:.4f}\")
print()
print('Comparison:')
print(f\"  Mean Difference: {data['analysis']['comparison']['mean_difference']:.4f}\")
print(f\"  Effect Size (Cohen's d): {data['analysis']['comparison']['effect_size_cohens_d']:.4f}\")
print()

cohens_d = data['analysis']['comparison']['effect_size_cohens_d']
if cohens_d > 0.8:
    effect = 'LARGE (d > 0.8)'
    conclusion = 'Vector similarity STRONGLY distinguishes matched pairs'
elif cohens_d > 0.5:
    effect = 'MEDIUM (0.5 < d < 0.8)'
    conclusion = 'Vector similarity MODERATELY distinguishes matched pairs'
elif cohens_d > 0.2:
    effect = 'SMALL (0.2 < d < 0.5)'
    conclusion = 'Vector similarity WEAKLY distinguishes matched pairs'
else:
    effect = 'NEGLIGIBLE (d < 0.2)'
    conclusion = 'Vector similarity does NOT effectively distinguish matched pairs'

print(f'Effect Size Interpretation: {effect}')
print(f'Conclusion: {conclusion}')
print()
"
fi

echo ""
echo "============================================"
echo "ANALYSIS COMPLETE"
echo "============================================"
echo ""
echo "Output files:"
echo "  Data:"
echo "    • outputs/embeddings/project_profile_embeddings.json"
echo "    • outputs/embeddings/similarity_comparison_results.json"
echo ""
echo "  Visualizations:"
echo "    • outputs/embeddings/similarity_histogram.png"
echo "    • outputs/embeddings/similarity_boxplot.png"
echo "    • outputs/embeddings/similarity_violin.png"
echo "    • outputs/embeddings/similarity_cdf.png"
echo "    • outputs/embeddings/similarity_dashboard.png"
echo ""
echo "Next steps:"
echo "  1. Review the visualizations in outputs/embeddings/"
echo "  2. Compare with knowledge graph-based methods"
echo "  3. Re-run with unit outline integration"


