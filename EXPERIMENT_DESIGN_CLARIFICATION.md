# 实验设计澄清

## 🎯 研究问题

**RQ**: 引入Unit Outline信息是否能提升学生-项目匹配效果？

## 📊 实验设计完整方案

### 方法对比矩阵

| 方法 | 表示方式 | 度量 | Project输入 | Student输入 |
|------|---------|------|------------|------------|
| **Method 1a** | Text Embedding | Cosine Similarity | PD only | Student Profile |
| **Method 1b** | Text Embedding | Cosine Similarity | **PD+UO** | Student Profile |
| **Method 2a** | Knowledge Graph | Jaccard + Edit Distance | PD only KG | Student KG |
| **Method 2b** | Knowledge Graph | Jaccard + Edit Distance | **PD+UO KG** | Student KG |

---

## 🔬 为什么需要4个方法都做？

### 1. 完整的ablation study

```
控制变量：
- 表示方式（Text vs KG）
- 信息来源（PD only vs PD+UO）

实验对比：
Method 1a vs 1b → 测试UO在Text Embedding中的作用
Method 2a vs 2b → 测试UO在KG中的作用
Method 1a vs 2a → 测试KG vs Text（baseline）
Method 1b vs 2b → 测试KG vs Text（enhanced）
```

### 2. 回答多个研究子问题

- **RQ1.1**: Text方法中，加入UO是否有帮助？
  - 对比 Method 1a vs 1b
  
- **RQ1.2**: KG方法中，加入UO是否有帮助？
  - 对比 Method 2a vs 2b
  
- **RQ2**: 哪种表示方式更好？
  - Baseline: 1a vs 2a
  - Enhanced: 1b vs 2b

### 3. 避免混淆因素

如果只做 1a vs 2b，你无法确定改进来自于：
- 引入UO？
- 使用KG？
- 两者结合？

---

## ✅ 需要做的实验

### 实验状态

| 实验 | 状态 | 位置 |
|------|------|------|
| Method 1a | ✅ 已完成 | `outputs/embeddings/` |
| Method 1b | ❌ **需要做** | 待生成 |
| Method 2a | ❌ **需要做** | 待生成 |
| Method 2b | ❌ **需要做** | `outputs1/` 中已有KG |

---

## 🚀 具体实施步骤

### Step 1: 生成 PD+UO 的文本融合文件

**目的**: 为 Method 1b 准备输入

```bash
# 创建新的目录
mkdir -p data/processed/enhanced_projects_md

# 对每个project，融合对应的unit信息
python -c "
import os
import glob

project_dir = 'data/processed/projects_md'
unit_dir = 'data/processed/units_md'
output_dir = 'data/processed/enhanced_projects_md'

# 读取所有项目
projects = glob.glob(f'{project_dir}/*.md')

for proj_path in projects:
    proj_name = os.path.basename(proj_path)
    
    # 读取project内容
    with open(proj_path, 'r', encoding='utf-8') as f:
        proj_content = f.read()
    
    # 读取units（两个都加上）
    unit_in20 = open(f'{unit_dir}/qut_IN20_39851_int_cms_unit.md', 'r', encoding='utf-8').read()
    unit_in27 = open(f'{unit_dir}/qut_IN27_44569.md', 'r', encoding='utf-8').read()
    
    # 融合内容
    enhanced_content = f'''# {proj_name.replace('.md', '')}

## Project Description
{proj_content}

---

## Related Unit Outline: IN20

{unit_in20}

---

## Related Unit Outline: IN27

{unit_in27}
'''
    
    # 保存
    output_path = f'{output_dir}/{proj_name}'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(enhanced_content)
    
    print(f'✅ Generated: {output_path}')
"
```

### Step 2: 生成 PD+UO 的 embeddings

**目的**: Method 1b

```bash
# 修改原有的embedding脚本，使用enhanced_projects_md目录
python -c "
# 类似 src/experiments/embedding_similarity_comparison.py
# 但使用 data/processed/enhanced_projects_md/ 作为项目目录
# 保存到 outputs/embeddings/enhanced_project_profile_embeddings.json
"
```

### Step 3: 计算 Method 1b 的相似度

```bash
# 对比 enhanced project embeddings 和 student profile embeddings
# 计算 cosine similarity
# 生成类似的统计报告
```

### Step 4: 生成 PD only KG（如果还没有）

**目的**: Method 2a

```bash
# 使用three_layer_project_kg.py 生成不含Unit的KG
python -c "
from src.knowledge_graphs.three_layer_project_kg import generate_all_three_layer_project_kgs
generate_all_three_layer_project_kgs(
    use_existing_weights=False  # 不使用enhanced权重
)
"
```

### Step 5: 生成 Student KG（如果还没有）

```bash
python -c "
from src.knowledge_graphs.enhanced_student_kg import EnhancedStudentKGGenerator
gen = EnhancedStudentKGGenerator()
gen.generate_all_student_kgs(
    profiles_dir='data/processed/profiles_md',
    output_dir='outputs1/knowledge_graphs/enhanced_student_kg'
)
"
```

### Step 6: 计算 KG 相似度（Method 2a & 2b）

创建新的脚本来计算图相似度：

```python
# kg_similarity_comparison.py

import json
import networkx as nx
from typing import Dict, List, Tuple

def load_kg(json_path: str) -> nx.Graph:
    """加载知识图谱为NetworkX图"""
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    G = nx.Graph()
    
    # 添加节点
    for node in data.get('nodes', []):
        G.add_node(node['id'], **node)
    
    # 添加边
    for edge in data.get('edges', []):
        G.add_edge(edge['source'], edge['target'], **edge)
    
    return G

def compute_jaccard_similarity(G1: nx.Graph, G2: nx.Graph) -> float:
    """计算两个图的Jaccard相似度（基于节点集合）"""
    nodes1 = set(G1.nodes())
    nodes2 = set(G2.nodes())
    
    intersection = len(nodes1 & nodes2)
    union = len(nodes1 | nodes2)
    
    return intersection / union if union > 0 else 0.0

def compute_edit_distance(G1: nx.Graph, G2: nx.Graph) -> int:
    """计算图编辑距离的简化版本"""
    nodes1 = set(G1.nodes())
    nodes2 = set(G2.nodes())
    
    # 节点差异
    node_diff = len(nodes1 ^ nodes2)
    
    # 边差异（只看共同节点的边）
    common_nodes = nodes1 & nodes2
    edges1 = set([(u, v) for u, v in G1.edges() if u in common_nodes and v in common_nodes])
    edges2 = set([(u, v) for u, v in G2.edges() if u in common_nodes and v in common_nodes])
    edge_diff = len(edges1 ^ edges2)
    
    return node_diff + edge_diff

def run_kg_similarity_experiment():
    """运行KG相似度实验"""
    
    # Method 2a: PD only KG vs Student KG
    project_kg_dir_pd = 'outputs/knowledge_graphs/three_layer_projects'
    
    # Method 2b: PD+UO KG vs Student KG  
    project_kg_dir_pduo = 'outputs1/knowledge_graphs/enhanced_in20_in27'
    
    student_kg_dir = 'outputs1/knowledge_graphs/enhanced_student_kg'
    
    results = {
        'method_2a': [],  # PD only
        'method_2b': []   # PD+UO
    }
    
    # 对每个项目
    for project in projects:
        for student in students:
            # 判断是否匹配（student来自project）
            is_match = student.startswith(project)
            
            # Method 2a
            proj_kg_pd = load_kg(f'{project_kg_dir_pd}/{project}_kg.json')
            student_kg = load_kg(f'{student_kg_dir}/{student}_kg.json')
            
            jaccard_2a = compute_jaccard_similarity(proj_kg_pd, student_kg)
            edit_dist_2a = compute_edit_distance(proj_kg_pd, student_kg)
            
            results['method_2a'].append({
                'project': project,
                'student': student,
                'is_match': is_match,
                'jaccard': jaccard_2a,
                'edit_distance': edit_dist_2a
            })
            
            # Method 2b
            proj_kg_pduo = load_kg(f'{project_kg_dir_pduo}/{project}/{project}_enhanced_kg.json')
            
            jaccard_2b = compute_jaccard_similarity(proj_kg_pduo, student_kg)
            edit_dist_2b = compute_edit_distance(proj_kg_pduo, student_kg)
            
            results['method_2b'].append({
                'project': project,
                'student': student,
                'is_match': is_match,
                'jaccard': jaccard_2b,
                'edit_distance': edit_dist_2b
            })
    
    # 分析结果
    analyze_results(results)
    
    return results

if __name__ == '__main__':
    results = run_kg_similarity_experiment()
```

---

## 📊 最终对比表格

| Method | Project Input | Student Input | Matched Pairs | Unmatched Pairs | Δ (Matched - Unmatched) |
|--------|---------------|---------------|---------------|-----------------|------------------------|
| 1a (Text, PD) | PD text | Student | Cosine↑ | Cosine↓ | Δ₁ₐ |
| 1b (Text, PD+UO) | PD+UO text | Student | Cosine↑↑ | Cosine↓ | **Δ₁ᵦ > Δ₁ₐ ?** |
| 2a (KG, PD) | PD KG | Student KG | Jaccard↑, Edit↓ | Jaccard↓, Edit↑ | Δ₂ₐ |
| 2b (KG, PD+UO) | PD+UO KG | Student KG | Jaccard↑↑, Edit↓↓ | Jaccard↓, Edit↑ | **Δ₂ᵦ > Δ₂ₐ ?** |

### 预期结果

1. **Δ₁ᵦ > Δ₁ₐ**: UO在Text方法中有帮助
2. **Δ₂ᵦ > Δ₂ₐ**: UO在KG方法中有帮助  
3. **Δ₂ₐ > Δ₁ₐ**: KG优于Text（baseline）
4. **Δ₂ᵦ > Δ₁ᵦ**: KG优于Text（enhanced）

---

## 🎯 结论

**是的，你需要补充 PD+UO 的 embedding 实验（Method 1b）**

原因：
1. ✅ 完整的ablation study
2. ✅ 单独验证UO在embedding中的作用
3. ✅ 公平对比KG vs Embedding
4. ✅ 更有说服力的论文结果

---

## 📁 文件组织

```
outputs/
├── embeddings/
│   ├── project_profile_embeddings.json          # Method 1a (已有)
│   ├── enhanced_project_embeddings.json         # Method 1b (需生成)
│   ├── student_embeddings.json                  # 共用
│   ├── method_1a_results.json                   # 已有
│   └── method_1b_results.json                   # 需生成
│
└── knowledge_graphs/
    ├── three_layer_projects/                    # Method 2a (PD only KG)
    │   └── {project}_kg.json
    │
    └── enhanced_in20_in27/                      # Method 2b (PD+UO KG)
        └── {project}/{project}_enhanced_kg.json

outputs1/
└── knowledge_graphs/
    └── enhanced_student_kg/                     # 共用
        └── {project}/{student}_kg.json

data/processed/
├── projects_md/                                 # Method 1a
├── enhanced_projects_md/                        # Method 1b (需生成)
└── profiles_md/                                 # 共用
```

---

## 🚀 下一步行动

**优先级：**

1. **高优先级**: 生成 enhanced_projects_md（融合PD+UO文本）
2. **高优先级**: 运行 Method 1b embedding实验
3. **中优先级**: 确认 Method 2a/2b 的KG文件已齐全
4. **中优先级**: 编写 KG相似度计算脚本
5. **低优先级**: 生成可视化对比图表

**预计时间**:
- Method 1b: 30-60分钟
- Method 2a/2b: 1-2小时
- 总计: 2-3小时

