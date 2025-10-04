#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Knowledge Graph Similarity Comparison Experiment

Method 2a: PD only KG vs Student KG
Method 2b: PD+UO KG vs Student KG

度量指标:
- Jaccard Similarity (节点集合相似度)
- Graph Edit Distance (图编辑距离)
"""

import os
import json
import glob
from pathlib import Path
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass, asdict
import numpy as np
from collections import defaultdict


@dataclass
class GraphSimilarityScore:
    """图相似度分数"""
    project_name: str
    student_id: str
    is_match: bool  # 学生是否由该项目生成
    jaccard_similarity: float  # 节点Jaccard相似度
    jaccard_edge_similarity: float  # 边Jaccard相似度（新增）
    edit_distance: int  # 图编辑距离
    common_nodes: int  # 共同节点数
    project_only_nodes: int  # 仅项目有的节点数
    student_only_nodes: int  # 仅学生有的节点数
    common_edges: int  # 共同边数（新增）
    project_only_edges: int  # 仅项目有的边数（新增）
    student_only_edges: int  # 仅学生有的边数（新增）


class KnowledgeGraphLoader:
    """知识图谱加载器"""
    
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
        
        # 如果是数组格式（three_layer_projects 或 project_proposal_only），需要加载对应的relationships文件
        if isinstance(data, list):
            # 检查是否是entities文件
            if '_entities.json' in file_path or file_path.endswith('entities.json'):
                # 尝试加载对应的relationships文件
                if '_entities.json' in file_path:
                    rel_file = file_path.replace('_entities.json', '_relationships.json')
                else:
                    # project_proposal_only格式：entities.json -> relationships.json
                    rel_file = file_path.replace('entities.json', 'relationships.json')
                
                relationships = []
                if Path(rel_file).exists():
                    with open(rel_file, 'r', encoding='utf-8') as f:
                        relationships = json.load(f)
                
                # 返回标准格式
                return {
                    'entities': data,
                    'relationships': relationships
                }
            else:
                # 可能是relationships文件，返回为relationships
                return {
                    'entities': [],
                    'relationships': data
                }
        
        # 其他情况，尝试包装为标准格式
        return data
    
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
            # 尝试 'nodes' 键
            if 'nodes' in kg_data:
                for node in kg_data['nodes']:
                    if isinstance(node, dict) and 'id' in node:
                        nodes.add(node['id'])
                    elif isinstance(node, str):
                        nodes.add(node)
            
            # 尝试 'entities' 键
            if 'entities' in kg_data:
                for entity in kg_data['entities']:
                    if isinstance(entity, dict) and 'id' in entity:
                        nodes.add(entity['id'])
                    elif isinstance(entity, str):
                        nodes.add(entity)
        
        return nodes
    
    @staticmethod
    def extract_edges(kg_data: Dict) -> Set[Tuple[str, str]]:
        """提取知识图谱中的所有边"""
        edges = set()
        
        if 'edges' in kg_data:
            for edge in kg_data['edges']:
                if isinstance(edge, dict):
                    source = edge.get('source') or edge.get('from')
                    target = edge.get('target') or edge.get('to')
                    if source and target:
                        edges.add((source, target))
        
        if 'relationships' in kg_data:
            for rel in kg_data['relationships']:
                if isinstance(rel, dict):
                    source = rel.get('source_id') or rel.get('source')
                    target = rel.get('target_id') or rel.get('target')
                    if source and target:
                        edges.add((source, target))
        
        return edges


class GraphSimilarityComparator:
    """图相似度计算器"""
    
    @staticmethod
    def compute_jaccard_similarity(set1: Set, set2: Set) -> float:
        """计算Jaccard相似度"""
        if not set1 and not set2:
            return 1.0
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    @staticmethod
    def compute_edit_distance(nodes1: Set, nodes2: Set, edges1: Set, edges2: Set) -> int:
        """计算简化的图编辑距离"""
        # 节点差异
        node_diff = len(nodes1 ^ nodes2)  # 对称差
        
        # 边差异（只考虑共同节点的边）
        common_nodes = nodes1 & nodes2
        edges1_filtered = {(s, t) for s, t in edges1 if s in common_nodes and t in common_nodes}
        edges2_filtered = {(s, t) for s, t in edges2 if s in common_nodes and t in common_nodes}
        edge_diff = len(edges1_filtered ^ edges2_filtered)
        
        return node_diff + edge_diff
    
    @staticmethod
    def compare_graphs(project_kg: Dict, student_kg: Dict, 
                      project_name: str, student_id: str, is_match: bool) -> GraphSimilarityScore:
        """对比两个知识图谱"""
        loader = KnowledgeGraphLoader()
        
        # 提取节点和边
        project_nodes = loader.extract_node_ids(project_kg)
        student_nodes = loader.extract_node_ids(student_kg)
        project_edges = loader.extract_edges(project_kg)
        student_edges = loader.extract_edges(student_kg)
        
        # 计算节点相似度
        jaccard_nodes = GraphSimilarityComparator.compute_jaccard_similarity(project_nodes, student_nodes)
        
        # 计算边相似度（新增）
        # 只考虑共同节点之间的边
        common_nodes = project_nodes & student_nodes
        if common_nodes:
            project_edges_filtered = {(s, t) for s, t in project_edges if s in common_nodes and t in common_nodes}
            student_edges_filtered = {(s, t) for s, t in student_edges if s in common_nodes and t in common_nodes}
            jaccard_edges = GraphSimilarityComparator.compute_jaccard_similarity(
                project_edges_filtered, student_edges_filtered
            )
        else:
            jaccard_edges = 0.0
        
        # 计算编辑距离
        edit_dist = GraphSimilarityComparator.compute_edit_distance(
            project_nodes, student_nodes, project_edges, student_edges
        )
        
        # 统计节点
        common_node_count = len(project_nodes & student_nodes)
        project_only_node_count = len(project_nodes - student_nodes)
        student_only_node_count = len(student_nodes - project_nodes)
        
        # 统计边（新增）
        common_edge_count = len(project_edges & student_edges)
        project_only_edge_count = len(project_edges - student_edges)
        student_only_edge_count = len(student_edges - project_edges)
        
        return GraphSimilarityScore(
            project_name=project_name,
            student_id=student_id,
            is_match=is_match,
            jaccard_similarity=jaccard_nodes,
            jaccard_edge_similarity=jaccard_edges,
            edit_distance=edit_dist,
            common_nodes=common_node_count,
            project_only_nodes=project_only_node_count,
            student_only_nodes=student_only_node_count,
            common_edges=common_edge_count,
            project_only_edges=project_only_edge_count,
            student_only_edges=student_only_edge_count
        )


class KGSimilarityExperiment:
    """KG相似度实验主类"""
    
    def __init__(self):
        self.loader = KnowledgeGraphLoader()
        self.comparator = GraphSimilarityComparator()
    
    def run_method_2a(self) -> List[GraphSimilarityScore]:
        """Method 2a: PD only KG vs Student KG"""
        print("=" * 80)
        print("Method 2a: PD only KG vs Student KG")
        print("=" * 80)
        print()
        
        project_kg_dir = "outputs1/knowledge_graphs/project_proposal_only"
        student_kg_dir = "outputs1/knowledge_graphs/enhanced_student_kg"
        mapping_file = "outputs1/knowledge_graphs/project_name_mapping.json"
        
        results = []
        
        # 加载项目名称映射
        if not Path(mapping_file).exists():
            print(f"❌ 映射文件不存在: {mapping_file}")
            return results
        
        with open(mapping_file, 'r', encoding='utf-8') as f:
            name_mapping = json.load(f)
        
        # 获取所有项目目录（新的目录结构）
        project_dirs = [d for d in Path(project_kg_dir).iterdir() if d.is_dir()]
        
        if not project_dirs:
            print("❌ 未找到项目KG目录")
            print(f"   目录: {project_kg_dir}")
            return results
        
        print(f"✓ 找到 {len(project_dirs)} 个项目KG")
        print(f"✓ 加载映射: {len(name_mapping)} 个映射")
        print()
        
        for proj_dir in project_dirs:
            # 提取简化项目名（目录名）
            simplified_name = proj_dir.name
            
            # 获取原始项目名
            original_name = name_mapping.get(simplified_name, simplified_name)
            
            if not original_name:
                print(f"⏭️  跳过空项目名: {simplified_name}")
                continue
            
            print(f"处理项目: {simplified_name}")
            print(f"  → 原始名称: {original_name}")
            
            # 加载项目KG（从子目录中的entities.json）
            proj_file = proj_dir / "entities.json"
            if not proj_file.exists():
                print(f"  ⚠️  未找到entities.json: {proj_file}")
                continue
            
            project_kg = self.loader.load_kg_json(str(proj_file))
            
            # 找到该项目的学生KG
            student_kg_pattern = f"{student_kg_dir}/{original_name}/*_enhanced_kg.json"
            student_files = glob.glob(student_kg_pattern)
            
            if not student_files:
                print(f"  ⚠️  未找到学生KG: {student_kg_pattern}")
                continue
            
            # 对该项目的每个学生计算相似度
            for student_file in student_files:
                student_id = Path(student_file).stem
                student_kg = self.loader.load_kg_json(student_file)
                
                score = self.comparator.compare_graphs(
                    project_kg, student_kg,
                    simplified_name, student_id, is_match=True
                )
                results.append(score)
            
            print(f"  ✓ 已处理 {len(student_files)} 个匹配学生")
            
            # TODO: 添加不匹配的学生对比
        
        print()
        print(f"✓ Method 2a 完成: {len(results)} 个对比")
        return results
    
    def run_method_2b(self) -> List[GraphSimilarityScore]:
        """Method 2b: PD+UO KG vs Student KG"""
        print("=" * 80)
        print("Method 2b: PD+UO KG vs Student KG")
        print("=" * 80)
        print()
        
        project_kg_dir = "outputs1/knowledge_graphs/enhanced_in20_in27"
        student_kg_dir = "outputs1/knowledge_graphs/enhanced_student_kg"
        
        results = []
        
        # 获取所有项目KG目录
        project_dirs = [d for d in Path(project_kg_dir).iterdir() if d.is_dir()]
        
        if not project_dirs:
            print("❌ 未找到项目KG目录")
            print(f"   目录: {project_kg_dir}")
            return results
        
        print(f"✓ 找到 {len(project_dirs)} 个项目KG目录")
        print()
        
        for proj_dir in project_dirs:
            proj_name = proj_dir.name
            
            print(f"处理项目: {proj_name}")
            
            # 找到项目KG文件
            kg_files = list(proj_dir.glob("*_enhanced_kg.json"))
            if not kg_files:
                print(f"  ⚠️  未找到KG文件")
                continue
            
            project_kg = self.loader.load_kg_json(str(kg_files[0]))
            
            # 找到该项目的学生KG
            student_kg_pattern = f"{student_kg_dir}/{proj_name}/*_kg.json"
            student_files = glob.glob(student_kg_pattern)
            
            if not student_files:
                print(f"  ⚠️  未找到学生KG: {student_kg_pattern}")
                continue
            
            # 对该项目的每个学生计算相似度
            for student_file in student_files:
                student_id = Path(student_file).stem
                student_kg = self.loader.load_kg_json(student_file)
                
                score = self.comparator.compare_graphs(
                    project_kg, student_kg,
                    proj_name, student_id, is_match=True
                )
                results.append(score)
            
            print(f"  ✓ 已处理 {len(student_files)} 个匹配学生")
        
        print()
        print(f"✓ Method 2b 完成: {len(results)} 个对比")
        return results
    
    def analyze_results(self, method_name: str, scores: List[GraphSimilarityScore]) -> Dict:
        """分析实验结果"""
        matched = [s for s in scores if s.is_match]
        unmatched = [s for s in scores if not s.is_match]
        
        def compute_stats(score_list, metric_name):
            if not score_list:
                return {}
            
            if metric_name == 'jaccard_nodes':
                values = [s.jaccard_similarity for s in score_list]
            elif metric_name == 'jaccard_edges':
                values = [s.jaccard_edge_similarity for s in score_list]
            else:  # edit_distance
                values = [s.edit_distance for s in score_list]
            
            return {
                'mean': float(np.mean(values)),
                'median': float(np.median(values)),
                'std': float(np.std(values)),
                'min': float(np.min(values)),
                'max': float(np.max(values)),
            }
        
        results = {
            'method': method_name,
            'total_pairs': len(scores),
            'matched_pairs': len(matched),
            'unmatched_pairs': len(unmatched),
            'matched_jaccard_nodes': compute_stats(matched, 'jaccard_nodes'),
            'matched_jaccard_edges': compute_stats(matched, 'jaccard_edges'),
            'matched_edit_distance': compute_stats(matched, 'edit_distance'),
            'unmatched_jaccard_nodes': compute_stats(unmatched, 'jaccard_nodes'),
            'unmatched_jaccard_edges': compute_stats(unmatched, 'jaccard_edges'),
            'unmatched_edit_distance': compute_stats(unmatched, 'edit_distance'),
        }
        
        # 计算效果大小
        if matched and unmatched:
            matched_j_nodes = [s.jaccard_similarity for s in matched]
            unmatched_j_nodes = [s.jaccard_similarity for s in unmatched]
            matched_j_edges = [s.jaccard_edge_similarity for s in matched]
            unmatched_j_edges = [s.jaccard_edge_similarity for s in unmatched]
            
            delta_jaccard_nodes = np.mean(matched_j_nodes) - np.mean(unmatched_j_nodes)
            delta_jaccard_edges = np.mean(matched_j_edges) - np.mean(unmatched_j_edges)
            results['delta_jaccard_nodes'] = float(delta_jaccard_nodes)
            results['delta_jaccard_edges'] = float(delta_jaccard_edges)
        
        return results
    
    def save_results(self, method_name: str, scores: List[GraphSimilarityScore], analysis: Dict):
        """保存结果"""
        output_dir = Path("outputs/kg_similarity")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存详细分数
        scores_file = output_dir / f"{method_name}_scores.json"
        with open(scores_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(s) for s in scores], f, indent=2, ensure_ascii=False)
        
        # 保存分析结果
        analysis_file = output_dir / f"{method_name}_analysis.json"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 结果已保存:")
        print(f"   - {scores_file}")
        print(f"   - {analysis_file}")


def main():
    print("=" * 80)
    print("🧪 Knowledge Graph Similarity Experiment")
    print("=" * 80)
    print()
    
    experiment = KGSimilarityExperiment()
    
    # Method 2a
    print("\n" + "=" * 80)
    scores_2a = experiment.run_method_2a()
    
    if scores_2a:
        analysis_2a = experiment.analyze_results("method_2a", scores_2a)
        experiment.save_results("method_2a", scores_2a, analysis_2a)
        
        print("\n📈 Method 2a 统计:")
        print(f"   匹配对 Jaccard: {analysis_2a['matched_jaccard']['mean']:.4f}")
        if analysis_2a['unmatched_jaccard']:
            print(f"   不匹配对 Jaccard: {analysis_2a['unmatched_jaccard']['mean']:.4f}")
    
    # Method 2b
    print("\n" + "=" * 80)
    scores_2b = experiment.run_method_2b()
    
    if scores_2b:
        analysis_2b = experiment.analyze_results("method_2b", scores_2b)
        experiment.save_results("method_2b", scores_2b, analysis_2b)
        
        print("\n📈 Method 2b 统计:")
        print(f"   匹配对 Jaccard: {analysis_2b['matched_jaccard']['mean']:.4f}")
        if analysis_2b['unmatched_jaccard']:
            print(f"   不匹配对 Jaccard: {analysis_2b['unmatched_jaccard']['mean']:.4f}")
    
    print("\n" + "=" * 80)
    print("✅ 实验完成!")
    print("=" * 80)
    print("\n📂 结果目录: outputs/kg_similarity/")


if __name__ == '__main__':
    main()

