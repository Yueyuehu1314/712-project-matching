# 3层项目知识图谱说明文档

## 📋 概述

本文档说明新生成的**3层结构项目知识图谱**，相比原有的2层结构，新结构更加清晰和有层次性。

## 🏗️ 结构对比

### 原有2层结构（已弃用）
```
Layer 1: Project（项目）
   ├─> Major（专业）
   ├─> Skill（技能）
   ├─> Technology（技术）
   └─> Professor（导师）❌ 已去除
```

**问题：**
- 结构过于扁平，缺乏层次感
- 所有概念直接连接到项目，关系混乱
- Professor节点对匹配无实质帮助
- 不利于理解项目的知识领域分布

### 新3层结构（推荐）
```
Layer 1: Project（项目）
   │
   ├─> Layer 2: Domain Categories（领域分类）
   │      ├─> Machine Learning & AI
   │      ├─> Data Science & Analytics
   │      ├─> Web Development
   │      ├─> Mobile Development
   │      ├─> Cybersecurity
   │      ├─> Signal Processing
   │      ├─> Academic Programs
   │      └─> ...
   │
   └─> Layer 3: Specific Requirements（具体要求）
          ├─> Skills（技能）
          ├─> Technologies（技术）
          └─> Majors（专业要求）
```

**优势：**
✅ 清晰的3层层次结构
✅ 去除了无用的Professor节点
✅ 通过Domain分类更好地组织知识
✅ 便于理解项目的技术栈和知识领域
✅ 更利于后续的项目-学生匹配

## 📁 目录结构

生成的文件位于：`outputs/knowledge_graphs/individual/three_layer_projects/`

每个项目生成以下文件：
- `<project_name>_entities.json` - 所有实体（节点）
- `<project_name>_relationships.json` - 所有关系（边）
- `<project_name>_stats.json` - 统计信息
- `<project_name>_kg.png` - 可视化图谱
- `summary_report.json` - 总体汇总报告

## 📊 层次详解

### Layer 1: 项目层（Project）
- **数量**: 每个知识图谱1个
- **类型**: PROJECT
- **作用**: 知识图谱的根节点
- **示例**: "AI-Based Human Activity Recognition"

### Layer 2: 领域层（Domain Categories）
- **数量**: 平均3-5个/项目
- **类型**: DOMAIN
- **作用**: 将技能和技术分组到相关领域
- **关系**: `Project --REQUIRES_DOMAIN--> Domain`

**主要领域分类:**
1. **Machine Learning & AI** - 机器学习和人工智能
2. **Data Science & Analytics** - 数据科学与分析
3. **Web Development** - Web开发
4. **Mobile Development** - 移动开发
5. **Cybersecurity** - 网络安全
6. **Database Systems** - 数据库系统
7. **Networking & Communication** - 网络与通信
8. **Software Engineering** - 软件工程
9. **Cloud Computing** - 云计算
10. **Signal Processing** - 信号处理
11. **Computer Vision & Sensing** - 计算机视觉与感知
12. **GIS & Spatial Analysis** - GIS与空间分析
13. **Business & Management** - 商业与管理
14. **Hardware & Embedded Systems** - 硬件与嵌入式
15. **Programming Languages** - 编程语言
16. **Academic Programs** - 学术项目（专业要求）
17. **General Skills/Technologies** - 通用技能/技术

### Layer 3: 具体要求层（Requirements）
- **数量**: 平均4-8个/项目
- **类型**: SKILL, TECHNOLOGY, MAJOR
- **作用**: 项目的具体技术和能力要求
- **关系**: 
  - `Domain --INCLUDES--> Skill`
  - `Domain --USES_TECH--> Technology`

## 🎨 可视化说明

### 布局方式：中心放射状（Radial Layout）

采用**中心放射状布局**，使知识图谱更加直观和美观：

- **中心（原点）**: Project节点（红色大圆）
- **内圈（半径2.5）**: Domain节点（青色中圆）- 均匀分布在圆周上
- **外圈（半径5.0）**: Skill/Technology/Major节点（彩色小圆）- 按所属Domain扇形分组

### 节点颜色
- 🔴 **红色** (#FF6B6B) - Project (Layer 1)
- 🔵 **青色** (#4ECDC4) - Domain (Layer 2)
- 🟢 **浅青色** (#95E1D3) - Major (Layer 3)
- 🟠 **浅橙色** (#FFA07A) - Skill (Layer 3)
- 🟣 **浅紫色** (#DDA0DD) - Technology (Layer 3)

### 节点大小
- **大** (3000) - Project节点（中心）
- **中** (2000) - Domain节点（内圈）
- **小** (800) - Skill/Technology/Major节点（外圈）

### 布局特点
✨ **放射状分布**: 从中心向外3层同心圆
✨ **角度均匀**: Domain节点在内圈均匀分布
✨ **扇形分组**: Layer3节点按Domain归属分组在外圈
✨ **清晰易读**: 避免节点重叠，层次分明

## 📈 统计示例

以 "AI-Based Human Activity" 项目为例：

```json
{
  "total_entities": 9,
  "total_relationships": 8,
  "layer_distribution": {
    "1": 1,  // 1个项目节点
    "2": 3,  // 3个领域节点
    "3": 5   // 5个具体要求节点
  },
  "entity_types": {
    "PROJECT": 1,
    "DOMAIN": 3,
    "SKILL": 2,
    "MAJOR": 2,
    "TECHNOLOGY": 1
  }
}
```

**层次关系:**
```
AI-Based Human Activity (Project)
├─> Machine Learning & AI (Domain)
│   ├─> Deep Learning (Skill)
│   └─> R (Technology)
├─> Signal Processing (Domain)
│   └─> Signal Processing (Skill)
└─> Academic Programs (Domain)
    ├─> Software Development (Major)
    └─> Computer (Major)
```

## 🔧 使用方法

### 生成所有项目的3层知识图谱
```bash
cd /Users/lynn/Documents/GitHub/ProjectMatching
python src/knowledge_graphs/three_layer_project_kg.py
```

### 在Python代码中使用
```python
from src.knowledge_graphs.three_layer_project_kg import ThreeLayerProjectKGGenerator

generator = ThreeLayerProjectKGGenerator()
stats = generator.generate_project_kg(
    project_file="data/processed/projects_md/example.md",
    output_dir="outputs/knowledge_graphs/individual/three_layer_projects"
)
```

## 📝 实体关系说明

### 关系类型

1. **REQUIRES_DOMAIN** (weight=1.0)
   - 从: Project
   - 到: Domain
   - 含义: 项目需要某个知识领域

2. **INCLUDES** (weight=0.8)
   - 从: Domain
   - 到: Skill/Major
   - 含义: 领域包含某个技能或专业

3. **USES_TECH** (weight=0.9)
   - 从: Domain
   - 到: Technology
   - 含义: 领域使用某项技术

## 🎯 与原有KG的比较

| 特性 | 2层结构 | 3层结构 |
|------|---------|---------|
| 层次深度 | 2层 | 3层 |
| 平均节点数 | 8-10 | 9-14 |
| 平均关系数 | 7-9 | 8-13 |
| Professor节点 | ✅ 包含 | ❌ 已移除 |
| Domain分类 | ❌ 无 | ✅ 有 |
| 结构清晰度 | 中 | 高 |
| 匹配友好度 | 中 | 高 |

## 🚀 后续应用

这个3层结构的知识图谱可以用于：

1. **项目-学生匹配算法**
   - 通过Domain层进行粗粒度匹配
   - 通过Skill/Tech层进行细粒度匹配

2. **技能gap分析**
   - 识别学生缺少的Domain知识
   - 推荐相关的课程或学习资源

3. **项目聚类分析**
   - 基于Domain分布对项目分类
   - 发现相似项目

4. **可视化展示**
   - 清晰展示项目的知识结构
   - 帮助学生理解项目要求

## 📊 全局统计

- **总项目数**: 20个
- **平均实体数**: 10.6个/项目
- **平均关系数**: 9.6个/项目
- **平均Domain数**: 4.0个/项目
- **平均Layer3节点数**: 5.6个/项目

## 🔍 示例查看

查看具体项目的知识图谱：
```bash
# 查看实体
cat outputs/knowledge_graphs/individual/three_layer_projects/AI-Based_Human_Activity_entities.json

# 查看关系
cat outputs/knowledge_graphs/individual/three_layer_projects/AI-Based_Human_Activity_relationships.json

# 查看可视化
open outputs/knowledge_graphs/individual/three_layer_projects/AI-Based_Human_Activity_kg.png
```

## 📮 反馈与改进

如需调整Domain分类或添加新的领域，请修改：
`src/knowledge_graphs/three_layer_project_kg.py` 中的 `skill_to_domain` 和 `tech_to_domain` 映射字典。

---

**生成时间**: 2025-10-03
**版本**: 1.0
**状态**: ✅ 已完成并测试

