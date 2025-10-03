# 3层项目知识图谱权重方案对比

## 📊 当前状态

✅ **已实现**：固定权重方案  
🎯 **是否需要改进**：取决于使用场景

---

## 方案A：固定权重（当前方案）

### 结构
```
Project → Domain: 1.0
Domain → Skill: 0.8
Domain → Technology: 0.9
```

### 优势
- ✅ **简单明了**：所有同类关系权重一致
- ✅ **易于理解**：视觉上一致性强
- ✅ **快速实现**：已经完成
- ✅ **适合可视化**：重点在结构而非权重

### 适用场景
1. **知识图谱可视化**：展示项目的知识结构
2. **快速原型**：不需要复杂的权重计算
3. **结构化展示**：关注领域分类而非细节差异

### 示例
```json
{
  "source_id": "project_AI_Based",
  "target_id": "domain_machine_learning_and_ai",
  "relation_type": "REQUIRES_DOMAIN",
  "weight": 1.0  // 固定
}
{
  "source_id": "domain_machine_learning_and_ai",
  "target_id": "skill_deep_learning",
  "relation_type": "INCLUDES",
  "weight": 0.8  // 固定
}
```

---

## 方案B：动态权重（可选升级）

### 结构
```
Project → Domain: 根据该Domain的技能数量/重要性
Domain → Skill: 根据技能的核心程度（0.5-1.0）
Domain → Technology: 根据技术的使用频率（0.6-1.0）
```

### 权重计算策略

#### 1. **Project → Domain 权重**
基于该Domain包含的技能数量和重要性：

```python
# 方法1：基于技能数量
weight = min(1.0, 0.5 + 0.1 * skill_count)

# 方法2：基于核心Domain判断
core_domains = {'Machine Learning & AI', 'Data Science & Analytics'}
weight = 1.0 if domain in core_domains else 0.7
```

**示例**：
- ML & AI (5个技能) → weight = 1.0
- Web Development (2个技能) → weight = 0.7

#### 2. **Domain → Skill 权重**
基于技能在项目中的重要性：

```python
# 方法1：基于关键词匹配
core_keywords = {'deep learning', 'machine learning', 'neural network'}
weight = 1.0 if skill in core_keywords else 0.6

# 方法2：基于在描述中的出现位置
weight = 0.9  # 标题中提到
weight = 0.7  # 正文中提到
weight = 0.5  # 仅在技能列表中

# 方法3：与enhanced_in20_in27对齐
# 从现有的项目KG中读取该技能的权重，归一化到0-1
```

**示例**：
- Deep Learning → weight = 1.0 (核心技能)
- Testing → weight = 0.6 (辅助技能)

#### 3. **Domain → Technology 权重**
基于技术的使用频率：

```python
essential_techs = {'python', 'tensorflow', 'pytorch'}
weight = 1.0 if tech in essential_techs else 0.7
```

### 优势
- ✅ **更精确的匹配**：可用于学生-项目推荐算法
- ✅ **区分重要性**：核心技能 vs 辅助技能
- ✅ **与现有KG对齐**：可与enhanced_in20_in27权重系统统一

### 劣势
- ❌ **复杂度增加**：需要定义权重计算规则
- ❌ **可能过度设计**：如果只用于可视化，没必要
- ❌ **需要调试**：权重阈值需要实验验证

### 适用场景
1. **项目-学生匹配算法**：需要精确的相似度计算
2. **推荐系统**：基于技能重要性排序
3. **技能分析**：区分核心技能和辅助技能

### 示例
```json
{
  "source_id": "project_AI_Based",
  "target_id": "domain_machine_learning_and_ai",
  "relation_type": "REQUIRES_DOMAIN",
  "weight": 1.0  // 核心领域
}
{
  "source_id": "domain_machine_learning_and_ai",
  "target_id": "skill_deep_learning",
  "relation_type": "INCLUDES",
  "weight": 1.0  // 核心技能
}
{
  "source_id": "domain_general_technologies",
  "target_id": "skill_testing",
  "relation_type": "INCLUDES",
  "weight": 0.6  // 辅助技能
}
```

---

## 方案C：与enhanced_in20_in27对齐（推荐用于匹配）

### 目标
使3层项目KG的权重与现有的`enhanced_in20_in27`知识图谱保持一致。

### 实现策略

#### 1. **读取现有权重**
```python
# 从 enhanced_in20_in27 中读取每个项目的技能权重
existing_kg_dir = "outputs/knowledge_graphs/enhanced_in20_in27"
project_kg_file = f"{existing_kg_dir}/{project_name}_relationships.json"

# 提取 REQUIRES_SKILL 关系的权重
skill_weights = {}
for rel in relationships:
    if rel['relation_type'] == 'REQUIRES_SKILL':
        skill_name = get_skill_name(rel['target_id'])
        skill_weights[skill_name] = rel['weight']  # 通常 2-20
```

#### 2. **归一化权重**
```python
# 将 2-20 的权重归一化到 0.5-1.0
max_weight = max(skill_weights.values()) if skill_weights else 10.0

for skill, weight in skill_weights.items():
    normalized = 0.5 + (weight / max_weight) * 0.5
    skill_weights[skill] = round(normalized, 2)
```

#### 3. **应用到3层KG**
```python
# Domain → Skill 权重使用归一化后的值
rel = KGRelationship(
    source_id=domain_id,
    target_id=skill_id,
    relation_type='INCLUDES',
    weight=skill_weights.get(skill_name, 0.7)  # 默认0.7
)
```

### 优势
- ✅ **一致性**：与现有项目KG权重体系统一
- ✅ **可复用**：可以直接用于匹配算法
- ✅ **已验证**：enhanced_in20_in27的权重已经过测试

### 示例权重映射
```
原始权重 (enhanced_in20_in27)  →  归一化权重 (3层KG)
─────────────────────────────────────────────────
10.0 (核心技能)                 →  1.0
7.0                            →  0.85
5.0                            →  0.75
3.0                            →  0.65
2.0 (边缘技能)                  →  0.6
```

---

## 🎯 推荐方案

### 场景1：**仅用于可视化** → 选择 **方案A（当前方案）**
- 已经完成 ✅
- 简单明了
- 无需修改

### 场景2：**用于项目-学生匹配** → 选择 **方案C（与enhanced对齐）**
- 复用现有权重系统
- 保持一致性
- 支持精确匹配

### 场景3：**独立的权重系统** → 选择 **方案B（动态权重）**
- 需要自定义权重规则
- 适合特殊需求
- 需要额外开发

---

## 📝 实现成本估算

| 方案 | 开发时间 | 复杂度 | 可维护性 | 是否推荐 |
|-----|---------|-------|---------|---------|
| **方案A（固定）** | ✅ 已完成 | ⭐ 低 | ⭐⭐⭐⭐⭐ 高 | ✅ 仅可视化 |
| **方案B（动态）** | 2-3小时 | ⭐⭐⭐⭐ 高 | ⭐⭐ 中 | ⚠️ 特殊需求 |
| **方案C（对齐）** | 1小时 | ⭐⭐⭐ 中 | ⭐⭐⭐⭐ 高 | ✅ 用于匹配 |

---

## ❓ 决策问题

**请回答以下问题，帮助选择方案**：

1. **这个3层KG的主要用途是什么？**
   - [ ] A. 主要用于可视化展示项目结构
   - [ ] B. 用于项目-学生匹配算法
   - [ ] C. 两者都有

2. **是否需要与现有的 enhanced_in20_in27 KG 保持一致？**
   - [ ] A. 是，需要统一权重系统
   - [ ] B. 否，这是独立的可视化系统

3. **是否需要区分技能的重要性（核心 vs 辅助）？**
   - [ ] A. 是，需要精确区分
   - [ ] B. 否，所有技能平等对待

**根据您的回答，我可以快速实现对应的方案！**

---

## 📌 快速实现指南

### 如果选择方案C（推荐）：

1. 修改 `three_layer_project_kg.py`
2. 添加函数读取 `enhanced_in20_in27` 的权重
3. 归一化并应用到3层KG
4. 重新生成所有图谱

**预计时间**：30-60分钟

### 如果保持方案A：

- 无需任何修改 ✅
- 当前已完成

---

**您倾向于哪个方案？** 🤔



