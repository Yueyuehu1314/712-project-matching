# Embedding Similarity Experiment - Execution Guide

## Overview

This guide helps you execute the embedding-based similarity comparison experiment to test whether vector cosine similarity can effectively distinguish between matched and unmatched project-student pairs.

**Research Hypothesis**: Student profiles generated for a specific project (Student_A for Project_A) should show higher embedding similarity with that project compared to profiles generated for other projects (Student_not_A for Project_A).

## Prerequisites

### 1. System Requirements
- **Python**: 3.8 or higher
- **RAM**: At least 4 GB available
- **Disk Space**: ~500 MB for embeddings and results
- **OS**: macOS, Linux, or Windows with WSL

### 2. Software Installation

#### Install Ollama
```bash
# macOS
brew install ollama

# Linux
curl https://ollama.ai/install.sh | sh

# For other platforms, visit: https://ollama.ai/
```

#### Install Python Dependencies
```bash
pip install requests numpy matplotlib seaborn
```

### 3. Download bge-m3 Model
```bash
ollama pull bge-m3
```

This will download the BGE-M3 embedding model (~2 GB). Wait for completion before proceeding.

## Quick Start

### Step 1: Verify Setup
```bash
# Start Ollama service (in a separate terminal)
ollama serve

# In your project terminal, run the test script
python test_embedding_setup.py
```

Expected output:
```
============================================================
EMBEDDING ANALYSIS SETUP TEST
============================================================

[Test 1/5] Checking Python dependencies...
  ✓ requests
  ✓ numpy

[Test 2/5] Checking Ollama service...
  ✓ Ollama is running

[Test 3/5] Checking bge-m3 model...
  ✓ bge-m3 model is available

[Test 4/5] Checking data directories...
  ✓ Found 20 project files
  ✓ Found 200 profile files across 20 projects

[Test 5/5] Testing embedding generation...
  ✓ Successfully generated test embedding (dimension: 1024)

============================================================
✓ ALL TESTS PASSED
============================================================
```

### Step 2: Run Full Analysis
```bash
./run_full_embedding_analysis.sh
```

This script will:
1. Generate embeddings for all projects and profiles (~15-30 minutes)
2. Compute cosine similarities for all pairs (~2-5 minutes)
3. Create visualizations (~1 minute)
4. Display summary results

## Step-by-Step Execution

If you prefer to run each step manually:

### Step 1: Generate Embeddings
```bash
python src/experiments/embedding_similarity_comparison.py
```

**What it does**:
- Reads all project files from `data/processed/projects_md/`
- Reads all profile files from `data/processed/profiles_md/`
- Generates bge-m3 embeddings for each document
- Saves to `outputs/embeddings/project_profile_embeddings.json`

**Progress indicators**:
```
=== Generating embeddings for 20 projects ===
[1/20] Processing: Project_A.md
[2/20] Processing: Project_B.md
...
✓ Generated 20 project embeddings

=== Generating embeddings for 200 profiles across 20 projects ===
[1/200] Processing: Project_A/n12345_John_Doe.md
...
✓ Generated 200 profile embeddings
```

**Expected duration**: 15-30 minutes (depends on CPU speed)

### Step 2: Compute Similarities
This happens automatically in Step 1 and produces:
- `outputs/embeddings/similarity_comparison_results.json`

**What it analyzes**:
- Compares each project with each profile
- Labels pairs as "matched" or "unmatched"
- Computes cosine similarity for all pairs
- Calculates statistics (mean, std, effect size)

### Step 3: Create Visualizations
```bash
python src/experiments/visualize_similarity_results.py
```

**Generates 5 plots**:
1. **Histogram**: Overlapping distributions
2. **Box Plot**: Quartile comparison
3. **Violin Plot**: Distribution shapes
4. **CDF**: Cumulative distributions
5. **Dashboard**: Comprehensive summary

**Output files**:
```
outputs/embeddings/
├── similarity_histogram.png
├── similarity_boxplot.png
├── similarity_violin.png
├── similarity_cdf.png
└── similarity_dashboard.png
```

## Understanding the Results

### Key Metrics

#### 1. Mean Similarity
- **Matched pairs**: Should be higher (e.g., 0.75-0.85)
- **Unmatched pairs**: Should be lower (e.g., 0.60-0.70)

#### 2. Cohen's d (Effect Size)
Measures how well embeddings distinguish matched from unmatched pairs:
- **d > 0.8**: Large effect → **Strong evidence** for using embeddings
- **0.5 < d < 0.8**: Medium effect → **Moderate evidence**
- **0.2 < d < 0.5**: Small effect → **Weak evidence**
- **d < 0.2**: Negligible → **Not effective**

### Example Results Interpretation

**Scenario 1: Strong Distinction**
```
Matched pairs: mean = 0.7845, std = 0.0523
Unmatched pairs: mean = 0.6523, std = 0.0612
Cohen's d: 2.31
```
**Interpretation**: Excellent! Large effect size indicates vector similarity strongly distinguishes matched pairs. Embeddings are highly effective.

**Scenario 2: Weak Distinction**
```
Matched pairs: mean = 0.7123, std = 0.0845
Unmatched pairs: mean = 0.6934, std = 0.0923
Cohen's d: 0.21
```
**Interpretation**: Small effect. Vector similarity shows limited ability to distinguish pairs. May need to combine with other methods.

## Output Files

### 1. Embeddings File
**Path**: `outputs/embeddings/project_profile_embeddings.json`

**Size**: ~100-200 MB

**Structure**:
```json
{
  "generated_at": "2025-10-04T14:30:00",
  "model": "bge-m3",
  "total_documents": 220,
  "embeddings": [
    {
      "file_path": "data/processed/projects_md/Project_A.md",
      "file_name": "Project_A.md",
      "doc_type": "project",
      "embedding": [0.123, -0.456, ..., 0.789],  // 1024 dimensions
      "matched_project": null
    },
    {
      "file_path": "data/processed/profiles_md/Project_A/student.md",
      "file_name": "student.md",
      "doc_type": "profile",
      "embedding": [0.234, -0.567, ..., 0.891],
      "matched_project": "Project_A",
      "project_folder": "Project_A"
    }
  ]
}
```

### 2. Results File
**Path**: `outputs/embeddings/similarity_comparison_results.json`

**Size**: ~50-100 KB

**Contains**:
- Statistical analysis (means, std devs, quartiles)
- Effect size calculation
- Raw similarity scores for all pairs

### 3. Visualizations
All PNG files at 300 DPI, suitable for publication.

## Troubleshooting

### Problem: "Ollama service is not available"
**Solution**:
```bash
# Start Ollama in a separate terminal
ollama serve

# Keep this terminal running while you execute the experiment
```

### Problem: "bge-m3 model not found"
**Solution**:
```bash
ollama pull bge-m3
```

### Problem: Script runs very slowly
**Possible causes**:
1. **CPU-only mode**: bge-m3 is running on CPU. This is normal but slower.
2. **Large dataset**: 200+ profiles take time to process.

**Optimization**:
- Close other applications to free RAM
- Run overnight if you have a large dataset
- Consider running on a server with more cores

### Problem: "Memory error" or script crashes
**Solution**:
```bash
# Process in smaller batches by modifying the script
# Or run on a machine with more RAM (8+ GB recommended)
```

### Problem: Visualizations not generated
**Ensure matplotlib is installed**:
```bash
pip install matplotlib seaborn
```

## Next Steps After Baseline

### 1. Analyze Results
- Review all visualizations
- Check if matched pairs have higher similarity
- Note the effect size

### 2. Compare with Other Methods
- Run knowledge graph-based matching
- Compare graph edit distance
- Compare Jaccard similarity
- Cross-reference results

### 3. Add Unit Outline Integration
- Re-run experiment with unit outline content included in profiles
- Compare effect sizes (with vs without unit outlines)
- This tests the research question: "Does adding unit outlines improve matching?"

### 4. Cross-Project Analysis
- Identify which unmatched pairs have unexpectedly high similarity
- Investigate why certain projects are similar
- Use insights to refine project categorization

## Performance Benchmarks

Based on typical hardware:

| Hardware | Embedding Time | Similarity Time | Total Time |
|----------|---------------|-----------------|------------|
| M1 Mac (8-core) | 10-15 min | 2 min | ~15 min |
| Intel i7 (4-core) | 20-30 min | 3 min | ~25 min |
| Intel i5 (2-core) | 40-60 min | 5 min | ~50 min |

*Note: Times for ~220 documents (20 projects + 200 profiles)*

## Advanced Usage

### Running on a Subset
To test on a smaller dataset first:
```bash
# Modify the script to limit files
# Edit src/experiments/embedding_similarity_comparison.py
# Add: project_files = project_files[:5]  # First 5 projects only
```

### Changing the Embedding Model
To use a different model:
```bash
# In embedding_similarity_comparison.py, change:
# self.client = OllamaEmbeddingClient(model="your-model-name")
```

### Batch Processing
For very large datasets, modify the script to save embeddings incrementally.

## Questions or Issues?

If you encounter problems:
1. Check the test script output: `python test_embedding_setup.py`
2. Verify Ollama is running: `curl http://localhost:11434/api/tags`
3. Check disk space: `df -h`
4. Review error messages carefully

## Citation

If you use this code in your research:
```
@misc{embedding_similarity_2025,
  title={Embedding-Based Similarity Analysis for Project-Student Matching},
  author={Your Name},
  year={2025},
  howpublished={GitHub repository: ProjectMatching}
}
```


