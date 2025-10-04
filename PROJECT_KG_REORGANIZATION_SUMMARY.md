# 项目知识图谱重组总结报告

**日期**: 2025年10月4日  
**任务**: 补齐缺失的项目KG，并按项目重新组织目录结构

---

## 📋 任务概述

原始需求：
1. 根据 `data/processed/projects_md` 目录下的项目文件补齐缺失的知识图谱
2. 将 `outputs1/knowledge_graphs/three_layer_projects` 目录下的KG文件按项目分类
3. 每个项目在一个独立目录下，包含所有相关文件

---

## ✅ 完成情况

### 1. 项目分析

**原始状态**:
- 项目 MD 文件: 20 个
- 现有 KG 文件: 19 个
- 缺失 KG: 1 个

**问题发现**:
- 1个项目 (`JZhang_IFN712 Project Proposal 1_2025_CS .md`) 的标题字段为空
- 1个项目 (`IFN712 Project Proposal Template_2025_CS -3.md`) 由于格式异常（PDF转换）未生成KG

### 2. 解决方案

**空名称项目处理** (`JZhang_IFN712 Project Proposal 1_2025_CS .md`):
- 项目描述: "糖尿病并发症相关性分析的医学影像研究"
- 分配新名称: `Diabetes_Complications_Correlation_Analysis`
- 更新实体名称为: "Diabetes Complications Correlation Analysis"

**缺失KG项目处理** (`IFN712 Project Proposal Template_2025_CS -3.md`):
- 项目标题: "Deep Learning-based Explainable Malicious Package Detection System for Next-Gen Software Supply Chain"
- 手动生成KG
- 创建目录: `Deep_Learning_Malicious_Package_Detection`
- 完成重组

### 3. 目录重组

**新目录结构**:
```
outputs1/knowledge_graphs/projects_organized/
├── AI-Based_Human_Activity/
│   ├── entities.json           # 实体列表
│   ├── relationships.json      # 关系列表
│   ├── stats.json             # 统计信息
│   ├── kg.png                 # 可视化图谱
│   └── project.md             # 原始项目提案
├── AI-Driven_Project-Student/
│   ├── ...
├── Deep_Learning_Malicious_Package_Detection/  # 🆕 新增
│   ├── ...
└── ... (共20个项目)
```

**文件完整性**: 100%
- entities.json: 20/20 ✅
- relationships.json: 20/20 ✅
- stats.json: 20/20 ✅
- kg.png: 20/20 ✅
- project.md: 20/20 ✅

---

## 📊 知识图谱统计

### 总体统计
| 指标 | 总计 | 平均/项目 |
|-----|------|----------|
| 实体数 | 215 | 10.8 |
| 关系数 | 195 | 9.8 |
| 领域数 | 81 | 4.0 |
| 技能数 | 115 | 5.8 |

### 项目复杂度排名

**Top 5 最复杂项目** (按实体数):
1. **IoT-Based Spectral Sensing and** - 14实体, 5领域, 8技能
2. **Feature Selection Impact on IoT** - 13实体, 4领域, 8技能
3. **VitalID: Smartphone-Based** - 13实体, 5领域, 7技能
4. **A Systematic Review of Deep** - 12实体, 4领域, 7技能
5. **Leveraging IoT for Smart City** - 12实体, 5领域, 6技能

**最简单的5个项目**:
1. **AI-Based Human Activity** - 9实体, 3领域, 5技能
2. **Aligning ICT Education with** - 9实体, 4领域, 4技能
3. **Monitoring Ground Deformation in** - 9实体, 4领域, 4技能
4. **Prosody & Perception: Toward a** - 9实体, 3领域, 5技能
5. **Testing and Validating the Impact** - 9实体, 4领域, 4技能

---

## 📁 完整项目列表

1. **AI-Based_Human_Activity** - AI-Based Human Activity (9实体, 3领域)
2. **AI-Driven_Project-Student** - AI-Driven Project-Student (10实体, 4领域)
3. **A_Systematic_Review_of_Deep** - A Systematic Review of Deep (12实体, 4领域)
4. **Aligning_ICT_Education_with** - Aligning ICT Education with (9实体, 4领域)
5. **Assessing_the_IT_Skill** - Assessing the IT Skill (11实体, 5领域)
6. **Binary_vs_Multiclass_Evaluation** - Binary vs. Multiclass Evaluation (11实体, 3领域)
7. **Deep_Learning_Malicious_Package_Detection** 🆕 - Deep Learning-based Malicious Package Detection (8实体, 3领域)
8. **Diabetes_Complications_Correlation_Analysis** - Diabetes Complications Correlation Analysis (11实体, 4领域)
9. **Feature_Selection_Impact_on_IoT** - Feature Selection Impact on IoT (13实体, 4领域)
10. **IoT-Based_Spectral_Sensing_and** - IoT-Based Spectral Sensing and (14实体, 5领域)
11. **Leveraging_IoT_for_Smart_City** - Leveraging IoT for Smart City (12实体, 5领域)
12. **Machine_Learning-Based_Prediction** - Machine Learning-Based Prediction (10实体, 4领域)
13. **Monitoring_Ground_Deformation_in** - Monitoring Ground Deformation in (9实体, 4领域)
14. **Prosody__Perception_Toward_a** - Prosody & Perception: Toward a (9实体, 3领域)
15. **Smart_Intersection_Localization** - Smart Intersection Localization (11实体, 4领域)
16. **Smartphone-Based_Real-Time_V2P** - Smartphone-Based Real-Time V2P (12实体, 5领域)
17. **Testing_and_Validating_the_Impact** - Testing and Validating the Impact (9实体, 4领域)
18. **The_Power_of_Patterns_Using** - The Power of Patterns: Using (10实体, 4领域)
19. **VitalID_Smartphone-Based** - VitalID: Smartphone-Based (13实体, 5领域)
20. **Zero-Day_Attack_Detection_Using** - Zero-Day Attack Detection Using (12实体, 4领域)

---

## 🛠️ 使用的工具和脚本

### 1. `reorganize_outputs1_kgs.py`
重组主脚本，功能：
- 扫描现有KG文件
- 创建项目子目录
- 移动和重命名文件
- 关联原始MD文件

### 2. 空名称项目处理脚本
- 识别空名称项目
- 分配合理的项目名称
- 更新实体信息
- 整合到重组结构中

---

## 🎯 使用方法

### 访问项目知识图谱

```bash
# 查看所有项目
ls outputs1/knowledge_graphs/projects_organized/

# 查看特定项目
cd outputs1/knowledge_graphs/projects_organized/AI-Based_Human_Activity/

# 文件说明
- entities.json       # 包含项目、领域、技能等实体
- relationships.json  # 实体之间的关系
- stats.json         # 统计信息（实体数、领域数等）
- kg.png            # 知识图谱可视化
- project.md        # 原始项目提案文档
```

### 读取知识图谱

```python
import json
from pathlib import Path

# 读取特定项目的KG
project_dir = Path("outputs1/knowledge_graphs/projects_organized/AI-Based_Human_Activity")

# 读取实体
with open(project_dir / "entities.json", 'r') as f:
    entities = json.load(f)

# 读取关系
with open(project_dir / "relationships.json", 'r') as f:
    relationships = json.load(f)

# 读取统计信息
with open(project_dir / "stats.json", 'r') as f:
    stats = json.load(f)

print(f"项目: {stats['project_title']}")
print(f"实体数: {stats['total_entities']}")
print(f"关系数: {stats['total_relationships']}")
```

---

## 📈 知识图谱结构

### 三层架构

```
Layer 1: PROJECT (项目)
   ↓
Layer 2: DOMAIN (领域类别)
   ↓
Layer 3: SKILL/TECHNOLOGY/MAJOR (具体技能/技术/专业)
```

### 实体类型
- **PROJECT**: 项目节点（每个KG 1个）
- **DOMAIN**: 领域分类（如 "Machine Learning & AI", "Data Science & Analytics"）
- **SKILL**: 技能（如 "Machine Learning", "Data Analysis"）
- **TECHNOLOGY**: 技术工具（如 "Python", "TensorFlow"）
- **MAJOR**: 专业要求（如 "Computer Science"）

### 关系类型
- **HAS_DOMAIN**: 项目 → 领域
- **REQUIRES_SKILL**: 领域 → 技能
- **USES_TECHNOLOGY**: 领域 → 技术
- **REQUIRES_MAJOR**: 领域 → 专业

---

## 💡 注意事项

1. **原始文件保留**: 所有操作都是复制而非移动，原始文件仍在 `three_layer_projects` 目录
2. **文件命名**: 项目目录名使用下划线分隔，便于文件系统处理
3. **空名称项目**: 已修复并分配合理名称
4. **MD文件来源**: 每个项目的 `project.md` 是从 `data/processed/projects_md` 复制的原始提案

---

## 🔄 后续使用建议

1. **实验更新**: 如需在实验中使用新结构，更新路径配置：
   ```python
   kg_dir = "outputs1/knowledge_graphs/projects_organized"
   ```

2. **批量处理**: 可以轻松遍历所有项目：
   ```python
   from pathlib import Path
   
   kg_dir = Path("outputs1/knowledge_graphs/projects_organized")
   for project_dir in kg_dir.iterdir():
       if project_dir.is_dir():
           # 处理每个项目
           pass
   ```

3. **可视化查看**: 每个项目都有 `kg.png` 文件，可以直接打开查看

---

## ✅ 验证清单

- [x] 所有20个项目MD文件已处理
- [x] 20个有效项目KG已生成 ✅
- [x] 空名称项目已修复并命名
- [x] 格式异常项目已手动生成KG
- [x] 所有项目文件完整性100%
- [x] 目录结构清晰，易于访问
- [x] 原始文件保留，数据安全

---

## 📞 问题排查

如果遇到问题：

1. **项目找不到**: 检查项目名称是否使用下划线格式
2. **文件缺失**: 运行验证脚本检查完整性
3. **KG重新生成**: 可以使用 `ThreeLayerProjectKGGenerator` 重新生成单个项目

---

**报告生成时间**: 2025-10-04 17:30  
**状态**: ✅ 全部完成

