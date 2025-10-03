# IFN712 Project Proposal Template_2025_CS -3 知识图谱生成报告

生成日期: 2025年10月3日

---

## 📋 项目信息

**项目名称**: Deep Learning-based Explainable Malicious Package Detection System for Next-Gen Software Supply Chain

**项目文件**: `data/processed/projects_md/IFN712 Project Proposal Template_2025_CS -3.md`

**导师团队**:
- Prof. Raja Jurdak (r.jurdak@qut.edu.au)
- Dr. Gowri Ramachandran (g.ramachandran@qut.edu.au)
- Dr. Chadni Islam (c.islam@ecu.edu.au)

**适合专业**: Cybersecurity, Software Engineering, Computer Science, Data Science

**需要学生**: 5人

**项目类型**: HDR研究项目（需要签署IP协议）

---

## ✅ 生成的知识图谱类型

### 1️⃣ 项目基本知识图谱 (Project Description KG)

**状态**: ✅ 已存在

**位置**: `outputs/knowledge_graphs/individual/individual_kg/projects/`

**文件**:
- `project_IFN712_Project_Proposal_Template_2025_CS_-3__entities.json`
- `project_IFN712_Project_Proposal_Template_2025_CS_-3__relationships.json`
- `project_IFN712_Project_Proposal_Template_2025_CS_-3__stats.json`
- `project_IFN712_Project_Proposal_Template_2025_CS_-3__kg.png`

**统计数据**:
- **实体数**: 8
- **关系数**: 7
- **实体类型**: 
  - PROJECT: 1
  - SKILL: 6
  - TECHNOLOGY: 1

**说明**: 这是从项目描述文档中提取的基本知识图谱，包含项目所需的核心技能和技术。

---

### 2️⃣ 增强知识图谱 (Project + IN20 + IN27)

**状态**: ✅ 已存在

**位置**: `outputs/knowledge_graphs/enhanced_in20_in27/IFN712 Project Proposal Template_2025_CS -3/`

**文件**:
- `IFN712 Project Proposal Template_2025_CS -3_enhanced_kg.json` (63 KB)
- `IFN712 Project Proposal Template_2025_CS -3_enhanced_kg_full.png` (3.1 MB) - 完整版可视化
- `IFN712 Project Proposal Template_2025_CS -3_enhanced_kg_simple.png` (514 KB) - 简化版可视化

**统计数据**:
- **节点数**: 117
- **边数**: 194
- **数据源**: PD (Project Description) + IN20 (Computer Science课程) + IN27 (Data Analytics课程)

**节点类型分布**:
- PROJECT: 1个
- SKILL: 8个（包括双重支持、IN20支持、IN27支持和PD扩展的技能）
- UNIT: 108个（课程单元）

**特色**:
- ✨ 融合了项目需求与QUT课程大纲
- 🎨 彩色编码区分技能来源（IN20/IN27/双重支持/仅PD）
- 📊 完整的课程单元映射

---

### 3️⃣ 学生档案 (Student Profiles)

**状态**: ✅ 已生成 10个

**位置**: `enhanced_profile_md/`

**背景分布**:
- **IN20背景** (Computer Science): 5个学生
- **IN27背景** (Data Analytics): 5个学生

**学生列表**:

#### IN20背景学生 (Computer Science)
1. Finley Flores (n335f2be5)
2. Rory Johnson (nfd66da84)
3. Peyton Hill (nba9e3de4)
4. Emery Taylor (n72f28e37)
5. Cameron Hernandez (nb065aafc)

#### IN27背景学生 (Data Analytics)
6. Taylor Harris (n825574e8)
7. Tyler Johnson (nff065a74)
8. Finley Wilson (n1370d1a5)
9. Rory Moore (n5dd13e45)
10. Drew Wilson (n8ab07320)

**档案内容**:
每个学生档案包含：
- 基本信息（姓名、学号、专业、年级、课程背景）
- 学术背景描述（150-200字）
- 已修课程列表（6-8门课程）
- 项目经历（3个项目，每个约50字）
- 工作经验（100字以内）
- 研究兴趣（5-7项）
- 技术技能（8-10项）

---

### 4️⃣ 学生知识图谱 (Student KGs)

**状态**: ✅ 已生成 10个

**位置**: `outputs/knowledge_graphs/enhanced_student_kg/IFN712 Project Proposal Template_2025_CS -3/`

**文件统计**:
- JSON文件: 10个（每个约14 KB）
- PNG可视化: 10个（每个约1.3-1.4 MB）

**每个学生的KG统计**:

| 学生姓名 | 学号 | 背景 | 实体数 | 关系数 | 课程数 | 技能数 | 项目数 |
|---------|------|------|--------|--------|--------|--------|--------|
| Finley Flores | n335f2be5 | IN20 | 30 | 39 | 6 | 14 | 3 |
| Rory Johnson | nfd66da84 | IN20 | 32 | 40 | 6 | 16 | 3 |
| Peyton Hill | nba9e3de4 | IN20 | 29 | 37 | 6 | 13 | 3 |
| Emery Taylor | n72f28e37 | IN20 | 31 | 38 | 6 | 15 | 3 |
| Cameron Hernandez | nb065aafc | IN20 | 31 | 40 | 6 | 15 | 3 |
| Taylor Harris | n825574e8 | IN27 | 30 | 40 | 7 | 13 | 3 |
| Tyler Johnson | nff065a74 | IN27 | 31 | 40 | 7 | 14 | 3 |
| Finley Wilson | n1370d1a5 | IN27 | 30 | 38 | 7 | 13 | 3 |
| Rory Moore | n5dd13e45 | IN27 | 31 | 40 | 7 | 14 | 3 |
| Drew Wilson | n8ab07320 | IN27 | 30 | 38 | 7 | 13 | 3 |

**平均统计**:
- **平均实体数**: 30.5个/学生
- **平均关系数**: 39.0个/学生
- **平均课程数**: 6.5门/学生（IN20: 6门，IN27: 7门）
- **平均技能数**: 14.0个/学生
- **项目经历**: 3个/学生

**KG结构**:
每个学生KG包含以下实体类型：
- **STUDENT**: 学生节点（中心）
- **MAJOR**: 专业
- **COURSE**: 已修课程
- **SKILL**: 掌握的技能
- **PROJECT_EXPERIENCE**: 项目经历
- **WORK_EXPERIENCE**: 工作经历（可选）
- **INTEREST**: 研究兴趣

关系类型：
- `STUDIED_MAJOR`: 学生 → 专业
- `COMPLETED_COURSE`: 学生 → 课程
- `TEACHES_SKILL`: 课程 → 技能
- `PARTICIPATED_IN_PROJECT`: 学生 → 项目经历
- `REQUIRES_SKILL`: 项目经历 → 技能
- `HAS_SKILL`: 学生 → 技能
- `INTERESTED_IN`: 学生 → 研究兴趣

---

## 🎯 生成流程

### 步骤1: 生成学生档案
```bash
python3 -c "
from src.profile.enhanced_student_profile_generator import EnhancedProjectMatchingSystem
system = EnhancedProjectMatchingSystem()
system.initialize()
generated = system.generate_students_for_project(
    'data/processed/projects_md/IFN712 Project Proposal Template_2025_CS -3.md',
    num_students=10,
    model='qwen3:32b'
)
"
```

**结果**: 生成10个混合背景学生档案（5个IN20 + 5个IN27）

### 步骤2: 生成学生知识图谱
```bash
python3 -c "
from src.knowledge_graphs.enhanced_student_kg import EnhancedStudentKGBuilder
builder = EnhancedStudentKGBuilder(
    in20_data_path='outputs/knowledge_graphs/enhanced_in20_in27/IFN712 Project Proposal Template_2025_CS -3/IFN712 Project Proposal Template_2025_CS -3_enhanced_kg.json'
)
builder.create_enhanced_student_kg(student_file, output_dir)
"
```

**结果**: 为每个学生生成JSON KG和PNG可视化

---

## 📊 目录结构

```
ProjectMatching/
├── data/processed/projects_md/
│   └── IFN712 Project Proposal Template_2025_CS -3.md
│
├── enhanced_profile_md/
│   ├── IFN712 Project Proposal Template_2025_CS -3_IN20_0.md
│   ├── IFN712 Project Proposal Template_2025_CS -3_IN20_1.md
│   ├── ... (10个学生档案)
│   └── IFN712 Project Proposal Template_2025_CS -3_IN27_4.md
│
└── outputs/knowledge_graphs/
    ├── individual/individual_kg/projects/
    │   ├── project_IFN712_Project_Proposal_Template_2025_CS_-3__*.json
    │   └── project_IFN712_Project_Proposal_Template_2025_CS_-3__kg.png
    │
    ├── enhanced_in20_in27/
    │   └── IFN712 Project Proposal Template_2025_CS -3/
    │       ├── *_enhanced_kg.json
    │       ├── *_enhanced_kg_full.png
    │       └── *_enhanced_kg_simple.png
    │
    └── enhanced_student_kg/
        └── IFN712 Project Proposal Template_2025_CS -3/
            ├── student_n335f2be5_Finley_Flores_enhanced_kg.json
            ├── student_n335f2be5_Finley_Flores_kg.png
            ├── ... (20个文件：10个JSON + 10个PNG)
            └── student_n8ab07320_Drew_Wilson_kg.png
```

---

## ✨ 特色功能

### 1. 多层知识图谱
- **Layer 1**: 项目基本KG（来自项目描述）
- **Layer 2**: 增强KG（融合IN20和IN27课程信息）
- **Layer 3**: 学生KG（包含学生背景、课程、技能、项目）

### 2. 混合背景学生
- 50% IN20背景（Computer Science专业）
- 50% IN27背景（Data Analytics专业）
- 真实模拟QUT学生背景多样性

### 3. 课程-技能映射
- 自动从IN20/IN27课程大纲提取技能
- 将课程与技能关联
- 学生通过课程获得技能的完整路径

### 4. 可视化
- 彩色编码节点类型
- 层级布局
- 完整版和简化版两种可视化

---

## 🎉 总结

✅ **项目基本KG**: 已存在
✅ **增强KG (PD+IN20+IN27)**: 已存在  
✅ **学生档案**: 10个（IN20: 5，IN27: 5）
✅ **学生知识图谱**: 10个（每人包含JSON和PNG）

**IFN712 Project Proposal Template_2025_CS -3 项目的所有知识图谱已完整生成！**

---

## 📝 备注

1. 项目KG在2025年9月8日首次生成
2. 增强KG在2025年10月2日生成（包含IN20和IN27课程信息）
3. 学生档案在2025年10月3日生成（使用Ollama qwen3:32b模型）
4. 学生KG在2025年10月3日生成（基于增强KG数据）

所有生成的数据均已保存在相应目录中，可用于后续的项目-学生匹配分析。

