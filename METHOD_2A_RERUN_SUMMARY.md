# Method 2a 实验重新运行总结

> 日期: 2025-10-04  
> 状态: ✅ 完成

---

## 📋 执行步骤

### 1. 删除旧结果
```bash
rm -f outputs/kg_similarity/method_2a_*.json
rm -f outputs/kg_similarity/method_2a_*.png
```

**删除的文件:**
- `method_2a_analysis.json`
- `method_2a_scores.json`
- `method_2a_*.png` (可视化图表)

---

### 2. 更新代码配置

**修改文件**: `run_kg_similarity_experiment.py`

#### 变更 1: 更新项目KG目录路径

```python
# 旧路径
project_kg_dir = "outputs1/knowledge_graphs/three_layer_projects"

# 新路径
project_kg_dir = "outputs1/knowledge_graphs/project_proposal_only"
```

#### 变更 2: 适配新的目录结构

**旧结构** (three_layer_projects):
```
three_layer_projects/
  - AI-Based_Human_Activity_entities.json
  - AI-Based_Human_Activity_relationships.json
  - ...
```

**新结构** (project_proposal_only):
```
project_proposal_only/
  - AI-Based_Human_Activity/
    - entities.json
    - relationships.json
    - kg.png
    - project.md
    - stats.json
  - ...
```

#### 变更 3: 更新文件加载逻辑

```python
# 从扁平结构改为目录结构
project_dirs = [d for d in Path(project_kg_dir).iterdir() if d.is_dir()]

for proj_dir in project_dirs:
    simplified_name = proj_dir.name
    proj_file = proj_dir / "entities.json"
    # ...
```

#### 变更 4: 增强KG加载器

支持两种entities.json格式：
- `*_entities.json` (three_layer格式)
- `entities.json` (project_proposal_only格式)

```python
if '_entities.json' in file_path or file_path.endswith('entities.json'):
    if '_entities.json' in file_path:
        rel_file = file_path.replace('_entities.json', '_relationships.json')
    else:
        rel_file = file_path.replace('entities.json', 'relationships.json')
    # ...
```

---

### 3. 运行实验

```bash
python run_kg_similarity_experiment.py
```

---

## 📊 实验结果

### 输入数据

| 项 | 数量 | 说明 |
|----|------|------|
| **项目总数** | 20 | `project_proposal_only` 目录下的项目 |
| **有映射的项目** | 18 | 在 `project_name_mapping.json` 中有映射 |
| **处理的项目** | 18 | 成功找到学生KG的项目 |
| **每项目学生数** | 10 | 由该项目生成的学生档案 |
| **总对比数** | 180 | 18 × 10 = 180 matched pairs |

### 输出文件

**保存位置**: `outputs/kg_similarity/`

1. **method_2a_scores.json** (51 KB)
   - 包含所有180个对比的详细分数
   - 每条记录包含：project_name, student_id, is_match, jaccard_similarity, edit_distance, 等

2. **method_2a_analysis.json** (454 B)
   - 统计分析结果
   - 包含均值、中位数、标准差、最小值、最大值

### 统计结果

```json
{
  "method": "method_2a",
  "total_pairs": 180,
  "matched_pairs": 180,
  "unmatched_pairs": 0,
  "matched_jaccard": {
    "mean": 0.0149,
    "median": 0.0,
    "std": 0.0202,
    "min": 0.0,
    "max": 0.0612
  },
  "matched_edit_distance": {
    "mean": 48.3,
    "median": 48.0,
    "std": 4.20,
    "min": 10.0,
    "max": 56.0
  }
}
```

### 关键发现

1. **Jaccard相似度很低**
   - 均值: 1.49%
   - 中位数: 0%
   - 说明项目KG(PD only)与学生KG之间重叠很少

2. **编辑距离较大**
   - 均值: 48.3
   - 说明需要大量编辑才能将一个图转换为另一个

3. **未找到学生KG的项目**
   - `Deep_Learning_Malicious_Package_Detection`
   - `Diabetes_Complications_Correlation_Analysis`
   
   这两个项目在 `project_proposal_only` 中存在，但在 `enhanced_student_kg` 中没有对应的学生目录（可能因为它们是后来添加的）

---

## 🔧 项目名称映射

**映射文件**: `outputs1/knowledge_graphs/project_name_mapping.json`

**映射数**: 18个

**示例**:
```json
{
  "AI-Based_Human_Activity": "HAR_WiFi_Proposal_Zhenguo-1",
  "Smart_Intersection_Localization": "Localization_Proposal_Zhenguo",
  "VitalID_Smartphone-Based": "VitalID_Proposal_Zhenguo",
  ...
}
```

**作用**: 将简化项目名（用于KG目录）映射到原始项目名（用于学生KG目录）

---

## ✅ 验证检查

- [x] 删除了所有旧的2a结果文件
- [x] 更新了项目KG路径为 `project_proposal_only`
- [x] 适配了新的目录结构（子目录格式）
- [x] 增强了KG加载器支持 `entities.json` 格式
- [x] 成功处理了18个项目
- [x] 生成了180个matched pairs的结果
- [x] 输出了统计分析文件

---

## 📝 注意事项

### 1. 数据完整性

- **20个项目**: 全部在 `project_proposal_only` 中
- **18个有映射**: 在 `project_name_mapping.json` 中
- **2个无学生KG**: Deep_Learning_Malicious_Package_Detection, Diabetes_Complications_Correlation_Analysis

### 2. 代码改动

- `run_kg_similarity_experiment.py` 已永久更新以支持新结构
- 同时兼容旧的 `_entities.json` 和新的 `entities.json` 格式
- Method 2b 代码已恢复（未注释），下次运行会包含2b

### 3. 结果解释

**低相似度原因**:
- PD only (仅项目描述) 的KG非常精简
- 学生KG包含学生profile的详细信息
- 两者的实体集合重叠度低

**后续比较**:
- Method 2b 将使用 PD+UO (项目描述+课程大纲) 的增强KG
- 预期相似度会更高

---

## 🎯 下一步

1. **运行 Method 2b** (如果需要):
   ```bash
   python run_kg_similarity_experiment.py
   ```
   现在会运行2a和2b两个方法

2. **可视化结果**:
   - 如果有可视化代码，重新生成图表
   - 比较2a和2b的结果

3. **分析结果**:
   - 详细分析为什么相似度这么低
   - 检查哪些项目-学生对相似度较高
   - 探索如何改进匹配算法

---

## 📂 相关文件

- `run_kg_similarity_experiment.py` - 实验主脚本
- `outputs/kg_similarity/method_2a_scores.json` - 详细分数
- `outputs/kg_similarity/method_2a_analysis.json` - 统计分析
- `outputs1/knowledge_graphs/project_proposal_only/` - 项目KG (PD only)
- `outputs1/knowledge_graphs/enhanced_student_kg/` - 学生KG
- `outputs1/knowledge_graphs/project_name_mapping.json` - 名称映射

---

**实验完成时间**: 2025-10-04 17:44  
**执行状态**: ✅ 成功

