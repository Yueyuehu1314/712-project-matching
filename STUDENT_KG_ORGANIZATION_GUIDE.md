# 学生知识图谱组织与增强指南

## 📋 概览

本文档说明了如何：
1. 按Project分类学生知识图谱文件
2. 为学生知识图谱补充前置课程(Prerequisite)信息

---

## 🎯 问题1: 学生KG按Project分类

### 背景

学生知识图谱文件当前都在同一个目录：
```
outputs/knowledge_graphs/individual/enhanced_student_kg/
  - student_n00114716_Finley_Thompson_enhanced_kg.json
  - student_n00114716_Finley_Thompson_kg.png
  - ... (187个学生)
```

但这些学生实际上来自20个不同的项目，其档案分别存储在：
```
data/processed/profiles_md/
  - IFN712_proposal_conversational_agent_prosody/
  - IFN712 Project Proposal Template_2025_Project matching/
  - HAR_WiFi_Proposal_Zhenguo-1/
  - ... (共20个项目)
```

### 解决方案

使用 `organize_student_kg_by_project.py` 脚本自动按项目分类：

```bash
python organize_student_kg_by_project.py
```

### 运行结果

```
✅ 组织完成！
  总学生数: 187
  成功组织: 187
  未找到项目: 0
  项目数量: 19

📊 各项目学生数量:
  - IFN712 Project Proposal Template_2025_Project matching: 10 个学生
  - IFN712 Project Proposal Template_2025_Feng_V2P: 10 个学生
  - IFN712 Project 12-1: 10 个学生
  ... (其他16个项目)
  - IFN712_proposal_conversational_agent_prosody: 9 个学生
```

### 输出结构

```
outputs/knowledge_graphs/individual/by_project/
  ├── IFN712_proposal_conversational_agent_prosody/
  │   ├── student_n00114716_Finley_Thompson_enhanced_kg.json
  │   ├── student_n00114716_Finley_Thompson_kg.png
  │   └── ... (9个学生)
  ├── HAR_WiFi_Proposal_Zhenguo-1/
  │   └── ... (10个学生)
  └── ... (共19个项目目录)
```

### 特点

- ✅ **复制模式**：保留原文件，不影响原始数据
- ✅ **自动映射**：从 `data/processed/profiles_md/` 自动读取学生-项目关系
- ✅ **完整性验证**：自动检查JSON和PNG文件配对

---

## 🔍 问题2: 是否需要补充前置课程信息？

### 分析结果

运行分析命令：
```bash
python add_prerequisites_to_student_kg.py --analyze-only
```

### 发现

```
✅ 加载前置课程信息: 24 个课程有前置要求
  📚 IN20: 0 个课程有前置要求
  📚 IN27: 24 个课程有前置要求

学生总数: 188
有前置课程要求的学生: 176 (93.6%)

最常见的缺失前置课程 (Top 10):
  - IFQ555: 176 个学生缺失
  - IFQ556: 148 个学生缺失
  - IFN501: 108 个学生缺失
  - IFN581: 98 个学生缺失
  - IFN556: 48 个学生缺失
  - IFN563: 40 个学生缺失
  - IFN555: 35 个学生缺失
```

### 分析解读

#### ✅ **需要补充的理由**

1. **覆盖率高**: 93.6%的学生(176/188)修了有前置要求的课程
2. **信息完整性**: 前置课程关系是课程依赖的重要组成部分
3. **匹配优化**: 了解学生的课程背景有助于更精准的项目匹配

#### 📊 **前置课程数据来源**

- **IN27 (Master of Data Analytics)**: 24个课程有前置要求
  - 例如：IFN619 需要 IFQ555, IFQ556
  - 例如：IFN632 需要 IFN501, IFN581
  
- **IN20 (Bachelor of IT)**: 当前提取到0个
  - 可能需要改进解析逻辑或检查文档格式

#### ⚠️ **缺失课程分析**

大多数学生缺失的课程（如 IFQ555, IFQ556）可能是：
- **本科基础课程**: 学生已在本科阶段完成
- **豁免课程**: 学生通过其他途径满足要求
- **不同学历背景**: 非必修课程

### 建议策略

#### 方案A: 仅添加关系（推荐）

**适用场景**: 只为学生已修的课程添加前置关系

```bash
python add_prerequisites_to_student_kg.py
```

**效果**:
- 不新增课程节点
- 只在学生修过的课程间建立 `PREREQUISITE_FOR` 关系
- 知识图谱规模不变

**示例**:
```
学生修了: IFN619, IFQ555, IFQ556

添加关系:
  IFQ555 --PREREQUISITE_FOR--> IFN619
  IFQ556 --PREREQUISITE_FOR--> IFN619
```

#### 方案B: 添加缺失节点

**适用场景**: 完整展示课程依赖链

```bash
python add_prerequisites_to_student_kg.py --add-missing
```

**效果**:
- 添加学生未修但需要的前置课程节点
- 节点标记为 `is_missing: True`
- 建立完整的前置关系链

**示例**:
```
学生修了: IFN619

添加节点: IFQ555 (missing), IFQ556 (missing)
添加关系:
  IFQ555 --PREREQUISITE_FOR--> IFN619
  IFQ556 --PREREQUISITE_FOR--> IFN619
```

---

## 🛠️ 使用指南

### 1. 按Project组织文件

```bash
cd /Users/lynn/Documents/GitHub/ProjectMatching

# 运行组织脚本（复制模式）
python organize_student_kg_by_project.py
```

**输出**: `outputs/knowledge_graphs/individual/by_project/`

---

### 2. 分析前置课程情况

```bash
# 仅分析，不修改文件
python add_prerequisites_to_student_kg.py --analyze-only
```

---

### 3. 添加前置课程信息

#### 选项1: 仅添加关系（推荐）

```bash
python add_prerequisites_to_student_kg.py \
  --kg-dir outputs/knowledge_graphs/individual/enhanced_student_kg
```

**输出**: `*_with_prereq.json` 文件

#### 选项2: 添加缺失节点

```bash
python add_prerequisites_to_student_kg.py \
  --kg-dir outputs/knowledge_graphs/individual/enhanced_student_kg \
  --add-missing
```

---

### 4. 针对特定项目处理

```bash
# 先组织到项目目录
python organize_student_kg_by_project.py

# 只处理某个项目的学生
python add_prerequisites_to_student_kg.py \
  --kg-dir "outputs/knowledge_graphs/individual/by_project/IFN712_proposal_conversational_agent_prosody"
```

---

## 📊 数据结构

### 添加前置课程前

```json
{
  "entities": [
    {
      "id": "course_ifn619",
      "name": "IFN619 Data Analytics",
      "entity_type": "COURSE"
    }
  ],
  "relationships": [
    {
      "source_id": "student_n00114716",
      "target_id": "course_ifn619",
      "relation_type": "COMPLETED_COURSE"
    }
  ]
}
```

### 添加前置课程后（方案A：仅关系）

```json
{
  "entities": [
    {
      "id": "course_ifn619",
      "name": "IFN619 Data Analytics",
      "entity_type": "COURSE"
    },
    {
      "id": "course_ifq555",
      "name": "IFQ555 Statistics",
      "entity_type": "COURSE"
    }
  ],
  "relationships": [
    {
      "source_id": "student_n00114716",
      "target_id": "course_ifn619",
      "relation_type": "COMPLETED_COURSE"
    },
    {
      "source_id": "course_ifq555",
      "target_id": "course_ifn619",
      "relation_type": "PREREQUISITE_FOR",
      "weight": 1.0,
      "properties": {
        "description": "IFQ555 is a prerequisite for IFN619"
      }
    }
  ],
  "metadata": {
    "prerequisite_analysis": {
      "courses_with_prereq": [...],
      "missing_prerequisites": [],
      "completed_prerequisites": ["IFQ555", "IFQ556"]
    }
  }
}
```

### 添加前置课程后（方案B：含缺失节点）

```json
{
  "entities": [
    {
      "id": "course_ifn619",
      "name": "IFN619 Data Analytics",
      "entity_type": "COURSE"
    },
    {
      "id": "course_ifq555",
      "name": "IFQ555",
      "entity_type": "COURSE",
      "properties": {
        "status": "prerequisite_not_completed",
        "is_missing": true
      }
    }
  ],
  "relationships": [
    {
      "source_id": "course_ifq555",
      "target_id": "course_ifn619",
      "relation_type": "PREREQUISITE_FOR",
      "weight": 1.0,
      "properties": {
        "description": "IFQ555 is a prerequisite for IFN619",
        "missing": true
      }
    }
  ]
}
```

---

## 🎨 可视化影响

### 当前可视化

```
Student (青色)
  └─→ IFN619 (紫色)
        └─→ Data Analytics (蓝色技能)
```

### 添加前置课程后

```
Student (青色)
  ├─→ IFQ555 (紫色)
  │     └─→ Statistics (蓝色技能)
  │
  ├─→ IFQ556 (紫色)
  │     └─→ Programming (蓝色技能)
  │
  └─→ IFN619 (紫色)
        ├─── IFQ555 (前置，虚线箭头)
        ├─── IFQ556 (前置，虚线箭头)
        └─→ Data Analytics (蓝色技能)
```

**新增关系类型**:
- `PREREQUISITE_FOR`: 课程 → 课程（前置关系）
- 可用不同颜色/样式的边区分

---

## 📝 建议

### ✅ 推荐做法

1. **先组织**: 使用 `organize_student_kg_by_project.py` 按项目分类
2. **再分析**: 运行 `--analyze-only` 了解前置课程情况
3. **选择性添加**: 使用方案A（仅关系），避免图谱过于复杂

### ⚠️ 注意事项

1. **IN20数据缺失**: 当前从IN20提取到0个前置课程
   - 建议检查 `data/processed/units_md/qut_IN20_39851_int_cms_unit.md` 格式
   - 可能需要改进 `_extract_unit_prerequisites()` 方法

2. **缺失课程含义**: 大量缺失的前置课程（如IFQ555）可能是合理的
   - 学生可能已在本科完成
   - 或通过其他途径豁免
   - 不一定需要添加到图谱中

3. **可视化复杂度**: 添加前置课程会增加图谱复杂度
   - 考虑只在JSON中保留，不在PNG中显示
   - 或使用可交互的网页版图谱

---

## 📚 相关文件

### 脚本

- ✅ `organize_student_kg_by_project.py` - 按项目分类学生KG
- ✅ `add_prerequisites_to_student_kg.py` - 添加前置课程信息

### 数据源

- `data/processed/profiles_md/` - 学生档案（按项目分组）
- `data/processed/units_md/qut_IN20_39851_int_cms_unit.md` - IN20课程手册
- `data/processed/units_md/qut_IN27_44569.md` - IN27课程手册

### 输出

- `outputs/knowledge_graphs/individual/enhanced_student_kg/` - 原始学生KG
- `outputs/knowledge_graphs/individual/by_project/` - 按项目分类的学生KG
- `*_with_prereq.json` - 添加前置课程后的KG

---

## 🚀 快速开始

### 最简单的方案

```bash
cd /Users/lynn/Documents/GitHub/ProjectMatching

# 1. 按项目分类
python organize_student_kg_by_project.py

# 2. 仅分析前置课程情况（不修改文件）
python add_prerequisites_to_student_kg.py --analyze-only

# 3. 如果需要，添加前置课程关系（推荐）
python add_prerequisites_to_student_kg.py
```

### 完整流程

```bash
# 1. 组织文件
python organize_student_kg_by_project.py

# 2. 分析
python add_prerequisites_to_student_kg.py --analyze-only

# 3. 为每个项目单独处理
for project_dir in outputs/knowledge_graphs/individual/by_project/*/; do
    echo "处理: $project_dir"
    python add_prerequisites_to_student_kg.py --kg-dir "$project_dir"
done
```

---

**创建日期**: 2025-10-02  
**状态**: ✅ 已实现并测试  
**建议**: 使用方案A（仅添加关系），避免图谱过于复杂




