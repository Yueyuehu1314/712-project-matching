# 知识图谱权重规则详解

本文档详细说明 **enhanced_student_kg** 和 **enhanced_in20_in27** 两个目录下知识图谱的权重计算规则。

---

## ⚠️ 重要更正

**关于 enhanced_in20_in27 项目KG的权重范围**：

之前说明中提到"所有权重上限1.0"是**不准确的**。实际情况：

- ✅ **学生KG (enhanced_student_kg)**: 权重范围 0-1（归一化）
- ❌ **项目KG (enhanced_in20_in27) 的边权重**: **无上限**（通常2-20）
  - 边权重代表**匹配频率/重要性**，不是可信度
  - 常见值: 2.0, 3.0, 5.0, 7.0, 10.0 等
- ✅ **项目KG的节点score**: 范围 0-1（归一化）

**详细更正说明请查看**: `WEIGHT_SYSTEM_CORRECTION.md`

---

## 一、学生知识图谱 (enhanced_student_kg) 权重规则

### 📁 位置
`outputs/knowledge_graphs/individual/enhanced_student_kg/`

### 🏗️ 图谱结构
学生KG是以**学生为中心**的个人知识图谱，包含：
- **中心节点**：学生 (STUDENT)
- **第2层节点**：专业(MAJOR)、课程(COURSE)、项目经历(PROJECT_EXPERIENCE)、兴趣(INTEREST)
- **第3层节点**：技能(SKILL)

### ⚖️ 权重规则详解

#### 1. **学生 → 专业 (STUDIED_MAJOR)**
```
权重: 1.0 (固定)
```
- **含义**：学生修读某个专业
- **理由**：专业是学生背景的核心属性，权重固定为最高值

#### 2. **学生 → 课程 (COMPLETED_COURSE)**
```
权重: 1.0 (固定)
```
- **含义**：学生完成了某门课程
- **理由**：课程完成是确定性事实，权重固定

#### 3. **课程 → 技能 (TEACHES_SKILL)**
```
权重: 0.9
```
- **含义**：课程教授某个技能
- **理由**：
  - 课程教授技能是可靠的能力来源
  - 不是1.0是因为：学生可能只是"学过"但不一定"掌握"
  - 从IN20/IN27数据或默认课程-技能映射中提取

**代码位置**: `enhanced_student_kg.py` 第306行
```python
rel = EnhancedRelationship(course_id, skill_id, 'TEACHES_SKILL', weight=0.9)
```

#### 4. **学生 → 技能 (HAS_SKILL)** - 分三种来源

##### 4.1 通过课程获得的技能
```
权重: 0.8
属性: {'source': 'course'}
```
- **含义**：学生通过修读课程获得技能
- **理由**：
  - 比课程教授权重(0.9)略低，反映学习效果的不确定性
  - 学生完成课程 ≠ 完全掌握所有技能
  
**代码位置**: `enhanced_student_kg.py` 第312-316行
```python
rel = EnhancedRelationship(student_entity_id, skill_id, 'HAS_SKILL', 
                          weight=0.8, 
                          properties={'source': 'course'})
```

##### 4.2 通过项目经历获得的技能
```
权重: 0.75
属性: {'source': 'project'}
```
- **含义**：学生通过项目实践获得技能
- **理由**：
  - 比课程学习稍低(0.8 vs 0.75)
  - 项目经历中提到的技能不一定是核心技能
  - 从项目描述文本中用关键词匹配提取
  
**代码位置**: `enhanced_student_kg.py` 第359-363行
```python
rel = EnhancedRelationship(student_entity_id, skill_id, 'HAS_SKILL',
                          weight=0.75,
                          properties={'source': 'project'})
```

##### 4.3 自学/其他途径获得的技能
```
权重: 0.6
属性: {'source': 'self-taught'}
```
- **含义**：学生自述拥有的技能，但无法从课程或项目中验证
- **理由**：
  - 权重最低，因为无法验证
  - 可能是自学、工作经历、爱好等获得
  - 可信度相对较低
  
**代码位置**: `enhanced_student_kg.py` 第380-384行
```python
rel = EnhancedRelationship(student_entity_id, skill_id, 'HAS_SKILL',
                          weight=0.6,
                          properties={'source': 'self-taught'})
```

#### 5. **学生 → 项目经历 (PARTICIPATED_IN_PROJECT)**
```
权重: 1.0 (固定)
```
- **含义**：学生参与过某个项目
- **理由**：项目参与是事实陈述，权重固定

#### 6. **项目经历 → 技能 (REQUIRES_SKILL)**
```
权重: 0.7
```
- **含义**：项目经历需要/使用某个技能
- **理由**：
  - 从项目描述文本中提取，不如课程教授可靠
  - 可能存在关键词误匹配
  
**代码位置**: `enhanced_student_kg.py` 第353-355行
```python
rel = EnhancedRelationship(project_exp_id, skill_id, 'REQUIRES_SKILL', weight=0.7)
```

#### 7. **学生 → 兴趣 (INTERESTED_IN)**
```
权重: 1.0 (固定)
```
- **含义**：学生对某个领域感兴趣
- **理由**：兴趣是学生自述，作为事实接受

#### 8. **课程 → 课程 (PREREQUISITE_FOR)** - 新增
```
权重: 1.0 (固定)
```
- **含义**：某门课程是另一门课程的前置课程
- **理由**：
  - 课程依赖关系是明确的
  - 从IN27数据的unit_prerequisites提取
  
**代码位置**: `add_prerequisites_to_student_kg.py`

---

## 二、项目知识图谱 (enhanced_in20_in27) 权重规则

### 📁 位置
`outputs/knowledge_graphs/enhanced_in20_in27/`

### 🏗️ 图谱结构
项目KG是融合了 **PD (Project Description) + IN20 + IN27** 的综合知识图谱，包含：
- **中心节点**：项目 (PROJECT)
- **技能节点**：SKILL（根据数据来源分类）
- **课程节点**：UNIT（QUT课程）
- **专业节点**：MAJOR

### ⚖️ 权重规则详解

#### 1. **技能节点的分数 (score) - 多源融合**

技能节点根据**数据来源**和**支持度**分为四类：

##### 1.1 双重支持技能 (dual_supported)
```
类别: dual_supported
来源: IN20+IN27
基础分数: original_score
最终分数: min(original_score × 1.3, 1.0)
```
- **含义**：同时在IN20课程数据和IN27专业数据中出现的技能
- **权重加成**：1.3倍（最重要的技能）
- **理由**：
  - 被课程和专业双重认可
  - 是核心必备技能
  
**代码位置**: `balanced_kg_generator_in20_in27.py` 第357-360行
```python
if in20_support and in27_support:
    category = "dual_supported"
    source = "IN20+IN27"
    score = support_info['score'] * 1.3  # 双重支持加权
```

##### 1.2 单一支持技能 (supported) - IN20来源
```
类别: supported
来源: IN20
基础分数: original_score
最终分数: original_score × 1.0
```
- **含义**：仅在IN20课程数据中出现的技能
- **权重加成**：1.0倍（无加成）
- **理由**：被课程认可，可靠但非核心

**代码位置**: `balanced_kg_generator_in20_in27.py` 第362-364行
```python
elif in20_support:
    category = "supported"
    source = "IN20"
    score = support_info['score'] * 1.0
```

##### 1.3 单一支持技能 (supported) - IN27来源
```
类别: supported
来源: IN27
基础分数: original_score
最终分数: original_score × 1.0
```
- **含义**：仅在IN27专业数据中出现的技能
- **权重加成**：1.0倍（无加成）
- **理由**：被专业要求认可

**代码位置**: `balanced_kg_generator_in20_in27.py` 第365-368行
```python
elif in27_support:
    category = "supported"
    source = "IN27"
    score = support_info['score'] * 1.0
```

##### 1.4 扩展技能 (extended) - 仅PD来源
```
类别: extended
来源: PD
基础分数: original_score
最终分数: original_score × 0.8
```
- **含义**：仅在项目描述(PD)中提到，但未被IN20/IN27支持
- **权重惩罚**：0.8倍（最低可信度）
- **理由**：
  - 可能是项目特定的、过于细化的技能
  - 或者是关键词提取误匹配
  - 缺乏学术支持

**代码位置**: `balanced_kg_generator_in20_in27.py` 第369-372行
```python
else:
    category = "extended"
    source = "PD"
    score = support_info['score'] * 0.8
```

#### 2. **项目 → 技能 (REQUIRES_SKILL)**
```
权重: 技能节点的score值（动态）
```
- **含义**：项目需要某个技能
- **权重**：等于技能节点的分数，反映技能的重要性和可信度
  
**代码位置**: `balanced_kg_generator_in20_in27.py` 第429-436行
```python
enhanced_edges.append(EnhancedKGEdge(
    source=project_node.id,
    target=support_info['id'],
    relation="REQUIRES_SKILL",
    weight=support_info['score'],  # 使用技能的分数
    category=support_info.get('category', 'extended'),
    source_type="PD"
))
```

#### 3. **技能 → 课程 (TAUGHT_IN)**
```
权重: 1.0 (固定) 或 从IN20边继承
```
- **含义**：技能在某门课程中教授
- **权重**：
  - 如果从IN20数据直接提取，权重为IN20中的值（通常1.0）
  - 如果是模糊匹配得到，权重可能略低

**代码位置**: `balanced_kg_generator_in20_in27.py` 第523-529行
```python
enhanced_edges.append(EnhancedKGEdge(
    source=target_id,  # skill
    target=unit_nodes_map[source_code],  # unit
    relation="TAUGHT_IN",
    weight=edge.get('weight', 1.0),
    source_type="IN20"
))
```

#### 4. **课程 → 课程 (PREREQUISITE_FOR)**
```
权重: 1.0 (固定)
```
- **含义**：课程前置关系
- **从IN27的unit_prerequisites数据中提取

**代码位置**: `balanced_kg_generator_in20_in27.py` 第550-558行
```python
for unit_code, prereqs in unit_prereqs_map.items():
    for prereq_code in prereqs:
        if prereq_code in unit_nodes_map:
            enhanced_edges.append(EnhancedKGEdge(
                source=unit_nodes_map[prereq_code],
                target=unit_nodes_map[unit_code],
                relation="PREREQUISITE_FOR",
                weight=1.0,
                source_type="IN27"
            ))
```

#### 5. **项目 → 专业 (REQUIRES_MAJOR)**
```
权重: 1.0 (固定)
```
- **含义**：项目需要某个专业背景
- **从项目描述中提取

#### 6. **专业 → 课程 (INCLUDES_UNIT)**
```
权重: 1.0 (固定)
```
- **含义**：专业包含某门课程
- **从IN27专业数据中提取

---

## 三、权重设计哲学

### 🎯 核心原则

1. **可验证性优先**
   - 有明确来源的关系权重更高
   - 课程学习(0.9/0.8) > 项目经历(0.75/0.7) > 自述(0.6)

2. **多源验证加权**
   - IN20+IN27双重支持：×1.3
   - 单一来源：×1.0
   - 仅PD提取：×0.8

3. **学习效果折扣**
   - 课程教授(0.9) > 学生掌握(0.8)
   - 反映"学过 ≠ 会用"的现实

4. **保守估计**
   - 所有权重上限1.0
   - 不确定的关系给予较低权重
   - 避免过度夸大匹配分数

### 📊 权重对比表

| 关系类型 | 权重 | 所属KG | 可信度 |
|---------|------|--------|--------|
| PREREQUISITE_FOR | 1.0 | 两者 | ⭐⭐⭐⭐⭐ |
| STUDIED_MAJOR | 1.0 | 学生 | ⭐⭐⭐⭐⭐ |
| COMPLETED_COURSE | 1.0 | 学生 | ⭐⭐⭐⭐⭐ |
| INTERESTED_IN | 1.0 | 学生 | ⭐⭐⭐⭐ |
| TEACHES_SKILL | 0.9 | 学生 | ⭐⭐⭐⭐ |
| HAS_SKILL (course) | 0.8 | 学生 | ⭐⭐⭐⭐ |
| HAS_SKILL (project) | 0.75 | 学生 | ⭐⭐⭐ |
| REQUIRES_SKILL | 0.7 | 学生 | ⭐⭐⭐ |
| HAS_SKILL (self-taught) | 0.6 | 学生 | ⭐⭐ |
| REQUIRES_SKILL (dual) | score×1.3 | 项目 | ⭐⭐⭐⭐⭐ |
| REQUIRES_SKILL (IN20/27) | score×1.0 | 项目 | ⭐⭐⭐⭐ |
| REQUIRES_SKILL (PD only) | score×0.8 | 项目 | ⭐⭐⭐ |

---

## 四、实际应用示例

### 示例1：学生KG中的技能权重
假设学生**张三**：
- 修读了课程 IFN666 (Web Development)
- 参与项目"E-commerce Website"
- 自述技能"React"

**权重分配**：
```
张三 --[COMPLETED_COURSE, 1.0]--> IFN666
IFN666 --[TEACHES_SKILL, 0.9]--> Web Development
张三 --[HAS_SKILL, 0.8, source=course]--> Web Development

张三 --[PARTICIPATED_IN_PROJECT, 1.0]--> E-commerce Project
E-commerce Project --[REQUIRES_SKILL, 0.7]--> JavaScript
张三 --[HAS_SKILL, 0.75, source=project]--> JavaScript

张三 --[HAS_SKILL, 0.6, source=self-taught]--> React
```

**解读**：
- Web Development：权重0.8（课程来源，最可信）
- JavaScript：权重0.75（项目来源，中等可信）
- React：权重0.6（无法验证，可信度最低）

### 示例2：项目KG中的技能分类
假设项目"AI Chatbot"需要技能：
- Machine Learning（IN20有，IN27有）
- Python（IN20有，IN27无）
- GPT API（仅PD提到）

**权重分配**：
```
Machine Learning:
  category: dual_supported
  source: IN20+IN27
  score: 0.85 × 1.3 = 1.0 (上限)
  
Python:
  category: supported
  source: IN20
  score: 0.75 × 1.0 = 0.75
  
GPT API:
  category: extended
  source: PD
  score: 0.60 × 0.8 = 0.48
```

**解读**：
- Machine Learning是最核心技能（双重认可，权重1.0）
- Python是重要但非核心技能（单一支持，权重0.75）
- GPT API是项目特定技能（无学术支持，权重0.48）

---

## 五、使用建议

### 🔍 查看可视化图片时

1. **学生KG**：
   - 查找边标签中的权重值
   - 识别`source`属性（course/project/self-taught）
   - 权重越高的技能越可信

2. **项目KG**：
   - 识别技能节点的颜色（category）
   - dual_supported技能优先匹配
   - extended技能谨慎考虑

### ⚙️ 调整权重时

如需调整权重，修改以下文件：

- **学生KG权重**：`src/knowledge_graphs/enhanced_student_kg.py`
  - 第306行：TEACHES_SKILL (0.9)
  - 第313行：HAS_SKILL from course (0.8)
  - 第360行：HAS_SKILL from project (0.75)
  - 第353行：REQUIRES_SKILL (0.7)
  - 第381行：HAS_SKILL self-taught (0.6)

- **项目KG权重**：`src/knowledge_graphs/balanced_kg_generator_in20_in27.py`
  - 第360行：dual_supported multiplier (1.3)
  - 第364行：IN20 multiplier (1.0)
  - 第368行：IN27 multiplier (1.0)
  - 第372行：PD-only multiplier (0.8)

---

## 六、常见问题 FAQ

**Q1: 为什么课程教授技能是0.9而不是1.0？**
A: 反映"教过≠学会"的现实。学生可能通过了课程但未完全掌握所有技能。

**Q2: 为什么自学技能权重这么低(0.6)？**
A: 因为无法验证。学生可能高估自己的能力，也可能只是略有了解。

**Q3: 双重支持为什么是1.3倍而不是2.0倍？**
A: 避免权重过高。1.3倍已经足够体现重要性，且确保最终权重不超过1.0。

**Q4: PREREQUISITE_FOR为什么固定1.0？**
A: 这是明确的课程依赖关系，没有不确定性，因此固定为最高权重。

**Q5: 如何知道一个技能是dual_supported？**
A: 查看可视化图片的图例，或查看JSON中的`category`和`source`字段。

---

**文档生成时间**: 2025-10-03  
**对应代码版本**: enhanced_student_kg.py, balanced_kg_generator_in20_in27.py  
**维护者**: Lynn

