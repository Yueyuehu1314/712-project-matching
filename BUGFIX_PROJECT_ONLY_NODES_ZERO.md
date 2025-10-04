# 🐛 Bug修复：project_only_nodes 为0的问题

> 日期: 2025-10-04  
> 问题: Method 2a 结果中 project_only_nodes 全部为0  
> 状态: ✅ 已修复

---

## 🔍 问题发现

在 `outputs/kg_similarity/method_2a_scores.json` 中发现：

```json
{
  "project_name": "Smart_Intersection_Localization",
  "student_id": "student_n01087640_Casey_Moore_enhanced_kg",
  "is_match": true,
  "jaccard_similarity": 0.0,
  "edit_distance": 37,
  "common_nodes": 0,
  "project_only_nodes": 0,  ← 所有记录都是0！
  "student_only_nodes": 37
}
```

**异常表现：**
- ✅ student_only_nodes: 正常（37个）
- ❌ project_only_nodes: 异常（0个）
- ❌ common_nodes: 异常（0个）
- ❌ jaccard_similarity: 异常（0.0）

但从可视化图片可以看到，项目KG明显有很多节点（约10-12个）！

---

## 🕵️ 根因分析

### 问题1: JSON 格式不匹配

**three_layer_projects** 使用 **数组格式**:
```json
// *_entities.json
[
  {"id": "project_xxx", "name": "...", ...},
  {"id": "domain_yyy", "name": "...", ...}
]
```

**enhanced_student_kg** 使用 **字典格式**:
```json
// *_enhanced_kg.json
{
  "entities": [...],
  "relationships": [...]
}
```

### 问题2: 代码只处理字典格式

原 `extract_node_ids` 方法：
```python
def extract_node_ids(kg_data: Dict) -> Set[str]:
    nodes = set()
    
    if 'nodes' in kg_data:  # 查找 kg_data['nodes']
        ...
    if 'entities' in kg_data:  # 查找 kg_data['entities']
        ...
    
    return nodes  # 对于数组格式，返回空集合！
```

**结果**：项目KG被加载为数组，但 `extract_node_ids` 没有处理数组格式，导致返回空集合。

### 问题3: 分离的 entities 和 relationships 文件

three_layer_projects 的结构：
```
A_Systematic_Review_of_Deep_entities.json       ← 只加载了这个
A_Systematic_Review_of_Deep_relationships.json  ← 没有加载
```

原代码只加载了 `*_entities.json`，没有加载对应的 relationships 文件。

---

## ✅ 解决方案

### 修复1: 更新 `load_kg_json` 方法

```python
@staticmethod
def load_kg_json(file_path: str) -> Dict:
    """加载KG JSON文件
    
    支持两种格式:
    1. 单个文件包含entities和relationships (enhanced_student_kg)
    2. 分离的entities和relationships文件 (three_layer_projects)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 如果已经是字典格式且包含entities，直接返回
    if isinstance(data, dict) and 'entities' in data:
        return data
    
    # 如果是数组格式（three_layer_projects），需要加载对应的relationships文件
    if isinstance(data, list):
        if '_entities.json' in file_path:
            # 尝试加载对应的relationships文件
            rel_file = file_path.replace('_entities.json', '_relationships.json')
            relationships = []
            if Path(rel_file).exists():
                with open(rel_file, 'r', encoding='utf-8') as f:
                    relationships = json.load(f)
            
            # 返回标准格式
            return {
                'entities': data,
                'relationships': relationships
            }
    
    return data
```

### 修复2: 更新 `extract_node_ids` 方法

```python
@staticmethod
def extract_node_ids(kg_data) -> Set[str]:
    """提取知识图谱中的所有节点ID
    
    支持两种格式:
    1. 数组格式: [{id, name, ...}, ...]  (three_layer_projects)
    2. 字典格式: {"entities": [...], "relationships": [...]}  (enhanced_student_kg)
    """
    nodes = set()
    
    # 格式1: 如果kg_data本身就是列表
    if isinstance(kg_data, list):
        for item in kg_data:
            if isinstance(item, dict) and 'id' in item:
                nodes.add(item['id'])
        return nodes
    
    # 格式2: 如果kg_data是字典
    if isinstance(kg_data, dict):
        if 'nodes' in kg_data:
            for node in kg_data['nodes']:
                if isinstance(node, dict) and 'id' in node:
                    nodes.add(node['id'])
        
        if 'entities' in kg_data:
            for entity in kg_data['entities']:
                if isinstance(entity, dict) and 'id' in entity:
                    nodes.add(entity['id'])
    
    return nodes
```

---

## 📊 修复效果对比

### 修复前 ❌

```
project_only_nodes:
  均值: 0.00
  最小: 0
  最大: 0
  零值数量: 180/180 (100%)

common_nodes:
  均值: 0.00
  jaccard_similarity: 0.0000
```

### 修复后 ✅

```
project_only_nodes:
  均值: 10.15
  最小: 8
  最大: 14
  零值数量: 0/180 (0%)

common_nodes:
  均值: 0.74
  最小: 0
  最大: 3

jaccard_similarity:
  均值: 0.0149
  最小: 0.0000
  最大: 0.0612
```

---

## 🎯 验证测试

```python
# 测试用例
proj_file = "outputs1/knowledge_graphs/three_layer_projects/A_Systematic_Review_of_Deep_entities.json"
student_file = "outputs1/knowledge_graphs/enhanced_student_kg/ZaenabAlammar_IFN712 Project Proposal 1_2025_CS_/student_n02123086_Emery_Miller_enhanced_kg.json"

# 结果
项目节点数: 12  (修复前: 0)
学生节点数: 39  (正常)
共同节点: 2    (修复前: 0)
项目独有: 10   (修复前: 0)
学生独有: 37   (正常)
Jaccard相似度: 0.0408  (修复前: 0.0000)
```

---

## 📝 经验教训

1. **数据格式一致性很重要**
   - 不同阶段生成的数据可能使用不同格式
   - 代码需要兼容多种格式

2. **分离文件需要配对加载**
   - entities + relationships 需要一起加载
   - 不能只加载一个文件

3. **测试用例要覆盖所有数据源**
   - 最初只测试了student_kg（字典格式）
   - 没有测试project_kg（数组格式）

4. **异常数据要及时发现**
   - 所有值都是0应该立即引起警觉
   - 对照可视化图片可以快速验证

---

## ✨ 总结

**问题根源**: JSON格式不兼容 + 分离文件未配对加载

**解决方法**: 
1. ✅ 统一加载逻辑，自动检测格式
2. ✅ 自动配对加载 entities + relationships
3. ✅ 支持数组和字典两种格式的节点提取

**修复结果**: 
- 180个对比全部正确
- project_only_nodes 从0恢复到平均10.15
- Jaccard相似度从0恢复到平均0.0149

**状态**: ✅ **完全修复！**

---

