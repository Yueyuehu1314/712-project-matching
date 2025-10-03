# 学生知识图谱更新总结

## 📅 更新时间
2025年10月3日

## ✅ 完成任务

### 1️⃣ 为所有边添加权重 (Weight)
**状态**: ✅ 已完成

所有 `*_enhanced_kg.json` 文件中的边都已经包含权重字段：

| 关系类型 | 权重值 | 说明 |
|---------|--------|------|
| `STUDIED_MAJOR` | 1.0 | 学生与专业的关系（确定性） |
| `COMPLETED_COURSE` | 1.0 | 学生完成课程（确定性） |
| `TEACHES_SKILL` | 0.9 | 课程教授技能（高置信度） |
| `HAS_SKILL` (from course) | 0.8 | 从课程获得的技能（推断性） |
| `HAS_SKILL` (self-taught) | 0.6 | 自学技能（置信度较低） |
| `INTERESTED_IN` | 1.0 | 研究兴趣（确定性） |

### 2️⃣ 添加课程前置关系 (Prerequisite)
**状态**: ✅ 已完成

使用 `add_prerequisites_to_student_kg.py` 脚本批量处理了所有学生KG：

#### 统计数据
- **处理学生数**: 188 人
- **总课程数**: 1,433 门
- **添加前置关系数**: 553 条
- **前置关系类型**: `PREREQUISITE_FOR`
- **前置关系权重**: 1.0（最高可信度）

#### 数据来源
- **IN20课程手册**: `data/processed/units_md/qut_IN20_39851_int_cms_unit.md`
- **IN27课程手册**: `data/processed/units_md/qut_IN27_44569.md`
- **识别前置课程**: 24 门课程有前置要求

#### 示例前置关系
```json
{
  "source_id": "course_ifn555_introduction_to_programming",
  "target_id": "course_ifn563_algorithms_and_complexity",
  "relation_type": "PREREQUISITE_FOR",
  "weight": 1.0,
  "properties": {
    "description": "IFN555 is a prerequisite for IFN563"
  }
}
```

## 📂 输出文件结构

```
outputs/knowledge_graphs/individual/enhanced_student_kg/
├── [项目名称1]/
│   ├── student_xxx_enhanced_kg.json      # ✅ 原始KG（有权重）
│   ├── student_xxx_with_prereq.json      # ✨ 新增：带前置课程的KG
│   └── student_xxx_kg.png                # 可视化
├── [项目名称2]/
│   ├── student_yyy_enhanced_kg.json
│   ├── student_yyy_with_prereq.json      # ✨ 新增
│   └── student_yyy_kg.png
└── ...
```

## 🔍 前置课程分析

### 有前置要求的学生
- **总学生数**: 188
- **有前置课程要求的学生**: 176 (93.6%)

### 最常见的缺失前置课程 (Top 7)
许多学生修了高级课程但档案中未显示基础课程：

| 课程代码 | 缺失学生数 |
|---------|----------|
| IFQ555 | 176 |
| IFQ556 | 148 |
| IFN501 | 108 |
| IFN581 | 98 |
| IFN556 | 48 |
| IFN563 | 40 |
| IFN555 | 35 |

**注意**: 这些"缺失"的前置课程可能是：
1. 学生实际已修但未记录在档案中
2. 通过等效课程满足了前置要求
3. 通过豁免(waiver)获得许可

## 🎯 使用建议

### 1. 项目匹配时考虑权重
在进行学生-项目匹配时，可以根据边的权重进行加权计算：

```python
# 伪代码示例
def calculate_match_score(student_kg, project_kg):
    score = 0
    for skill in project_required_skills:
        if skill in student_skills:
            edge_weight = get_edge_weight(student, skill)
            score += edge_weight * skill_importance
    return score
```

### 2. 利用前置课程关系
- **技能推断**: 如果学生修了高级课程，可以推断已掌握前置课程的技能
- **学习路径**: 为学生建议后续可修的课程
- **匹配优化**: 优先匹配已完成所有前置课程的学生

### 3. 文件选择
- **基础匹配**: 使用 `*_enhanced_kg.json`
- **高级匹配（推荐）**: 使用 `*_with_prereq.json`，包含更完整的课程关系

## 📊 Metadata 增强

每个 `*_with_prereq.json` 文件都在 metadata 中添加了前置课程分析：

```json
{
  "metadata": {
    "student_id": "student_n12784106",
    "student_name": "Phoenix Miller",
    "created_at": "2025-10-02T22:34:11.741742",
    "version": "2.0_enhanced",
    "prerequisite_analysis": {
      "courses_with_prereq": [
        {
          "course": "IFN563",
          "prerequisites": ["IFN555", "IFN556"]
        },
        {
          "course": "IFN564",
          "prerequisites": ["IFN555", "IFN563"]
        }
      ],
      "missing_prerequisites": ["IFN556"],
      "completed_prerequisites": ["IFN555", "IFN563"],
      "student_courses": ["IFN555", "IFN563", "IFN564", ...]
    }
  }
}
```

## 🚀 下一步建议

1. **可视化更新**: 更新PNG图片，显示前置课程关系
2. **权重调整**: 根据实际匹配效果调整不同关系类型的权重
3. **缺失节点**: 考虑是否添加学生未修但需要的前置课程节点（使用 `--add-missing` 参数）
4. **匹配算法**: 基于加权图实现更精确的匹配算法

## 📝 脚本使用

### 重新运行（如需更新）
```bash
# 仅添加前置关系（不创建缺失节点）
python add_prerequisites_to_student_kg.py \
  --kg-dir outputs/knowledge_graphs/individual/enhanced_student_kg

# 添加前置关系 + 创建缺失节点
python add_prerequisites_to_student_kg.py \
  --kg-dir outputs/knowledge_graphs/individual/enhanced_student_kg \
  --add-missing

# 仅分析，不修改文件
python add_prerequisites_to_student_kg.py \
  --kg-dir outputs/knowledge_graphs/individual/enhanced_student_kg \
  --analyze-only
```

---

**更新完成** ✅  
所有学生知识图谱已成功更新，包含完整的权重信息和前置课程关系。

