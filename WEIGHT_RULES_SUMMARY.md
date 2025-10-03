# 知识图谱权重规则速查表

## ⚠️ 重要更正

**项目KG的边权重无上限！** 常见值: 2.0, 3.0, 5.0, 7.0, 10.0等  
详见 `WEIGHT_SYSTEM_CORRECTION.md`

---

## 📊 快速对比

### 学生知识图谱 (enhanced_student_kg)

| 关系类型 | 权重 | 含义 | 可信度 |
|---------|------|------|--------|
| **STUDIED_MAJOR** | 1.0 | 学生修读专业 | ⭐⭐⭐⭐⭐ |
| **COMPLETED_COURSE** | 1.0 | 学生完成课程 | ⭐⭐⭐⭐⭐ |
| **PREREQUISITE_FOR** | 1.0 | 课程前置关系 | ⭐⭐⭐⭐⭐ |
| **INTERESTED_IN** | 1.0 | 学生研究兴趣 | ⭐⭐⭐⭐ |
| **PARTICIPATED_IN_PROJECT** | 1.0 | 参与项目经历 | ⭐⭐⭐⭐⭐ |
| **TEACHES_SKILL** | 0.9 | 课程教授技能 | ⭐⭐⭐⭐ |
| **HAS_SKILL** (course) | 0.8 | 通过课程获得技能 | ⭐⭐⭐⭐ |
| **HAS_SKILL** (project) | 0.75 | 通过项目获得技能 | ⭐⭐⭐ |
| **REQUIRES_SKILL** | 0.7 | 项目经历需要技能 | ⭐⭐⭐ |
| **HAS_SKILL** (self-taught) | 0.6 | 自学技能（无法验证） | ⭐⭐ |

### 项目知识图谱 (enhanced_in20_in27)

#### 节点分数 (0-1范围)
| 技能类型 | score计算 | 含义 | 可信度 |
|---------|----------|------|--------|
| **Skill (dual_supported)** | base × 1.3, max=1.0 | IN20+IN27双重认可 | ⭐⭐⭐⭐⭐ |
| **Skill (IN20)** | base × 1.0, max=1.0 | 仅IN20课程支持 | ⭐⭐⭐⭐ |
| **Skill (IN27)** | base × 1.0, max=1.0 | 仅IN27专业支持 | ⭐⭐⭐⭐ |
| **Skill (PD only)** | base × 0.8, max=1.0 | 仅项目描述提及 | ⭐⭐⭐ |

#### 边权重 (无上限！)
| 关系类型 | 权重范围 | 含义 | 说明 |
|---------|---------|------|------|
| **REQUIRES_SKILL** | 2-20 | 匹配分数 | 越高=越核心 |
| **TAUGHT_IN** | 2-10 | 匹配分数 | 技能-课程关联度 |
| **PREREQUISITE_FOR** | 1.0 | 固定 | 课程前置关系 |
| **REQUIRES_MAJOR** | 1.0 | 固定 | 项目需要专业 |
| **INCLUDES_UNIT** | 1.0 | 固定 | 专业包含课程 |

---

## 🔑 核心设计原则

### 1. **可验证性优先**
```
课程学习 (0.9/0.8) > 项目经历 (0.75/0.7) > 自述 (0.6)
```
- 有明确来源的关系权重更高
- 可以追溯验证的信息更可信

### 2. **多源验证加权**
```
IN20 + IN27 (×1.3) > 单一来源 (×1.0) > 仅PD (×0.8)
```
- 双重支持的技能获得加成
- 学术认可优于项目描述

### 3. **学习效果折扣**
```
课程教授 (0.9) > 学生掌握 (0.8)
```
- 反映"学过 ≠ 会用"的现实
- 为学习效果保留不确定性空间

### 4. **保守估计**
```
所有权重上限 1.0
```
- 避免过度夸大匹配分数
- 不确定的关系给予较低权重

---

## 💡 实战示例

### 示例1：学生张三的技能权重

**背景**：
- 修读课程：IFN666 Web Development
- 项目经历：E-commerce Website (提到"JavaScript")
- 自述技能：React

**权重分配**：
```
张三 --[1.0]--> IFN666 --[0.9]--> Web Development
张三 --[0.8, source=course]--> Web Development          ✅ 最可信

张三 --[1.0]--> E-commerce --[0.7]--> JavaScript
张三 --[0.75, source=project]--> JavaScript            ⚠️ 中等可信

张三 --[0.6, source=self-taught]--> React              ❌ 无法验证
```

### 示例2：项目AI Chatbot的技能分类

**背景**：
- Machine Learning：IN20有，IN27有
- Python：IN20有，IN27无
- GPT API：仅PD提到

**权重计算**：
```
Machine Learning:
  category: dual_supported
  source: IN20+IN27
  base: 0.85, final: 0.85 × 1.3 = 1.0 (上限)     ⭐⭐⭐⭐⭐

Python:
  category: supported
  source: IN20
  base: 0.75, final: 0.75 × 1.0 = 0.75           ⭐⭐⭐⭐

GPT API:
  category: extended
  source: PD
  base: 0.60, final: 0.60 × 0.8 = 0.48           ⭐⭐⭐
```

---

## 📂 相关文件

### 源代码
- **学生KG**: `src/knowledge_graphs/enhanced_student_kg.py`
- **项目KG**: `src/knowledge_graphs/balanced_kg_generator_in20_in27.py`

### 权重定义位置
| 权重类型 | 文件 | 行号 |
|---------|------|------|
| TEACHES_SKILL (0.9) | enhanced_student_kg.py | 306 |
| HAS_SKILL course (0.8) | enhanced_student_kg.py | 313 |
| HAS_SKILL project (0.75) | enhanced_student_kg.py | 360 |
| REQUIRES_SKILL (0.7) | enhanced_student_kg.py | 353 |
| HAS_SKILL self (0.6) | enhanced_student_kg.py | 381 |
| dual_supported (×1.3) | balanced_kg_generator_in20_in27.py | 360 |
| IN20/IN27 (×1.0) | balanced_kg_generator_in20_in27.py | 364, 368 |
| PD only (×0.8) | balanced_kg_generator_in20_in27.py | 372 |

### 可视化文件
- **权重对比图**: `WEIGHT_RULES_COMPARISON.png`
- **流程图**: `WEIGHT_FLOW_DIAGRAM.png`
- **详细文档**: `WEIGHT_RULES_EXPLANATION.md`

---

## 🔧 如何查看权重

### 1. 查看JSON文件
```json
{
  "relationships": [
    {
      "source_id": "student_n12345678",
      "target_id": "skill_python",
      "relation_type": "HAS_SKILL",
      "weight": 0.8,
      "properties": {
        "source": "course"
      }
    }
  ]
}
```

### 2. 查看可视化图片
- **学生KG**: 边标签显示权重（如果≠1.0）
- **项目KG**: 节点颜色区分类别，边显示权重

### 3. 使用可视化脚本
```bash
# 为学生KG生成可视化（显示权重）
python visualize_student_kg_with_prereq.py \
  --kg-dir outputs/knowledge_graphs/individual/enhanced_student_kg

# 为项目KG生成可视化
python test_in20_in27_generator.py
```

---

## ❓ 常见问题

**Q: 为什么课程教授是0.9不是1.0？**  
A: 反映"教过≠学会"。学生可能通过课程但未完全掌握技能。

**Q: 为什么自学技能只有0.6？**  
A: 无法验证。学生可能高估能力或只是略有了解。

**Q: 双重支持为什么是1.3倍？**  
A: 体现重要性，但避免过高。确保最终≤1.0。

**Q: 如何修改权重？**  
A: 编辑对应文件中的权重值，重新运行生成脚本。

---

**最后更新**: 2025-10-03  
**版本**: enhanced_student_kg.py, balanced_kg_generator_in20_in27.py

