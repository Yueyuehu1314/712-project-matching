# CS -3 项目快速参考

## 🎯 项目标识

**项目文件名**: `IFN712 Project Proposal Template_2025_CS -3`  
**项目标题**: Deep Learning-based Explainable Malicious Package Detection System for Next-Gen Software Supply Chain

---

## 📁 文件位置快速查找

### 原始项目文档
```
data/processed/projects_md/IFN712 Project Proposal Template_2025_CS -3.md
```

### 项目基本KG
```
outputs/knowledge_graphs/individual/individual_kg/projects/project_IFN712_Project_Proposal_Template_2025_CS_-3__*.json
```

### 项目增强KG (含IN20+IN27)
```
outputs/knowledge_graphs/enhanced_in20_in27/IFN712 Project Proposal Template_2025_CS -3/
├── IFN712 Project Proposal Template_2025_CS -3_enhanced_kg.json
├── IFN712 Project Proposal Template_2025_CS -3_enhanced_kg_full.png
└── IFN712 Project Proposal Template_2025_CS -3_enhanced_kg_simple.png
```

### 学生档案 (10个)
```
enhanced_profile_md/IFN712 Project Proposal Template_2025_CS -3_*.md
```

### 学生知识图谱 (10个)
```
outputs/knowledge_graphs/enhanced_student_kg/IFN712 Project Proposal Template_2025_CS -3/
├── student_*_enhanced_kg.json (10个) - 基础KG
├── student_*_kg.png (10个) - 基础可视化
├── student_*_with_prereq.json (10个) ✨ - 含先修课程的KG
└── student_*_with_prereq_visualization.png (10个) ✨ - 含先修课程的可视化
```

---

## 👥 学生列表

### IN20背景 (Computer Science) - 5人

1. **Finley Flores** (n335f2be5)
   - 30实体, 39关系, 14技能

2. **Rory Johnson** (nfd66da84)
   - 32实体, 40关系, 16技能

3. **Peyton Hill** (nba9e3de4)
   - 29实体, 37关系, 13技能

4. **Emery Taylor** (n72f28e37)
   - 31实体, 38关系, 15技能

5. **Cameron Hernandez** (nb065aafc)
   - 31实体, 40关系, 15技能

### IN27背景 (Data Analytics) - 5人

6. **Taylor Harris** (n825574e8)
   - 30实体, 40关系, 13技能

7. **Tyler Johnson** (nff065a74)
   - 31实体, 40关系, 14技能

8. **Finley Wilson** (n1370d1a5)
   - 30实体, 38关系, 13技能

9. **Rory Moore** (n5dd13e45)
   - 31实体, 40关系, 14技能

10. **Drew Wilson** (n8ab07320)
    - 30实体, 38关系, 13技能

---

## 📊 统计摘要

| 类型 | 数量 | 备注 |
|------|------|------|
| 项目基本KG节点 | 8 | PROJECT, SKILL, TECHNOLOGY |
| 增强KG节点 | 117 | 包含108个课程单元 |
| 增强KG边 | 194 | - |
| 学生档案 | 10 | IN20:5, IN27:5 |
| 学生基础KG | 10 | JSON + PNG |
| 学生先修KG ✨ | 10 | JSON + PNG (含先修课程) |
| 学生KG (平均) | 30.5实体 | 每个学生 |
| 学生关系 (平均) | 39.0关系 | 每个学生 |

---

## 🔍 如何使用这些数据

### 查看项目增强KG
```bash
# JSON数据
cat "outputs/knowledge_graphs/enhanced_in20_in27/IFN712 Project Proposal Template_2025_CS -3/IFN712 Project Proposal Template_2025_CS -3_enhanced_kg.json" | python3 -m json.tool | less

# 可视化（在Finder中打开）
open "outputs/knowledge_graphs/enhanced_in20_in27/IFN712 Project Proposal Template_2025_CS -3/IFN712 Project Proposal Template_2025_CS -3_enhanced_kg_full.png"
```

### 查看学生档案
```bash
# 查看第一个IN20学生
cat "enhanced_profile_md/IFN712 Project Proposal Template_2025_CS -3_IN20_0.md"

# 查看第一个IN27学生
cat "enhanced_profile_md/IFN712 Project Proposal Template_2025_CS -3_IN27_0.md"
```

### 查看学生KG
```bash
# 基础KG JSON数据
cat "outputs/knowledge_graphs/enhanced_student_kg/IFN712 Project Proposal Template_2025_CS -3/student_n335f2be5_Finley_Flores_enhanced_kg.json" | python3 -m json.tool | less

# 含先修课程的KG JSON数据 ✨
cat "outputs/knowledge_graphs/enhanced_student_kg/IFN712 Project Proposal Template_2025_CS -3/student_n335f2be5_Finley_Flores_with_prereq.json" | python3 -m json.tool | less

# 基础可视化
open "outputs/knowledge_graphs/enhanced_student_kg/IFN712 Project Proposal Template_2025_CS -3/student_n335f2be5_Finley_Flores_kg.png"

# 含先修课程的可视化 ✨
open "outputs/knowledge_graphs/enhanced_student_kg/IFN712 Project Proposal Template_2025_CS -3/student_n335f2be5_Finley_Flores_with_prereq_visualization.png"
```

### 批量查看所有学生KG可视化
```bash
cd "outputs/knowledge_graphs/enhanced_student_kg/IFN712 Project Proposal Template_2025_CS -3"

# 查看基础KG
open *_kg.png

# 查看含先修课程的KG ✨
open *_with_prereq_visualization.png
```

---

## 🛠️ 重新生成（如需要）

### 重新生成学生档案
```bash
cd /Users/lynn/Documents/GitHub/ProjectMatching

python3 << 'EOF'
from src.profile.enhanced_student_profile_generator import EnhancedProjectMatchingSystem
system = EnhancedProjectMatchingSystem()
system.initialize()
system.generate_students_for_project(
    'data/processed/projects_md/IFN712 Project Proposal Template_2025_CS -3.md',
    num_students=10,
    model='qwen3:32b'
)
EOF
```

### 重新生成学生基础KG
```bash
cd /Users/lynn/Documents/GitHub/ProjectMatching

python3 << 'EOF'
from src.knowledge_graphs.enhanced_student_kg import EnhancedStudentKGBuilder
import glob
import os

in20_27_path = 'outputs/knowledge_graphs/enhanced_in20_in27/IFN712 Project Proposal Template_2025_CS -3/IFN712 Project Proposal Template_2025_CS -3_enhanced_kg.json'
builder = EnhancedStudentKGBuilder(in20_data_path=in20_27_path)

student_files = sorted(glob.glob('enhanced_profile_md/IFN712 Project Proposal Template_2025_CS -3_*.md'))
output_dir = 'outputs/knowledge_graphs/enhanced_student_kg/IFN712 Project Proposal Template_2025_CS -3'

for student_file in student_files:
    builder.create_enhanced_student_kg(student_file, output_dir)
EOF
```

### 添加先修课程关系 ✨
```bash
cd /Users/lynn/Documents/GitHub/ProjectMatching

# 添加先修课程关系
python3 add_prerequisites_to_student_kg.py --kg-dir "outputs/knowledge_graphs/enhanced_student_kg/IFN712 Project Proposal Template_2025_CS -3"

# 生成可视化
python3 visualize_student_kg_with_prereq.py --kg-dir "outputs/knowledge_graphs/enhanced_student_kg/IFN712 Project Proposal Template_2025_CS -3"
```

---

## ✅ 完整性检查清单

- [x] 项目基本KG存在
- [x] 项目增强KG (PD+IN20+IN27) 存在
- [x] 10个学生档案已生成 (5个IN20 + 5个IN27)
- [x] 10个学生基础KG JSON文件已生成
- [x] 10个学生基础KG PNG可视化已生成
- [x] 10个学生先修KG JSON文件已生成 ✨
- [x] 10个学生先修KG PNG可视化已生成 ✨
- [x] 所有文件位于正确的目录
- [x] 文件大小正常（基础JSON ~14KB, 先修JSON ~14.5KB, 基础PNG ~1.3MB, 先修PNG ~1.65MB）

---

## 📞 项目联系信息

**学术导师**:
- Prof. Raja Jurdak: r.jurdak@qut.edu.au
- Dr. Gowri Ramachandran: g.ramachandran@qut.edu.au
- Dr. Chadni Islam: c.islam@ecu.edu.au

**项目类型**: HDR研究项目  
**IP协议**: 需要学生签署（IP归项目所有者）  
**需要学生数**: 5人  
**适合专业**: Cybersecurity, Software Engineering, Computer Science, Data Science

---

**生成日期**: 2025年10月3日  
**报告文件**: `CS-3_PROJECT_KG_GENERATION_REPORT.md`

