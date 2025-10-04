# Method 2a 准备就绪说明

> 日期: 2025-10-04  
> 状态: ✅ 准备就绪

---

## 📁 数据文件位置

### 项目知识图谱 (PD only)

**目录**: `outputs1/knowledge_graphs/three_layer_projects/`

**文件格式**: `*_entities.json` + `*_relationships.json`

**数量**: 18个有效项目 (19个文件，1个为空)

**示例**:
```
AI-Based_Human_Activity_entities.json
Smart_Intersection_Localization_entities.json
VitalID_Smartphone-Based_entities.json
...
```

### 学生知识图谱

**目录**: `outputs1/knowledge_graphs/enhanced_student_kg/`

**结构**: 按原始项目名分组

**文件格式**: `*_enhanced_kg.json`

**数量**: 20个项目目录，每个包含10个学生（部分项目可能少于10个）

**示例**:
```
HAR_WiFi_Proposal_Zhenguo-1/
  - student_n01803983_Blake_Allen_enhanced_kg.json
  - student_n04539845_Jordan_Wright_enhanced_kg.json
  - ... (10个学生)

IFN712 Project 13-1/
  - student_n02345678_Alice_Smith_enhanced_kg.json
  - ... (10个学生)
```

---

## 🔗 项目名称映射

由于 `three_layer_projects` 中的项目名称是**简化版**，而学生KG目录使用**原始项目名**，因此需要映射文件。

**映射文件**: `outputs1/knowledge_graphs/project_name_mapping.json`

**映射示例**:
```json
{
  "AI-Based_Human_Activity": "HAR_WiFi_Proposal_Zhenguo-1",
  "Smart_Intersection_Localization": "Localization_Proposal_Zhenguo",
  "VitalID_Smartphone-Based": "VitalID_Proposal_Zhenguo",
  "A_Systematic_Review_of_Deep": "ZaenabAlammar_IFN712 Project Proposal 1_2025_CS_",
  "Binary_vs_Multiclass_Evaluation": "IFN712 Project 14-1",
  ...
}
```

**总映射数**: 18个有效映射

---

## ✅ 代码更新

`run_kg_similarity_experiment.py` 的 `run_method_2a()` 方法已更新：

1. ✅ 正确的输入路径
2. ✅ 加载项目名称映射
3. ✅ 使用映射查找对应的学生目录
4. ✅ 只计算 matched pairs（学生来自该项目）

---

## 📊 预期输出

### Matched Pairs

对于每个项目：
- 加载项目KG（简化名）
- 通过映射找到原始项目名
- 加载该项目下的所有学生KG
- 计算相似度（Jaccard + Edit Distance）
- 标记为 `is_match=True`

**预计数量**: 18项目 × 10学生 = 180对 matched pairs

---

## ⚠️ 待补充功能

当前 Method 2a 只计算 **matched pairs**，还需要添加：

### Unmatched Pairs

对于每个项目：
- 加载该项目KG
- 遍历**其他17个项目**的学生目录
- 计算与其他项目学生的相似度
- 标记为 `is_match=False`

**预计数量**: 18项目 × (17其他项目 × 10学生) = 18 × 170 = **3060对** unmatched pairs

**总计**: 180 (matched) + 3060 (unmatched) = **3240对**

---

## 🚀 运行命令

### 当前版本（仅 matched pairs）

```bash
python run_kg_similarity_experiment.py --method 2a
```

### 完整版本（需要修改代码添加 unmatched pairs）

```bash
python run_kg_similarity_experiment.py --method 2a --include-unmatched
```

---

## 📝 下一步

1. ✅ 验证 matched pairs 计算正确（dry-run测试通过）
2. ❌ 添加 unmatched pairs 计算
3. ❌ 生成统计分析
4. ❌ 创建可视化图表
5. ❌ 与 Method 2b 对比

---

## 🎯 验证清单

- [x] 项目KG文件存在且可读
- [x] 学生KG文件存在且可读
- [x] 映射文件正确创建
- [x] 代码能正确加载和应用映射
- [x] Dry-run 测试通过
- [ ] 实际运行并生成结果
- [ ] 结果数量符合预期（180 matched pairs）
- [ ] 补充 unmatched pairs 计算

---

**准备好运行 Method 2a 了！** 🚀

