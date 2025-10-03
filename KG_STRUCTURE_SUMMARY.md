# 知识图谱结构说明

## 📊 完整四层结构

```
PROJECT (项目) → SKILL (技能) → UNIT (课程单元) → PROGRAM (学位项目)
```

## 🎨 可视化布局

### 层级布局（从左到右）

```
第1层         第2层              第3层                第4层
(x=0)         (x=4)              (x=8)               (x=12)

[PROJECT] ──→ [SKILL 1] ──────→ [UNIT 1] ──────────→ [PROGRAM 1]
              [SKILL 2] ──────→ [UNIT 2] ──────────→ [PROGRAM 2]
              [SKILL 3] ──────→ [UNIT 3] ──────────→ [PROGRAM 1]
              [SKILL 4] ──────→ [UNIT 4] ──────────→ [PROGRAM 3]
              ...               ...                  ...
```

## 🔗 关系类型

1. **PROJECT → SKILL**: `REQUIRES_SKILL`
   - 项目需要哪些技能

2. **SKILL → UNIT**: `TAUGHT_IN`
   - 技能在哪些课程单元中被教授
   - 来源：IN20课程手册 + IN27硕士大纲

3. **UNIT → PROGRAM**: `BELONGS_TO`
   - 课程单元属于哪个学位项目
   - 例如：Master of IT, Bachelor of Engineering

## 🎨 节点颜色编码

| 节点类型 | 颜色 | 含义 |
|---------|------|------|
| PROJECT | 🔴 `#FF6B6B` | 项目 |
| SKILL (双重支持) | 🟢 `#26de81` | IN20+IN27都支持 |
| SKILL (IN20) | 🔵 `#4ECDC4` | 仅IN20支持 |
| SKILL (IN27) | 🟣 `#9b59b6` | 仅IN27支持 |
| SKILL (PD扩展) | 🟠 `#FFB347` | 仅项目描述提及 |
| UNIT | 🟡 `#FFD93D` | 课程单元 |
| PROGRAM | 🟣 `#A569BD` | 学位项目 |

## 📊 统计数据

- **项目数量**: 20个
- **平均节点数**: 128-130个/项目
- **平均技能数**: 7-9个/项目
- **平均UNIT数**: 100-120个/项目
- **平均PROGRAM数**: 2-3个/项目

## 📁 输出文件

每个项目生成3个文件：

1. **JSON数据**: `*_enhanced_kg.json`
   - 完整的节点和边数据

2. **完整版图谱**: `*_enhanced_kg_full.png` ⭐
   - 显示全部四层结构
   - 包含所有UNIT和PROGRAM

3. **简化版图谱**: `*_enhanced_kg_simple.png`
   - 只显示PROJECT和SKILL
   - 圆环布局，更清晰

## 🎯 应用场景

### 1. 项目-学生匹配
- 查看项目需要哪些技能
- 匹配学生已有技能
- 识别技能差距

### 2. 课程推荐
- 为项目推荐相关课程
- 展示哪些UNIT教授所需技能
- 推荐合适的PROGRAM

### 3. 学位对比
- 对比不同学位对项目的支持程度
- Master vs Bachelor的课程覆盖

### 4. 技能映射
- 某个技能在哪些课程中被教授
- 技能的多课程覆盖情况

## 🔧 生成器

- **脚本**: `src/knowledge_graphs/balanced_kg_generator_in20_in27.py`
- **版本**: v3.0
- **数据源**: 
  - PD: Project Descriptions
  - IN20: Course Information (2020)
  - IN27: Master Program Syllabus (2027)

## 📍 输出目录

```
outputs/knowledge_graphs/enhanced_in20_in27/
├── AI-Based Human Activity Recognition.../
├── Feature Selection Impact on IoT.../
├── Leveraging IoT for Smart City.../
└── ...
```
