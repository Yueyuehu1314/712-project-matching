# 统一数据格式说明

## 📋 正负样本数据格式规范

为了便于管理和分析，所有4个实验方法（Method 1a, 1b, 2a, 2b）都使用**统一的数据格式**。

### ✅ 核心原则

1. **正负样本保存在同一个JSON文件中**
2. **使用 `is_match` 字段区分正负样本**
   - `is_match: true` → 正样本（项目与由其生成的学生）
   - `is_match: false` → 负样本（项目与由其他项目生成的学生）
3. **便于统计分析和可视化**

### 📊 样本配对逻辑

**从项目视角：**
- 有20个项目，每个项目生成10个学生档案
- **对于 Project A：**
  - ✅ **正样本（10个）**：由 Project A 生成的10个学生
  - ❌ **负样本（190个）**：由其他19个项目生成的190个学生
- **样本比例：1:19** （每个项目有10个正样本，190个负样本）
- **总配对数：20个项目 × 200个学生 = 4000对**
  - 200个正样本对（每个项目10个）
  - 3800个负样本对（每个项目190个）

---

## 📊 各方法的数据格式

### Method 1a - PD only Embedding

**文件位置**: `outputs/embeddings/1a/similarity_comparison_results.json`

**数据结构**:
```json
{
  "generated_at": "2025-10-04T14:05:06.965233",
  "embeddings_file": "outputs/embeddings/project_profile_embeddings.json",
  "analysis": {
    "matched_pairs": {
      "count": 200,
      "mean": 0.7133,
      "std": 0.1161,
      ...
    },
    "unmatched_pairs": {
      "count": 3800,
      "mean": 0.7106,
      "std": 0.1154,
      ...
    }
  },
  "raw_similarities": [
    {
      "student_id": "student_project0_0",
      "project_id": "project0",
      "similarity": 0.7234,
      "is_match": true  // 正样本
    },
    {
      "student_id": "student_project0_0",
      "project_id": "project1",
      "similarity": 0.6123,
      "is_match": false  // 负样本
    },
    ...
  ]
}
```

**关键字段**:
- `student_id`: 学生ID
- `project_id`: 项目ID
- `similarity`: 余弦相似度 (0-1)
- `is_match`: 是否为匹配的正样本

**样本比例**: 1:19 (200个正样本, 3800个负样本)

---

### Method 1b - PD+UO+Profile Embedding

**文件位置**: `outputs/embeddings/1b/similarity_comparison_results.json`

**数据结构**: 与Method 1a相同

**关键字段**:
- `student_id`: 学生ID
- `project_id`: 项目ID
- `similarity`: 余弦相似度 (0-1)
- `is_match`: 是否为匹配的正样本

**样本比例**: 1:19 (200个正样本, 3800个负样本)

---

### Method 2a - 基础KG相似度

**文件位置**: 
- `outputs/kg_similarity/2a/method_2a_scores_with_negatives.json` (新)
- `outputs/kg_similarity/2a/method_2a_analysis_with_negatives.json` (新)

**数据结构** (scores文件):
```json
[
  {
    "student_id": "student_project0_0",
    "project_id": "project0",
    "project_folder": "IFN712_proposal_...",
    "is_match": true,  // 正样本
    "jaccard_similarity": 0.0234,
    "edit_distance": 45
  },
  {
    "student_id": "student_project0_0",
    "project_id": "project1",
    "project_folder": "IFN712_proposal_...",
    "is_match": false,  // 负样本
    "jaccard_similarity": 0.0012,
    "edit_distance": 52
  },
  ...
]
```

**关键字段**:
- `student_id`: 学生ID
- `project_id`: 项目ID
- `jaccard_similarity`: Jaccard相似度 (0-1)
- `edit_distance`: 图编辑距离（步数）
- `is_match`: 是否为匹配的正样本

**样本比例**: 1:19 (200个正样本, 3800个负样本)

**分析文件结构**:
```json
{
  "total_pairs": 4000,
  "matched_count": 200,
  "unmatched_count": 3800,
  "matched_jaccard": {
    "mean": 0.0149,
    "median": 0.0000,
    "std": 0.0202,
    "min": 0.0000,
    "max": 0.0612
  },
  "unmatched_jaccard": {
    "mean": 0.0023,
    "median": 0.0000,
    "std": 0.0045,
    "min": 0.0000,
    "max": 0.0234
  },
  "matched_edit_distance": {
    "mean": 48.3,
    "median": 48.0,
    "std": 4.2,
    "min": 10.0,
    "max": 56.0
  },
  "unmatched_edit_distance": {
    "mean": 51.2,
    "median": 52.0,
    "std": 3.8,
    "min": 38.0,
    "max": 64.0
  }
}
```

---

### Method 2b - 增强KG相似度

**文件位置**: 
- `outputs/kg_similarity/2b/method_2b_scores_with_negatives.json` (新)
- `outputs/kg_similarity/2b/method_2b_analysis_with_negatives.json` (新)

**数据结构** (scores文件):
```json
[
  {
    "student_id": "student_project0_0",
    "project_id": "project0",
    "project_folder": "IFN712_proposal_...",
    "is_match": true,  // 正样本
    "node_jaccard": 0.0492,
    "edge_jaccard": 0.9950,
    "edit_distance": 35,
    "readiness_score": 0.0993
  },
  {
    "student_id": "student_project0_0",
    "project_id": "project1",
    "project_folder": "IFN712_proposal_...",
    "is_match": false,  // 负样本
    "node_jaccard": 0.0123,
    "edge_jaccard": 0.9920,
    "edit_distance": 42,
    "readiness_score": 0.0456
  },
  ...
]
```

**关键字段**:
- `student_id`: 学生ID
- `project_id`: 项目ID
- `node_jaccard`: 节点Jaccard相似度 (0-1)
- `edge_jaccard`: 边Jaccard相似度 (0-1)
- `edit_distance`: 图编辑距离（步数）
- `readiness_score`: 准备度评分 (0-1)
- `is_match`: 是否为匹配的正样本

**样本比例**: 1:19 (200个正样本, 3800个负样本)

---

## 🎯 为什么采用这种格式？

### ✅ 优点

1. **易于管理**
   - 单一文件，不需要管理多个文件
   - 版本控制友好
   - 备份和迁移简单

2. **便于分析**
   - 一次加载即可获取所有数据
   - 方便计算正负样本的对比统计
   - 易于可视化（正负样本对比图）

3. **数据一致性**
   - 避免正负样本文件不同步
   - 保证样本总数的准确性
   - 便于验证数据完整性

4. **易于扩展**
   - 添加新字段无需修改文件结构
   - 可以轻松添加更多负样本
   - 支持多种采样策略

### ❌ 为什么不分开保存？

分开保存正负样本到不同文件会导致：
- ❌ 文件管理复杂（2倍文件数）
- ❌ 容易出现数据不一致
- ❌ 分析时需要同时读取多个文件
- ❌ 难以保证正负样本的对应关系
- ❌ 版本控制困难

---

## 📈 使用示例

### Python读取和分析

```python
import json
import numpy as np

# 读取数据
with open('outputs/kg_similarity/2a/method_2a_scores_with_negatives.json') as f:
    data = json.load(f)

# 分离正负样本
matched = [item for item in data if item['is_match']]
unmatched = [item for item in data if not item['is_match']]

# 统计分析
print(f"正样本数: {len(matched)}")
print(f"负样本数: {len(unmatched)}")
print(f"正样本平均Jaccard: {np.mean([x['jaccard_similarity'] for x in matched]):.4f}")
print(f"负样本平均Jaccard: {np.mean([x['jaccard_similarity'] for x in unmatched]):.4f}")

# 按学生分组
from collections import defaultdict
student_rankings = defaultdict(list)

for item in data:
    student_rankings[item['student_id']].append(
        (item['project_id'], item['jaccard_similarity'], item['is_match'])
    )

# 对每个学生的项目按相似度排序
for student_id in student_rankings:
    student_rankings[student_id].sort(key=lambda x: x[1], reverse=True)
```

---

## 🔄 如何重新生成带负样本的Method 2数据

运行以下脚本：

```bash
python rerun_method2_with_neg_samples.py
```

该脚本会：
1. 加载所有项目和学生知识图谱
2. 为每个学生生成：
   - 1个正样本（与其匹配的项目）
   - 10个负样本（随机采样的其他项目）
3. 计算所有配对的相似度
4. 保存到统一格式的JSON文件
5. 生成分析报告

---

## 📝 注意事项

1. **负样本采样策略**
   - **使用全部负样本**：每个项目与其他19个项目的所有学生配对
   - 可以改进为"困难负样本"（相似度较高但不匹配）
   - 样本比例固定为 1:19（10正样本 : 190负样本）

2. **文件命名**
   - 新格式文件名包含 `_with_negatives` 后缀
   - 旧文件保留作为参考
   - 诊断脚本会优先使用新格式

3. **兼容性**
   - 诊断脚本 `quick_diagnosis.py` 已更新
   - 支持自动检测新旧格式
   - 可视化脚本需要相应更新

---

## 🎓 最佳实践

1. **数据生成**
   ```bash
   # Method 1a/1b 已有正负样本
   # Method 2a/2b 需要重新生成
   python rerun_method2_with_neg_samples.py
   ```

2. **诊断分析**
   ```bash
   python quick_diagnosis.py
   ```

3. **可视化**
   ```bash
   # 需要更新可视化脚本以使用新格式
   python visualize_method_results.py --method 2a
   ```

4. **评估指标**
   ```bash
   python src/experiments/improved_evaluation_metrics.py --method all
   ```

---

## 📚 相关文档

- `IMPROVEMENT_STRATEGIES.md`: 改进策略
- `EXPERIMENT_RESULTS_SUMMARY.md`: 实验结果总结
- `quick_diagnosis.py`: 快速诊断脚本
- `rerun_method2_with_neg_samples.py`: 重新生成Method 2数据

---

**最后更新**: 2025-10-04

