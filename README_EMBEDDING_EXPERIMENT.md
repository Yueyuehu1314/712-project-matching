# Embedding Similarity Comparison Experiment

## Research Question

**Does vector cosine similarity effectively distinguish between matched and unmatched project-student pairs?**

This experiment tests whether profiles generated for a specific project (Student_A for Project_A) show higher embedding similarity compared to profiles generated for other projects (Student_not_A for Project_A).

## Methodology

### 1. Data Sources
- **Projects**: All markdown files in `data/processed/projects_md/`
- **Student Profiles**: All markdown files in `data/processed/profiles_md/` (organized by project folders)

### 2. Embedding Generation
- **Model**: `bge-m3` (via Ollama)
- **Process**: Each document (project proposal or student profile) is converted to a dense vector embedding
- **Output**: `outputs/embeddings/project_profile_embeddings.json`

### 3. Similarity Comparison
- **Metric**: Cosine similarity between project and profile embeddings
- **Matched Pairs**: Profile was generated for that specific project (same project folder)
- **Unmatched Pairs**: Profile was generated for a different project

### 4. Analysis
- Compare mean similarity scores between matched and unmatched pairs
- Calculate effect size (Cohen's d) to measure strength of distinction
- Generate statistical summary and distributions

## How to Run

### Prerequisites

1. **Install Ollama**: https://ollama.ai/
2. **Start Ollama service**:
   ```bash
   ollama serve
   ```
3. **Pull bge-m3 model** (if not already installed):
   ```bash
   ollama pull bge-m3
   ```

### Execute Experiment

**Option 1: Using the shell script**
```bash
./run_embedding_experiment.sh
```

**Option 2: Direct Python execution**
```bash
python src/experiments/embedding_similarity_comparison.py
```

## Expected Results

### Hypothesis
- **H1**: Matched pairs should show **higher** cosine similarity than unmatched pairs
- **H0**: No significant difference between matched and unmatched pairs

### Interpretation of Effect Size (Cohen's d)
- **d > 0.8**: Large effect - Strong evidence that embedding similarity distinguishes matches
- **0.5 < d < 0.8**: Medium effect - Moderate distinction
- **0.2 < d < 0.5**: Small effect - Weak distinction
- **d < 0.2**: Negligible effect - Embedding similarity does not distinguish well

## Output Files

### 1. Embeddings File
**Location**: `outputs/embeddings/project_profile_embeddings.json`

**Structure**:
```json
{
  "generated_at": "2025-10-04T...",
  "model": "bge-m3",
  "total_documents": 220,
  "embeddings": [
    {
      "file_path": "data/processed/projects_md/Project_A.md",
      "file_name": "Project_A.md",
      "doc_type": "project",
      "content": "...",
      "embedding": [0.123, -0.456, ...],
      "matched_project": null,
      "project_folder": null
    },
    {
      "file_path": "data/processed/profiles_md/Project_A/n12345_John_Doe.md",
      "file_name": "n12345_John_Doe.md",
      "doc_type": "profile",
      "content": "...",
      "embedding": [0.234, -0.567, ...],
      "matched_project": "Project_A",
      "project_folder": "Project_A"
    }
  ]
}
```

### 2. Results File
**Location**: `outputs/embeddings/similarity_comparison_results.json`

**Structure**:
```json
{
  "generated_at": "2025-10-04T...",
  "embeddings_file": "outputs/embeddings/project_profile_embeddings.json",
  "analysis": {
    "matched_pairs": {
      "count": 200,
      "mean": 0.7845,
      "std": 0.0523,
      "min": 0.6234,
      "max": 0.8912,
      "median": 0.7912,
      "q25": 0.7456,
      "q75": 0.8234
    },
    "unmatched_pairs": {
      "count": 3800,
      "mean": 0.6523,
      "std": 0.0612,
      "min": 0.4123,
      "max": 0.7845,
      "median": 0.6512,
      "q25": 0.6123,
      "q75": 0.6934
    },
    "comparison": {
      "mean_difference": 0.1322,
      "effect_size_cohens_d": 2.31
    }
  },
  "raw_similarities": {
    "matched": [0.78, 0.81, 0.76, ...],
    "unmatched": [0.65, 0.63, 0.67, ...]
  }
}
```

## Performance Notes

### Execution Time
- **Embedding Generation**: ~1-2 minutes per 100 documents (depends on hardware)
- **Similarity Computation**: ~1 second per 1000 comparisons
- **Total Time**: Approximately 15-30 minutes for full dataset

### Resource Usage
- **Memory**: ~2-4 GB (for storing embeddings)
- **Disk**: ~100-200 MB (JSON output files)
- **GPU**: Not required (bge-m3 via Ollama can run on CPU)

## Next Steps

After completing this baseline experiment:

1. **Knowledge Graph Comparison**: Compare results with graph edit distance and Jaccard scores
2. **Unit Outline Integration**: Re-run experiment with unit outline content included
3. **Cross-Project Analysis**: Analyze which unmatched pairs show unexpectedly high similarity
4. **Visualization**: Create plots showing similarity distributions

## Troubleshooting

### Ollama Connection Error
```
Error: Ollama service is not available
```
**Solution**: Start Ollama with `ollama serve` in a separate terminal

### Model Not Found
```
Warning: bge-m3 model not found
```
**Solution**: Pull the model with `ollama pull bge-m3`

### Memory Issues
If you encounter memory errors:
- Process embeddings in batches
- Reduce the number of documents
- Use a machine with more RAM

## Code Structure

```
src/experiments/embedding_similarity_comparison.py
├── OllamaEmbeddingClient: Handles embedding generation via Ollama API
├── EmbeddingGenerator: Processes all projects and profiles
├── SimilarityComparator: Computes and analyzes cosine similarities
└── main(): Orchestrates the full experiment pipeline
```

## Citation

If you use this code in your research, please cite:

```
@misc{project_matching_embeddings,
  title={Embedding-Based Similarity Analysis for Project-Student Matching},
  author={Your Name},
  year={2025},
  note={GitHub repository: ProjectMatching}
}
```


