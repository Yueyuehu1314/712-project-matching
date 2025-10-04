"""
Step 1: Load and Parse Knowledge Graphs (Version 2)
载入两种版本的Project KG和Student KG
- Project Baseline KG: outputs1/three_layer_projects (只有项目proposal)
- Project Enhanced KG: outputs1/enhanced_in20_in27 (项目 + 课程大纲)
- Student KG: outputs1/enhanced_student_kg (学生profile)
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple

def load_kg_file(kg_path: str) -> Dict:
    """载入单个KG文件"""
    with open(kg_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_kg_nodes_edges(kg: Dict) -> Tuple[Set[str], Set[Tuple[str, str, str]]]:
    """
    从KG中提取节点和边的集合
    返回: (nodes_set, edges_set)
    nodes_set: 节点ID的集合
    edges_set: (source, relation, target) 三元组的集合
    
    支持两种格式:
    - Project KG: 'nodes' + 'edges'
    - Student KG: 'entities' + 'relationships'
    """
    nodes = set()
    edges = set()
    
    # 提取节点 (支持两种格式)
    for node in kg.get('nodes', kg.get('entities', [])):
        nodes.add(node['id'])
    
    # 提取边 (支持两种格式)
    for edge in kg.get('edges', kg.get('relationships', [])):
        # Project KG格式: source, relation, target
        # Student KG格式: from_id, relationship_type, to_id
        source = edge.get('source', edge.get('from_id'))
        relation = edge.get('relation', edge.get('relationship_type'))
        target = edge.get('target', edge.get('to_id'))
        edge_tuple = (source, relation, target)
        edges.add(edge_tuple)
    
    return nodes, edges

def load_baseline_project_kgs(baseline_kg_dir: str) -> Dict[str, Dict]:
    """
    载入Baseline Project KG（three_layer格式）
    文件格式: {project_simplified_name}_entities.json 和 _relationships.json
    """
    project_kgs = {}
    
    # 获取所有的entities文件
    entities_files = [f for f in os.listdir(baseline_kg_dir) if f.endswith('_entities.json')]
    
    for entities_file in entities_files:
        project_simplified_name = entities_file.replace('_entities.json', '')
        relationships_file = f"{project_simplified_name}_relationships.json"
        
        entities_path = os.path.join(baseline_kg_dir, entities_file)
        relationships_path = os.path.join(baseline_kg_dir, relationships_file)
        
        if not os.path.exists(relationships_path):
            print(f"⚠️  Missing relationships file for {project_simplified_name}")
            continue
        
        # 载入entities和relationships
        entities = load_kg_file(entities_path)
        relationships = load_kg_file(relationships_path)
        
        # 构建KG
        kg = {
            'nodes': entities,
            'edges': relationships
        }
        
        # 从第一个entity中获取原始项目名
        if entities and len(entities) > 0:
            # 从file_path中提取原始项目文件夹名
            file_path = entities[0].get('properties', {}).get('file_path', '')
            # 例如: "data/processed/projects_md/IFN712 Project Proposal Template_2025_Project matching.md"
            if file_path:
                original_project_name = file_path.split('/')[-1].replace('.md', '')
            else:
                original_project_name = project_simplified_name
        else:
            original_project_name = project_simplified_name
        
        # 提取节点和边
        nodes, edges = extract_kg_nodes_edges(kg)
        
        project_kgs[original_project_name] = {
            'kg': kg,
            'nodes': nodes,
            'edges': edges,
            'path': entities_path,
            'folder': original_project_name,  # 使用原始名称
            'simplified_name': project_simplified_name,
            'type': 'baseline'
        }
        print(f"✓ Loaded baseline project: {original_project_name}")
        print(f"  - Simplified: {project_simplified_name}")
        print(f"  - Nodes: {len(nodes)}, Edges: {len(edges)}")
    
    return project_kgs

def load_enhanced_project_kgs(project_kg_dir: str) -> Dict[str, Dict]:
    """
    载入Enhanced Project KG（标准格式）
    """
    project_kgs = {}
    
    for project_folder in os.listdir(project_kg_dir):
        project_path = os.path.join(project_kg_dir, project_folder)
        if not os.path.isdir(project_path):
            continue
        
        # 查找KG JSON文件（不是backup）
        for file in os.listdir(project_path):
            if file.endswith('_enhanced_kg.json') and not file.endswith('.backup'):
                kg_path = os.path.join(project_path, file)
                kg = load_kg_file(kg_path)
                project_name = kg.get('project', project_folder)
                
                # 提取节点和边
                nodes, edges = extract_kg_nodes_edges(kg)
                
                project_kgs[project_name] = {
                    'kg': kg,
                    'nodes': nodes,
                    'edges': edges,
                    'path': kg_path,
                    'folder': project_folder,
                    'type': 'enhanced'
                }
                print(f"✓ Loaded enhanced project: {project_name}")
                print(f"  - Nodes: {len(nodes)}, Edges: {len(edges)}")
                break
    
    return project_kgs

def load_all_student_kgs(student_kg_dir: str) -> Dict[str, Dict]:
    """载入所有Student KG"""
    student_kgs = {}
    
    for project_folder in os.listdir(student_kg_dir):
        project_path = os.path.join(student_kg_dir, project_folder)
        if not os.path.isdir(project_path):
            continue
        
        # 每个项目文件夹下有20个学生的KG
        students_for_project = {}
        
        for file in os.listdir(project_path):
            if file.endswith('_enhanced_kg.json'):
                kg_path = os.path.join(project_path, file)
                kg = load_kg_file(kg_path)
                
                # 提取学生ID (例如: student_n01803983_Blake_Allen)
                student_id = file.replace('_enhanced_kg.json', '')
                
                # 提取节点和边
                nodes, edges = extract_kg_nodes_edges(kg)
                
                students_for_project[student_id] = {
                    'kg': kg,
                    'nodes': nodes,
                    'edges': edges,
                    'path': kg_path,
                    'project_folder': project_folder
                }
        
        if students_for_project:
            student_kgs[project_folder] = students_for_project
            print(f"✓ Loaded {len(students_for_project)} students for project: {project_folder}")
    
    return student_kgs

def build_matched_unmatched_pairs(project_kgs: Dict, student_kgs: Dict, kg_version: str) -> Tuple[List, List]:
    """
    建立matched和unmatched的学生-项目对
    Matched: 学生的project_folder == 项目名
    Unmatched: 学生的project_folder != 项目名
    
    kg_version: "baseline" 或 "enhanced"
    """
    matched_pairs = []
    unmatched_pairs = []
    
    # 遍历所有项目
    for project_name, project_data in project_kgs.items():
        # 遍历所有学生
        for student_project_folder, students in student_kgs.items():
            for student_id, student_data in students.items():
                pair = {
                    'project_name': project_name,
                    'project_folder': project_data['folder'],
                    'project_kg_version': kg_version,
                    'student_id': student_id,
                    'student_project_folder': student_project_folder,
                    'project_nodes': project_data['nodes'],
                    'project_edges': project_data['edges'],
                    'student_nodes': student_data['nodes'],
                    'student_edges': student_data['edges']
                }
                
                # 判断是否matched
                if student_project_folder == project_name:
                    matched_pairs.append(pair)
                else:
                    unmatched_pairs.append(pair)
    
    return matched_pairs, unmatched_pairs

def main():
    print("=" * 80)
    print("Step 1: Loading Knowledge Graphs (Version 2)")
    print("=" * 80)
    print()
    
    # 路径设置
    baseline_project_kg_dir = "outputs1/knowledge_graphs/three_layer_projects"
    enhanced_project_kg_dir = "outputs1/knowledge_graphs/enhanced_in20_in27"
    student_kg_dir = "outputs1/knowledge_graphs/enhanced_student_kg"
    output_dir = "outputs/kg_comparison"
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. 载入Baseline Project KG
    print("📁 Loading Baseline Project KGs (Project Proposal Only)...")
    baseline_project_kgs = load_baseline_project_kgs(baseline_project_kg_dir)
    print(f"\n✅ Loaded {len(baseline_project_kgs)} baseline projects\n")
    
    # 2. 载入Enhanced Project KG
    print("📁 Loading Enhanced Project KGs (Project + Unit Outline)...")
    enhanced_project_kgs = load_enhanced_project_kgs(enhanced_project_kg_dir)
    print(f"\n✅ Loaded {len(enhanced_project_kgs)} enhanced projects\n")
    
    # 3. 载入Student KG
    print("👨‍🎓 Loading Student KGs...")
    student_kgs = load_all_student_kgs(student_kg_dir)
    total_students = sum(len(students) for students in student_kgs.values())
    print(f"\n✅ Loaded {total_students} students\n")
    
    # 4. 建立配对关系 - Baseline版本
    print("🔗 Building matched/unmatched pairs (Baseline)...")
    baseline_matched, baseline_unmatched = build_matched_unmatched_pairs(
        baseline_project_kgs, student_kgs, kg_version="baseline"
    )
    print(f"✅ Baseline matched pairs: {len(baseline_matched)}")
    print(f"✅ Baseline unmatched pairs: {len(baseline_unmatched)}")
    print()
    
    # 5. 建立配对关系 - Enhanced版本
    print("🔗 Building matched/unmatched pairs (Enhanced)...")
    enhanced_matched, enhanced_unmatched = build_matched_unmatched_pairs(
        enhanced_project_kgs, student_kgs, kg_version="enhanced"
    )
    print(f"✅ Enhanced matched pairs: {len(enhanced_matched)}")
    print(f"✅ Enhanced unmatched pairs: {len(enhanced_unmatched)}")
    print()
    
    # 6. 保存结果
    output_data = {
        'summary': {
            'num_baseline_projects': len(baseline_project_kgs),
            'num_enhanced_projects': len(enhanced_project_kgs),
            'num_students': total_students,
            'baseline_matched_pairs': len(baseline_matched),
            'baseline_unmatched_pairs': len(baseline_unmatched),
            'enhanced_matched_pairs': len(enhanced_matched),
            'enhanced_unmatched_pairs': len(enhanced_unmatched)
        },
        'baseline_projects': list(baseline_project_kgs.keys()),
        'enhanced_projects': list(enhanced_project_kgs.keys()),
        'baseline_matched_preview': [
            {
                'project': p['project_name'],
                'student': p['student_id'],
                'project_nodes': len(p['project_nodes']),
                'project_edges': len(p['project_edges']),
                'student_nodes': len(p['student_nodes']),
                'student_edges': len(p['student_edges'])
            }
            for p in baseline_matched[:20]  # 前20个
        ],
        'enhanced_matched_preview': [
            {
                'project': p['project_name'],
                'student': p['student_id'],
                'project_nodes': len(p['project_nodes']),
                'project_edges': len(p['project_edges']),
                'student_nodes': len(p['student_nodes']),
                'student_edges': len(p['student_edges'])
            }
            for p in enhanced_matched[:20]  # 前20个
        ]
    }
    
    output_file = os.path.join(output_dir, 'step1_kg_loaded_v2.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Results saved to: {output_file}")
    print()
    print("=" * 80)
    print("✅ Step 1 Complete!")
    print("=" * 80)
    print()
    print("📊 Summary:")
    print(f"  Baseline: {len(baseline_project_kgs)} projects × {total_students} students")
    print(f"           = {len(baseline_matched)} matched + {len(baseline_unmatched)} unmatched")
    print(f"  Enhanced: {len(enhanced_project_kgs)} projects × {total_students} students")
    print(f"           = {len(enhanced_matched)} matched + {len(enhanced_unmatched)} unmatched")

if __name__ == '__main__':
    main()

