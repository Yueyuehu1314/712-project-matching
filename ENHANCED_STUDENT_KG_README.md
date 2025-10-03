# 增强版学生知识图谱系统

## 概述

增强版学生知识图谱(Enhanced Student Knowledge Graph)是一个多层次的知识表示系统，用于全面展示学生的学习经历、技能获取路径和研究兴趣。

## 🎯 核心改进

### 从2层到多层结构

**之前的简单版本（2层）：**
```
学生 ─→ 技能/课程/兴趣
```

**新的增强版本（多层）：**
```
学生 (中心)
├─→ 专业
├─→ 课程 ─→ 技能 (课程教授的技能)
├─→ 项目经历 ─→ 技能 (项目所需的技能)
├─→ 工作经历 ─→ 技能
├─→ 研究兴趣
└─→ 技能 (自学技能)
```

## 📊 新的节点类型

1. **STUDENT** - 学生主节点
2. **MAJOR** - 专业
3. **COURSE** - 课程（修过的单元）
4. **SKILL** - 技能
5. **PROJECT_EXPERIENCE** - 项目经历
6. **WORK_EXPERIENCE** - 工作经历
7. **INTEREST** - 研究兴趣

## 🔗 新的关系类型

1. **STUDIED_MAJOR** - 学生 → 专业
2. **COMPLETED_COURSE** - 学生 → 课程
3. **TEACHES_SKILL** - 课程 → 技能（重要！显示课程教授哪些技能）
4. **PARTICIPATED_IN_PROJECT** - 学生 → 项目经历
5. **REQUIRES_SKILL** - 项目经历 → 技能（显示项目需要哪些技能）
6. **WORKED_AT** - 学生 → 工作经历
7. **HAS_SKILL** - 学生 → 技能（可来自课程、项目或自学）
8. **INTERESTED_IN** - 学生 → 兴趣

## 💡 核心特性

### 1. 技能来源追踪

每个技能都有明确的来源标记：

- **通过课程获得** (`source: 'course'`) - 从修过的课程中学到
- **通过项目获得** (`source: 'project'`) - 从项目经验中获得
- **自学获得** (`source: 'self-taught'`) - 学生列出但未通过课程或项目获得

### 2. 课程-技能自动映射

系统从以下来源自动提取课程教授的技能：

1. **IN20/IN27数据** - 从课程单元数据中提取UNIT → SKILL映射
2. **预定义映射** - 常见QUT课程的技能映射
3. **关键词推断** - 基于课程名称的智能推断

例如：
```
IFN555 Introduction to Programming
  └─→ Programming, Problem Solving, Algorithms

IFN619 Data Analytics and Visualisation
  └─→ Data Visualization, Statistical Analysis, Data Science
```

### 3. 项目经历作为独立实体

项目经历不再只是文本，而是独立的节点，可以：
- 连接到所需技能
- 显示学生的实践经验
- 支持项目-技能匹配分析

### 4. 多维度可视化

生成的图谱包含：
- **节点大小** - 中心节点（学生）最大，课程/项目中等，技能/兴趣较小
- **颜色编码** - 不同类型节点使用不同颜色
- **边的样式** - 不同关系使用不同的线型和颜色
  - 紫色虚线：课程 → 技能
  - 红色点线：项目 → 技能
  - 绿色实线：学生 → 课程
  - 蓝色实线：学生 → 技能

## 📁 输出文件

每个学生生成以下文件：

```
outputs/knowledge_graphs/individual/enhanced_student_kg/
├── student_{id}_{name}_enhanced_kg.json     # JSON格式数据
└── student_{id}_{name}_kg.png                # 可视化图像
```

## 📈 统计数据

基于200个学生的测试：

- **平均每个学生**:
  - 40个实体
  - 60条关系
  - 8门课程
  - 25个技能
  - 多层次连接

- **总计**:
  - 7,790个实体
  - 11,297条关系

## 🚀 使用方法

### 批量生成所有学生的知识图谱

```bash
cd /Users/lynn/Documents/GitHub/ProjectMatching
python src/knowledge_graphs/enhanced_student_kg.py
```

### 在代码中使用

```python
from src.knowledge_graphs.enhanced_student_kg import EnhancedStudentKGBuilder

# 初始化（可选加载IN20/IN27数据以获得更准确的课程-技能映射）
builder = EnhancedStudentKGBuilder(
    in20_data_path="path/to/in20_data.json"
)

# 为单个学生生成知识图谱
stats = builder.create_enhanced_student_kg(
    student_file="data/processed/profiles_md/student.md",
    output_dir="outputs/knowledge_graphs/individual/enhanced_student_kg"
)

# 批量生成
results = builder.build_all_enhanced_student_kgs(
    student_dir="data/processed/profiles_md"
)
```

## 🎨 可视化示例

### Finley Thompson的知识图谱

```
            Computer Science (MAJOR)
                    ↑
                    |
              Finley Thompson (STUDENT)
               /    |    |    \
              /     |    |     \
         IFN555  IFN619  ...  Research Interests
           ↓       ↓              ↓
      Programming  Data Viz   NLP, Audio...
           ↓       ↓
    (学生通过课程获得这些技能)
```

- **41个实体**: 1学生 + 1专业 + 8课程 + 26技能 + 5兴趣
- **61条关系**: 包括课程→技能、学生→技能等

## 🔍 应用场景

### 1. 项目-学生匹配

可以比较：
- 项目需要的技能 vs 学生拥有的技能
- 技能的来源（课程学的 vs 项目做的）
- 通过课程先修关系预测学生潜力

### 2. 学习路径分析

追踪：
- 学生通过哪些课程获得了哪些技能
- 哪些技能是自学的
- 项目经验如何补充课堂学习

### 3. 课程推荐

基于：
- 学生已修课程和已获技能
- 感兴趣的研究方向
- 项目经验的技能缺口

### 4. 技能差距分析

识别：
- 学生想做的项目需要哪些技能
- 这些技能通过哪些课程可以获得
- 是否需要额外的自学或培训

## 🆚 对比：简单版 vs 增强版

| 特性 | 简单版 | 增强版 |
|------|--------|--------|
| 结构层次 | 2层 | 多层(4-5层) |
| 课程-技能连接 | ❌ 无 | ✅ 有 |
| 项目作为节点 | ❌ 无 | ✅ 有 |
| 技能来源追踪 | ❌ 无 | ✅ 有 |
| 实体数量 | ~20 | ~40 |
| 关系数量 | ~25 | ~60 |
| 可用于匹配 | 基础 | 高级 |

## 📊 数据示例

### JSON结构

```json
{
  "entities": [
    {
      "id": "student_n00114716",
      "name": "Finley Thompson",
      "entity_type": "STUDENT",
      "properties": {
        "student_id": "n00114716",
        "major": "Computer Science",
        "year": "4th Year"
      }
    },
    {
      "id": "course_ifn555_introduction_to_programming",
      "name": "IFN555 Introduction to Programming",
      "entity_type": "COURSE"
    },
    {
      "id": "skill_programming",
      "name": "Programming",
      "entity_type": "SKILL"
    }
  ],
  "relationships": [
    {
      "source_id": "student_n00114716",
      "target_id": "course_ifn555_introduction_to_programming",
      "relation_type": "COMPLETED_COURSE",
      "weight": 1.0
    },
    {
      "source_id": "course_ifn555_introduction_to_programming",
      "target_id": "skill_programming",
      "relation_type": "TEACHES_SKILL",
      "weight": 0.9
    },
    {
      "source_id": "student_n00114716",
      "target_id": "skill_programming",
      "relation_type": "HAS_SKILL",
      "weight": 0.8,
      "properties": {
        "source": "course"
      }
    }
  ]
}
```

## 🔧 技术实现

### 课程代码提取

```python
def _extract_course_code(course_name: str) -> str:
    """提取课程代码如 IFN555"""
    match = re.search(r'(IFN|CAB|IAB|ITN)\d{3}', course_name.upper())
    return match.group(0) if match else None
```

### 技能提取

```python
def _extract_skills_from_text(text: str) -> List[str]:
    """从项目描述中提取技能关键词"""
    skills = []
    text_lower = text.lower()
    
    skill_keywords = {
        'Machine Learning': ['machine learning', 'ml', 'deep learning'],
        'Python': ['python'],
        'Web Development': ['web development', 'html', 'css'],
        # ...
    }
    
    for skill, keywords in skill_keywords.items():
        if any(kw in text_lower for kw in keywords):
            skills.append(skill)
    
    return list(set(skills))
```

## 📝 下一步改进

1. **工作经历节点** - 添加工作经验及其相关技能
2. **技能权重** - 基于课程成绩或项目规模调整技能权重
3. **技能图谱** - 构建技能之间的依赖关系
4. **时间维度** - 添加时间轴，显示技能获取顺序
5. **互动可视化** - 使用Plotly创建可交互的网页版知识图谱

## 📚 相关文件

- `src/knowledge_graphs/enhanced_student_kg.py` - 增强版生成器代码
- `outputs/knowledge_graphs/individual/enhanced_student_kg/` - 输出目录
- `experiments/archive/old_generators/individual_knowledge_graphs.py` - 旧版本

## 🎉 总结

增强版学生知识图谱通过多层次结构和丰富的关系类型，提供了更全面、更细致的学生能力画像。这不仅有助于更精确的项目-学生匹配，还能支持学习路径规划、技能差距分析等多种应用场景。

---

**生成日期**: 2025-10-02  
**版本**: 2.0 Enhanced  
**状态**: ✅ 已完成并测试






