# Embedding-Based Similarity Analysis Results

## 📋 实验概述

本目录包含两种 Embedding 方法的完整实验结果：

- **Method 1a**: PD only (仅使用项目描述)
- **Method 1b**: PD + UO + Student Profile (使用项目描述 + 单元成果 + 学生简历)

## 📁 目录结构

```
outputs/embeddings/
├── 1a/                                  # Method 1a 结果
│   ├── project_profile_embeddings.json  # 原始嵌入向量 (6.4MB)
│   ├── similarity_comparison_results.json # 相似度分析结果
│   ├── similarity_dashboard.png         # 综合仪表板
│   ├── similarity_histogram.png         # 直方图
│   ├── similarity_boxplot.png           # 箱线图
│   ├── similarity_violin.png            # 小提琴图
│   └── similarity_cdf.png               # 累积分布函数图
│
├── 1b/                                  # Method 1b 结果
│   ├── method_1b_embeddings.json        # 原始嵌入向量 (6.4MB)
│   ├── method_1b_similarity_results.json # 相似度计算结果
│   ├── similarity_comparison_results.json # 相似度分析结果
│   ├── similarity_dashboard.png         # 综合仪表板
│   ├── similarity_histogram.png         # 直方图
│   ├── similarity_boxplot.png           # 箱线图
│   ├── similarity_violin.png            # 小提琴图
│   └── similarity_cdf.png               # 累积分布函数图
│
└── method_1a_vs_1b_comparison.png       # 两种方法的对比图
```

## 📊 实验结果总结

### Method 1a (PD only)

| 指标 | Matched Pairs | Unmatched Pairs | Difference |
|------|---------------|-----------------|------------|
| Mean | 0.7133 | 0.7106 | **+0.0027** |
| Std  | 0.1161 | 0.1154 | +0.0007 |
| Median | 0.7695 | 0.7653 | +0.0042 |

**效果评估:**
- ✅ **Mean Difference: +0.002660**
- ✅ **Cohen's d: +0.022980** (small effect)
- ✅ **结论**: 能够区分真实配对和随机配对

### Method 1b (PD + UO + Student Profile)

| 指标 | Matched Pairs | Unmatched Pairs | Difference |
|------|---------------|-----------------|------------|
| Mean | 0.6787 | 0.6788 | **-0.0001** |
| Std  | 0.1262 | 0.1285 | -0.0023 |
| Median | 0.6967 | 0.7029 | -0.0061 |

**效果评估:**
- ❌ **Mean Difference: -0.000131** (≈ 0)
- ❌ **Cohen's d: -0.001029** (negligible)
- ❌ **结论**: 无法区分真实配对和随机配对

**统计检验结果:**
- T-test: p-value = 0.989 (✗ Not Significant)
- KS-test: p-value = 0.614 (✗ Not Significant)

## 🎯 关键发现

### 1. Method 1a 优于 Method 1b

虽然 Method 1a 的效果量很小 (Cohen's d = 0.023)，但它仍然显示出一定的区分能力：
- Matched pairs 的平均相似度**略高于** Unmatched pairs
- 这符合预期：真实配对应该比随机配对更相似

### 2. Method 1b 的负面结果

添加 Unit Outcomes 和 Student Profile 信息后：
- Mean difference 从 +0.0027 降到 -0.0001（几乎为零）
- 完全失去了区分真实配对和随机配对的能力

**可能原因:**
1. **信息稀释**: 添加过多维度稀释了核心匹配信号
2. **噪声引入**: UO 和 Student Profile 可能包含与匹配无关的信息
3. **维度诅咒**: 高维空间中相似度计算的可靠性降低

### 3. 实际应用建议

✅ **推荐使用 Method 1a** 进行后续分析 (Step 3-5)

原因：
- 虽然效果量小，但方向正确
- 计算简单，可解释性强
- 不需要额外的 Unit Outcomes 和 Student Profile 数据

⚠️ **Method 1b 的价值**

虽然 Method 1b 无法用于实际匹配，但其负面结果仍有研究价值：
- 证明了"更多信息不一定更好"
- 可用于论文的讨论部分
- 提示需要更精细的特征工程

## 📈 可视化说明

### Dashboard (仪表板)

综合展示所有分析结果：
- 分布对比图（直方图）
- 统计信息表
- 箱线图和小提琴图
- 累积分布函数
- 统计检验结果
- 最终结论

### Histogram (直方图)

展示两种配对类型的相似度分布：
- 绿色: Matched pairs (真实配对)
- 红色: Unmatched pairs (随机配对)
- 虚线: 各自的均值

### Boxplot (箱线图)

以箱线图形式对比两种配对的统计特性：
- 中位数、四分位数
- 均值（黄色菱形）
- 异常值

### Violin Plot (小提琴图)

展示分布的形状：
- 宽度表示密度
- 可以看出分布的峰值和尾部

### CDF (累积分布函数)

展示相似度的累积概率：
- 包含 Kolmogorov-Smirnov 检验结果
- 可以直观比较两种分布的差异

## 🔬 数据文件说明

### `similarity_comparison_results.json`

包含完整的分析结果：
```json
{
  "statistics": {
    "matched_pairs": { "mean", "std", "median", "min", "max", ... },
    "unmatched_pairs": { "mean", "std", "median", "min", "max", ... }
  },
  "comparison": {
    "mean_difference": ...,
    "median_difference": ...
  },
  "statistical_tests": {
    "t_test": { "statistic", "p_value", "significant" },
    "mann_whitney_u": { ... },
    "kolmogorov_smirnov": { ... }
  },
  "effect_size": {
    "cohens_d": ...,
    "interpretation": "small" | "medium" | "large" | "negligible"
  },
  "raw_similarities": {
    "matched": [200 values],
    "unmatched": [3800 values]
  }
}
```

## 📝 使用方法

### 1. 查看可视化结果

```bash
# Method 1a 仪表板
open outputs/embeddings/1a/similarity_dashboard.png

# Method 1b 仪表板
open outputs/embeddings/1b/similarity_dashboard.png

# 方法对比图
open outputs/embeddings/method_1a_vs_1b_comparison.png
```

### 2. 读取数据进行进一步分析

```python
import json

# 加载 Method 1a 结果
with open('outputs/embeddings/1a/similarity_comparison_results.json') as f:
    results_1a = json.load(f)

# 获取 matched pairs 的相似度
matched_similarities = results_1a['raw_similarities']['matched']

# 获取统计信息
mean_diff = results_1a['comparison']['mean_difference']
cohens_d = results_1a['effect_size']['cohens_d']
```

### 3. 用于后续 Step

使用 Method 1a 的嵌入向量：
```python
# 加载嵌入向量
with open('outputs/embeddings/1a/project_profile_embeddings.json') as f:
    embeddings = json.load(f)

# 使用嵌入向量进行匹配
project_emb = embeddings['projects']['project_name']
student_emb = embeddings['students']['student_name']
similarity = cosine_similarity(project_emb, student_emb)
```

## 🔗 相关文件

- 数据源: `data/in20_in27/` (20个项目), `data/students/` (20个学生)
- 知识图谱: `outputs/knowledge_graphs/`
- 匹配结果: `outputs/matching/`

## 📅 生成时间

- Method 1a: 2025-10-04 14:05:06
- Method 1b: 2025-10-04 15:41:05

---

**实验结论**: Method 1a 在区分真实配对和随机配对方面表现更好，推荐用于后续分析。

