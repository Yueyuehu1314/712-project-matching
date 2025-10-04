#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新运行Method 2a和2b，添加正负样本对比
统一数据格式：正负样本保存在同一个JSON文件中，用is_match字段区分
"""

import json
import os
import re
from pathlib import Path
import sys
import numpy as np
from typing import Dict, List, Tuple, Set, Optional
import networkx as nx


def _extract_project_identifier(entities: List[Dict]) -> Tuple[Optional[str], Optional[str]]:
    """从项目实体列表中推断项目唯一编码和标题"""
    for node in entities:
        if not isinstance(node, dict):
            continue
        node_type = node.get('entity_type') or node.get('type')
        if node_type and node_type.upper() == 'PROJECT':
            title = node.get('name')
            file_path = node.get('properties', {}).get('file_path', '')
            identifier = os.path.splitext(os.path.basename(file_path))[0] if file_path else node.get('id')
            return identifier, title
    return None, None


def load_baseline_project_kgs(project_kg_dir: str) -> Dict:
    """加载基础项目知识图谱"""
    project_kgs = {}
    
    for project_folder in os.listdir(project_kg_dir):
        project_path = os.path.join(project_kg_dir, project_folder)
        if not os.path.isdir(project_path):
            continue
        
        entities_file = os.path.join(project_path, 'entities.json')
        relationships_file = os.path.join(project_path, 'relationships.json')
        
        if not os.path.exists(entities_file) or not os.path.exists(relationships_file):
            continue
        
        with open(entities_file, 'r', encoding='utf-8') as f:
            entities = json.load(f)
        
        with open(relationships_file, 'r', encoding='utf-8') as f:
            relationships = json.load(f)
        
        project_id, project_title = _extract_project_identifier(entities)

        project_kgs[project_folder] = {
            'folder': project_folder,
            'nodes': entities,
            'edges': relationships,
            'project_id': project_id,
            'project_title': project_title
        }
    
    return project_kgs


def load_enhanced_project_kgs(project_kg_dir: str) -> Dict[str, Dict]:
    """加载增强项目知识图谱，按项目唯一编码索引"""
    project_kgs: Dict[str, Dict] = {}

    if not os.path.exists(project_kg_dir):
        print(f"⚠️  增强项目KG目录不存在: {project_kg_dir}")
        return project_kgs

    for project_folder in os.listdir(project_kg_dir):
        project_path = os.path.join(project_kg_dir, project_folder)
        if not os.path.isdir(project_path):
            continue

        kg_file = None
        for file_name in os.listdir(project_path):
            if file_name.endswith('_enhanced_kg.json'):
                kg_file = os.path.join(project_path, file_name)
                break

        if kg_file is None or not os.path.exists(kg_file):
            continue

        with open(kg_file, 'r', encoding='utf-8') as f:
            kg_data = json.load(f)

        project_id = kg_data.get('project') or kg_data.get('project_id')
        if not project_id:
            continue

        project_kgs[project_id] = {
            'folder': project_folder,
            'file': kg_file,
            'project_title': kg_data.get('project_title', project_folder),
            'project_id': project_id,
            'nodes': kg_data.get('nodes', []),
            'edges': kg_data.get('edges', [])
        }

    return project_kgs


def load_all_student_kgs(student_kg_dir: str) -> Dict[str, Dict]:
    """加载所有学生知识图谱，按项目文件夹分组"""
    student_kgs = {}
    
    for project_folder in os.listdir(student_kg_dir):
        project_path = os.path.join(student_kg_dir, project_folder)
        if not os.path.isdir(project_path):
            continue
        
        students = {}
        for student_file in os.listdir(project_path):
            if not student_file.endswith('.json'):
                continue

            # 仅保留增强学生KG版本，排除包含前置课程等额外文件
            if not student_file.endswith('_enhanced_kg.json'):
                continue

            student_path = os.path.join(project_path, student_file)
            with open(student_path, 'r', encoding='utf-8') as f:
                student_data = json.load(f)
            
            student_id = student_file.replace('.json', '')
            # 兼容两种格式：nodes/edges 或 entities/relationships
            nodes = student_data.get('nodes', student_data.get('entities', []))
            edges = student_data.get('edges', student_data.get('relationships', []))
            students[student_id] = {
                'nodes': nodes,
                'edges': edges
            }
        
        if students:
            student_kgs[project_folder] = students
    
    return student_kgs


def build_all_pairs(project_kgs: Dict, student_kgs: Dict, name_mapping: Dict, kg_version: str, use_all_negatives: bool = True) -> List:
    """
    建立所有学生-项目对（正样本+负样本）
    
    对于每个项目：
    - 正样本：该项目生成的10个学生
    - 负样本：其他项目生成的所有学生（190个）
    
    Args:
        project_kgs: 项目知识图谱字典
        student_kgs: 学生知识图谱字典（按项目分组）
        name_mapping: 项目名称映射字典（简称->全称）
        kg_version: "baseline" 或 "enhanced"
        use_all_negatives: 是否使用所有负样本（True）或采样（False）
    
    Returns:
        包含正负样本的配对列表，每项有is_match字段
    """
    all_pairs = []
    
    # 遍历每个项目
    for project_name, project_data in project_kgs.items():

        # 查找该项目对应的学生文件夹名
        student_folder_name = name_mapping.get(project_name, project_name)
        
        # 1. 正样本：该项目生成的学生
        if student_folder_name in student_kgs:
            for student_id, student_data in student_kgs[student_folder_name].items():
                all_pairs.append({
                    'project_name': project_name,
                    'project_folder': project_data['folder'],
                    'project_kg_version': kg_version,
                    'project_code': project_data.get('project_id'),
                    'project_title': project_data.get('project_title'),
                    'student_id': student_id,
                    'student_project_folder': student_folder_name,
                    'project_nodes': project_data['nodes'],
                    'project_edges': project_data['edges'],
                    'student_nodes': student_data['nodes'],
                    'student_edges': student_data['edges'],
                    'is_match': True  # 正样本
                })
        
        # 2. 负样本：其他项目生成的学生
        for other_student_folder, students in student_kgs.items():
            if other_student_folder == student_folder_name:
                continue  # 跳过同一项目的学生（已在正样本中）
            
            for student_id, student_data in students.items():
                all_pairs.append({
                    'project_name': project_name,
                    'project_folder': project_data['folder'],
                    'project_kg_version': kg_version,
                    'project_code': project_data.get('project_id'),
                    'project_title': project_data.get('project_title'),
                    'student_id': student_id,
                    'student_project_folder': other_student_folder,  # 学生真实的来源项目
                    'project_nodes': project_data['nodes'],
                    'project_edges': project_data['edges'],
                    'student_nodes': student_data['nodes'],
                    'student_edges': student_data['edges'],
                    'is_match': False  # 负样本
                })
    
    return all_pairs


NODE_TYPE_WEIGHTS = {
    'PROJECT': 3.0,
    'STUDENT': 3.0,
    'PROGRAM': 2.5,
    'UNIT': 2.0,
    'COURSE': 2.0,
    'SKILL': 2.0,
    'DOMAIN': 1.5,
    'MAJOR': 1.5,
    'COMPETENCY': 1.5,
    'DEFAULT': 1.0
}

RELATION_TYPE_WEIGHTS = {
    'REQUIRES_DOMAIN': 2.0,
    'INCLUDES': 1.5,
    'COMPLETED_COURSE': 2.0,
    'STUDIED_MAJOR': 1.5,
    'HAS_SKILL': 1.8,
    'TEACHES_SKILL': 1.6,
    'SUPPORTS_SKILL': 1.6,
    'SUPPORTS_COURSE': 1.6,
    'DEFAULT': 1.0
}


def _normalize_node_identifier(node: Dict) -> str:
    """生成节点的统一标识"""
    raw_id = node.get('id', '')
    name = node.get('name', '')

    # 优先提取课程/单元代码，例如 IFN553、CAB401
    for text in (raw_id, name):
        if not text:
            continue
        match = re.search(r'[A-Z]{3}\d{3}', text.upper())
        if match:
            return match.group(0)

    return raw_id or name or node.get('label', '')


def _extract_node_labels(nodes: List) -> Set[str]:
    """提取节点的唯一标签集合"""
    labels: Set[str] = set()
    for node in nodes:
        if isinstance(node, dict):
            labels.add(_normalize_node_identifier(node))
        else:
            labels.add(str(node))
    labels.discard('')
    return labels


def _extract_node_info(nodes: List) -> Dict[str, str]:
    """提取节点映射: 标识 -> 类型"""
    info: Dict[str, str] = {}
    for node in nodes:
        if not isinstance(node, dict):
            key = str(node)
            if key:
                info[key] = 'DEFAULT'
            continue

        key = _normalize_node_identifier(node)
        if not key:
            continue

        node_type = node.get('entity_type') or node.get('type') or node.get('node_type') or 'DEFAULT'
        info[key] = node_type.upper()
    return info


def _extract_edge_info(edges: List) -> Dict[Tuple[str, str, str], str]:
    """提取边映射: (source, target, relation) -> relation"""
    info: Dict[Tuple[str, str, str], str] = {}
    for edge in edges:
        if not isinstance(edge, dict):
            continue

        src = edge.get('source') or edge.get('source_id') or ''
        tgt = edge.get('target') or edge.get('target_id') or ''
        relation = edge.get('relation') or edge.get('relation_type') or ''
        if not src or not tgt:
            continue

        info[(src, tgt, relation)] = relation.upper() if relation else 'DEFAULT'
    return info


def calculate_jaccard_similarity(nodes1: List, nodes2: List, return_sets: bool = False):
    """计算两个节点列表的Jaccard相似度，可选返回节点集合"""
    set1 = _extract_node_labels(nodes1)
    set2 = _extract_node_labels(nodes2)

    if not set1 and not set2:
        return (0.0, set1, set2) if return_sets else 0.0

    intersection = len(set1 & set2)
    union = len(set1 | set2)
    similarity = intersection / union if union > 0 else 0.0

    if return_sets:
        return similarity, set1, set2
    return similarity


def calculate_graph_edit_distance(nodes1: List, edges1: List, nodes2: List, edges2: List) -> int:
    """计算图编辑距离（加权版）"""
    node_info1 = _extract_node_info(nodes1)
    node_info2 = _extract_node_info(nodes2)

    node_diff = 0.0

    # 节点缺失/额外的成本
    for key in node_info1.keys() - node_info2.keys():
        node_type = node_info1[key]
        node_diff += NODE_TYPE_WEIGHTS.get(node_type, NODE_TYPE_WEIGHTS['DEFAULT'])

    for key in node_info2.keys() - node_info1.keys():
        node_type = node_info2[key]
        node_diff += NODE_TYPE_WEIGHTS.get(node_type, NODE_TYPE_WEIGHTS['DEFAULT'])

    # 节点类型不匹配的成本
    for key in node_info1.keys() & node_info2.keys():
        type1 = node_info1[key]
        type2 = node_info2[key]
        if type1 != type2:
            node_diff += 0.5 * (NODE_TYPE_WEIGHTS.get(type1, NODE_TYPE_WEIGHTS['DEFAULT']) +
                                NODE_TYPE_WEIGHTS.get(type2, NODE_TYPE_WEIGHTS['DEFAULT']))

    # 边差异
    edge_info1 = _extract_edge_info(edges1)
    edge_info2 = _extract_edge_info(edges2)
    edge_diff = 0.0

    for key, relation in edge_info1.items():
        if key not in edge_info2:
            edge_diff += RELATION_TYPE_WEIGHTS.get(relation, RELATION_TYPE_WEIGHTS['DEFAULT'])

    for key, relation in edge_info2.items():
        if key not in edge_info1:
            edge_diff += RELATION_TYPE_WEIGHTS.get(relation, RELATION_TYPE_WEIGHTS['DEFAULT'])

    return node_diff + edge_diff


def calculate_node_edge_jaccard(nodes1: List, edges1: List, nodes2: List, edges2: List) -> Tuple[float, float]:
    """分别计算节点和边的Jaccard相似度"""
    # 节点Jaccard
    node_jaccard = calculate_jaccard_similarity(nodes1, nodes2)
    
    # 边Jaccard
    edge_set1 = set()
    for edge in edges1:
        if isinstance(edge, dict):
            src = edge.get('source', '')
            tgt = edge.get('target', '')
            if src and tgt:
                edge_set1.add((src, tgt))
    
    edge_set2 = set()
    for edge in edges2:
        if isinstance(edge, dict):
            src = edge.get('source', '')
            tgt = edge.get('target', '')
            if src and tgt:
                edge_set2.add((src, tgt))
    
    if not edge_set1 and not edge_set2:
        edge_jaccard = 0.0
    else:
        intersection = len(edge_set1 & edge_set2)
        union = len(edge_set1 | edge_set2)
        edge_jaccard = intersection / union if union > 0 else 0.0
    
    return node_jaccard, edge_jaccard


def calculate_similarity_for_pairs(pairs: List, method_name: str) -> List:
    """计算所有配对的相似度"""
    results = []
    
    print(f"\n计算 {len(pairs)} 对配对的相似度...")
    
    for i, pair in enumerate(pairs, 1):
        if i % 100 == 0:
            print(f"  进度: {i}/{len(pairs)}")
        
        try:
            # 计算相似度
            if method_name == "2a":
                # Method 2a: 基础Jaccard + 编辑距离
                similarity, student_node_set, project_node_set = calculate_jaccard_similarity(
                    pair['student_nodes'], pair['project_nodes'], return_sets=True
                )
                edit_distance = calculate_graph_edit_distance(
                    pair['student_nodes'], pair['student_edges'],
                    pair['project_nodes'], pair['project_edges']
                )
                common_nodes = len(student_node_set & project_node_set)
                project_only_nodes = len(project_node_set - student_node_set)
                student_only_nodes = len(student_node_set - project_node_set)
                
                result = {
                    'project_name': pair['project_name'],
                    'student_id': pair['student_id'],
                    'project_id': pair['project_name'],
                    'project_code': pair.get('project_code'),
                    'project_folder': pair['project_folder'],
                    'student_project_folder': pair['student_project_folder'],
                    'project_title': pair.get('project_title'),
                    'is_match': pair['is_match'],
                    'jaccard_similarity': similarity,
                    'edit_distance': edit_distance,
                    'common_nodes': common_nodes,
                    'project_only_nodes': project_only_nodes,
                    'student_only_nodes': student_only_nodes,
                    'label': 'positive' if pair['is_match'] else 'negative'
                }
            
            elif method_name == "2b":
                # Method 2b: 增强KG（节点/边分离的Jaccard）
                node_jaccard, edge_jaccard = calculate_node_edge_jaccard(
                    pair['student_nodes'], pair['student_edges'],
                    pair['project_nodes'], pair['project_edges']
                )
                edit_distance = calculate_graph_edit_distance(
                    pair['student_nodes'], pair['student_edges'],
                    pair['project_nodes'], pair['project_edges']
                )
                
                # 计算准备度（简化版，可以扩展）
                readiness = (node_jaccard * 0.7 + edge_jaccard * 0.3)
                
                result = {
                    'project_name': pair['project_name'],
                    'student_id': pair['student_id'],
                    'project_id': pair['project_name'],
                    'project_code': pair.get('project_code'),
                    'project_folder': pair['project_folder'],
                    'student_project_folder': pair['student_project_folder'],
                    'project_title': pair.get('project_title'),
                    'is_match': pair['is_match'],
                    'node_jaccard': node_jaccard,
                    'edge_jaccard': edge_jaccard,
                    'edit_distance': edit_distance,
                    'readiness_score': readiness,
                    'label': 'positive' if pair['is_match'] else 'negative'
                }
            
            results.append(result)
        
        except Exception as e:
            print(f"⚠️  计算失败 (学生: {pair['student_id']}, 项目: {pair['project_name']}): {e}")
            continue
    
    return results


def analyze_results(results: List, method_name: str) -> Dict:
    """分析结果（正负样本对比）"""
    matched = [r for r in results if r['is_match']]
    unmatched = [r for r in results if not r['is_match']]
    
    print(f"\n{'='*70}")
    print(f"📊 分析结果 - {method_name}")
    print(f"{'='*70}")
    print(f"正样本数: {len(matched)}")
    print(f"负样本数: {len(unmatched)}")
    
    analysis = {
        'total_pairs': len(results),
        'matched_count': len(matched),
        'unmatched_count': len(unmatched)
    }
    
    # 如果没有数据，直接返回
    if len(matched) == 0 or len(unmatched) == 0:
        print("\n⚠️  警告：正样本或负样本为空，无法计算统计信息")
        return analysis
    
    if method_name == "2a":
        # Jaccard相似度分析
        matched_jaccards = [r['jaccard_similarity'] for r in matched]
        unmatched_jaccards = [r['jaccard_similarity'] for r in unmatched]
        
        analysis['matched_jaccard'] = {
            'mean': float(np.mean(matched_jaccards)),
            'median': float(np.median(matched_jaccards)),
            'std': float(np.std(matched_jaccards)),
            'min': float(np.min(matched_jaccards)),
            'max': float(np.max(matched_jaccards))
        }
        
        analysis['unmatched_jaccard'] = {
            'mean': float(np.mean(unmatched_jaccards)),
            'median': float(np.median(unmatched_jaccards)),
            'std': float(np.std(unmatched_jaccards)),
            'min': float(np.min(unmatched_jaccards)),
            'max': float(np.max(unmatched_jaccards))
        }
        
        # 编辑距离分析
        matched_edits = [r['edit_distance'] for r in matched]
        unmatched_edits = [r['edit_distance'] for r in unmatched]
        
        analysis['matched_edit_distance'] = {
            'mean': float(np.mean(matched_edits)),
            'median': float(np.median(matched_edits)),
            'std': float(np.std(matched_edits)),
            'min': float(np.min(matched_edits)),
            'max': float(np.max(matched_edits))
        }
        
        analysis['unmatched_edit_distance'] = {
            'mean': float(np.mean(unmatched_edits)),
            'median': float(np.median(unmatched_edits)),
            'std': float(np.std(unmatched_edits)),
            'min': float(np.min(unmatched_edits)),
            'max': float(np.max(unmatched_edits))
        }
        
        print(f"\n正样本:")
        print(f"  Jaccard: {analysis['matched_jaccard']['mean']:.4f} ± {analysis['matched_jaccard']['std']:.4f}")
        print(f"  编辑距离: {analysis['matched_edit_distance']['mean']:.2f} ± {analysis['matched_edit_distance']['std']:.2f}")
        
        print(f"\n负样本:")
        print(f"  Jaccard: {analysis['unmatched_jaccard']['mean']:.4f} ± {analysis['unmatched_jaccard']['std']:.4f}")
        print(f"  编辑距离: {analysis['unmatched_edit_distance']['mean']:.2f} ± {analysis['unmatched_edit_distance']['std']:.2f}")
    
    elif method_name == "2b":
        # 节点Jaccard分析
        matched_node_jaccards = [r['node_jaccard'] for r in matched]
        unmatched_node_jaccards = [r['node_jaccard'] for r in unmatched]
        
        analysis['matched_node_jaccard'] = {
            'mean': float(np.mean(matched_node_jaccards)),
            'median': float(np.median(matched_node_jaccards)),
            'std': float(np.std(matched_node_jaccards)),
            'min': float(np.min(matched_node_jaccards)),
            'max': float(np.max(matched_node_jaccards))
        }
        
        analysis['unmatched_node_jaccard'] = {
            'mean': float(np.mean(unmatched_node_jaccards)),
            'median': float(np.median(unmatched_node_jaccards)),
            'std': float(np.std(unmatched_node_jaccards)),
            'min': float(np.min(unmatched_node_jaccards)),
            'max': float(np.max(unmatched_node_jaccards))
        }
        
        # 编辑距离分析
        matched_edits = [r['edit_distance'] for r in matched]
        unmatched_edits = [r['edit_distance'] for r in unmatched]
        
        analysis['matched_edit_distance'] = {
            'mean': float(np.mean(matched_edits)),
            'median': float(np.median(matched_edits)),
            'std': float(np.std(matched_edits)),
            'min': float(np.min(matched_edits)),
            'max': float(np.max(matched_edits))
        }
        
        analysis['unmatched_edit_distance'] = {
            'mean': float(np.mean(unmatched_edits)),
            'median': float(np.median(unmatched_edits)),
            'std': float(np.std(unmatched_edits)),
            'min': float(np.min(unmatched_edits)),
            'max': float(np.max(unmatched_edits))
        }

        matched_readiness = [r['readiness_score'] for r in matched]
        unmatched_readiness = [r['readiness_score'] for r in unmatched]

        analysis['matched_readiness'] = {
            'mean': float(np.mean(matched_readiness)),
            'median': float(np.median(matched_readiness)),
            'std': float(np.std(matched_readiness)),
            'min': float(np.min(matched_readiness)),
            'max': float(np.max(matched_readiness))
        }

        analysis['unmatched_readiness'] = {
            'mean': float(np.mean(unmatched_readiness)),
            'median': float(np.median(unmatched_readiness)),
            'std': float(np.std(unmatched_readiness)),
            'min': float(np.min(unmatched_readiness)),
            'max': float(np.max(unmatched_readiness))
        }
        
        print(f"\n正样本:")
        print(f"  节点Jaccard: {analysis['matched_node_jaccard']['mean']:.4f} ± {analysis['matched_node_jaccard']['std']:.4f}")
        print(f"  编辑距离: {analysis['matched_edit_distance']['mean']:.2f} ± {analysis['matched_edit_distance']['std']:.2f}")
        print(f"  Readiness: {analysis['matched_readiness']['mean']:.4f} ± {analysis['matched_readiness']['std']:.4f}")
        
        print(f"\n负样本:")
        print(f"  节点Jaccard: {analysis['unmatched_node_jaccard']['mean']:.4f} ± {analysis['unmatched_node_jaccard']['std']:.4f}")
        print(f"  编辑距离: {analysis['unmatched_edit_distance']['mean']:.2f} ± {analysis['unmatched_edit_distance']['std']:.2f}")
        print(f"  Readiness: {analysis['unmatched_readiness']['mean']:.4f} ± {analysis['unmatched_readiness']['std']:.4f}")
    
    return analysis


def main():
    print("\n" + "="*80)
    print("🔄 重新运行Method 2a和2b（包含正负样本）")
    print("="*80 + "\n")
    
    # 设置路径
    baseline_project_kg_dir = "outputs/knowledge_graphs/project_proposal_only"
    enhanced_project_kg_dir = "outputs/knowledge_graphs/enhanced_in20_in27"
    student_kg_dir = "outputs/knowledge_graphs/enhanced_student_kg"
    name_mapping_file = "outputs/knowledge_graphs/project_name_mapping.json"
    
    # 读取项目名称映射
    print("📁 加载项目名称映射...")
    with open(name_mapping_file, 'r', encoding='utf-8') as f:
        name_mapping = json.load(f)
    
    print(f"  映射关系: {len(name_mapping)}个项目")
    
    # 载入数据
    print("\n📁 加载项目和学生知识图谱...")
    baseline_projects = load_baseline_project_kgs(baseline_project_kg_dir)
    enhanced_projects = load_enhanced_project_kgs(enhanced_project_kg_dir)
    students = load_all_student_kgs(student_kg_dir)
    
    print(f"✅ 基础项目: {len(baseline_projects)}")
    print(f"✅ 增强项目: {len(enhanced_projects)}")
    print(f"✅ 学生总数: {sum(len(s) for s in students.values())}")
    
    # ========== Method 2a ==========
    print("\n" + "="*80)
    print("📊 Method 2a - 基础知识图谱相似度（正负样本）")
    print("="*80)
    
    # 生成配对（每个项目10个正样本 + 190个负样本）
    pairs_2a = build_all_pairs(baseline_projects, students, name_mapping, "baseline", use_all_negatives=True)
    print(f"\n总配对数: {len(pairs_2a)}")
    matched_count = len([p for p in pairs_2a if p['is_match']])
    unmatched_count = len([p for p in pairs_2a if not p['is_match']])
    print(f"  正样本: {matched_count}")
    print(f"  负样本: {unmatched_count}")
    if matched_count > 0:
        print(f"  样本比例: 1:{unmatched_count // matched_count}")
    
    # 计算相似度
    results_2a = calculate_similarity_for_pairs(pairs_2a, "2a")
    
    # 分析结果
    analysis_2a = analyze_results(results_2a, "2a")
    
    # 保存结果
    output_dir_2a = "outputs/kg_similarity/2a"
    os.makedirs(output_dir_2a, exist_ok=True)
    
    with open(f"{output_dir_2a}/method_2a_scores_with_negatives.json", 'w') as f:
        json.dump(results_2a, f, indent=2, ensure_ascii=False)
    
    with open(f"{output_dir_2a}/method_2a_analysis_with_negatives.json", 'w') as f:
        json.dump(analysis_2a, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Method 2a结果已保存到: {output_dir_2a}")
    
    # ========== Method 2b ==========
    print("\n" + "="*80)
    print("📊 Method 2b - 增强知识图谱相似度（正负样本）")
    print("="*80)

    enhanced_projects_for_pairs: Dict[str, Dict] = {}
    missing_enhanced = []

    for project_name, project_data in baseline_projects.items():
        project_code = project_data.get('project_id')
        if not project_code:
            missing_enhanced.append(project_name)
            continue

        enhanced_data = enhanced_projects.get(project_code)
        if not enhanced_data:
            missing_enhanced.append(project_name)
            continue

        enhanced_projects_for_pairs[project_name] = {
            'folder': enhanced_data.get('folder', project_name),
            'project_id': project_code,
            'project_title': enhanced_data.get('project_title', project_data.get('project_title')),
            'nodes': enhanced_data.get('nodes', []),
            'edges': enhanced_data.get('edges', [])
        }

    if missing_enhanced:
        print("\n⚠️  以下项目缺少对应的增强KG，将被跳过Method 2b:")
        for name in missing_enhanced:
            print(f"  - {name}")

    pairs_2b = build_all_pairs(enhanced_projects_for_pairs, students, name_mapping, "enhanced", use_all_negatives=True)
    print(f"\n总配对数: {len(pairs_2b)}")
    matched_count = len([p for p in pairs_2b if p['is_match']])
    unmatched_count = len([p for p in pairs_2b if not p['is_match']])
    print(f"  正样本: {matched_count}")
    print(f"  负样本: {unmatched_count}")
    if matched_count > 0:
        print(f"  样本比例: 1:{unmatched_count // matched_count}")

    results_2b = calculate_similarity_for_pairs(pairs_2b, "2b")
    analysis_2b = analyze_results(results_2b, "2b")

    output_dir_2b = "outputs/kg_similarity/2b"
    os.makedirs(output_dir_2b, exist_ok=True)

    with open(f"{output_dir_2b}/method_2b_scores_with_negatives.json", 'w') as f:
        json.dump(results_2b, f, indent=2, ensure_ascii=False)

    with open(f"{output_dir_2b}/method_2b_analysis_with_negatives.json", 'w') as f:
        json.dump(analysis_2b, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Method 2b结果已保存到: {output_dir_2b}")

    print("\n" + "="*80)
    print("✅ 完成！所有结果已保存")
    print("="*80)
    print("\n💡 提示:")
    print("  - 所有正负样本都保存在同一个JSON文件中")
    print("  - 使用 'is_match' 字段区分正样本(True)和负样本(False)")
    print("  - 可以运行 python quick_diagnosis.py 查看新的诊断结果")


if __name__ == "__main__":
    main()
