# 3层项目知识图谱 - 权重可视化更新

## ✅ 更新内容

### 问题
之前生成的3层项目知识图谱虽然在JSON文件中存储了权重，但**图片上看不到权重标签**。

### 解决方案
修改了 `three_layer_project_kg.py` 的可视化函数，**添加了边的权重标签显示**。

---

## 🎨 可视化改进

### 改进前 ❌
- 边上没有任何标签
- 无法直观看出关系的权重
- 需要查看JSON文件才能知道权重

### 改进后 ✅
- **红色权重标签**显示在边上
- 白色半透明背景，易于阅读
- 字体大小7，清晰不遮挡节点
- **默认只显示非1.0的权重**（减少视觉干扰）

---

## 📊 当前权重体系

### 固定权重方案

| 关系类型 | 权重 | 是否显示 | 含义 |
|---------|------|---------|------|
| **REQUIRES_DOMAIN** | 1.0 | ❌ 不显示 | Project → Domain |
| **INCLUDES** | 0.8 | ✅ 显示 | Domain → Skill/Major |
| **USES_TECH** | 0.9 | ✅ 显示 | Domain → Technology |

### 显示逻辑

```python
# 默认模式：只显示非1.0的权重
for u, v, data in G.edges(data=True):
    weight = data.get('weight', 1.0)
    if weight != 1.0:  # 只显示0.8和0.9
        edge_labels[(u, v)] = f"{weight:.1f}"
```

**优势**：
- ✅ 减少视觉干扰（Project → Domain 的1.0权重太常见）
- ✅ 突出重要信息（0.8和0.9的差异）
- ✅ 图片更简洁清晰

---

## 🔧 可选功能

### 显示所有权重（包括1.0）

如果需要显示**所有权重**（包括1.0），可以修改代码：

```python
# 在 three_layer_project_kg.py 的 _save_three_layer_kg 函数中
self._visualize_three_layer_kg(G, project_title, output_dir, safe_title, 
                               show_all_weights=True)  # 设为True
```

**效果**：
- Project → Domain 的边上也会显示 `1.0`
- 所有边都有权重标签

**建议**：
- 如果图谱较简单（<10个节点）→ 可以显示所有权重
- 如果图谱较复杂（>15个节点）→ 只显示非1.0权重（当前默认）

---

## 📁 更新的文件

### 修改的代码
- `src/knowledge_graphs/three_layer_project_kg.py`
  - 第607-618行：添加了 `show_all_weights` 参数
  - 第707-718行：添加了边权重标签绘制逻辑

### 重新生成的输出
- `outputs/knowledge_graphs/individual/three_layer_projects/*.png`
  - 所有20个项目的知识图谱已更新
  - 现在都显示权重标签（0.8和0.9）

---

## 🎯 可视化示例

### 简单项目（9个节点）
**AI-Based Human Activity Recognition**

- 3个Domain节点
- 5个Skill/Tech节点
- 权重标签：`0.8`（Skill）、`0.9`（Tech）
- 清晰的放射状布局

### 复杂项目（14个节点）
**IoT-Based Spectral Sensing**

- 5个Domain节点
- 8个Skill/Tech节点
- 权重标签分布在各条边上
- 扇形分组避免重叠

---

## 💡 权重含义

### 当前固定权重的语义

| 权重 | 含义 | 设计理由 |
|-----|------|---------|
| **1.0** | Project需要这个Domain | Domain是项目的必需领域，权重最高 |
| **0.9** | Domain使用这个Technology | Technology是该领域的核心工具，权重较高 |
| **0.8** | Domain包含这个Skill/Major | Skill是该领域的一部分，但可能不是唯一来源 |

### 为什么0.9 > 0.8？

- **Technology（0.9）**：通常是具体的工具/框架，使用明确
  - 例如：Machine Learning & AI → TensorFlow (0.9)
  
- **Skill（0.8）**：可能在多个领域都有，不够唯一
  - 例如：Machine Learning & AI → Deep Learning (0.8)
  - Deep Learning 也可能在 Computer Vision 领域中

---

## 🚀 未来改进方向

如果需要**更精确的权重系统**，可以考虑以下方案：

### 方案1：基于技能重要性的动态权重
```python
# 核心技能
weight = 1.0 if is_core_skill else 0.6

# 示例
Deep Learning → 1.0 (核心)
Testing → 0.6 (辅助)
```

### 方案2：与enhanced_in20_in27对齐
```python
# 从现有项目KG中读取权重，归一化到0.5-1.0
existing_weight = 10.0  # 来自 enhanced_in20_in27
normalized = 0.5 + (existing_weight / 20.0) * 0.5  # → 0.75
```

### 方案3：基于频率的权重
```python
# 技能在项目描述中的出现次数
occurrences = count_skill_in_description(skill)
weight = min(1.0, 0.5 + occurrences * 0.1)
```

**建议**：
- 如果只用于**可视化**：保持当前固定权重 ✅
- 如果用于**项目-学生匹配**：考虑方案2（对齐existing KG）

---

## 📝 技术细节

### 边标签样式
```python
nx.draw_networkx_edge_labels(
    G, pos, edge_labels, 
    font_size=7,           # 小字体，不遮挡
    font_color='red',      # 红色醒目
    bbox=dict(
        boxstyle="round,pad=0.2",  # 圆角矩形
        facecolor='white',          # 白色背景
        alpha=0.7,                  # 70%透明度
        edgecolor='none'            # 无边框
    )
)
```

### 权重格式化
```python
edge_labels[(u, v)] = f"{weight:.1f}"  # 保留1位小数
# 例如: 0.8, 0.9, 1.0
```

---

## ✅ 验证清单

- [x] 权重已存储在JSON文件中
- [x] 权重已显示在PNG图片上
- [x] 只显示非1.0权重（减少干扰）
- [x] 红色标签清晰可读
- [x] 所有20个项目已重新生成
- [x] 放射状布局保持完好
- [x] 标签不遮挡节点

---

## 🎉 总结

**问题已解决！** ✅

现在的3层项目知识图谱：
1. ✅ **结构清晰**：3层层次（Project → Domain → Details）
2. ✅ **布局美观**：中心放射状，扇形分组
3. ✅ **权重可见**：红色标签显示在边上
4. ✅ **简洁直观**：只显示关键权重（0.8, 0.9）
5. ✅ **可扩展**：支持future动态权重系统

**如需进一步优化权重计算策略，请参考 `THREE_LAYER_WEIGHT_OPTIONS.md`**



