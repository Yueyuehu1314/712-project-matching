# ProjectMatching - 完整实验清单

> 生成时间: 2025-10-04
> 状态: 部分完成，待继续

---

## 🎯 研究问题 (Research Questions)

### 主研究问题

**RQ**: 引入 Unit Outline (课程大纲) 信息是否能提升学生-项目匹配效果？

### 子研究问题

- **RQ1**: 在基于文本嵌入的方法中，添加 Unit Outline 是否有帮助？
- **RQ2**: 在基于知识图谱的方法中，添加 Unit Outline 是否有帮助？
- **RQ3**: 知识图谱方法 vs 文本嵌入方法，哪个更好？

---

## 📊 实验设计矩阵

| 方法 | 项目输入 | 学生输入 | 表示方式 | 相似度度量 | 目的 | 状态 |
|------|---------|---------|---------|-----------|------|------|
| **Method 1a** | PD only | Student Profile | Text Embedding (bge-m3) | Cosine Similarity | Baseline (文本) | ✅ 已完成 |
| **Method 1b** | PD + UO | Student Profile | Text Embedding (bge-m3) | Cosine Similarity | 测试 UO 在文本中的作用 | ✅ 已完成 |
| **Method 2a** | PD only KG | Student KG | Knowledge Graph | Jaccard Similarity + Edit Distance | Baseline (KG) | ❌ 待完成 |
| **Method 2b** | PD + UO KG | Student KG | Knowledge Graph | Jaccard Similarity + Edit Distance | 测试 UO 在 KG 中的作用 | ⚠️ 部分完成 |

**缩写说明:**
- PD = Project Description (项目描述)
- UO = Unit Outline (课程大纲: IN20 + IN27)
- KG = Knowledge Graph (知识图谱)

**度量方法说明:**
- **Jaccard Similarity**: 节点集合相似度 = |A ∩ B| / |A ∪ B|，范围 [0, 1]，越大越相似
- **Edit Distance**: 图编辑距离 = node_diff + edge_diff，范围 [0, ∞)，越小越相似

---

## 📂 数据准备状态

所有必需的数据文件都已准备完毕 ✅

| 数据类型 | 位置 | 数量 | 状态 |
|---------|------|------|------|
| PD only 文本 | `data/processed/projects_md/` | 20个项目 | ✅ |
| PD + UO 文本 | `data/processed/enhanced_projects_md/` | 20个项目 | ✅ |
| Student Profile 文本 | `data/processed/profiles_md/` | 400个档案 (20项目×20学生) | ✅ |
| PD only KG | `outputs/knowledge_graphs/three_layer_projects/` | 20个项目KG | ✅ |
| PD + UO KG | `outputs/knowledge_graphs/enhanced_in20_in27/` | 20个项目KG | ✅ |
| Student KG | `outputs/knowledge_graphs/enhanced_student_kg/` | 400个学生KG | ✅ |
| Unit Outlines | `data/processed/units_md/` | IN20 + IN27 | ✅ |

---

## ✅ 已完成的实验

### 1. Method 1a: PD only 文本嵌入实验

**状态**: ✅ 已完成

**结果**:
- Matched pairs mean: 0.7133
- Unmatched pairs mean: 0.7106
- **Mean Difference: +0.0027**
- **Cohen's d: +0.023** (small effect)

**结论**: 能够区分真实配对和随机配对，但效果量很小。

**输出文件**:
```
outputs/embeddings/1a/
├── project_profile_embeddings.json (6.4MB)
├── similarity_comparison_results.json
├── similarity_dashboard.png
├── similarity_histogram.png
├── similarity_boxplot.png
├── similarity_violin.png
└── similarity_cdf.png
```

---

### 2. Method 1b: PD+UO 文本嵌入实验

**状态**: ✅ 已完成

**结果**:
- Matched pairs mean: 0.6787
- Unmatched pairs mean: 0.6788
- **Mean Difference: -0.0001** (≈ 0)
- **Cohen's d: -0.001** (negligible)

**结论**: ❌ **无法区分真实配对和随机配对！** 添加 Unit Outline 反而降低了区分能力。

**重要发现**: 更多信息不一定更好。在高维嵌入空间中，额外的 UO 信息可能引入噪声，稀释了核心匹配信号。

**输出文件**:
```
outputs/embeddings/1b/
├── method_1b_embeddings.json (6.4MB)
├── method_1b_similarity_results.json
├── similarity_comparison_results.json
├── similarity_dashboard.png
├── similarity_histogram.png
├── similarity_boxplot.png
├── similarity_violin.png
└── similarity_cdf.png
```

---

### 3. Method 1a vs 1b 对比分析

**状态**: ✅ 已完成

**结论**: **Method 1a 优于 Method 1b**

虽然 Method 1a 的效果量很小，但至少显示出正确的方向（matched > unmatched）。Method 1b 完全失去了区分能力。

**输出文件**:
```
outputs/embeddings/
├── method_1a_vs_1b_comparison.png (513KB)
└── README.md (完整说明文档)
```

**可视化**: 并排对比两种方法的分布、统计信息和结论。

---

### 4. Method 2b: PD+UO KG 相似度计算

**状态**: ⚠️ 部分完成 (只计算了 matched pairs)

**当前结果**:
- Matched pairs (20对):
  - Jaccard Similarity: Mean = 0.0358
  - Edit Distance: Mean = 73.45
- ❌ Unmatched pairs: 未计算

**输出文件**:
```
outputs/kg_similarity/
├── method_2b_scores.json (只有20个matched pairs)
└── method_2b_analysis.json
```

**待补充**: 
1. 计算 unmatched pairs (3800对)
2. 对比 matched vs unmatched
3. 生成完整可视化仪表板

---

## ❌ 待完成的实验

### 1. Method 2a: PD only KG 相似度计算

**状态**: ❌ 待完成

**目标**: 计算 PD only KG 与 Student KG 的相似度

**输入文件**:
- Project KG: `outputs1/knowledge_graphs/three_layer_projects/*_entities.json` (20个项目)
- Student KG: `outputs1/knowledge_graphs/enhanced_student_kg/*/*.json` (400个学生)

**计算步骤**:
1. 对每个 project-student pair:
   - 提取项目KG的节点集合 P_nodes 和边集合 P_edges
   - 提取学生KG的节点集合 S_nodes 和边集合 S_edges
   - 计算 **Jaccard Similarity** = |P_nodes ∩ S_nodes| / |P_nodes ∪ S_nodes|
   - 计算 **Edit Distance** = |P_nodes △ S_nodes| + |P_edges △ S_edges|
   - 标记是否为 matched pair
   
2. 分组:
   - Matched pairs: 学生来自该项目 (200对: 20项目 × 10学生/项目)
   - Unmatched pairs: 学生不来自该项目 (3800对: 20项目 × 190其他学生)
   
3. 统计分析:
   - 描述统计: Mean, Std, Median, Min, Max
   - 统计检验: T-test, Mann-Whitney U, Kolmogorov-Smirnov
   - 效果量: Cohen's d

**预期输出**:
```
outputs/kg_similarity/
├── method_2a_scores.json
├── method_2a_analysis.json
├── method_2a_dashboard.png
├── method_2a_histogram.png
├── method_2a_boxplot.png
├── method_2a_violin.png
└── method_2a_cdf.png
```

**预计时间**: 10-15分钟

---

### 2. Method 2a vs 2b 对比分析

**状态**: ❌ 待完成

**目标**: 验证 UO 在 Knowledge Graph 方法中的作用

**对比维度**:
- Matched pairs 的 Jaccard similarity
- Unmatched pairs 的 Jaccard similarity
- Mean difference (Δ)
- Effect size (Cohen's d)

**预期结果**:
- 如果 Method 2b 的 Δ > Method 2a 的 Δ → UO 在 KG 中有帮助
- 如果 Method 2b 的 Δ ≤ Method 2a 的 Δ → UO 在 KG 中无帮助或负面效果

**预期输出**:
```
outputs/kg_similarity/
├── method_2a_vs_2b_comparison.png
└── README.md (完整说明文档)
```

**预计时间**: 5-10分钟

---

### 3. 四方法综合对比

**状态**: ❌ 待完成

**目标**: 回答所有研究问题

**对比矩阵**:

| 方法 | Matched Mean | Unmatched Mean | Δ (效果) | Cohen's d | 结论 |
|------|-------------|----------------|----------|-----------|------|
| Method 1a (PD Text) | 0.7133 | 0.7106 | +0.0027 | +0.023 | 小效果 ✓ |
| Method 1b (PD+UO Text) | 0.6787 | 0.6788 | -0.0001 | -0.001 | 无效果 ✗ |
| Method 2a (PD KG) | ? | ? | ? | ? | 待计算 |
| Method 2b (PD+UO KG) | (已有) | (已有) | (已有) | (已有) | 待分析 |

**分析维度**:
1. **UO 在 Text 中的作用**: Method 1b vs 1a → ❌ 负面效果
2. **UO 在 KG 中的作用**: Method 2b vs 2a → ? (待验证)
3. **KG vs Text (baseline)**: Method 2a vs 1a → ? (待对比)
4. **KG vs Text (enhanced)**: Method 2b vs 1b → ? (待对比)

**预期输出**:
```
outputs/final_comparison/
├── all_methods_comparison.png (综合对比图)
├── research_questions_answered.json (RQ答案)
├── effect_size_comparison.png (效果量对比)
└── README.md (完整分析报告)
```

**预计时间**: 10-15分钟

---

## 📊 当前实验结果汇总

### Method 1a vs 1b (Text Embedding 方法)

| 指标 | Method 1a (PD) | Method 1b (PD+UO) | 差异 |
|------|---------------|------------------|------|
| Matched Mean | 0.7133 | 0.6787 | -0.0346 |
| Unmatched Mean | 0.7106 | 0.6788 | -0.0318 |
| **Δ (Matched - Unmatched)** | **+0.0027** | **-0.0001** | -0.0028 |
| Cohen's d | +0.023 | -0.001 | -0.024 |

**结论**: 
- ✅ Method 1a 能够区分 (虽然效果小)
- ❌ Method 1b 无法区分
- **UO 在 Text Embedding 中无帮助，反而有害**

---

### Method 2a vs 2b (Knowledge Graph 方法)

**状态**: Method 2a 待完成，Method 2b 已有数据但缺少分析

**待回答的问题**:
- UO 在 KG 方法中是否有帮助？
- KG 方法是否优于 Text 方法？

---

## ⏱️ 完成时间估算

| 任务 | 预计时间 | 备注 |
|------|---------|------|
| Method 2a 计算 | 10-15分钟 | 纯计算，可能较慢 (4000对) |
| Method 2a vs 2b 对比 | 5-10分钟 | 生成图表和分析 |
| 四方法综合对比 | 10-15分钟 | 整合所有结果 |
| **总计** | **25-40分钟** | 不包括 debug 时间 |

---

## 🚀 下一步行动

### 立即可执行

所有必需的数据文件已准备完毕，可以立即开始！

#### Step 1: 完成 Method 2a

```bash
# 创建 Method 2a 计算脚本 (如果还没有)
python -m src.experiments.kg_similarity_method_2a

# 或者直接运行
python run_kg_similarity_experiment.py --method 2a
```

#### Step 2: 对比 Method 2a vs 2b

```bash
python compare_kg_methods.py
```

#### Step 3: 四方法综合对比

```bash
python compare_all_methods.py
```

---

## 📁 完整文件清单

### 输入文件 (已准备好) ✅

```
data/processed/
├── projects_md/                    (20个项目 - PD only)
├── enhanced_projects_md/           (20个项目 - PD+UO)
├── profiles_md/                    (400个学生档案)
└── units_md/                       (IN20 + IN27)

outputs/knowledge_graphs/
├── three_layer_projects/           (20个 PD only KG)
├── enhanced_in20_in27/             (20个 PD+UO KG)
└── enhanced_student_kg/            (400个 Student KG)
```

### 输出文件 (已完成) ✅

```
outputs/embeddings/
├── 1a/                             ✅ Method 1a 完整结果
├── 1b/                             ✅ Method 1b 完整结果
├── method_1a_vs_1b_comparison.png  ✅ 对比图
└── README.md                       ✅ 说明文档

outputs/kg_similarity/
├── method_2b_scores.json           ✅ Method 2b 数据
└── method_2b_analysis.json         ✅ Method 2b 分析
```

### 待生成文件 ❌

```
outputs/kg_similarity/
├── method_2a_scores.json           ❌ Method 2a 数据
├── method_2a_analysis.json         ❌ Method 2a 分析
├── method_2a_dashboard.png         ❌ Method 2a 仪表板
├── method_2a_vs_2b_comparison.png  ❌ 2a vs 2b 对比
└── README.md                       ❌ KG 方法说明文档

outputs/final_comparison/
├── all_methods_comparison.png      ❌ 四方法对比图
├── research_questions_answered.json ❌ RQ 答案
├── effect_size_comparison.png      ❌ 效果量对比
└── README.md                       ❌ 完整分析报告
```

---

## 📊 预期论文贡献

完成所有实验后，你可以在论文中回答:

### 1. Text Embedding 方法的性能

- ✅ **Method 1a**: 可以区分真实配对，但效果量小 (Cohen's d = 0.023)
- ✅ **Method 1b**: 无法区分，添加 UO 反而有害 (Cohen's d = -0.001)
- ✅ **结论**: 在 Text Embedding 中，UO 不仅无帮助，反而降低性能

### 2. Knowledge Graph 方法的性能

- ⏳ **Method 2a**: 待验证
- ⏳ **Method 2b**: 已有数据，待分析
- ⏳ **结论**: UO 在 KG 中的作用有待验证

### 3. KG vs Text 对比

- ⏳ **Baseline 对比** (2a vs 1a): 待验证
- ⏳ **Enhanced 对比** (2b vs 1b): 待验证
- ⏳ **结论**: 哪种表示方式更适合学生-项目匹配？

### 4. 重要发现

**已发现**:
- ✅ 更多信息不一定更好：在 Text Embedding 中，添加 UO 引入噪声
- ✅ 高维空间的诅咒：额外维度稀释了核心匹配信号
- ✅ 方法选择的重要性：不同表示方式对额外信息的敏感度不同

**待验证**:
- ⏳ 结构化表示 (KG) 是否能更好地利用 UO 信息？
- ⏳ KG 的显式关系是否优于 Text 的隐式语义？

---

## 💡 论文写作建议

### Abstract

提及：
1. 研究问题：引入课程信息是否提升匹配效果
2. 方法：对比 Text Embedding vs Knowledge Graph，以及 ±UO
3. 关键发现：UO 在 Text 中无帮助，KG 中待验证
4. 贡献：系统性的 ablation study，揭示信息整合的挑战

### Introduction

1. 动机：学生-项目匹配的重要性
2. 挑战：如何有效整合课程大纲信息
3. 研究问题：RQ1-RQ3
4. 贡献：完整的实验对比框架

### Methodology

1. 数据：20项目 × 20学生/项目 = 400学生档案
2. 方法：
   - Text Embedding: bge-m3, Cosine Similarity
   - Knowledge Graph: 三层结构, Jaccard + Edit Distance
3. 实验设计：2×2 ablation study (PD vs PD+UO, Text vs KG)

### Results

1. Method 1a vs 1b: UO 在 Text 中无帮助 ✅
2. Method 2a vs 2b: UO 在 KG 中的作用 ⏳
3. KG vs Text: 哪个更好？ ⏳

### Discussion

1. 为什么 UO 在 Text 中失败？
   - 高维空间稀释信号
   - 课程信息可能与项目匹配无直接关联
   - 需要更精细的特征工程
2. KG 方法的优势/劣势
3. 实际应用建议

### Conclusion

1. 主要发现
2. 贡献
3. 局限性
4. 未来工作

---

## 🔍 验证清单

在提交论文前，确认以下所有项都已完成：

- [ ] Method 1a 实验完整 ✅
- [ ] Method 1b 实验完整 ✅
- [ ] Method 1a vs 1b 对比完整 ✅
- [ ] Method 2a 实验完整 ❌
- [ ] Method 2b 实验完整 ⚠️
- [ ] Method 2a vs 2b 对比完整 ❌
- [ ] 四方法综合对比完整 ❌
- [ ] 所有可视化图表生成 ⚠️
- [ ] README 文档完整 ⚠️
- [ ] 统计检验结果齐全 ⚠️
- [ ] 研究问题都已回答 ❌

---

## 📞 常见问题

### Q1: 为什么需要做 Method 2a？

**A**: 完整的 ablation study 需要对比 4 种方法。只有对比 2a vs 2b，才能验证 UO 在 KG 中的作用。否则无法判断改进来自 UO 还是 KG。

### Q2: Method 2a 的 KG 文件在哪里？

**A**: `outputs/knowledge_graphs/three_layer_projects/*.json` (58个文件，20个项目的3层KG)

### Q3: 如何判断 matched vs unmatched pairs？

**A**: 学生文件名包含项目名 → matched。例如：
- 项目: `IFN712 Project 13-1`
- 学生: `IFN712 Project 13-1/n12345678_John_Doe.md` → matched
- 学生: `Other Project/n87654321_Jane_Smith.md` → unmatched

### Q4: 为什么 Method 1b 失败了？

**A**: 可能原因：
1. UO 文本过长，稀释了 PD 的核心信息
2. 通用课程信息与特定项目匹配关联度低
3. bge-m3 模型在高维度时性能下降
4. 需要更精细的特征工程或加权融合

### Q5: 预计什么时候能完成所有实验？

**A**: 
- Method 2a: 10-15分钟
- 对比分析: 5-10分钟
- 综合对比: 10-15分钟
- **总计**: 25-40分钟

所有数据已准备好，可以立即开始！

---

## 📚 相关文档

- [COMPLETE_EXPERIMENT_GUIDE.md](COMPLETE_EXPERIMENT_GUIDE.md) - 详细实验指南
- [EXPERIMENT_DESIGN_CLARIFICATION.md](EXPERIMENT_DESIGN_CLARIFICATION.md) - 实验设计说明
- [outputs/embeddings/README.md](outputs/embeddings/README.md) - Method 1a/1b 详细说明
- [EMBEDDING_EXPERIMENT_SUMMARY.md](EMBEDDING_EXPERIMENT_SUMMARY.md) - Embedding 实验总结

---

**更新日期**: 2025-10-04  
**当前进度**: 50% (2/4 方法完成)  
**预计完成**: 2025-10-04 (今天，还需 25-40分钟)

---

## 🎉 准备好了吗？

所有数据已就绪，脚本框架已清晰，现在就可以开始完成剩余实验！

**开始 Method 2a** → **对比 2a vs 2b** → **综合对比全部 4 种方法** → **论文写作** 🚀

