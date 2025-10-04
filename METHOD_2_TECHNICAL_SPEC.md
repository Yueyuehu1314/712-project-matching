# Method 2a & 2b 技术规格说明

> 知识图谱相似度计算的详细技术规格
> 更新时间: 2025-10-04

---

## 📊 度量方法

Method 2a 和 Method 2b 使用**完全相同**的相似度度量方法：

### 1. Jaccard Similarity (节点集合相似度)

**公式**:
```
Jaccard(A, B) = |A ∩ B| / |A ∪ B|
```

**计算步骤**:
1. 提取项目KG的所有节点 ID 集合: `P_nodes`
2. 提取学生KG的所有节点 ID 集合: `S_nodes`
3. 计算交集: `intersection = P_nodes ∩ S_nodes`
4. 计算并集: `union = P_nodes ∪ S_nodes`
5. Jaccard = |intersection| / |union|

**特性**:
- 范围: [0, 1]
- 0 = 完全不相似 (没有共同节点)
- 1 = 完全相同 (节点集合完全一致)
- **越大越相似**

**代码实现** (from `run_kg_similarity_experiment.py`):
```python
def compute_jaccard_similarity(set1: Set, set2: Set) -> float:
    """计算Jaccard相似度"""
    if not set1 and not set2:
        return 1.0
    
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    
    return intersection / union if union > 0 else 0.0
```

---

### 2. Edit Distance (图编辑距离)

**公式**:
```
Edit_Distance = node_diff + edge_diff
```

其中:
- `node_diff = |P_nodes △ S_nodes|` (对称差，不同的节点数)
- `edge_diff = |P_edges △ S_edges|` (对称差，不同的边数)

**计算步骤**:
1. 提取两个图的节点集合: `P_nodes`, `S_nodes`
2. 提取两个图的边集合: `P_edges`, `S_edges`
3. 计算节点对称差: `node_diff = |P_nodes △ S_nodes|`
4. 找到共同节点: `common = P_nodes ∩ S_nodes`
5. 过滤只保留共同节点的边:
   - `P_edges_filtered = {(s,t) ∈ P_edges | s,t ∈ common}`
   - `S_edges_filtered = {(s,t) ∈ S_edges | s,t ∈ common}`
6. 计算边对称差: `edge_diff = |P_edges_filtered △ S_edges_filtered|`
7. Edit Distance = node_diff + edge_diff

**特性**:
- 范围: [0, ∞)
- 0 = 完全相同
- 值越大 = 差异越大
- **越小越相似**

**物理意义**: 将一个图转换为另一个图所需的最少操作数（增删节点和边）

**代码实现** (from `run_kg_similarity_experiment.py`):
```python
def compute_edit_distance(nodes1: Set, nodes2: Set, edges1: Set, edges2: Set) -> int:
    """计算简化的图编辑距离"""
    # 节点差异
    node_diff = len(nodes1 ^ nodes2)  # 对称差
    
    # 边差异（只考虑共同节点的边）
    common_nodes = nodes1 & nodes2
    edges1_filtered = {(s, t) for s, t in edges1 if s in common_nodes and t in common_nodes}
    edges2_filtered = {(s, t) for s, t in edges2 if s in common_nodes and t in common_nodes}
    edge_diff = len(edges1_filtered ^ edges2_filtered)
    
    return node_diff + edge_diff
```

---

## 🆚 Method 2a vs Method 2b

两个方法的**唯一区别**是输入的项目知识图谱：

| 特性 | Method 2a | Method 2b |
|------|-----------|-----------|
| **项目输入** | PD only (仅项目描述) | PD + UO (项目描述 + 课程大纲) |
| **项目KG目录** | `outputs1/knowledge_graphs/three_layer_projects/` | `outputs1/knowledge_graphs/enhanced_in20_in27/` |
| **项目KG文件** | `*_entities.json` | `*_enhanced_kg.json` |
| **学生输入** | Student Profile | Student Profile (相同) |
| **学生KG目录** | `outputs1/knowledge_graphs/enhanced_student_kg/` | `outputs1/knowledge_graphs/enhanced_student_kg/` (相同) |
| **度量方法** | Jaccard + Edit Distance | Jaccard + Edit Distance (相同) |
| **总对比数** | 20 × 200 = 4000 对 | 20 × 200 = 4000 对 |

---

## 📈 实验设计

### 数据集

| 项 | 数量 | 说明 |
|----|------|------|
| 项目数 | 20 | IFN712 项目提案 |
| 每项目学生数 | 20 | 由LLM生成的学生档案 |
| 总学生数 | 400 | 20 × 20 = 400 |
| 每项目对比数 | 200 | 该项目 vs 所有学生 |
| **总对比数** | **4000** | 20 × 200 = 4000 pairs |

### Matched vs Unmatched Pairs

对于每个项目 P:
- **Matched pairs** (20对): 项目 P 与由 P 生成的 20 个学生
- **Unmatched pairs** (180对): 项目 P 与由其他 19 个项目生成的 380 个学生

**全局统计**:
- Total matched pairs: 20 × 20 = **200 对**
- Total unmatched pairs: 20 × 180 = **3600 对**
- Total: **3800 对**

**注意**: 实际上每个项目只和它自己的20个学生是matched，和其他19个项目的380个学生是unmatched，所以是 20 × (20 + 380) = 20 × 400，但去重后总共是200个matched + 3800个unmatched = 4000对。

---

## 🎯 实验目标

### 主要研究问题

**RQ2**: 在知识图谱方法中，添加 Unit Outline 信息是否能提升匹配效果？

### 评估标准

如果 Method 2b 优于 Method 2a，需要满足：

1. **Jaccard Similarity**:
   - Matched pairs 的 Jaccard 更高
   - Unmatched pairs 的 Jaccard 更低
   - **Δ_Jaccard(2b) = Matched_mean - Unmatched_mean > Δ_Jaccard(2a)**

2. **Edit Distance**:
   - Matched pairs 的 Edit Distance 更低
   - Unmatched pairs 的 Edit Distance 更高
   - **Δ_EditDist(2b) = Unmatched_mean - Matched_mean > Δ_EditDist(2a)**

3. **效果量**:
   - Cohen's d 更大 (绝对值)
   - 统计显著性: p < 0.05

---

## 📊 统计分析

对每个方法，分别计算 Jaccard 和 Edit Distance 的：

### 描述统计
- Mean (均值)
- Median (中位数)
- Std (标准差)
- Min (最小值)
- Max (最大值)

### 统计检验
- **T-test**: 检验 matched vs unmatched 的均值差异
- **Mann-Whitney U**: 非参数检验
- **Kolmogorov-Smirnov**: 分布差异检验

### 效果量
- **Cohen's d**: 标准化效果量
  - d < 0.2: 小效果
  - 0.2 ≤ d < 0.5: 中等效果
  - d ≥ 0.5: 大效果

---

## 🔍 当前状态

### Method 2b (⚠️ 部分完成)

**已完成**:
- ✅ 计算了 20 个 matched pairs
- ✅ 生成了 `method_2b_scores.json` 和 `method_2b_analysis.json`

**当前结果**:
```json
{
  "matched_jaccard": {
    "mean": 0.0358,
    "median": 0.0426,
    "std": 0.0117,
    "min": 0.0167,
    "max": 0.0517
  },
  "matched_edit_distance": {
    "mean": 73.45,
    "median": 74.0,
    "std": 16.38,
    "min": 55.0,
    "max": 90.0
  }
}
```

**缺失**:
- ❌ Unmatched pairs (3800对)
- ❌ Matched vs Unmatched 对比
- ❌ 统计检验结果
- ❌ 可视化图表

### Method 2a (❌ 待完成)

**需要完成**:
- ❌ 计算 matched pairs (200对)
- ❌ 计算 unmatched pairs (3800对)
- ❌ 完整统计分析
- ❌ 生成所有输出文件

---

## 📁 输出文件规格

### Method 2a 需要生成的文件

```
outputs/kg_similarity/
├── method_2a_scores.json          # 所有对比的详细分数 (4000条记录)
├── method_2a_analysis.json        # 统计分析结果
├── method_2a_dashboard.png        # 综合仪表板
├── method_2a_histogram.png        # 分布直方图
├── method_2a_boxplot.png          # 箱线图
├── method_2a_violin.png           # 小提琴图
└── method_2a_cdf.png              # 累积分布函数
```

### `method_2a_scores.json` 格式

```json
[
  {
    "project_name": "IFN712 Project 13-1",
    "student_id": "student_n12345678_John_Doe_enhanced_kg",
    "is_match": true,
    "jaccard_similarity": 0.0452,
    "edit_distance": 68,
    "common_nodes": 5,
    "project_only_nodes": 25,
    "student_only_nodes": 27
  },
  // ... 3999 more records
]
```

### `method_2a_analysis.json` 格式

```json
{
  "method": "method_2a",
  "total_pairs": 4000,
  "matched_pairs": 200,
  "unmatched_pairs": 3800,
  
  "matched_jaccard": {
    "mean": 0.XXXX,
    "median": 0.XXXX,
    "std": 0.XXXX,
    "min": 0.XXXX,
    "max": 0.XXXX
  },
  "unmatched_jaccard": {
    "mean": 0.XXXX,
    "median": 0.XXXX,
    "std": 0.XXXX,
    "min": 0.XXXX,
    "max": 0.XXXX
  },
  "jaccard_delta": 0.XXXX,
  "jaccard_cohens_d": 0.XXXX,
  "jaccard_ttest": {
    "statistic": 0.XXXX,
    "pvalue": 0.XXXX
  },
  "jaccard_mannwhitneyu": {
    "statistic": 0.XXXX,
    "pvalue": 0.XXXX
  },
  "jaccard_ks": {
    "statistic": 0.XXXX,
    "pvalue": 0.XXXX
  },
  
  "matched_edit_distance": { /* same structure */ },
  "unmatched_edit_distance": { /* same structure */ },
  "edit_distance_delta": 0.XXXX,
  "edit_distance_cohens_d": 0.XXXX,
  "edit_distance_ttest": { /* same structure */ },
  "edit_distance_mannwhitneyu": { /* same structure */ },
  "edit_distance_ks": { /* same structure */ }
}
```

---

## 🚀 实施步骤

### Step 1: 补充完成 Method 2b

修改 `run_kg_similarity_experiment.py` 的 `run_method_2b()` 函数，添加 unmatched pairs 的计算：

```python
def run_method_2b(self) -> List[GraphSimilarityScore]:
    """Method 2b: PD+UO KG vs Student KG"""
    results = []
    
    # 1. Matched pairs (已有的代码)
    # ... existing code ...
    
    # 2. Unmatched pairs (新增)
    for proj_dir in project_dirs:
        proj_name = proj_dir.name
        project_kg = self.loader.load_kg_json(str(kg_files[0]))
        
        # 获取所有其他项目的学生
        for other_proj_dir in project_dirs:
            if other_proj_dir.name == proj_name:
                continue  # 跳过自己的学生
            
            student_files = glob.glob(f"{student_kg_dir}/{other_proj_dir.name}/*_kg.json")
            
            for student_file in student_files:
                student_id = Path(student_file).stem
                student_kg = self.loader.load_kg_json(student_file)
                
                score = self.comparator.compare_graphs(
                    project_kg, student_kg,
                    proj_name, student_id, is_match=False
                )
                results.append(score)
    
    return results
```

### Step 2: 运行 Method 2a

使用相同的代码结构，但读取 `three_layer_projects` 目录的KG文件。

### Step 3: 生成可视化

参考 Method 1a/1b 的可视化代码，生成类似的图表。

### Step 4: 对比分析

创建对比脚本，生成 Method 2a vs 2b 的综合对比报告。

---

## 📊 预期结果示例

### 假设的理想结果 (如果 UO 有帮助)

| 指标 | Method 2a (PD only) | Method 2b (PD+UO) | 改进 |
|------|-------------------|------------------|------|
| **Jaccard (Matched)** | 0.035 | 0.045 | +28.6% ✓ |
| **Jaccard (Unmatched)** | 0.032 | 0.028 | -12.5% ✓ |
| **Δ Jaccard** | +0.003 | **+0.017** | +466% ✓✓ |
| **Edit Dist (Matched)** | 75 | 65 | -13.3% ✓ |
| **Edit Dist (Unmatched)** | 78 | 80 | +2.6% ✓ |
| **Δ Edit Dist** | -3 | **-15** | +400% ✓✓ |
| **Cohen's d (Jaccard)** | 0.05 | **0.25** | +400% ✓✓ |

**结论**: UO 在 KG 方法中显著提升了区分能力！

### 假设的负面结果 (如果 UO 无帮助)

| 指标 | Method 2a (PD only) | Method 2b (PD+UO) | 改进 |
|------|-------------------|------------------|------|
| **Δ Jaccard** | +0.005 | +0.003 | -40% ✗ |
| **Δ Edit Dist** | -5 | -3 | -40% ✗ |
| **Cohen's d** | 0.08 | 0.05 | -37.5% ✗ |

**结论**: UO 在 KG 方法中也无帮助，甚至降低了性能。

---

## 🔗 相关文件

- **实现代码**: `run_kg_similarity_experiment.py`
- **实验指南**: `COMPLETE_EXPERIMENT_GUIDE.md`
- **完整清单**: `COMPLETE_EXPERIMENT_LIST.md`
- **Method 1 对比**: `outputs/embeddings/README.md`

---

## 📝 总结

✅ **明确的计算方法**:
- Jaccard Similarity (节点相似度)
- Edit Distance (图编辑距离)

✅ **清晰的对比设计**:
- Method 2a: PD only KG (baseline)
- Method 2b: PD + UO KG (enhanced)

✅ **完整的统计分析**:
- 描述统计 + 统计检验 + 效果量

🎯 **明确的研究问题**:
- UO 在知识图谱中是否有帮助？
- KG vs Text 哪个更好？

---

**准备好开始实验了吗？** 🚀

所有数据已就绪，代码框架已清晰，只需要运行计算和分析！

