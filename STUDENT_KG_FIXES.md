# 学生知识图谱修复说明

## 🔍 发现的问题

通过检查生成的学生知识图谱可视化，发现以下问题：

### 1. ❌ 图例不完整
**原问题：**
- 左上角图例缺少 **MAJOR**（专业）节点说明
- 图例缺少 **PROJECT_EXPERIENCE**（项目经历）节点说明
- **INTEREST**（兴趣）标记错误：显示为红色圆圈，但实际应该是黄色
- 边的图例不完整：只显示了2种关系类型（TEACHES_SKILL 和 REQUIRES_SKILL）
- 缺少其他重要关系的说明（如学生→专业、学生→课程、学生→兴趣等）

**实际图中存在但图例缺失的元素：**
- ✅ 绿色圆圈：MAJOR（专业）- 图中有，但图例没说明
- ✅ 红色圆圈：PROJECT_EXPERIENCE（项目经历）- 图中有，但图例错误标记为INTEREST
- ✅ 黄色圆圈：INTEREST（兴趣）- 图中有，但图例标记错误
- ✅ 黄金色线：Student → Interest - 图中有，但图例没说明

### 2. ❌ 项目经历未被识别为独立节点
**原问题：**
- 项目经历以三级标题（`### 项目名称`）格式存在
- 原解析器只识别列表项（`- 项目`），无法解析三级标题格式
- 导致统计显示 `项目: 0`

**预期行为：**
- 应该将每个 `### 项目名称` 及其描述解析为独立的项目节点
- 从项目描述中提取技能关键词
- 创建 项目 → 技能 的连接

### 3. ❓ Edge Weight 是否需要显示
**问题：**
- 当前边有不同的权重值（0.6-1.0）
- 但在可视化中没有显示这些权重
- 需要确认是否应该在图上显示权重标签

## ✅ 修复方案

### 修复1: 完善图例系统

**改进：** 将图例分为两个部分 - 节点类型和关系类型

```python
# 节点类型图例（左上角）
node_legend_elements = [
    Student (青色大圆圈)
    Major (绿色圆圈)
    Course (紫色圆圈)
    Skill (蓝色圆圈)
    Project Experience (红色圆圈)  ← 新增
    Interest (黄色圆圈)            ← 修正颜色
]

# 关系类型图例（右上角）
edge_legend_elements = [
    Student → Major (深绿色实线)       ← 新增
    Student → Course (绿色实线)        ← 新增
    Course → Skill (紫色虚线)
    Student → Project (橙色实线)       ← 新增
    Project → Skill (红色点线)
    Student → Skill (蓝色实线)         ← 新增
    Student → Interest (金色实线)      ← 新增
]
```

**代码位置：** `src/knowledge_graphs/enhanced_student_kg.py` 第569-610行

### 修复2: 改进项目解析器

**改进：** 支持三级标题格式的项目

```python
def _parse_student_content(self, content: str):
    # 新增项目解析逻辑
    current_project_title = None
    current_project_desc = []
    
    # 当遇到 ### 项目标题
    if line.startswith('###'):
        # 保存之前的项目
        if current_project_title and current_project_desc:
            info['projects'].append(f"{title}: {' '.join(desc)}")
        
        # 开始新项目
        current_project_title = line.lstrip('### ').strip()
        current_project_desc = []
    
    # 收集项目描述
    elif current_project_title and line.strip():
        current_project_desc.append(line.strip())
```

**解析示例：**
```markdown
### Speech Emotion Recognition System  
Developed a machine learning model...

### Chatbot Sentiment Analysis Tool  
Designed a conversational agent...
```

解析结果：
```python
[
    "Speech Emotion Recognition System: Developed a machine learning model...",
    "Chatbot Sentiment Analysis Tool: Designed a conversational agent..."
]
```

**代码位置：** `src/knowledge_graphs/enhanced_student_kg.py` 第418-497行

### 修复3: 添加Edge Weight显示（可选功能）

**改进：** 添加参数控制是否显示边的权重

```python
def _create_enhanced_visualization(self, ..., show_edge_weights: bool = True):
    """
    创建增强版可视化
    
    Args:
        show_edge_weights: 是否显示边的权重标签
    """
    
    if show_edge_weights:
        edge_labels = {}
        for u, v, data in graph.edges(data=True):
            weight = data.get('weight', 1.0)
            # 只显示权重不为1.0的边，避免图过于拥挤
            if weight != 1.0:
                edge_labels[(u, v)] = f"{weight:.2f}"
        
        # 绘制边的权重标签
        nx.draw_networkx_edge_labels(
            graph, pos, edge_labels,
            font_size=6, 
            font_color='darkred',
            bbox=dict(boxstyle='round,pad=0.3', 
                     facecolor='white', 
                     alpha=0.7)
        )
```

**权重含义：**
- `1.0`: 学生→专业、学生→课程、学生→项目、学生→兴趣
- `0.9`: 课程→技能（TEACHES_SKILL）
- `0.8`: 学生→技能（通过课程获得）
- `0.75`: 学生→技能（通过项目获得）
- `0.7`: 项目→技能（REQUIRES_SKILL）
- `0.6`: 学生→技能（自学）

**代码位置：** `src/knowledge_graphs/enhanced_student_kg.py` 第495-503行，571-586行

## 📊 修复效果对比

### 修复前
```
Finley Thompson 知识图谱:
- 实体: 41 (无项目节点)
- 关系: 61
- 项目: 0 ❌
- 图例: 不完整 ❌
- Edge weights: 不显示
```

### 修复后
```
Finley Thompson 知识图谱:
- 实体: 46 (包含3个项目节点) ✅
- 关系: 70
- 项目: 3 ✅
  - Speech Emotion Recognition System
  - Chatbot Sentiment Analysis Tool
  - Interactive Audio Data Visualizer
- 图例: 完整（节点6种 + 关系7种） ✅
- Edge weights: 可选显示 ✅
```

### 新增连接
```
项目经历节点 → 技能节点:
- Speech Emotion Recognition → Machine Learning, Python
- Chatbot Sentiment Analysis → NLP, Machine Learning
- Interactive Audio Visualizer → Data Visualization, Web Development
```

## 🎨 可视化改进

### 图例布局

```
┌─────────────────────────────────────────────────────┐
│  Node Types (左上)          Relationships (右上)   │
│  ● Student (青色)           ─── Student → Major    │
│  ● Major (绿色)             ─── Student → Course   │
│  ● Course (紫色)            ---- Course → Skill    │
│  ● Skill (蓝色)             ─── Student → Project  │
│  ● Project Exp (红色)       ··· Project → Skill    │
│  ● Interest (黄色)          ─── Student → Skill    │
│                              ─── Student → Interest │
└─────────────────────────────────────────────────────┘
```

### Edge Weight显示

```
Course ────0.9───→ Skill
         (紫色虚线)

Project ·····0.7·····→ Skill
          (红色点线)

Student ────0.8───→ Skill
         (蓝色实线)
```

## 🧪 测试结果

### 测试文件
```bash
python test_enhanced_kg_single.py
```

### 输出
```
✅ 加载IN20数据: 120 节点
📚 构建课程-技能映射: 13 个课程
🎓 创建增强学生知识图谱: Finley Thompson (n00114716)
  ✅ 已保存: student_n00114716_Finley_Thompson
  📊 统计: 46 实体, 70 关系
     - 课程: 8, 技能: 28, 项目: 3 ✅

统计信息: {
    'total_entities': 46,
    'total_relationships': 70,
    'courses': 8,
    'skills': 28,
    'projects': 3,  ← 成功识别3个项目！
    'interests': 5,
    'skills_from_courses': 18,
    'skills_from_projects': 4  ← 从项目提取了4个技能！
}
```

## 📝 后续建议

### 批量重新生成
建议重新生成所有200个学生的知识图谱以应用修复：

```bash
python src/knowledge_graphs/enhanced_student_kg.py
```

### 可选配置
如果觉得边的权重标签太拥挤，可以关闭：

```python
self._create_enhanced_visualization(
    graph, entity_id, name, output_dir, base_filename,
    show_edge_weights=False  # 关闭权重显示
)
```

### 进一步优化
1. **项目-技能匹配精度**：可以扩展技能关键词库
2. **可交互可视化**：使用Plotly创建网页版图谱
3. **时间轴**：添加课程和项目的时间顺序

## 📚 相关文件

- ✅ `src/knowledge_graphs/enhanced_student_kg.py` - 已修复的生成器
- ✅ `test_enhanced_kg_single.py` - 单个测试脚本
- ✅ `outputs/knowledge_graphs/individual/enhanced_student_kg/` - 输出目录

---

**修复日期**: 2025-10-02  
**修复内容**: 图例完善、项目解析、边权重显示  
**状态**: ✅ 已完成并测试






