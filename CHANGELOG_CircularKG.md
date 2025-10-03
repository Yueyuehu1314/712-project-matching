# 知识图谱可视化改进 - 完整层级结构

## 📅 更新时间
2025-10-02 (最新版本)

## 🎯 改进目标
恢复并优化完整的四层知识图谱结构，清晰展示：**PROJECT → SKILL → UNIT → PROGRAM**

## ✨ 主要变化

### 1. **保留完整层级节点** ✅
- ✅ `PROJECT` 节点 - 项目需求
- ✅ `SKILL` 节点 - 所需技能
- ✅ `UNIT` 节点 - 教授该技能的课程单元
- ✅ `PROGRAM` 节点 - 课程所属的学位项目（Master of IT, Bachelor等）

### 2. **采用层级布局（从左到右）**
- 📍 **第1层（PROJECT）**: 项目节点位于最左侧 (x=0)
- 📍 **第2层（SKILL）**: 技能节点位于第二列 (x=4)
- 📍 **第3层（UNIT）**: 课程单元节点位于第三列 (x=8)
- 📍 **第4层（PROGRAM）**: 学位项目节点位于最右侧 (x=12)
- 📏 Y轴根据同层节点数量自动调整，确保均匀分布

### 3. **优化视觉效果**
#### 节点颜色和大小：
- 🔴 **PROJECT**: `#FF6B6B` (粉红色) - 6000 大小
- 🟢 **SKILL (双重支持)**: `#26de81` (鲜绿色) - 3000 大小 - 同时被IN20和IN27支持
- 🔵 **SKILL (IN20)**: `#4ECDC4` (青色) - 3000 大小 - 课程支持
- 🟣 **SKILL (IN27)**: `#9b59b6` (紫色) - 3000 大小 - 教学大纲支持  
- 🟠 **SKILL (PD扩展)**: `#FFB347` (橙色) - 3000 大小 - 仅项目描述中提到
- 🟡 **UNIT**: `#FFD93D` (黄色) - 2500 大小 - 课程单元
- 🟣 **PROGRAM**: `#A569BD` (紫罗兰) - 2800 大小 - 学位项目

#### 边样式和关系：
- 🔴 **PROJECT → SKILL**: REQUIRES_SKILL (项目需要的技能)
- 🔵 **SKILL → UNIT**: TAUGHT_IN (技能在哪个课程单元中教授)
- 🟣 **UNIT → PROGRAM**: BELONGS_TO (课程单元属于哪个学位项目)

### 4. **完整图例**
包含所有节点和边类型：
- 1个PROJECT节点
- 4种SKILL类型（双重支持、IN20、IN27、PD扩展）
- UNIT节点（课程单元）
- PROGRAM节点（学位项目）
- 3种边类型关系

## 📊 层级结构示例

```
[PROJECT]  →  [SKILL1]  →  [UNIT1]  →  [PROGRAM1]
               [SKILL2]  →  [UNIT2]  →  [PROGRAM2]
               [SKILL3]  →  [UNIT3]  →  [PROGRAM1]
               [SKILL4]  →  [UNIT4]  →  [PROGRAM3]
               ...           ...          ...

从左到右四层结构，清晰展示：
1. 项目需要哪些技能
2. 每个技能在哪些课程单元中教授
3. 这些课程单元属于哪些学位项目
```

## 📁 输出文件

每个项目生成3个文件：
1. **`*_enhanced_kg.json`** - JSON格式数据（包含所有节点和边信息）
2. **`*_enhanced_kg_full.png`** - 完整版层级图 ⭐推荐（显示全部四层）
3. **`*_enhanced_kg_simple.png`** - 简化版圆环图（仅显示项目和技能）

## 📈 统计信息

- **处理项目数**: 20个
- **成功率**: 100% (20/20)
- **平均节点数**: 128-130个 (包括PROJECT + SKILL + UNIT + PROGRAM)
- **平均技能数**: 7-9个
- **平均UNIT数**: 约100-120个课程单元
- **平均PROGRAM数**: 2-3个学位项目
- **平均边数**: 115-120条（包括所有层级关系）

## 🔧 技术实现

### 关键代码修改：

1. **恢复UNIT/PROGRAM节点** (`create_enhanced_balanced_kg` 第277-302行)
```python
# 3.3 添加IN20中的Unit和Program节点
for node in in20_nodes:
    if node['type'] == 'UNIT':
        unit_node = EnhancedKGNode(id=unit_id, name=node['name'], 
                                    type='UNIT', score=1.0)
        enhanced_nodes.append(unit_node)
    elif node['type'] == 'PROGRAM':
        program_node = EnhancedKGNode(id=program_id, name=node['name'],
                                       type='PROGRAM', score=1.0)
        enhanced_nodes.append(program_node)
```

2. **添加完整边关系** (`create_enhanced_balanced_kg` 第320-343行)
```python
# 4.2 添加IN20的结构边（技能->Unit, Unit->Program）
for edge in in20_edges:
    # SKILL → UNIT 边
    if source_id.startswith('skill_') and target_id in unit_nodes_map:
        enhanced_edges.append(EnhancedKGEdge(source=source_id, 
                                             target=unit_id,
                                             relation="TAUGHT_IN"))
    # UNIT → PROGRAM 边
    elif source_id in unit_nodes_map and target_id in program_nodes_map:
        enhanced_edges.append(EnhancedKGEdge(source=unit_id,
                                             target=program_id,
                                             relation="BELONGS_TO"))
```

3. **层级布局算法** (`_create_hierarchical_layout` 第829-873行)
```python
# 创建四层从左到右的布局
layer_x = {'PROJECT': 0, 'SKILL': 4, 'UNIT': 8, 'PROGRAM': 12}

# 布置PROJECT节点（左侧）
pos[project_node.id] = (layer_x['PROJECT'], 0)

# 布置SKILL节点（第二列，垂直分布）
for i, skill in enumerate(skill_nodes):
    pos[skill.id] = (layer_x['SKILL'], y_start + i * 2)

# 布置UNIT节点（第三列）
for i, unit in enumerate(unit_nodes):
    pos[unit.id] = (layer_x['UNIT'], y_start + i * 1.5)

# 布置PROGRAM节点（最右侧）
for i, program in enumerate(program_nodes):
    pos[program.id] = (layer_x['PROGRAM'], y_start + i * 3)
```

4. **完整可视化** (`create_enhanced_visualization` 第456-473行)
```python
# 不过滤，显示所有节点和边
G = nx.DiGraph()
for node in nodes:  # 包括PROJECT, SKILL, UNIT, PROGRAM
    G.add_node(node.id, **asdict(node))
for edge in edges:  # 包括所有层级关系
    G.add_edge(edge.source, edge.target, **asdict(edge))
```

## ✅ 验证

所有20个项目成功生成完整层级知识图谱：
- ✅ HAR_WiFi_Proposal_Zhenguo-1 (129节点, 116边)
- ✅ Feature Selection Impact on IoT Attack Detection (130节点, 117边)
- ✅ Leveraging IoT for Smart City Solutions (129节点, 116边)
- ✅ VitalID Authentication (130节点, 117边)
- ✅ Plant Health Monitoring (130节点, 117边)
- ✅ ... 共20个项目，全部成功 ✅

### 知识图谱包含完整信息：
- 每个项目需要的技能 (SKILL)
- 每个技能在哪些课程单元中教授 (UNIT)
- 每个课程单元属于哪个学位项目 (PROGRAM: Master of IT, Bachelor等)

## 📍 文件位置

生成的图谱保存在：
```
outputs/knowledge_graphs/enhanced_in20_in27/
├── [项目标题1]/
│   ├── *_enhanced_kg.json
│   ├── *_enhanced_kg_full.png
│   └── *_enhanced_kg_simple.png
├── [项目标题2]/
│   └── ...
...
```

---

## 🎓 应用价值

这个完整的四层知识图谱可以回答：

1. **项目匹配**: 学生需要学习哪些课程才能胜任某个项目？
2. **技能映射**: 某个技能在哪些课程中被教授？
3. **课程推荐**: 对于特定项目，推荐哪些UNIT和PROGRAM？
4. **差距分析**: 学生已有技能 vs 项目需求技能的差距
5. **学位对比**: 不同学位项目(Master/Bachelor)对项目的支持程度

---

**生成器**: `src/knowledge_graphs/balanced_kg_generator_in20_in27.py`
**版本**: v3.0 - Complete Hierarchical Layout (PROJECT → SKILL → UNIT → PROGRAM)
**日期**: 2025-10-02
