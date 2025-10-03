# 增强知识图谱生成器 (PD + IN20 + IN27)

## 📋 概述

`balanced_kg_generator_in20_in27.py` 是一个融合了 **Project Description (PD)**、**IN20 Course** 和 **IN27 Master Program** 的增强知识图谱生成器。

## 🎯 核心功能

### 1. 融合三种数据源
- **PD (Project Description)**: 项目描述中提取的技能需求
- **IN20 (Course Unit)**: 课程大纲中的技能支持
- **IN27 (Master of Data Analytics)**: 硕士项目中的课程和技能

### 2. 技能分类

| 类别 | 说明 | 颜色标识 | 符号 |
|------|------|----------|------|
| **双重支持** | 同时被 IN20 和 IN27 支持 | 🟢 鲜绿色 | ✓✓ |
| **IN20支持** | 仅被 IN20 支持 | 🔵 天蓝色 | ✓ |
| **IN27支持** | 仅被 IN27 支持 | 🟣 紫色 | ✓ |
| **PD扩展** | 项目独特需求，课程未覆盖 | 🟠 橙色 | + |

### 3. 权重机制

```python
# 技能权重计算
if IN20支持 and IN27支持:
    score = base_score * 1.3  # 双重支持加权
elif IN20支持 or IN27支持:
    score = base_score * 1.0  # 单一支持
else:
    score = base_score * 0.8  # 扩展技能
```

### 4. 边的权重显示

- 实线粗线 (width=4): 双重支持关系
- 实线中线 (width=3): IN20支持关系  
- 虚线细线 (width=2.5): PD扩展需求

边上标注数值为权重分数 (0.5-1.0)

## 📊 输出文件

为每个项目生成 3 个文件：

1. **`{project}_enhanced_kg.json`**
   - 完整的知识图谱数据（JSON格式）
   - 包含所有节点、边和元数据

2. **`{project}_enhanced_kg_full.png`**
   - 完整可视化
   - 包含 PROJECT、SKILL、UNIT、PROGRAM 所有节点

3. **`{project}_enhanced_kg_simple.png`** ⭐ **推荐**
   - 简化可视化
   - 只显示项目和技能节点
   - 径向布局，项目在中心，技能围绕分布
   - 类似于你提供的 Python 课程知识图谱风格

## 🚀 使用方法

### 方法 1: 测试单个项目

```bash
cd /Users/lynn/Documents/GitHub/ProjectMatching
python3 test_in20_in27_generator.py
```

### 方法 2: 在代码中使用

```python
from src.knowledge_graphs.balanced_kg_generator_in20_in27 import BalancedKGGeneratorIN20IN27

generator = BalancedKGGeneratorIN20IN27()
generator.generate_for_project('IFN712 Project 13-1')
```

### 方法 3: 批量生成所有项目

```bash
cd /Users/lynn/Documents/GitHub/ProjectMatching
python3 src/knowledge_graphs/balanced_kg_generator_in20_in27.py
```

这将处理20个项目：
- IFN712 Project 1-20

## 📁 目录结构

```
ProjectMatching/
├── src/knowledge_graphs/
│   └── balanced_kg_generator_in20_in27.py    # 主生成器
├── data/processed/units_md/
│   ├── qut_IN20_39851_int_cms_unit.md        # IN20数据
│   └── qut_IN27_44569.md                      # IN27数据
├── outputs/knowledge_graphs/
│   ├── archive/
│   │   ├── clean_kg_output/                   # PD数据源
│   │   └── complete_clean_kg_output/          # PD+IN20数据源
│   └── enhanced_in20_in27/                    # 新输出目录
│       └── {project_name}/
│           ├── {project}_enhanced_kg.json
│           ├── {project}_enhanced_kg_full.png
│           └── {project}_enhanced_kg_simple.png
└── test_in20_in27_generator.py                # 测试脚本
```

## 🎨 可视化特性

### 节点样式

| 类型 | 颜色 | 大小 | 说明 |
|------|------|------|------|
| PROJECT | 🔴 红色 | 6000 | 项目节点（中心） |
| SKILL (双重支持) | 🟢 鲜绿色 | 4000 | IN20+IN27支持 |
| SKILL (IN20) | 🔵 天蓝色 | 4000 | 仅IN20支持 |
| SKILL (IN27) | 🟣 紫色 | 4000 | 仅IN27支持 |
| SKILL (PD扩展) | 🟠 橙色 | 4000 | 未被课程覆盖 |
| UNIT | 🩵 青色 | 2000 | 课程单元 |
| PROGRAM | 🩷 淡紫色 | 2500 | 学位项目 |

### 边样式

| 类型 | 颜色 | 宽度 | 透明度 | 样式 |
|------|------|------|--------|------|
| 双重支持 | 🟢 鲜绿色 | 4 | 0.9 | 实线 |
| IN20支持 | 🔵 天蓝色 | 3 | 0.8 | 实线 |
| PD扩展 | 🟠 橙色 | 2.5 | 0.7 | 虚线 |
| 结构关系 | ⚪ 灰色 | 2 | 0.6 | 实线 |

## 💡 示例输出

### 示例项目: IFN712 Project 13-1

#### 数据统计:
- PD 技能: 9
- IN20 节点: 126
- IN20 边: 236  
- IN27 技能: 10

#### KG 构建结果:
- 节点总数: 130
- 边总数: 127
- 双重支持技能: 2 (machine learning, data analytics)
- IN20支持技能: 121
- IN27支持技能: 2

#### 技能分类示例:
- ✓✓ **machine learning** (双重支持)
- ✓✓ **data analytics** (双重支持)
- ✓ **cyber security** (IN20支持)
- ✓ **programming** (IN20支持)
- ✓ **database** (IN20支持)
+ **mobile development** (PD扩展)
+ **user experience** (PD扩展)
+ **web development** (PD扩展)
+ **networking** (PD扩展)

## 📈 与现有知识图谱的对比

| 特性 | PD Only | PD + IN20 | **PD + IN20 + IN27** ⭐ |
|------|---------|-----------|-------------------------|
| 数据源 | 项目描述 | 项目 + 1门课程 | 项目 + 1门课程 + 硕士项目 |
| 技能覆盖 | 基础 | 中等 | **最全面** |
| 支持验证 | 无 | 单一课程 | **双重验证** |
| 学生匹配 | 低准确度 | 中等准确度 | **高准确度** |
| 技能分类 | 2类 | 2类 | **4类（更精细）** |

## ⚙️ 配置选项

在 `BalancedKGGeneratorIN20IN27` 类中可以调整：

```python
# 技能同义词映射
self.synonyms = {
    'ai': 'artificial intelligence',
    'ml': 'machine learning',
    'data science': 'data analytics',
    # 添加更多...
}

# IN27 技能提取模式
skill_patterns = [
    r'data analytics?', 
    r'machine learning',
    # 添加更多...
]

# 布局参数
radius = 5  # 径向布局半径
cols = 4    # UNIT节点列数
```

## 🐛 故障排除

### 问题 1: 找不到数据文件
```bash
⚠️  IN27 文件不存在
```
**解决**: 确保 `data/processed/units_md/qut_IN27_44569.md` 存在

### 问题 2: 生成的图太密集
**解决**: 查看简化版本 `*_enhanced_kg_simple.png`

### 问题 3: 技能未被识别为IN27支持
**解决**: 检查 `skill_patterns` 和 `synonyms` 配置，添加相关模式

## 🔮 未来改进

- [ ] 支持更多硕士项目 (IN28, IN30, etc.)
- [ ] 动态提取技能而非硬编码模式
- [ ] 添加交互式可视化 (Plotly/D3.js)
- [ ] 支持技能层次结构 (父技能-子技能)
- [ ] 添加时间维度 (课程学期序列)

## 📚 相关文档

- `balanced_kg_generator.py` - PD + IN20 基础生成器
- `project_knowledge_graph.py` - 原始知识图谱实现
- `enhanced_project_kg.py` - Unit Outline 集成

## 👥 联系方式

如有问题或建议，请联系项目维护者。

---

**生成日期**: 2025-10-02  
**版本**: 1.0  
**作者**: AI Assistant & Lynn



