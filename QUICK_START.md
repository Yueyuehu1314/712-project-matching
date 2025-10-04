# Quick Start Guide - Embedding Similarity Experiment

## 🚀 3-Step Setup

### Step 1: Start Ollama (in a separate terminal)
```bash
ollama serve
```
Keep this terminal running!

### Step 2: Verify Setup
```bash
python test_embedding_setup.py
```
All 5 tests should pass ✓

### Step 3: Run Experiment
```bash
./run_full_embedding_analysis.sh
```
Wait 20-30 minutes for completion.

---

## 📊 View Results

```bash
# Open the comprehensive dashboard
open outputs/embeddings/similarity_dashboard.png

# View JSON results
python -m json.tool < outputs/embeddings/similarity_comparison_results.json | less
```

---

## 🎯 What This Does

**Tests the hypothesis**: Do student profiles generated for a specific project show higher embedding similarity with that project compared to profiles generated for other projects?

**Measures**:
- Mean cosine similarity (matched vs unmatched pairs)
- Effect size (Cohen's d) - how well embeddings distinguish matches
- Statistical distributions

**Expected Result**: Matched pairs should have significantly higher similarity

---

## 📁 Output Files

All results saved to `outputs/embeddings/`:
- `project_profile_embeddings.json` - All embedding vectors (~150 MB)
- `similarity_comparison_results.json` - Statistical analysis (~80 KB)
- `similarity_dashboard.png` - Comprehensive visualization
- 4 other PNG plots (histogram, boxplot, violin, CDF)

---

## ❓ Troubleshooting

**Problem**: "Ollama service is not available"
```bash
# Solution: Start Ollama
ollama serve
```

**Problem**: "bge-m3 model not found"
```bash
# Solution: Download the model
ollama pull bge-m3
```

**Problem**: "Module not found"
```bash
# Solution: Install dependencies
pip install requests numpy matplotlib seaborn
```

---

## 📖 More Information

- **Technical details**: See `README_EMBEDDING_EXPERIMENT.md`
- **Step-by-step guide**: See `EXPERIMENT_GUIDE.md`
- **File descriptions**: See `EMBEDDING_EXPERIMENT_SUMMARY.md`
- **Project structure**: See `PROJECT_STRUCTURE.md`

---

## ⏱️ Time Estimates

- Setup (first time): ~5 minutes
- Model download: ~5 minutes (once)
- Experiment run: ~20-30 minutes
- Result review: ~5 minutes

**Total first run**: ~40 minutes
**Subsequent runs**: ~25 minutes

---

## 💡 Key Metrics to Look For

After running, check these in the results:

1. **Mean Similarity**:
   - Matched pairs: Should be **higher** (e.g., 0.75-0.85)
   - Unmatched pairs: Should be **lower** (e.g., 0.60-0.70)

2. **Cohen's d (Effect Size)**:
   - **> 0.8**: Strong evidence (embeddings work well)
   - **0.5-0.8**: Moderate evidence
   - **0.2-0.5**: Weak evidence
   - **< 0.2**: Not effective

3. **Visual Check**:
   - Histogram: Should show two separated distributions
   - Box plot: Matched box should be higher than unmatched

---

## 🎓 Research Context

This is **Step 1** of your research:
1. ✅ Baseline embedding comparison (this experiment)
2. ⬜ Knowledge graph comparison
3. ⬜ Compare methods
4. ⬜ Add unit outlines
5. ⬜ Measure unit outline impact

---

## 🔄 Next Steps After This Experiment

1. Review the results and document findings
2. Run knowledge graph-based similarity comparison
3. Compare effectiveness of different methods
4. Re-run with unit outline integration
5. Measure the impact of unit outlines on matching quality

---

## ✅ Success Checklist

- [x] All files created successfully
- [ ] Ollama installed and running
- [ ] bge-m3 model downloaded
- [ ] Test script passes all checks
- [ ] Experiment completed successfully
- [ ] Results reviewed and documented
- [ ] Dashboard visualization reviewed
- [ ] Cohen's d noted for comparison

---

**Ready to start? Run:**
```bash
python test_embedding_setup.py && ./run_full_embedding_analysis.sh
```
