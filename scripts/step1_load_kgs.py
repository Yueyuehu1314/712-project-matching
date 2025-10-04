"""
Step 1: Load and Parse Knowledge Graphs
载入Project KG和Student KG，并建立matched/unmatched对应关系
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

def load_all_project_kgs(project_kg_dir: str) -> Dict[str, Dict]:
    """载入所有Project KG"""
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
                    'folder': project_folder
                }
                print(f"✓ Loaded project: {project_name}")
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

def build_matched_unmatched_pairs(project_kgs: Dict, student_kgs: Dict) -> Tuple[List, List]:
    """
    建立matched和unmatched的学生-项目对
    Matched: 学生的project_folder == 项目名
    Unmatched: 学生的project_folder != 项目名
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
    print("Step 1: Loading Knowledge Graphs")
    print("=" * 80)
    print()
    
    # 路径设置
    project_kg_dir = "outputs1/knowledge_graphs/enhanced_in20_in27"
    student_kg_dir = "outputs1/knowledge_graphs/enhanced_student_kg"
    output_dir = "outputs/kg_comparison"
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. 载入Project KG
    print("📁 Loading Project KGs...")
    project_kgs = load_all_project_kgs(project_kg_dir)
    print(f"\n✅ Loaded {len(project_kgs)} projects\n")
    
    # 2. 载入Student KG
    print("👨‍🎓 Loading Student KGs...")
    student_kgs = load_all_student_kgs(student_kg_dir)
    total_students = sum(len(students) for students in student_kgs.values())
    print(f"\n✅ Loaded {total_students} students\n")
    
    # 3. 建立配对关系
    print("🔗 Building matched/unmatched pairs...")
    matched_pairs, unmatched_pairs = build_matched_unmatched_pairs(project_kgs, student_kgs)
    print(f"✅ Matched pairs: {len(matched_pairs)}")
    print(f"✅ Unmatched pairs: {len(unmatched_pairs)}")
    print()
    
    # 4. 保存结果
    output_data = {
        'summary': {
            'num_projects': len(project_kgs),
            'num_students': total_students,
            'num_matched_pairs': len(matched_pairs),
            'num_unmatched_pairs': len(unmatched_pairs)
        },
        'project_list': list(project_kgs.keys()),
        'matched_pairs_preview': [
            {
                'project': p['project_name'],
                'student': p['student_id'],
                'project_nodes': len(p['project_nodes']),
                'project_edges': len(p['project_edges']),
                'student_nodes': len(p['student_nodes']),
                'student_edges': len(p['student_edges'])
            }
            for p in matched_pairs
        ],
        'unmatched_pairs_preview': [
            {
                'project': p['project_name'],
                'student': p['student_id'],
                'project_nodes': len(p['project_nodes']),
                'project_edges': len(p['project_edges']),
                'student_nodes': len(p['student_nodes']),
                'student_edges': len(p['student_edges'])
            }
            for p in unmatched_pairs[:100]  # 只保存前100个unmatched作为预览
        ]
    }
    
    output_file = os.path.join(output_dir, 'step1_kg_loaded.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Results saved to: {output_file}")
    print()
    print("=" * 80)
    print("✅ Step 1 Complete!")
    print("=" * 80)

if __name__ == '__main__':
    main()
