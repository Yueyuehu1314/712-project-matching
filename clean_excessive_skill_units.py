#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理技能关联过多unit的问题
对于关联超过阈值数量unit的技能,只保留权重最高的几个unit
"""

import json
from pathlib import Path
from typing import Dict, Set, List
from collections import defaultdict


def load_kg(file_path: str) -> Dict:
    """加载知识图谱JSON文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_kg(kg: Dict, file_path: str):
    """保存知识图谱JSON文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(kg, f, indent=2, ensure_ascii=False)


def clean_excessive_units(kg: Dict, max_units_per_skill: int = 15) -> Dict:
    """
    清理技能关联过多unit的问题
    
    参数:
        max_units_per_skill: 每个技能最多保留的unit数量
    """
    
    # 找出项目节点
    project_id = None
    for node in kg.get('nodes', []):
        if node['type'] == 'PROJECT':
            project_id = node['id']
            break
    
    if not project_id:
        return kg
    
    # 找出项目需要的技能
    project_skills = {}
    for edge in kg.get('edges', []):
        if edge['source'] == project_id and edge['relation'] == 'REQUIRES_SKILL':
            project_skills[edge['target']] = edge.get('weight', 0)
    
    print(f"  项目需要的技能数: {len(project_skills)}")
    
    # 统计每个技能关联的unit及其权重
    skill_units = defaultdict(list)  # {skill_id: [(unit_id, weight, edge)]}
    
    for edge in kg.get('edges', []):
        if edge['relation'] == 'TAUGHT_IN' and edge['source'] in project_skills:
            if edge['target'].startswith('unit_'):
                skill_units[edge['source']].append({
                    'unit_id': edge['target'],
                    'weight': edge.get('weight', 1.0),
                    'edge': edge
                })
    
    # 识别需要处理的技能(关联unit过多的技能)
    units_to_keep = set()
    units_to_remove = set()
    edges_to_remove = []
    
    for skill_id, unit_edges in skill_units.items():
        skill_name = next((n['name'] for n in kg['nodes'] if n['id'] == skill_id), skill_id)
        
        if len(unit_edges) > max_units_per_skill:
            # 按权重排序,只保留权重最高的unit
            sorted_units = sorted(unit_edges, key=lambda x: x['weight'], reverse=True)
            kept_units = sorted_units[:max_units_per_skill]
            removed_units = sorted_units[max_units_per_skill:]
            
            print(f"  技能 '{skill_name}': 关联{len(unit_edges)}个unit -> 保留{len(kept_units)}个")
            
            for item in kept_units:
                units_to_keep.add(item['unit_id'])
            
            for item in removed_units:
                units_to_remove.add(item['unit_id'])
                edges_to_remove.append(item['edge'])
        else:
            # unit数量合理,全部保留
            for item in unit_edges:
                units_to_keep.add(item['unit_id'])
    
    # 专业要求的unit也要保留
    for edge in kg.get('edges', []):
        if edge['relation'] == 'REQUIRES_UNIT' and edge['target'].startswith('unit_'):
            units_to_keep.add(edge['target'])
    
    # 保留必要unit的先决条件
    def find_prerequisites(unit_id: str, visited: Set[str]):
        """递归查找unit的所有先决条件"""
        if unit_id in visited:
            return
        visited.add(unit_id)
        
        for edge in kg.get('edges', []):
            if (edge['relation'] == 'PREREQUISITE_FOR' and 
                edge['target'] == unit_id and 
                edge['source'].startswith('unit_') and
                edge['source'] != unit_id):
                find_prerequisites(edge['source'], visited)
    
    all_units_to_keep = set(units_to_keep)
    for unit in units_to_keep:
        find_prerequisites(unit, all_units_to_keep)
    
    # 更新要删除的unit集合(排除先决条件链中的unit)
    final_units_to_remove = units_to_remove - all_units_to_keep
    
    print(f"  初始要删除的unit: {len(units_to_remove)}")
    print(f"  保留的unit(包括先决条件): {len(all_units_to_keep)}")
    print(f"  最终删除的unit: {len(final_units_to_remove)}")
    
    if len(final_units_to_remove) == 0:
        print("  没有需要删除的unit")
        return kg
    
    # 删除nodes
    cleaned_nodes = []
    for node in kg.get('nodes', []):
        if node['id'] not in final_units_to_remove:
            cleaned_nodes.append(node)
    
    # 删除edges
    cleaned_edges = []
    for edge in kg.get('edges', []):
        # 跳过与删除unit相关的边
        if edge['source'] in final_units_to_remove or edge['target'] in final_units_to_remove:
            continue
        cleaned_edges.append(edge)
    
    kg['nodes'] = cleaned_nodes
    kg['edges'] = cleaned_edges
    
    return kg


def process_kg_file(file_path: str, max_units_per_skill: int = 15):
    """处理单个KG文件"""
    print(f"\n{'='*100}")
    print(f"处理文件: {file_path.split('/')[-1]}")
    print(f"{'='*100}")
    
    kg = load_kg(file_path)
    
    # 清理前统计
    total_units_before = sum(1 for n in kg['nodes'] if n['type'] == 'UNIT')
    print(f"  清理前unit总数: {total_units_before}")
    
    # 清理
    cleaned_kg = clean_excessive_units(kg, max_units_per_skill)
    
    # 清理后统计
    total_units_after = sum(1 for n in cleaned_kg['nodes'] if n['type'] == 'UNIT')
    print(f"  清理后unit总数: {total_units_after}")
    print(f"  删除了 {total_units_before - total_units_after} 个unit")
    
    # 保存
    save_kg(cleaned_kg, file_path)
    print(f"  已保存")


def main():
    """主函数"""
    base_dir = Path("/Users/lynn/Documents/GitHub/ProjectMatching/outputs/knowledge_graphs/enhanced_in20_in27")
    
    kg_files = [
        base_dir / "AI-Driven Project-Student Matching under Data Scarcity and Privacy Constraints" / 
        "AI-Driven Project-Student Matching under Data Scarcity and Privacy Constraints_enhanced_kg.json",
        
        base_dir / "Assessing the IT Skill Requirements Expected from Graduates Among Various Industry Professionals" /
        "Assessing the IT Skill Requirements Expected from Graduates Among Various Industry Professionals_enhanced_kg.json",
        
        base_dir / "IoT-Based Spectral Sensing and Machine Learning for Plant Health Monitoring" /
        "IoT-Based Spectral Sensing and Machine Learning for Plant Health Monitoring_enhanced_kg.json",
        
        base_dir / "JZhang_IFN712 Project Proposal 1_2025_CS " /
        "JZhang_IFN712 Project Proposal 1_2025_CS _enhanced_kg.json",
        
        base_dir / "Smart Intersection Localization for Pedestrians Using Bluetooth and Deep learning" /
        "Smart Intersection Localization for Pedestrians Using Bluetooth and Deep learning_enhanced_kg.json",
        
        base_dir / "VitalID_ Smartphone-Based Identity Authentication Using Heart Rate and Breathing Signals" /
        "VitalID_ Smartphone-Based Identity Authentication Using Heart Rate and Breathing Signals_enhanced_kg.json",
    ]
    
    # 设置每个技能最多保留的unit数量
    # 可以根据需要调整这个值
    MAX_UNITS_PER_SKILL = 10
    
    print("\n" + "="*100)
    print(f"开始清理技能关联过多unit的问题 (每个技能最多保留{MAX_UNITS_PER_SKILL}个unit)")
    print("="*100)
    
    for kg_file in kg_files:
        if kg_file.exists():
            process_kg_file(str(kg_file), MAX_UNITS_PER_SKILL)
        else:
            print(f"\n警告: 文件不存在 - {kg_file}")
    
    print("\n" + "="*100)
    print("清理完成!")
    print("="*100 + "\n")


if __name__ == "__main__":
    main()


