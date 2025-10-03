# 先修课程集成指南

## 概述

本指南说明如何在学生知识图谱中使用先修课程（Prerequisite）信息。

## 🎯 为什么需要先修课程信息？

### 数据支持
- **93.6%的学生**（176/188）修过有前置要求的课程
- 成功添加了**553条前置关系**
- 从IN27课程手册提取了**24门课程**的前置要求

### 实际价值
1. **学习路径验证** - 验证学生是否按正确顺序学习课程
2. **技能评估** - 完成前置课程意味着技能掌握更扎实
3. **项目匹配** - 确保学生具备完整知识体系

## 📁 文件说明

### 生成的文件
```
outputs/knowledge_graphs/individual/enhanced_student_kg/
├── [项目名]/
│   ├── student_xxx_enhanced_kg.json          # 原始KG
│   ├── student_xxx_with_prereq.json          # ✨ 带前置课程关系的KG
│   └── student_xxx_kg.png                    # 可视化
```

### 前置课程关系示例

```json
{
  "source_id": "course_ifn555_introduction_to_programming",
  "target_id": "course_ifn666_web_technologies",
  "relation_type": "PREREQUISITE_FOR",
  "weight": 1.0,
  "properties": {
    "description": "IFN555 is a prerequisite for IFN666"
  }
}
```

## 🔧 使用方法

### 方法1：重新生成前置课程关系

```bash
# 仅分析，不修改文件
python add_prerequisites_to_student_kg.py --analyze-only

# 添加前置关系（推荐）
python add_prerequisites_to_student_kg.py

# 添加前置关系 + 缺失的前置课程节点
python add_prerequisites_to_student_kg.py --add-missing
```

### 方法2：在代码中使用

```python
from add_prerequisites_to_student_kg import PrerequisiteAnalyzer
import json

# 初始化分析器
analyzer = PrerequisiteAnalyzer()

# 读取学生KG
with open('student_kg.json', 'r') as f:
    kg_data = json.load(f)

# 添加前置课程信息
enhanced_kg, stats = analyzer.add_prerequisites_to_kg(
    kg_data,
    add_missing=False  # 是否添加缺失的前置课程节点
)

# 保存增强后的KG
with open('student_kg_with_prereq.json', 'w') as f:
    json.dump(enhanced_kg, f, indent=2, ensure_ascii=False)
```

### 方法3：集成到生成流程

在 `src/knowledge_graphs/enhanced_student_kg.py` 的 `_save_enhanced_kg()` 方法中添加：

```python
def _save_enhanced_kg(self, entity_id: str, name: str, entities: Dict,
                     relationships: List, graph: nx.MultiDiGraph, output_dir: str):
    """保存增强版知识图谱"""
    
    # ... 原有代码 ...
    
    # 添加前置课程信息
    from add_prerequisites_to_student_kg import PrerequisiteAnalyzer
    analyzer = PrerequisiteAnalyzer()
    kg_data, stats = analyzer.add_prerequisites_to_kg(kg_data, add_missing=False)
    
    # 保存（覆盖原文件或另存）
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(kg_data, f, ensure_ascii=False, indent=2)
```

## 📊 统计信息

### 处理结果
- **处理学生数**: 188名
- **总课程数**: 1,433门
- **添加前置关系**: 553条

### 最常见的缺失前置课程

| 课程代码 | 缺失学生数 | 说明 |
|---------|----------|------|
| IFQ555  | 176      | 可能是老课程代码（等效于IFN555） |
| IFQ556  | 148      | 可能是老课程代码（等效于IFN556） |
| IFN501  | 108      | 基础课程 |
| IFN581  | 98       | 数据库课程 |

**注意**：IFQ开头的课程可能是旧的课程代码，与IFN课程等效。

## 🎨 可视化

### 关系类型

增强后的KG包含以下关系类型：

| 关系类型 | 说明 | 可视化建议颜色 |
|---------|------|--------------|
| COMPLETED_COURSE | 学生完成课程 | 绿色 |
| PREREQUISITE_FOR | 前置课程关系 | **紫色虚线** ⭐ |
| TEACHES_SKILL | 课程教授技能 | 紫色 |
| HAS_SKILL | 学生拥有技能 | 蓝色 |

### 建议的可视化方案

```python
# 前置课程关系使用特殊样式
edge_styles = {
    'PREREQUISITE_FOR': {
        'color': 'purple', 
        'width': 3, 
        'style': 'dashed',
        'alpha': 0.9
    }
}
```

## 🔍 分析案例

### 案例1：验证学习路径

**学生**: Phoenix Hill  
**前置关系**:
- IFN555 → IFN666 (编程入门 → Web技术) ✅
- IFN555 → IFN564 (编程入门 → 机器学习) ✅

**结论**: 学生按正确顺序学习，具备扎实基础。

### 案例2：识别知识缺口

**学生**: 某学生修了IFN666但没修IFN555  
**分析**: 可能缺少编程基础，在项目中可能遇到困难  
**建议**: 分配简单项目或提供额外支持

## 🚀 下一步

1. **✅ 已完成**: 为所有学生KG添加前置课程关系
2. **建议**:
   - 在项目匹配算法中使用 `*_with_prereq.json` 文件
   - 根据前置课程完成情况调整匹配权重
   - 创建带前置关系的可视化图谱

## 📝 参考文件

- `add_prerequisites_to_student_kg.py` - 前置课程补充工具
- `data/processed/units_md/qut_IN27_44569.md` - IN27课程手册（包含前置课程信息）
- `data/processed/units_md/qut_IN20_39851_int_cms_unit.md` - IN20课程手册

## 🤝 贡献

如果发现前置课程映射错误，请修改 `add_prerequisites_to_student_kg.py` 中的 `_extract_unit_prerequisites()` 方法。

---

**最后更新**: 2025-10-02



