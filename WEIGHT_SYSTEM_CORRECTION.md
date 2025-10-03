# ⚠️ 权重系统更正说明

## 重要更正

之前的 `WEIGHT_RULES_EXPLANATION.md` 和 `WEIGHT_RULES_SUMMARY.md` 中关于 **enhanced_in20_in27 项目KG的权重规则有误**。

实际上，**项目KG中的权重并不限制在0-1范围内**，而是基于**文本匹配频率的原始分数**。

---

## 📊 两种不同的权重系统

### 1️⃣ 学生KG (enhanced_student_kg) - **归一化权重** (0-1范围)

✅ **这部分之前的说明是正确的**

```
权重范围: 0-1
设计原则: 表示关系的可信度/置信度

PREREQUISITE_FOR: 1.0
STUDIED_MAJOR: 1.0
COMPLETED_COURSE: 1.0
TEACHES_SKILL: 0.9
HAS_SKILL (course): 0.8
HAS_SKILL (project): 0.75
REQUIRES_SKILL: 0.7
HAS_SKILL (self-taught): 0.6
```

**含义**: 权重表示**关系的可靠性**和**信息来源的可信度**

---

### 2️⃣ 项目KG (enhanced_in20_in27) - **原始匹配分数** (无上限)

❌ **之前说权重最高是1.0 - 这是错误的！**

✅ **实际情况**：

```
权重范围: 0 到无上限（通常1-10，最高可达20+）
设计原则: 表示技能在文本中的匹配频率/重要性

REQUIRES_SKILL: 2.5, 3.0, 5.0, 7.0 等
TAUGHT_IN: 2, 5.0, 7.0 等
PREREQUISITE_FOR: 1.0 (固定)
```

**含义**: 权重表示**技能在项目描述中的出现频次**和**匹配强度**

---

## 🔍 项目KG权重计算详解

### 计算逻辑 (来自 `batch_complete_clean_kg.py`)

```python
def extract_project_skills(self, project_text: str) -> List[Tuple[str, float]]:
    score = 0
    
    # 1. 完整匹配 +5分
    if skill in text_lower:
        score += 5
    
    # 2. 词汇匹配 +1分/次
    for word in skill_words:
        score += text_lower.count(word)
    
    # 3. 同义词匹配 +3分
    for synonym in synonyms:
        if synonym in text_lower:
            score += 3
    
    # 4. 上下文加权 +2分
    # 如: "using machine learning", "develop AI"
    for context in ['using', 'with', 'implement', 'develop', ...]:
        if f"{context} {word}" in text_lower:
            score += 2
    
    return score  # 可能是 2, 5, 7, 10, 15 等任意值
```

### 实际示例

假设项目描述中多次提到"machine learning"：

```text
"This project uses machine learning to develop an AI system. 
The machine learning algorithms will be implemented using Python. 
Students should have machine learning experience."
```

**权重计算**：
- 完整匹配 "machine learning": +5
- 词汇 "machine" 出现3次: +3
- 词汇 "learning" 出现3次: +3
- 上下文 "uses machine": +2
- 上下文 "have machine": +2
- **总分**: 5+3+3+2+2 = **15**

所以边权重是 `REQUIRES_SKILL, weight: 15.0` ✅

---

## 📈 权重分数含义对照表

| 权重范围 | 含义 | 示例 |
|---------|------|------|
| **2-3** | 弱匹配 | 技能被提及1-2次，或只有同义词匹配 |
| **5-7** | 中等匹配 | 完整匹配1次 + 词汇匹配几次 |
| **10-15** | 强匹配 | 多次完整匹配或高频词汇出现 |
| **20+** | 核心技能 | 项目描述核心关键词，大量重复 |

---

## 🎯 为什么用两种不同的权重系统？

### 学生KG: 归一化权重 (0-1)
- **目的**: 评估**信息可信度**
- **场景**: 学生技能来源可能不可靠（自述 vs 课程证明）
- **需求**: 统一标准来比较不同来源的可信度

### 项目KG: 原始匹配分数 (无上限)
- **目的**: 评估**技能重要性**
- **场景**: 从项目描述提取技能需求
- **需求**: 保留匹配强度信息，高分=核心技能

---

## 🔧 如何解读可视化图中的权重

### enhanced_student_kg 图中：
```
学生 --[0.8]--> Python
```
- **含义**: 学生通过课程获得Python技能，可信度80%

### enhanced_in20_in27 图中：
```
项目 --[7.0]--> Machine Learning
```
- **含义**: Machine Learning在项目描述中匹配分数7分，是重要技能

```
Machine Learning --[5.0]--> IFN680
```
- **含义**: Machine Learning与课程IFN680的关联分数5分

---

## ⚙️ 技能分类的加成系统

虽然原始权重无上限，但技能节点的 **score** 字段确实有加成系统：

```python
# 来自 balanced_kg_generator_in20_in27.py

if in20_support and in27_support:
    # 双重支持
    score = support_info['score'] * 1.3
    score = min(score, 1.0)  # 上限1.0
    
elif in20_support or in27_support:
    # 单一支持
    score = support_info['score'] * 1.0
    score = min(score, 1.0)
    
else:
    # 仅PD
    score = support_info['score'] * 0.8
    score = min(score, 1.0)
```

**注意**: 这个加成是用于技能**节点的score属性**，不是**边的weight**！

---

## 📁 JSON文件中的结构

### 边 (edges) - 原始匹配分数
```json
{
  "source": "project_xxx",
  "target": "skill_machine_learning",
  "relation": "REQUIRES_SKILL",
  "weight": 7.0,  // ← 这个可以>1
  "category": "supported",
  "source_type": "PD"
}
```

### 节点 (nodes) - 归一化分数
```json
{
  "id": "skill_machine_learning",
  "name": "machine learning",
  "type": "SKILL",
  "score": 1.0,  // ← 这个限制在0-1
  "category": "dual_supported",
  "source": "IN20+IN27"
}
```

---

## 📚 更新的文档索引

### 正确的文档
✅ **学生KG权重**: `WEIGHT_RULES_EXPLANATION.md` 第一部分  
✅ **本文档**: `WEIGHT_SYSTEM_CORRECTION.md` (当前文件)

### 需要修正的文档
❌ **项目KG权重**: `WEIGHT_RULES_EXPLANATION.md` 第二部分 - **边权重说明有误**  
❌ **速查表**: `WEIGHT_RULES_SUMMARY.md` 第二部分 - **项目KG部分有误**

---

## 🛠️ 代码位置索引

### 学生KG权重 (0-1范围)
- **文件**: `src/knowledge_graphs/enhanced_student_kg.py`
- **行号**: 306 (0.9), 313 (0.8), 360 (0.75), 353 (0.7), 381 (0.6)

### 项目KG原始分数计算
- **文件**: `src/knowledge_graphs/batch_complete_clean_kg.py`
- **函数**: `extract_project_skills()` 第168-204行
- **逻辑**:
  - 完整匹配: +5
  - 词汇匹配: +1/次
  - 同义词: +3
  - 上下文: +2

### 技能节点分类加成 (0-1范围)
- **文件**: `src/knowledge_graphs/balanced_kg_generator_in20_in27.py`
- **行号**: 357-372
- **应用于**: 技能节点的 `score` 字段，不是边的 `weight`

---

## ❓ FAQ

**Q1: 为什么图中显示的权重是7.0而不是1.0？**  
A: 项目KG的边权重反映**匹配频率**，不是可信度。7.0表示该技能在项目描述中匹配分数为7。

**Q2: 权重7.0比1.0更重要吗？**  
A: 在项目KG中是的。分数越高=技能越重要/越核心。

**Q3: 学生KG和项目KG的权重能直接比较吗？**  
A: 不能！它们代表不同的含义：
- 学生KG: 可信度 (0-1)
- 项目KG: 匹配强度 (无上限)

**Q4: 为什么要用两种不同的系统？**  
A: 因为目标不同：
- 学生KG: 评估技能来源可靠性
- 项目KG: 评估技能需求重要性

**Q5: 权重上限是多少？**  
A: 
- 学生KG: 1.0（硬上限）
- 项目KG边: 无上限（实际通常<20）
- 项目KG节点score: 1.0（硬上限）

---

**文档更新时间**: 2025-10-03  
**更正原因**: 发现项目KG权重系统理解错误  
**影响范围**: enhanced_in20_in27 目录下的所有KG

