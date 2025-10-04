# Embedding Similarity Experiment - File Summary

## Created Files Overview

This document summarizes all files created for the embedding-based similarity comparison experiment.

## 📁 Core Python Scripts

### 1. `src/experiments/embedding_similarity_comparison.py`
**Purpose**: Main analysis script for generating embeddings and computing similarities

**Key Components**:
- `OllamaEmbeddingClient`: Handles bge-m3 embedding generation via Ollama
- `EmbeddingGenerator`: Processes all projects and profiles
- `SimilarityComparator`: Computes cosine similarities and statistical analysis
- `main()`: Orchestrates the full pipeline

**Input**:
- Projects: `data/processed/projects_md/**/*.md`
- Profiles: `data/processed/profiles_md/**/*.md`

**Output**:
- `outputs/embeddings/project_profile_embeddings.json`
- `outputs/embeddings/similarity_comparison_results.json`

**Runtime**: ~15-30 minutes for 200+ documents

---

### 2. `src/experiments/visualize_similarity_results.py`
**Purpose**: Create visualizations of similarity distributions

**Generates 5 plots**:
1. Histogram comparison (overlapping distributions)
2. Box plot comparison (quartile analysis)
3. Violin plot (distribution shapes)
4. Cumulative distribution function (CDF)
5. Comprehensive dashboard (all metrics in one view)

**Output**:
- `outputs/embeddings/similarity_histogram.png`
- `outputs/embeddings/similarity_boxplot.png`
- `outputs/embeddings/similarity_violin.png`
- `outputs/embeddings/similarity_cdf.png`
- `outputs/embeddings/similarity_dashboard.png`

**Runtime**: ~1 minute

---

## 🔧 Execution Scripts

### 3. `run_embedding_experiment.sh`
**Purpose**: Quick run script for embedding generation and comparison only

**Steps**:
1. Check Ollama service
2. Check bge-m3 model
3. Run embedding analysis

**Usage**: `./run_embedding_experiment.sh`

---

### 4. `run_full_embedding_analysis.sh`
**Purpose**: Comprehensive script that runs everything (recommended)

**Steps**:
1. Verify prerequisites (Ollama, bge-m3)
2. Generate embeddings and compute similarities
3. Create all visualizations
4. Display summary report

**Usage**: `./run_full_embedding_analysis.sh`

**Features**:
- Progress indicators
- Error handling
- Summary statistics display
- File size reporting

---

### 5. `test_embedding_setup.py`
**Purpose**: Verification script to test setup before running full analysis

**Tests**:
1. Python dependencies (requests, numpy)
2. Ollama service availability
3. bge-m3 model availability
4. Data directories existence
5. Embedding generation (quick test)

**Usage**: `python test_embedding_setup.py`

**When to use**: Before first run, or when troubleshooting issues

---

## 📖 Documentation

### 6. `README_EMBEDDING_EXPERIMENT.md`
**Purpose**: Technical documentation and methodology

**Contents**:
- Research question
- Methodology details
- Data sources
- Expected results
- Output file structures
- Performance notes
- Troubleshooting guide

**Target audience**: Researchers and technical users

---

### 7. `EXPERIMENT_GUIDE.md`
**Purpose**: Step-by-step execution guide

**Contents**:
- Prerequisites and installation
- Quick start instructions
- Step-by-step execution
- Results interpretation guide
- Advanced usage examples
- Performance benchmarks
- FAQ and troubleshooting

**Target audience**: Anyone running the experiment

---

### 8. `EMBEDDING_EXPERIMENT_SUMMARY.md` (this file)
**Purpose**: Quick reference for all created files

---

## 📊 Output Files (Generated After Running)

### Data Files
```
outputs/embeddings/
├── project_profile_embeddings.json       (~100-200 MB)
└── similarity_comparison_results.json    (~50-100 KB)
```

### Visualization Files
```
outputs/embeddings/
├── similarity_histogram.png
├── similarity_boxplot.png
├── similarity_violin.png
├── similarity_cdf.png
└── similarity_dashboard.png
```

---

## 🚀 Quick Start Guide

### 1. First-time Setup
```bash
# Install Ollama
brew install ollama  # macOS
# or visit https://ollama.ai for other platforms

# Start Ollama
ollama serve

# Pull bge-m3 model
ollama pull bge-m3

# Install Python dependencies
pip install requests numpy matplotlib seaborn
```

### 2. Verify Setup
```bash
python test_embedding_setup.py
```

### 3. Run Full Analysis
```bash
./run_full_embedding_analysis.sh
```

### 4. View Results
```bash
# Open visualizations
open outputs/embeddings/similarity_dashboard.png

# View JSON results
cat outputs/embeddings/similarity_comparison_results.json | python -m json.tool
```

---

## 📋 Research Workflow

```
┌─────────────────────────────────────────────────────────┐
│ STEP 1: Baseline Embedding Comparison                  │
│ (This experiment - no unit outlines)                   │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 2: Knowledge Graph Comparison                     │
│ - Graph edit distance                                   │
│ - Jaccard similarity                                    │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 3: Compare Results                                 │
│ Which method distinguishes better?                      │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 4: Add Unit Outlines                              │
│ Re-run embedding comparison with unit content          │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 5: Measure Impact                                  │
│ Does unit outline integration improve results?          │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Research Questions

1. **Primary**: Can vector cosine similarity distinguish matched from unmatched pairs?
   - Measured by: Mean difference and Cohen's d effect size

2. **Secondary**: How does this compare to knowledge graph methods?
   - Compare effect sizes across methods

3. **Main Research Question**: Does adding unit outlines improve matching?
   - Compare effect sizes: baseline vs with-unit-outlines

---

## 💡 Expected Outcomes

### Success Criteria
- **Strong evidence**: Cohen's d > 0.8
  - Matched pairs show significantly higher similarity
  - Clear separation in distributions

- **Moderate evidence**: 0.5 < Cohen's d < 0.8
  - Matched pairs show higher similarity
  - Some overlap in distributions

- **Weak/No evidence**: Cohen's d < 0.5
  - Limited distinction between matched and unmatched
  - May need to combine with other methods

---

## 🔄 Maintenance and Updates

### To modify the experiment:

1. **Change embedding model**:
   - Edit `src/experiments/embedding_similarity_comparison.py`
   - Change `model="bge-m3"` to your preferred model

2. **Process subset of data**:
   - Modify file list limits in `EmbeddingGenerator` methods

3. **Adjust matching criteria**:
   - Modify `is_matched_pair()` method in `SimilarityComparator`

4. **Add new visualizations**:
   - Add methods to `visualize_similarity_results.py`

---

## 📞 Support

If you need help:
1. Run test script: `python test_embedding_setup.py`
2. Check Ollama status: `curl http://localhost:11434/api/tags`
3. Review documentation: `EXPERIMENT_GUIDE.md`
4. Check error messages in terminal output

---

## 📝 Notes

- All code is documented with docstrings
- No Chinese characters in code (English only)
- Follow PEP 8 style guidelines
- JSON outputs are human-readable (indented)
- Visualizations are publication-quality (300 DPI)

---

## ✅ Completion Checklist

Before running the experiment:
- [ ] Ollama installed and running
- [ ] bge-m3 model downloaded
- [ ] Python dependencies installed
- [ ] Test script passes all checks
- [ ] Data directories exist and contain files

After running:
- [ ] Embeddings JSON generated successfully
- [ ] Results JSON contains analysis
- [ ] All 5 visualizations created
- [ ] Review mean similarities and effect size
- [ ] Document findings for research paper

---

## 🎓 Academic Context

This experiment forms part of research investigating:
- **Vector similarity** vs **graph-based similarity**
- Impact of **unit outline integration** on matching accuracy
- Effectiveness of different **similarity metrics** for student-project matching

Results will inform the design of the final matching system.
