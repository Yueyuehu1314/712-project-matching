# Project Structure - Embedding Experiment

## Directory Tree

```
ProjectMatching/
│
├── data/
│   └── processed/
│       ├── projects_md/              # Input: Project proposals
│       │   ├── Project_A.md
│       │   ├── Project_B.md
│       │   └── ...
│       │
│       └── profiles_md/              # Input: Student profiles
│           ├── Project_A/
│           │   ├── n12345_John_Doe.md
│           │   ├── n67890_Jane_Smith.md
│           │   └── ... (10 students)
│           ├── Project_B/
│           └── ...
│
├── src/
│   └── experiments/
│       ├── embedding_similarity_comparison.py    # Main analysis script
│       └── visualize_similarity_results.py       # Visualization script
│
├── outputs/
│   └── embeddings/                               # Generated outputs
│       ├── project_profile_embeddings.json       # Embedding vectors
│       ├── similarity_comparison_results.json    # Analysis results
│       ├── similarity_histogram.png              # Distribution plot
│       ├── similarity_boxplot.png                # Quartile comparison
│       ├── similarity_violin.png                 # Distribution shapes
│       ├── similarity_cdf.png                    # Cumulative distribution
│       └── similarity_dashboard.png              # Comprehensive view
│
├── test_embedding_setup.py                       # Setup verification
├── run_embedding_experiment.sh                   # Quick run script
├── run_full_embedding_analysis.sh                # Full pipeline script
│
├── README_EMBEDDING_EXPERIMENT.md                # Technical documentation
├── EXPERIMENT_GUIDE.md                           # Execution guide
├── EMBEDDING_EXPERIMENT_SUMMARY.md               # File summary
└── PROJECT_STRUCTURE.md                          # This file
```

## File Categories

### 📥 Input Files
- **Project Proposals**: `data/processed/projects_md/**/*.md`
  - ~20 project files
  - Contain project descriptions, requirements, skills needed
  
- **Student Profiles**: `data/processed/profiles_md/**/*.md`
  - ~200 profile files (10 per project)
  - Contain student background, skills, completed courses

### 🔧 Processing Scripts
1. **Main Analysis**: `src/experiments/embedding_similarity_comparison.py`
   - Generates embeddings using bge-m3
   - Computes cosine similarities
   - Performs statistical analysis

2. **Visualization**: `src/experiments/visualize_similarity_results.py`
   - Creates 5 different plot types
   - Generates comprehensive dashboard

3. **Test Script**: `test_embedding_setup.py`
   - Verifies Ollama connection
   - Checks model availability
   - Tests embedding generation

### 🚀 Execution Scripts
1. **Quick Run**: `run_embedding_experiment.sh`
   - Runs analysis only

2. **Full Pipeline**: `run_full_embedding_analysis.sh` (recommended)
   - Runs analysis + visualization + summary

### 📤 Output Files
1. **Embeddings**: `outputs/embeddings/project_profile_embeddings.json`
   - 1024-dimensional vectors for each document
   - ~100-200 MB

2. **Results**: `outputs/embeddings/similarity_comparison_results.json`
   - Statistical analysis
   - Mean, std, effect size
   - Raw similarity scores
   - ~50-100 KB

3. **Visualizations**: 5 PNG files
   - Publication-quality (300 DPI)
   - Multiple views of the same data

### 📚 Documentation
1. **Technical Docs**: `README_EMBEDDING_EXPERIMENT.md`
2. **User Guide**: `EXPERIMENT_GUIDE.md`
3. **File Summary**: `EMBEDDING_EXPERIMENT_SUMMARY.md`
4. **Structure**: `PROJECT_STRUCTURE.md` (this file)

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     INPUT DATA                              │
├─────────────────────────────────────────────────────────────┤
│ Projects (20 files) + Profiles (200 files)                 │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│               EMBEDDING GENERATION                          │
├─────────────────────────────────────────────────────────────┤
│ Ollama (bge-m3) → 1024-dim vectors                         │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│            SAVE EMBEDDINGS TO JSON                          │
├─────────────────────────────────────────────────────────────┤
│ project_profile_embeddings.json (100-200 MB)               │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│           COMPUTE COSINE SIMILARITIES                       │
├─────────────────────────────────────────────────────────────┤
│ All project-profile pairs (~4000 comparisons)              │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│              CLASSIFY PAIRS                                 │
├─────────────────────────────────────────────────────────────┤
│ Matched: Student_A ↔ Project_A (200 pairs)                │
│ Unmatched: Student_not_A ↔ Project_A (3800 pairs)         │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│           STATISTICAL ANALYSIS                              │
├─────────────────────────────────────────────────────────────┤
│ Mean, Std, Effect Size (Cohen's d)                         │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│            SAVE RESULTS TO JSON                             │
├─────────────────────────────────────────────────────────────┤
│ similarity_comparison_results.json (50-100 KB)             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│              CREATE VISUALIZATIONS                          │
├─────────────────────────────────────────────────────────────┤
│ 5 PNG plots showing distributions and comparisons          │
└─────────────────────────────────────────────────────────────┘
```

## Execution Order

### First Time Setup
```bash
1. ollama serve              # Start Ollama service
2. ollama pull bge-m3        # Download model (once)
3. pip install requirements  # Install Python packages (once)
```

### Every Run
```bash
1. python test_embedding_setup.py           # Verify setup
2. ./run_full_embedding_analysis.sh         # Run experiment
3. open outputs/embeddings/*.png            # View results
```

## File Size Estimates

| File | Size | Notes |
|------|------|-------|
| project_profile_embeddings.json | 100-200 MB | Depends on # of documents |
| similarity_comparison_results.json | 50-100 KB | Includes raw scores |
| Each PNG visualization | 200-500 KB | 300 DPI, publication quality |
| Total output size | ~200 MB | Per experiment run |

## Runtime Estimates

| Step | Time | Parallelizable? |
|------|------|-----------------|
| Embedding generation | 15-30 min | No (sequential API calls) |
| Similarity computation | 2-5 min | Yes (but implemented sequentially) |
| Visualization | 1 min | No |
| **Total** | **20-40 min** | - |

*Note: Times for ~220 documents on typical laptop (4-8 cores)*

## Dependencies

### External Services
- **Ollama**: Local LLM service (http://localhost:11434)
- **bge-m3 model**: BGE-M3 embedding model (~2 GB)

### Python Packages
- `requests`: HTTP client for Ollama API
- `numpy`: Numerical computations
- `matplotlib`: Plotting library
- `seaborn`: Statistical visualizations

### System Requirements
- **RAM**: 4+ GB available
- **Disk**: 500 MB free space
- **CPU**: Any modern processor (GPU not required)
- **OS**: macOS, Linux, or Windows with WSL

## Quick Reference

### To run the experiment:
```bash
./run_full_embedding_analysis.sh
```

### To view results:
```bash
open outputs/embeddings/similarity_dashboard.png
python -m json.tool < outputs/embeddings/similarity_comparison_results.json
```

### To troubleshoot:
```bash
python test_embedding_setup.py
curl http://localhost:11434/api/tags
```

### To modify:
- Edit `src/experiments/embedding_similarity_comparison.py` for analysis logic
- Edit `src/experiments/visualize_similarity_results.py` for plots
- Edit shell scripts for execution flow

## Notes

- All output files are gitignored (add `outputs/` to `.gitignore`)
- Embeddings can be cached and reused for multiple analyses
- Visualizations are publication-ready (high DPI)
- Code follows PEP 8 style guidelines
- All docstrings use English (no Chinese characters in code)
