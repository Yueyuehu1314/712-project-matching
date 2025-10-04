#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Method 2b Enhanced: KG Similarity with Gap Analysis

增强版Method 2b实验，包含：
1. 节点和边的Jaccard相似度
2. 详细的gap分析（学生缺少什么）
3. 学习建议生成
"""

import os
import json
import glob
from pathlib import Path
from typing import Dict, List, Set
import numpy as np
from collections import defaultdict

# 导入原有的类
from run_kg_similarity_experiment import (
    KnowledgeGraphLoader,
    GraphSimilarityComparator,
    GraphSimilarityScore
)


class GapAnalyzer:
    """学生-项目知识差距分析器"""
    
    def __init__(self):
        self.loader = KnowledgeGraphLoader()
    
    def analyze_gap(self, project_kg: Dict, student_kg: Dict, 
                    project_name: str, student_id: str) -> Dict:
        """分析学生相对于项目的知识差距"""
        
        # 提取节点和边
        project_nodes = self.loader.extract_node_ids(project_kg)
        student_nodes = self.loader.extract_node_ids(student_kg)
        project_edges = self.loader.extract_edges(project_kg)
        student_edges = self.loader.extract_edges(student_kg)
        
        # 获取实体详情
        project_entities = self._get_entity_details(project_kg)
        student_entities = self._get_entity_details(student_kg)
        
        # 计算缺失的节点
        missing_nodes = project_nodes - student_nodes
        missing_node_details = [
            project_entities.get(node_id, {'id': node_id, 'name': node_id})
            for node_id in missing_nodes
        ]
        
        # 计算缺失的边（只考虑共同节点之间的边）
        common_nodes = project_nodes & student_nodes
        if common_nodes:
            project_edges_filtered = {(s, t) for s, t in project_edges 
                                     if s in common_nodes and t in common_nodes}
            student_edges_filtered = {(s, t) for s, t in student_edges 
                                     if s in common_nodes and t in common_nodes}
            missing_edges = project_edges_filtered - student_edges_filtered
        else:
            missing_edges = set()
        
        # 计算modification steps
        node_steps = len(missing_nodes)
        edge_steps = len(missing_edges)
        total_steps = node_steps + edge_steps
        
        return {
            'project_name': project_name,
            'student_id': student_id,
            'total_modification_steps': total_steps,
            'missing_nodes_count': node_steps,
            'missing_edges_count': edge_steps,
            'missing_nodes': sorted([
                {
                    'id': entity.get('id', ''),
                    'name': entity.get('name', ''),
                    'type': entity.get('type', 'Unknown')
                }
                for entity in missing_node_details
            ], key=lambda x: x['type']),
            'missing_edges': [
                {
                    'source': s,
                    'target': t,
                    'source_name': project_entities.get(s, {}).get('name', s),
                    'target_name': project_entities.get(t, {}).get('name', t)
                }
                for s, t in sorted(missing_edges)
            ],
            'common_nodes_count': len(common_nodes),
            'readiness_score': len(common_nodes) / len(project_nodes) if project_nodes else 0.0
        }
    
    def _get_entity_details(self, kg_data: Dict) -> Dict:
        """提取实体详情"""
        entities = {}
        
        if isinstance(kg_data, dict):
            if 'entities' in kg_data:
                for entity in kg_data['entities']:
                    if isinstance(entity, dict) and 'id' in entity:
                        entities[entity['id']] = entity
        elif isinstance(kg_data, list):
            for entity in kg_data:
                if isinstance(entity, dict) and 'id' in entity:
                    entities[entity['id']] = entity
        
        return entities
    
    def generate_learning_recommendations(self, gap_analysis: Dict) -> List[str]:
        """基于gap分析生成学习建议"""
        recommendations = []
        
        missing_nodes = gap_analysis['missing_nodes']
        missing_edges = gap_analysis['missing_edges']
        total_steps = gap_analysis['total_modification_steps']
        readiness = gap_analysis['readiness_score']
        
        # 总体评估
        if readiness >= 0.8:
            recommendations.append("✅ 高度匹配！学生已掌握项目所需的大部分知识。")
        elif readiness >= 0.5:
            recommendations.append("⚠️ 中等匹配。学生需要补充一些关键技能。")
        else:
            recommendations.append("❌ 匹配度较低。学生需要大量学习才能胜任此项目。")
        
        recommendations.append(f"\n📊 需要 {total_steps} 个学习步骤 ({gap_analysis['missing_nodes_count']} 个技能 + {gap_analysis['missing_edges_count']} 个知识关系)")
        
        # 按类型分组缺失的技能
        skills_by_type = defaultdict(list)
        for node in missing_nodes:
            node_type = node.get('type', 'Unknown')
            node_name = node.get('name', node.get('id', ''))
            skills_by_type[node_type].append(node_name)
        
        if skills_by_type:
            recommendations.append("\n📚 需要学习的技能：")
            for skill_type, skills in sorted(skills_by_type.items()):
                if skills:
                    recommendations.append(f"\n  {skill_type}:")
                    for skill in sorted(skills)[:5]:  # 最多显示5个
                        recommendations.append(f"    • {skill}")
                    if len(skills) > 5:
                        recommendations.append(f"    ... 以及其他 {len(skills) - 5} 个")
        
        # 推荐课程
        if missing_nodes:
            recommendations.append("\n🎓 建议修读的课程：")
            # 这里可以根据缺失的技能推荐具体课程
            # 简化版本：基于技能类型推荐
            skill_types = set(node.get('type', '') for node in missing_nodes)
            if 'Technology' in skill_types or 'Tool' in skill_types:
                recommendations.append("    • 相关技术课程（如编程、框架使用）")
            if 'Domain' in skill_types or 'Concept' in skill_types:
                recommendations.append("    • 专业领域课程（如机器学习、数据科学）")
            if 'Method' in skill_types:
                recommendations.append("    • 方法论课程（如研究方法、算法设计）")
        
        return recommendations


def load_project_name_mapping(mapping_file: str) -> Dict[str, str]:
    """
    加载项目名称映射文件
    
    Returns:
        Dict[简化名称 -> 原始项目目录名]
    """
    if not os.path.exists(mapping_file):
        print(f"⚠️  映射文件不存在: {mapping_file}")
        return {}
    
    with open(mapping_file, 'r', encoding='utf-8') as f:
        mapping = json.load(f)
    
    print(f"✓ 加载项目名称映射: {len(mapping)} 个项目")
    return mapping


def create_full_title_to_student_dir_mapping(
    project_kg_dir: str, 
    student_kg_dir: str,
    mapping: Dict[str, str]
) -> Dict[str, str]:
    """
    创建完整项目标题到学生KG目录的映射
    
    Args:
        project_kg_dir: 项目KG目录（enhanced_in20_in27）
        student_kg_dir: 学生KG目录（enhanced_student_kg）
        mapping: 简化名称到原始目录的映射
    
    Returns:
        Dict[完整项目目录名 -> 学生KG目录名]
    """
    title_mapping = {}
    
    # 获取所有学生KG目录名称
    student_dirs = {d.name for d in Path(student_kg_dir).iterdir() if d.is_dir()}
    
    # 遍历项目KG目录
    for proj_dir in Path(project_kg_dir).iterdir():
        if not proj_dir.is_dir():
            continue
        
        full_title = proj_dir.name
        
        # 方法1: 直接匹配（项目名称相同）
        if full_title in student_dirs:
            title_mapping[full_title] = full_title
            print(f"  ✓ 直接匹配: {full_title}")
            continue
        
        # 方法2: 检查是否在映射的值中（原始项目名）
        if full_title in mapping.values():
            title_mapping[full_title] = full_title
            print(f"  ✓ 映射值匹配: {full_title}")
            continue
        
        # 方法3: 通过简化名称的映射匹配
        matched = False
        best_match = None
        best_score = 0
        best_simplified = None
        
        for simplified, original in mapping.items():
            # 检查简化名称的主要部分是否在完整标题中
            simplified_parts = simplified.replace('_', ' ').replace('-', ' ').split()
            
            # 计算匹配分数
            matches = sum(1 for part in simplified_parts 
                        if len(part) > 2 and part.lower() in full_title.lower())
            
            # 如果匹配分数更好
            if matches > best_score:
                best_score = matches
                best_match = original
                best_simplified = simplified
        
        # 如果至少有2个关键词匹配
        if best_simplified and best_score >= 2:
            title_mapping[full_title] = best_match
            matched = True
            print(f"  ✓ 关键词匹配: {full_title[:50]}... -> {best_match}")
        
        if not matched:
            # 方法4: 尝试直接在学生目录中查找包含相似关键词的目录
            title_keywords = set(w.lower() for w in full_title.replace('_', ' ').split() if len(w) > 3)
            for student_dir in student_dirs:
                student_keywords = set(w.lower() for w in student_dir.replace('_', ' ').split() if len(w) > 3)
                common = title_keywords & student_keywords
                if len(common) >= 3:
                    title_mapping[full_title] = student_dir
                    print(f"  ✓ 关键词搜索: {full_title[:50]}... -> {student_dir}")
                    matched = True
                    break
        
        if not matched:
            print(f"  ⚠️  未找到映射: {full_title}")
    
    return title_mapping


def run_method_2b_with_gap_analysis():
    """运行Method 2b并生成gap分析"""
    
    print("=" * 80)
    print("Method 2b Enhanced: KG Similarity + Gap Analysis")
    print("=" * 80)
    print()
    
    # 配置路径
    project_kg_dir = "outputs1/knowledge_graphs/enhanced_in20_in27"
    student_kg_dir = "outputs1/knowledge_graphs/enhanced_student_kg"
    mapping_file = "outputs1/knowledge_graphs/project_name_mapping.json"
    output_dir = Path("outputs/kg_similarity")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 加载项目名称映射
    print("📋 加载项目名称映射...")
    name_mapping = load_project_name_mapping(mapping_file)
    
    # 创建完整标题到学生目录的映射
    print("\n🔗 建立项目标题映射...")
    title_to_student_dir = create_full_title_to_student_dir_mapping(
        project_kg_dir, student_kg_dir, name_mapping
    )
    
    print(f"\n✓ 成功映射: {len(title_to_student_dir)} 个项目")
    print()
    
    # 初始化
    loader = KnowledgeGraphLoader()
    comparator = GraphSimilarityComparator()
    gap_analyzer = GapAnalyzer()
    
    # 获取所有项目目录
    project_dirs = [d for d in Path(project_kg_dir).iterdir() if d.is_dir()]
    
    if not project_dirs:
        print("❌ 未找到项目KG目录")
        return
    
    print(f"找到 {len(project_dirs)} 个项目目录")
    print()
    
    # 存储结果
    all_scores = []
    all_gaps = []
    
    # 对每个项目
    for proj_dir in sorted(project_dirs):
        proj_name = proj_dir.name
        
        print(f"处理项目: {proj_name}")
        
        # 加载项目KG
        kg_files = list(proj_dir.glob("*_enhanced_kg.json"))
        if not kg_files:
            print(f"  ⚠️  未找到KG文件")
            continue
        
        project_kg = loader.load_kg_json(str(kg_files[0]))
        
        # 查找对应的学生KG目录
        student_dir_name = title_to_student_dir.get(proj_name)
        if not student_dir_name:
            print(f"  ⚠️  未找到学生KG目录映射")
            continue
        
        # 找到该项目的学生KG
        student_kg_path = Path(student_kg_dir) / student_dir_name
        if not student_kg_path.exists():
            print(f"  ⚠️  学生KG目录不存在: {student_dir_name}")
            continue
        
        student_files = list(student_kg_path.glob("*_enhanced_kg.json"))
        
        if not student_files:
            print(f"  ⚠️  未找到学生KG文件")
            continue
        
        # 对每个学生
        for student_file in student_files:
            student_id = Path(student_file).stem
            student_kg = loader.load_kg_json(student_file)
            
            # 计算相似度
            score = comparator.compare_graphs(
                project_kg, student_kg,
                proj_name, student_id, is_match=True
            )
            all_scores.append(score)
            
            # 分析gap
            gap = gap_analyzer.analyze_gap(
                project_kg, student_kg,
                proj_name, student_id
            )
            all_gaps.append(gap)
        
        print(f"  ✓ 已处理 {len(student_files)} 个学生")
    
    print()
    print(f"✓ 总共处理了 {len(all_scores)} 个项目-学生对")
    print()
    
    # 保存详细结果
    print("💾 保存结果...")
    
    # 1. 相似度分数
    scores_file = output_dir / "method_2b_scores_enhanced.json"
    with open(scores_file, 'w', encoding='utf-8') as f:
        json.dump([vars(s) for s in all_scores], f, indent=2, ensure_ascii=False)
    print(f"   - {scores_file}")
    
    # 2. Gap分析
    gaps_file = output_dir / "method_2b_gaps.json"
    with open(gaps_file, 'w', encoding='utf-8') as f:
        json.dump(all_gaps, f, indent=2, ensure_ascii=False)
    print(f"   - {gaps_file}")
    
    # 3. 统计分析
    analysis = analyze_results(all_scores, all_gaps)
    analysis_file = output_dir / "method_2b_analysis_enhanced.json"
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    print(f"   - {analysis_file}")
    
    # 4. 生成学习建议报告
    generate_learning_report(all_gaps, gap_analyzer, output_dir)
    
    print()
    print("✅ 实验完成！")
    
    return all_scores, all_gaps, analysis


def analyze_results(scores: List[GraphSimilarityScore], gaps: List[Dict]) -> Dict:
    """分析结果"""
    
    # 相似度统计
    jaccard_nodes = [s.jaccard_similarity for s in scores]
    jaccard_edges = [s.jaccard_edge_similarity for s in scores]
    edit_distances = [s.edit_distance for s in scores]
    
    # Gap统计
    modification_steps = [g['total_modification_steps'] for g in gaps]
    readiness_scores = [g['readiness_score'] for g in gaps]
    missing_nodes_counts = [g['missing_nodes_count'] for g in gaps]
    missing_edges_counts = [g['missing_edges_count'] for g in gaps]
    
    return {
        'method': 'method_2b_enhanced',
        'total_pairs': len(scores),
        'similarity_metrics': {
            'jaccard_nodes': {
                'mean': float(np.mean(jaccard_nodes)),
                'median': float(np.median(jaccard_nodes)),
                'std': float(np.std(jaccard_nodes)),
                'min': float(np.min(jaccard_nodes)),
                'max': float(np.max(jaccard_nodes))
            },
            'jaccard_edges': {
                'mean': float(np.mean(jaccard_edges)),
                'median': float(np.median(jaccard_edges)),
                'std': float(np.std(jaccard_edges)),
                'min': float(np.min(jaccard_edges)),
                'max': float(np.max(jaccard_edges))
            },
            'edit_distance': {
                'mean': float(np.mean(edit_distances)),
                'median': float(np.median(edit_distances)),
                'std': float(np.std(edit_distances)),
                'min': float(np.min(edit_distances)),
                'max': float(np.max(edit_distances))
            }
        },
        'gap_analysis': {
            'modification_steps': {
                'mean': float(np.mean(modification_steps)),
                'median': float(np.median(modification_steps)),
                'std': float(np.std(modification_steps)),
                'min': float(np.min(modification_steps)),
                'max': float(np.max(modification_steps))
            },
            'readiness_score': {
                'mean': float(np.mean(readiness_scores)),
                'median': float(np.median(readiness_scores)),
                'std': float(np.std(readiness_scores)),
                'min': float(np.min(readiness_scores)),
                'max': float(np.max(readiness_scores))
            },
            'missing_nodes': {
                'mean': float(np.mean(missing_nodes_counts)),
                'median': float(np.median(missing_nodes_counts)),
                'std': float(np.std(missing_nodes_counts)),
                'min': float(np.min(missing_nodes_counts)),
                'max': float(np.max(missing_nodes_counts))
            },
            'missing_edges': {
                'mean': float(np.mean(missing_edges_counts)),
                'median': float(np.median(missing_edges_counts)),
                'std': float(np.std(missing_edges_counts)),
                'min': float(np.min(missing_edges_counts)),
                'max': float(np.max(missing_edges_counts))
            }
        }
    }


def generate_learning_report(gaps: List[Dict], gap_analyzer: GapAnalyzer, output_dir: Path):
    """生成学习建议报告"""
    
    report_file = output_dir / "method_2b_learning_recommendations.txt"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("Method 2b: 学生学习建议报告\n")
        f.write("=" * 80 + "\n\n")
        
        # 按项目分组
        gaps_by_project = defaultdict(list)
        for gap in gaps:
            gaps_by_project[gap['project_name']].append(gap)
        
        # 为每个项目生成报告
        for project_name in sorted(gaps_by_project.keys()):
            project_gaps = gaps_by_project[project_name]
            
            f.write(f"\n{'=' * 80}\n")
            f.write(f"项目: {project_name}\n")
            f.write(f"{'=' * 80}\n\n")
            
            # 找到最佳匹配的学生
            best_gap = min(project_gaps, key=lambda x: x['total_modification_steps'])
            
            f.write(f"📊 统计摘要:\n")
            f.write(f"  - 总学生数: {len(project_gaps)}\n")
            f.write(f"  - 平均modification steps: {np.mean([g['total_modification_steps'] for g in project_gaps]):.1f}\n")
            f.write(f"  - 平均readiness: {np.mean([g['readiness_score'] for g in project_gaps]):.2%}\n")
            f.write(f"  - 最佳匹配学生: {best_gap['student_id']} (steps={best_gap['total_modification_steps']})\n\n")
            
            # 为前3名学生生成详细建议
            top_students = sorted(project_gaps, key=lambda x: x['total_modification_steps'])[:3]
            
            f.write(f"🎯 Top 3 最匹配学生的学习建议:\n\n")
            
            for i, gap in enumerate(top_students, 1):
                f.write(f"{'-' * 80}\n")
                f.write(f"第 {i} 名: {gap['student_id']}\n")
                f.write(f"{'-' * 80}\n\n")
                
                recommendations = gap_analyzer.generate_learning_recommendations(gap)
                for rec in recommendations:
                    f.write(rec + "\n")
                
                f.write("\n")
    
    print(f"   - {report_file}")


if __name__ == "__main__":
    scores, gaps, analysis = run_method_2b_with_gap_analysis()

