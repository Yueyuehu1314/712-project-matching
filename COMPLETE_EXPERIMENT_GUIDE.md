# 完整实验执行指南

## 🎯 实验目标

研究问题：**引入Unit Outline信息是否能提升学生-项目匹配效果？**

## 📊 实验设计

### 四种方法对比

| 方法 | Project表示 | Student表示 | 相似度度量 | 预期结果 |
|------|------------|-------------|-----------|---------|
| **Method 1a** | PD only (text) | Student Profile | Cosine Similarity | Baseline |
| **Method 1b** | PD+UO (text) | Student Profile | Cosine Similarity | 比1a更好 |
| **Method 2a** | PD only (KG) | Student KG | Jaccard + Edit Distance | Baseline |
| **Method 2b** | PD+UO (KG) | Student KG | Jaccard + Edit Distance | 比2a更好 |

### 对比维度

1. **UO的作用**
   - Text方法: Method 1a vs 1b
   - KG方法: Method 2a vs 2b

2. **KG vs Text**
   - Baseline: Method 1a vs 2a
   - Enhanced: Method 1b vs 2b

---

## 🚀 执行步骤

### ✅ Step 0: 前置检查（已完成）

```bash
cd /Users/lynn/Documents/GitHub/ProjectMatching

# 检查文件状态
ls data/processed/projects_md/*.md | wc -l          # 应该: 20
ls data/processed/enhanced_projects_md/*.md | wc -l # 应该: 20
ls outputs1/knowledge_graphs/enhanced_student_kg/*/*.json | wc -l  # 应该: 200+
```

**状态:**
- ✅ PD only文本
- ✅ PD+UO文本（已生成）
- ✅ Student Profile文本
- ✅ Method 1a embeddings（已完成）
- ✅ Method 2a KG (PD only)
- ✅ Method 2b KG (PD+UO)
- ✅ Student KG

---

### 🔲 Step 1: 运行 Method 1b（PD+UO Embedding）

**预计时间**: 20-30分钟

```bash
# 确保Ollama正在运行
ollama serve  # 在另一个终端窗口

# 运行Method 1b
python run_method_1b_embedding.py
```

**输出:**
```
outputs/embeddings/
├── method_1b_embeddings.json
├── method_1b_similarity_results.json
├── method_1b_histogram.png
├── method_1b_boxplot.png
└── method_1b_dashboard.png
```

**预期结果:**
- Matched pairs 的 cosine similarity 应该高于 unmatched pairs
- 与 Method 1a 对比，delta应该更大

---

### 🔲 Step 2: 运行 Method 2a & 2b（KG相似度对比）

**预计时间**: 2-5分钟

```bash
python run_kg_similarity_experiment.py
```

**输出:**
```
outputs/kg_similarity/
├── method_2a_scores.json
├── method_2a_analysis.json
├── method_2b_scores.json
└── method_2b_analysis.json
```

**预期结果:**
- Matched pairs 的 Jaccard 相似度应该高，Edit Distance 应该低
- Method 2b 应该比 Method 2a 效果更好

---

### 🔲 Step 3: 对比所有方法

创建对比脚本：

```bash
python << 'EOF'
import json
import pandas as pd

# 加载所有结果
with open('outputs/embeddings/similarity_comparison_results.json') as f:
    method_1a = json.load(f)

with open('outputs/embeddings/method_1b_similarity_results.json') as f:
    method_1b = json.load(f)

with open('outputs/kg_similarity/method_2a_analysis.json') as f:
    method_2a = json.load(f)

with open('outputs/kg_similarity/method_2b_analysis.json') as f:
    method_2b = json.load(f)

# 创建对比表格
results = {
    'Method': ['1a (PD Text)', '1b (PD+UO Text)', '2a (PD KG)', '2b (PD+UO KG)'],
    'Matched Score': [
        f"{method_1a['matched']['mean']:.4f}",
        f"{method_1b['matched']['mean']:.4f}",
        f"{method_2a['matched_jaccard']['mean']:.4f}",
        f"{method_2b['matched_jaccard']['mean']:.4f}"
    ],
    'Unmatched Score': [
        f"{method_1a['unmatched']['mean']:.4f}",
        f"{method_1b['unmatched']['mean']:.4f}",
        f"{method_2a['unmatched_jaccard']['mean']:.4f}",
        f"{method_2b['unmatched_jaccard']['mean']:.4f}"
    ],
    'Delta': [
        f"{method_1a['matched']['mean'] - method_1a['unmatched']['mean']:.4f}",
        f"{method_1b['matched']['mean'] - method_1b['unmatched']['mean']:.4f}",
        f"{method_2a['delta_jaccard']:.4f}",
        f"{method_2b['delta_jaccard']:.4f}"
    ]
}

df = pd.DataFrame(results)
print("\n" + "=" * 80)
print("📊 实验结果对比")
print("=" * 80)
print(df.to_string(index=False))
print()

# 保存
df.to_csv('outputs/method_comparison_summary.csv', index=False)
print("✅ 已保存: outputs/method_comparison_summary.csv")

EOF
```

---

## 📈 预期结果解读

### 1. Unit Outline的作用

**Text方法:**
```
Method 1b Delta > Method 1a Delta  ✓
→ UO在文本embedding中有帮助
```

**KG方法:**
```
Method 2b Delta > Method 2a Delta  ✓
→ UO在知识图谱中有帮助
```

### 2. KG vs Text

**Baseline:**
```
Method 2a Delta > Method 1a Delta  ?
→ KG是否优于Text（无UO情况下）
```

**Enhanced:**
```
Method 2b Delta > Method 1b Delta  ?
→ KG是否优于Text（有UO情况下）
```

---

## 📊 可视化对比

创建综合对比图：

```python
import matplotlib.pyplot as plt
import numpy as np

methods = ['1a\n(PD Text)', '1b\n(PD+UO Text)', '2a\n(PD KG)', '2b\n(PD+UO KG)']
deltas = [delta_1a, delta_1b, delta_2a, delta_2b]

fig, ax = plt.subplots(figsize=(10, 6))
colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12']
bars = ax.bar(methods, deltas, color=colors, alpha=0.7)

ax.set_ylabel('Δ (Matched - Unmatched)', fontsize=12)
ax.set_title('Method Comparison: Effect Size', fontsize=14, fontweight='bold')
ax.axhline(y=0, color='gray', linestyle='--', alpha=0.3)
ax.grid(axis='y', alpha=0.3)

# 添加数值标签
for bar, delta in zip(bars, deltas):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{delta:.4f}',
            ha='center', va='bottom', fontsize=10)

plt.tight_layout()
plt.savefig('outputs/method_comparison_deltas.png', dpi=300)
print("✅ 已保存: outputs/method_comparison_deltas.png")
```

---

## 📝 论文结果表格

### Table 1: Method Comparison

| Method | Input | Representation | Matched | Unmatched | Δ | Effect Size |
|--------|-------|----------------|---------|-----------|---|-------------|
| 1a | PD | Text | 0.XXX | 0.XXX | 0.XXX | d=X.XX |
| 1b | PD+UO | Text | 0.XXX | 0.XXX | **0.XXX** | d=X.XX |
| 2a | PD | KG | 0.XXX | 0.XXX | 0.XXX | d=X.XX |
| 2b | PD+UO | KG | 0.XXX | 0.XXX | **0.XXX** | d=X.XX |

### Table 2: Ablation Study

| Comparison | Improvement | p-value | Conclusion |
|------------|-------------|---------|------------|
| 1b vs 1a | +X.XX% | < 0.001 | UO improves text methods |
| 2b vs 2a | +X.XX% | < 0.001 | UO improves KG methods |
| 2a vs 1a | +X.XX% | < 0.001 | KG > Text (baseline) |
| 2b vs 1b | +X.XX% | < 0.001 | KG > Text (enhanced) |

---

## 🔍 验证清单

运行完成后，确认以下文件存在：

```bash
# Method 1a (已有)
outputs/embeddings/project_profile_embeddings.json
outputs/embeddings/similarity_comparison_results.json

# Method 1b (新生成)
outputs/embeddings/method_1b_embeddings.json
outputs/embeddings/method_1b_similarity_results.json

# Method 2a & 2b
outputs/kg_similarity/method_2a_analysis.json
outputs/kg_similarity/method_2b_analysis.json

# 对比结果
outputs/method_comparison_summary.csv
outputs/method_comparison_deltas.png
```

---

## ⏱️ 时间估算

| 步骤 | 时间 | 备注 |
|------|------|------|
| Step 0 | 已完成 | 文件已准备好 |
| Step 1 (Method 1b) | 20-30分钟 | 需要Ollama |
| Step 2 (Method 2a/2b) | 2-5分钟 | 纯计算 |
| Step 3 (对比分析) | 5分钟 | 生成表格和图表 |
| **总计** | **~40分钟** | |

---

## 🎯 下一步行动

**现在就可以开始:**

```bash
# 1. 检查Ollama
ollama serve

# 2. 新开一个终端，运行Method 1b
cd /Users/lynn/Documents/GitHub/ProjectMatching
python run_method_1b_embedding.py

# 3. Method 1b完成后，运行KG实验
python run_kg_similarity_experiment.py

# 4. 生成对比分析
python -c "
import json
# ... (上面的对比代码)
"
```

---

## 📞 问题排查

### Q: Method 1b运行失败

**检查:**
```bash
# Ollama是否运行?
curl http://localhost:11434/api/tags

# bge-m3模型是否存在?
ollama list | grep bge-m3

# 输入文件是否存在?
ls data/processed/enhanced_projects_md/*.md | wc -l  # 应该20个
```

### Q: Method 2运行失败

**检查:**
```bash
# KG文件是否存在?
ls outputs/knowledge_graphs/three_layer_projects/*_entities.json | wc -l
ls outputs1/knowledge_graphs/enhanced_in20_in27/*/*.json | wc -l
ls outputs1/knowledge_graphs/enhanced_student_kg/*/*.json | wc -l
```

---

## 🎉 完成标志

当你看到以下输出，说明实验完成：

```
✅ Method 1b Experiment Complete!
   Matched pairs mean: 0.XXXX
   Unmatched pairs mean: 0.XXXX
   Effect size (Cohen's d): X.XX

✅ Method 2 Experiment Complete!
   Method 2a Jaccard: 0.XXXX
   Method 2b Jaccard: 0.XXXX
   
📊 所有结果已保存，可以进行论文写作！
```

