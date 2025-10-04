# 项目知识图谱快速参考

## 📁 新目录位置

```
outputs1/knowledge_graphs/projects_organized/
```

## 🗂️ 目录结构

```
projects_organized/
├── AI-Based_Human_Activity/
├── AI-Driven_Project-Student/
├── ... (共19个项目)
└── Zero-Day_Attack_Detection_Using/
```

## 📄 每个项目包含的文件

```
项目名称/
├── entities.json           # 实体列表（项目、领域、技能）
├── relationships.json      # 实体间的关系
├── stats.json             # 统计信息
├── kg.png                 # 知识图谱可视化
└── project.md             # 原始项目提案
```

## 🔍 快速查看项目

```bash
# 列出所有项目
ls outputs1/knowledge_graphs/projects_organized/

# 查看特定项目
cd outputs1/knowledge_graphs/projects_organized/AI-Based_Human_Activity/
ls -la

# 查看可视化
open outputs1/knowledge_graphs/projects_organized/AI-Based_Human_Activity/kg.png
```

## 💻 Python 使用示例

### 读取单个项目

```python
import json
from pathlib import Path

project_name = "AI-Based_Human_Activity"
project_dir = Path(f"outputs1/knowledge_graphs/projects_organized/{project_name}")

# 读取实体
with open(project_dir / "entities.json") as f:
    entities = json.load(f)

# 读取关系
with open(project_dir / "relationships.json") as f:
    relationships = json.load(f)

# 读取统计
with open(project_dir / "stats.json") as f:
    stats = json.load(f)

print(f"项目: {stats['project_title']}")
print(f"实体数: {stats['total_entities']}")
```

### 遍历所有项目

```python
from pathlib import Path
import json

kg_dir = Path("outputs1/knowledge_graphs/projects_organized")

for project_dir in sorted(kg_dir.iterdir()):
    if project_dir.is_dir():
        stats_file = project_dir / "stats.json"
        if stats_file.exists():
            with open(stats_file) as f:
                stats = json.load(f)
            
            print(f"{stats['project_title']}: {stats['total_entities']} entities")
```

## 📊 统计数据

- **总项目数**: 19
- **总实体数**: 207
- **总关系数**: 188
- **平均实体/项目**: 10.9
- **平均领域/项目**: 4.1
- **平均技能/项目**: 5.8

## 🏆 项目排名

### 最复杂 (Top 5)
1. IoT-Based Spectral Sensing and (14实体)
2. Feature Selection Impact on IoT (13实体)
3. VitalID: Smartphone-Based (13实体)
4. A Systematic Review of Deep (12实体)
5. Leveraging IoT for Smart City (12实体)

### 最简单 (5个)
1. AI-Based Human Activity (9实体)
2. Aligning ICT Education with (9实体)
3. Monitoring Ground Deformation in (9实体)
4. Prosody & Perception: Toward a (9实体)
5. Testing and Validating the Impact (9实体)

## 📋 完整项目列表

1. AI-Based_Human_Activity
2. AI-Driven_Project-Student
3. A_Systematic_Review_of_Deep
4. Aligning_ICT_Education_with
5. Assessing_the_IT_Skill
6. Binary_vs_Multiclass_Evaluation
7. Diabetes_Complications_Correlation_Analysis
8. Feature_Selection_Impact_on_IoT
9. IoT-Based_Spectral_Sensing_and
10. Leveraging_IoT_for_Smart_City
11. Machine_Learning-Based_Prediction
12. Monitoring_Ground_Deformation_in
13. Prosody__Perception_Toward_a
14. Smart_Intersection_Localization
15. Smartphone-Based_Real-Time_V2P
16. Testing_and_Validating_the_Impact
17. The_Power_of_Patterns_Using
18. VitalID_Smartphone-Based
19. Zero-Day_Attack_Detection_Using

## 🔧 重新运行重组

如果需要重新组织：

```bash
python3 reorganize_outputs1_kgs.py
```

## 📖 详细文档

查看完整报告: `PROJECT_KG_REORGANIZATION_SUMMARY.md`
