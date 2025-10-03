# 3层项目知识图谱 - 快速开始指南

## 🚀 5分钟快速上手

### 1️⃣ 基础使用（固定权重）

```bash
cd /Users/lynn/Documents/GitHub/ProjectMatching

python -c "
from src.knowledge_graphs.three_layer_project_kg import generate_all_three_layer_project_kgs
generate_all_three_layer_project_kgs()
"
```

**输出：**
```
outputs/knowledge_graphs/individual/three_layer_projects/
├── {Project}_kg.png              # 可视化图片
├── {Project}_relationships.json  # 关系（权重0.8/0.9）
└── summary_report.json          # 汇总报告
```

**权重：**
- `REQUIRES_DOMAIN`: 1.0（不显示）
- `INCLUDES`: 0.8（显示）
- `USES_TECH`: 0.9（显示）

---

### 2️⃣ 高级使用（权重对齐）

```bash
cd /Users/lynn/Documents/GitHub/ProjectMatching

python -c "
from src.knowledge_graphs.three_layer_project_kg import generate_all_three_layer_project_kgs
generate_all_three_layer_project_kgs(use_existing_weights=True)
"
```

**效果：**
- ✅ 从 `enhanced_in20_in27/` 读取权重
- ✅ 归一化到 0.5-1.0 范围
- ✅ 约30%技能使用对齐权重

**权重示例：**
```
machine learning: 5.0 → 0.583 (对齐)
deep learning: (未匹配) → 0.8 (默认)
```

---

## 📊 可视化示例

### 图片说明

<img src="outputs/knowledge_graphs/individual/three_layer_projects/IoT-Based_Spectral_Sensing_and_kg.png" width="600">

**图例：**
- 🔴 红色大圆：Project（Layer 1）
- 🟢 绿色中圆：Domain（Layer 2）
- 🔵 蓝色/橙色/紫色小圆：Skill/Major/Technology（Layer 3）
- 🔢 红色标签：边的权重（非1.0才显示）

---

## 🎯 权重方案选择

### 什么时候用固定权重？

```python
generate_all_three_layer_project_kgs()  # 默认
```

**适用场景：**
- ✅ 快速可视化
- ✅ 不需要精确权重
- ✅ 100%覆盖率（所有技能都有权重）

---

### 什么时候用权重对齐？

```python
generate_all_three_layer_project_kgs(use_existing_weights=True)
```

**适用场景：**
- ✅ 项目-学生匹配系统
- ✅ 需要反映技能重要性差异
- ✅ 与 enhanced_in20_in27 保持一致

**前提条件：**
- ⚠️ 需要先生成 `enhanced_in20_in27/` 知识图谱

---

## 🔍 查看结果

### 1. 查看权重（JSON）

```bash
cat outputs/knowledge_graphs/individual/three_layer_projects/IoT-Based_Spectral_Sensing_and_relationships.json
```

**找出对齐的权重：**
```bash
jq '.[] | select(.weight != 0.8 and .weight != 0.9 and .weight != 1.0)' \
  outputs/knowledge_graphs/individual/three_layer_projects/IoT-Based_Spectral_Sensing_and_relationships.json
```

**输出示例：**
```json
{
  "source_id": "domain_machine_learning_and_ai",
  "target_id": "skill_machine_learning",
  "relation_type": "INCLUDES",
  "weight": 0.5833333333333334
}
```

### 2. 查看图片

```bash
open outputs/knowledge_graphs/individual/three_layer_projects/IoT-Based_Spectral_Sensing_and_kg.png
```

---

## 📐 权重归一化公式

### 从 enhanced_in20_in27 到 三层KG

```
原始权重范围: 2.0 - 20.0 (enhanced_in20_in27)
归一化范围:  0.5 - 1.0  (三层KG)

公式: normalized = 0.5 + (weight - 2.0) / 18.0 * 0.5
```

**示例：**
| 原始 | 归一化 | 显示 |
|-----|-------|------|
| 2.0 | 0.500 | 0.5 |
| 5.0 | 0.583 | 0.6 |
| 10.0 | 0.722 | 0.7 |
| 15.0 | 0.861 | 0.9 |
| 20.0 | 1.000 | 1.0 |

---

## ⚙️ Python API

### 基础用法

```python
from src.knowledge_graphs.three_layer_project_kg import ThreeLayerProjectKGGenerator

# 创建生成器
generator = ThreeLayerProjectKGGenerator()

# 生成单个项目
generator.generate_project_kg(
    project_file="data/processed/projects_md/HAR_WiFi_Proposal_Zhenguo-1.md",
    output_dir="outputs/knowledge_graphs/individual/three_layer_projects"
)
```

### 启用权重对齐

```python
from src.knowledge_graphs.three_layer_project_kg import ThreeLayerProjectKGGenerator

# 创建生成器（启用权重对齐）
generator = ThreeLayerProjectKGGenerator(use_existing_weights=True)

# 生成单个项目
generator.generate_project_kg(
    project_file="data/processed/projects_md/Plant_sensing_Proposal_Zhenguo.md",
    output_dir="outputs/knowledge_graphs/individual/three_layer_projects"
)
```

### 批量生成

```python
from src.knowledge_graphs.three_layer_project_kg import generate_all_three_layer_project_kgs

# 方式1：固定权重
generate_all_three_layer_project_kgs()

# 方式2：权重对齐
generate_all_three_layer_project_kgs(use_existing_weights=True)

# 方式3：自定义目录
generate_all_three_layer_project_kgs(
    project_dir="data/processed/projects_md",
    output_dir="outputs/knowledge_graphs/individual/three_layer_projects",
    use_existing_weights=True
)
```

---

## 🔍 验证权重对齐

### 测试单个项目

```python
from src.knowledge_graphs.three_layer_project_kg import ThreeLayerProjectKGGenerator

gen = ThreeLayerProjectKGGenerator(use_existing_weights=True)

# 查看加载的权重数据
print("Loaded projects:", len(gen.existing_weights))

# 测试权重获取
project_name = 'Plant_sensing_Proposal_Zhenguo'
skills = ['machine learning', 'networking', 'programming']

for skill in skills:
    weight = gen._get_weight_for_skill(project_name, skill)
    print(f"{skill}: {weight:.3f}")
```

**输出示例：**
```
Loaded projects: 20
machine learning: 0.583  ← 从 5.0 归一化
networking: 0.583        ← 从 5.0 归一化
programming: 0.556       ← 从 3.0 归一化
```

---

## 📂 文件结构

```
outputs/knowledge_graphs/individual/three_layer_projects/
├── AI-Based_Human_Activity_entities.json
├── AI-Based_Human_Activity_relationships.json  ← 权重在这里
├── AI-Based_Human_Activity_stats.json
├── AI-Based_Human_Activity_kg.png              ← 可视化图片
├── IoT-Based_Spectral_Sensing_and_entities.json
├── IoT-Based_Spectral_Sensing_and_relationships.json
├── IoT-Based_Spectral_Sensing_and_stats.json
├── IoT-Based_Spectral_Sensing_and_kg.png
├── ...
└── summary_report.json                         ← 汇总统计
```

---

## 🐛 常见问题

### Q1: 权重对齐后还是0.8/0.9？

**原因：** 技能名称未匹配

**解决：**
```python
# 检查项目的权重数据
gen = ThreeLayerProjectKGGenerator(use_existing_weights=True)
project_weights = gen.existing_weights.get('项目名称', {})
print(project_weights)  # 查看可用的技能
```

**常见不匹配：**
- 三层KG: `deep learning` ❌
- enhanced: `machine learning` ✅
- 解决: 需要技能映射（future功能）

---

### Q2: 如何查看哪些权重被对齐了？

```bash
# 找出非默认权重的关系
jq '.[] | select(.weight != 0.8 and .weight != 0.9 and .weight != 1.0) | {skill: .target_id, weight: .weight}' \
  outputs/knowledge_graphs/individual/three_layer_projects/*_relationships.json
```

---

### Q3: 为什么匹配率只有30%？

**原因：** 技能粒度不同

- **enhanced_in20_in27**: 粗粒度（8-10个标准技能）
  - `machine learning`, `data analytics`, `networking`
  
- **三层KG**: 细粒度（从MD直接提取）
  - `deep learning`, `neural networks`, `computer vision`

**未来改进：**
- [ ] 技能标准化映射
- [ ] 语义相似度匹配
- [ ] 层次化权重继承

---

## 📚 相关文档

- **详细实现文档**: `THREE_LAYER_WEIGHT_ALIGNMENT.md`
- **权重规则说明**: `WEIGHT_RULES_EXPLANATION.md`
- **可视化更新**: `WEIGHT_VISUALIZATION_UPDATE.md`

---

## ✅ 快速验证

### 一行命令验证权重对齐

```bash
cd /Users/lynn/Documents/GitHub/ProjectMatching && \
python -c "
from src.knowledge_graphs.three_layer_project_kg import ThreeLayerProjectKGGenerator
gen = ThreeLayerProjectKGGenerator(use_existing_weights=True)
w = gen._get_weight_for_skill('Plant_sensing_Proposal_Zhenguo', 'machine learning')
print(f'machine learning: {w:.3f}')
expected = 0.5 + (5.0 - 2.0) / 18.0 * 0.5
print(f'expected: {expected:.3f}')
print('✅ SUCCESS' if abs(w - expected) < 0.001 else '❌ FAILED')
"
```

**预期输出：**
```
📥 从 enhanced_in20_in27 加载权重数据...
  ✅ 已加载 20 个项目的权重数据
machine learning: 0.583
expected: 0.583
✅ SUCCESS
```

---

**🎉 现在你已经掌握了3层项目知识图谱的权重对齐功能！**



