# 正负样本配对逻辑详解

## 🎯 核心概念

**从项目视角进行匹配**：每个项目需要找到最适合它的学生。

- **正样本**：该项目生成的学生（理论上应该匹配该项目）
- **负样本**：其他项目生成的学生（理论上不应该匹配该项目）

---

## 📊 数据概览

- **项目总数**：20个项目
- **学生总数**：200个学生（每个项目生成10个学生档案）
- **配对总数**：20个项目 × 200个学生 = **4000对**

---

## 🔍 配对示例

### 以 Project A 为例

```
Project A 的配对：

✅ 正样本（10对）：
  - Project A  ←→  student_projectA_0  ✓ (is_match=True)
  - Project A  ←→  student_projectA_1  ✓
  - Project A  ←→  student_projectA_2  ✓
  - ...
  - Project A  ←→  student_projectA_9  ✓

❌ 负样本（190对）：
  - Project A  ←→  student_projectB_0  ✗ (is_match=False)
  - Project A  ←→  student_projectB_1  ✗
  - ...
  - Project A  ←→  student_projectB_9  ✗
  - Project A  ←→  student_projectC_0  ✗
  - ...
  - Project A  ←→  student_projectT_9  ✗

总计：10 + 190 = 200对
```

### 完整配对矩阵

```
             | Stu_A_0 | Stu_A_1 | ... | Stu_B_0 | Stu_B_1 | ... | Stu_T_9 |
-------------|---------|---------|-----|---------|---------|-----|---------|
Project A    |    ✓    |    ✓    | ... |    ✗    |    ✗    | ... |    ✗    |
Project B    |    ✗    |    ✗    | ... |    ✓    |    ✓    | ... |    ✗    |
Project C    |    ✗    |    ✗    | ... |    ✗    |    ✗    | ... |    ✗    |
...          |   ...   |   ...   | ... |   ...   |   ...   | ... |   ...   |
Project T    |    ✗    |    ✗    | ... |    ✗    |    ✗    | ... |    ✓    |

✓ = 正样本 (is_match=True)
✗ = 负样本 (is_match=False)
```

---

## 📈 统计信息

### 总体统计

| 指标 | 数值 |
|------|------|
| 总配对数 | 4000 |
| 正样本数 | 200 (5%) |
| 负样本数 | 3800 (95%) |
| 样本比例 | 1:19 |

### 每个项目的统计

| 指标 | 数值 |
|------|------|
| 每个项目的配对数 | 200 |
| 正样本（本项目的学生） | 10 |
| 负样本（其他项目的学生） | 190 |
| 样本比例 | 1:19 |

### 每个学生的统计

| 指标 | 数值 |
|------|------|
| 每个学生的配对数 | 20 |
| 正样本（该学生的来源项目） | 1 |
| 负样本（其他项目） | 19 |
| 样本比例 | 1:19 |

---

## 💡 为什么这样设计？

### ✅ 优点

1. **符合真实场景**
   - 项目需要从所有学生中找到最匹配的
   - 每个学生只有1个真正适合的项目

2. **数据充分**
   - 充分利用所有可能的配对
   - 提供足够的正负样本对比

3. **评估全面**
   - 可以计算Top-K准确率
   - 可以评估排序质量
   - 可以分析错误匹配的模式

4. **一致性好**
   - 与Method 1a/1b保持一致
   - 便于跨方法对比

---

## 🎓 实际应用场景

### 场景1：项目招募学生

```
场景：Project A 需要招募学生

步骤：
1. 计算 Project A 与所有200个学生的相似度
2. 按相似度排序
3. 推荐Top-10学生给项目负责人

期望结果：
- 前10名中应该包含大部分（理想全部）由Project A生成的学生
- Top-1准确率：第1名是否是Project A的学生
- Top-5准确率：前5名中有几个是Project A的学生
```

### 场景2：学生选择项目

```
场景：student_projectA_0 需要选择项目

步骤：
1. 计算该学生与所有20个项目的相似度
2. 按相似度排序
3. 推荐Top-3项目给学生

期望结果：
- Project A 应该排在第1名
- Top-1准确率：第1名是否是Project A
```

---

## 📊 数据格式示例

### JSON结构

```json
[
  {
    "project_id": "project0",
    "student_id": "student_project0_0",
    "is_match": true,
    "similarity": 0.7234,
    "jaccard_similarity": 0.0234,
    "edit_distance": 45
  },
  {
    "project_id": "project0",
    "student_id": "student_project1_0",
    "is_match": false,
    "similarity": 0.6123,
    "jaccard_similarity": 0.0012,
    "edit_distance": 52
  },
  ...
]
```

### Python分析示例

```python
import json
from collections import defaultdict

# 读取数据
with open('method_2a_scores_with_negatives.json') as f:
    data = json.load(f)

# 按项目分组
project_scores = defaultdict(list)
for item in data:
    project_scores[item['project_id']].append(item)

# 对每个项目按相似度排序
for project_id in project_scores:
    project_scores[project_id].sort(
        key=lambda x: x['jaccard_similarity'], 
        reverse=True
    )

# 计算Top-K准确率
def calculate_topk_accuracy(scores, k=10):
    """计算前K个推荐中正样本的比例"""
    top_k = scores[:k]
    correct = sum(1 for item in top_k if item['is_match'])
    return correct / k

# 评估Project 0
project0_scores = project_scores['project0']
top10_acc = calculate_topk_accuracy(project0_scores, k=10)
print(f"Project 0 的Top-10准确率: {top10_acc:.2%}")

# 检查第1名是否正确
rank1_correct = project0_scores[0]['is_match']
print(f"Project 0 的Top-1准确率: {'✓' if rank1_correct else '✗'}")
```

---

## 🔧 技术实现

### 配对生成逻辑

```python
def build_all_pairs(project_kgs, student_kgs):
    """
    生成所有项目-学生配对
    """
    all_pairs = []
    
    # 遍历每个项目
    for project_name, project_data in project_kgs.items():
        
        # 1. 正样本：该项目生成的学生
        if project_name in student_kgs:
            for student_id, student_data in student_kgs[project_name].items():
                all_pairs.append({
                    'project_name': project_name,
                    'student_id': student_id,
                    'is_match': True,  # 正样本
                    'project_nodes': project_data['nodes'],
                    'student_nodes': student_data['nodes'],
                    ...
                })
        
        # 2. 负样本：其他项目生成的学生
        for other_project_name, students in student_kgs.items():
            if other_project_name == project_name:
                continue  # 跳过正样本
            
            for student_id, student_data in students.items():
                all_pairs.append({
                    'project_name': project_name,
                    'student_id': student_id,
                    'is_match': False,  # 负样本
                    'project_nodes': project_data['nodes'],
                    'student_nodes': student_data['nodes'],
                    ...
                })
    
    return all_pairs
```

---

## 📚 相关文档

- `UNIFIED_DATA_FORMAT.md`: 统一数据格式说明
- `rerun_method2_with_neg_samples.py`: 重新生成Method 2数据的脚本
- `EXPERIMENT_RESULTS_SUMMARY.md`: 实验结果总结

---

**最后更新**: 2025-10-04


