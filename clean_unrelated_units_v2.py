#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理知识图谱中与项目无直接关系的unit节点
只保留项目直接需要的技能所对应的unit
"""

import json
from pathlib import Path
from typing import Dict, Set
from collections import defaultdict


def load_kg(file_path: str) -> Dict:
    """加载知识图谱JSON文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_kg(kg: Dict, file_path: str):
    """保存知识图谱JSON文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(kg, f, indent=2, ensure_ascii=False)


def find_project_relevant_units(kg: Dict) -> Set[str]:
    """
    找出与项目直接相关的unit节点
    
    相关的unit包括:
    1. 项目需要的技能所对应的unit
    2. 项目适合的专业所要求的unit  
    3. 上述unit的直接和间接先决条件
    """
    
    # 1. 找出项目节点
    project_id = None
    for node in kg.get('nodes', []):
        if node['type'] == 'PROJECT':
            project_id = node['id']
            break
    
    if not project_id:
        print("  错误: 未找到PROJECT节点")
        return set()
    
    # 2. 找出项目需要的技能和适合的专业
    project_skills = set()
    project_majors = set()
    
    for edge in kg.get('edges', []):
        if edge['source'] == project_id:
            if edge['relation'] == 'REQUIRES_SKILL':
                project_skills.add(edge['target'])
            elif edge['relation'] == 'SUITABLE_FOR_MAJOR':
                project_majors.add(edge['target'])
    
    print(f"  项目需要的技能数: {len(project_skills)}")
    print(f"  项目适合的专业数: {len(project_majors)}")
    
    # 3. 找出这些技能教授的unit和专业要求的unit
    relevant_units = set()
    
    for edge in kg.get('edges', []):
        # 技能 -> unit (TAUGHT_IN)
        if edge['relation'] == 'TAUGHT_IN':
            if edge['source'] in project_skills and edge['target'].startswith('unit_'):
                relevant_units.add(edge['target'])
        
        # 专业 -> unit (REQUIRES_UNIT)
        if edge['relation'] == 'REQUIRES_UNIT':
            if edge['source'] in project_majors and edge['target'].startswith('unit_'):
                relevant_units.add(edge['target'])
    
    print(f"  直接相关的unit数: {len(relevant_units)}")
    
    # 4. 递归找出这些unit的所有先决条件
    def find_all_prerequisites(unit_id: str, visited: Set[str]):
        """递归查找unit的所有先决条件"""
        if unit_id in visited:
            return
        visited.add(unit_id)
        
        for edge in kg.get('edges', []):
            if (edge['relation'] == 'PREREQUISITE_FOR' and 
                edge['target'] == unit_id and 
                edge['source'].startswith('unit_') and
                edge['source'] != unit_id):
                find_all_prerequisites(edge['source'], visited)
    
    all_relevant_units = set(relevant_units)
    for unit in relevant_units:
        find_all_prerequisites(unit, all_relevant_units)
    
    print(f"  包含先决条件后的unit数: {len(all_relevant_units)}")
    
    return all_relevant_units


def clean_kg(kg: Dict) -> Dict:
    """清理知识图谱中与项目无关的unit节点"""
    
    # 找出项目相关的unit
    relevant_units = find_project_relevant_units(kg)
    
    # 找出所有unit
    all_units = set()
    for node in kg.get('nodes', []):
        if node['type'] == 'UNIT':
            all_units.add(node['id'])
    
    # 找出要删除的unit
    units_to_remove = all_units - relevant_units
    
    print(f"  总unit节点数: {len(all_units)}")
    print(f"  需要删除的unit节点数: {len(units_to_remove)}")
    
    if len(units_to_remove) == 0:
        print("  没有需要删除的unit节点")
        return kg
    
    # 同时需要删除那些只与被删除unit相关的技能
    # 找出哪些技能只教授被删除的unit
    skills_to_check = set()
    for edge in kg.get('edges', []):
        if edge['relation'] == 'TAUGHT_IN' and edge['target'] in units_to_remove:
            if edge['source'].startswith('skill_'):
                skills_to_check.add(edge['source'])
    
    skills_to_remove = set()
    for skill_id in skills_to_check:
        # 检查这个技能是否只教授被删除的unit
        taught_units = set()
        for edge in kg.get('edges', []):
            if edge['relation'] == 'TAUGHT_IN' and edge['source'] == skill_id:
                taught_units.add(edge['target'])
        
        if taught_units.issubset(units_to_remove):
            skills_to_remove.add(skill_id)
    
    print(f"  需要删除的技能节点数: {len(skills_to_remove)}")
    
    nodes_to_remove = units_to_remove | skills_to_remove
    
    # 删除节点
    cleaned_nodes = []
    for node in kg.get('nodes', []):
        if node['id'] not in nodes_to_remove:
            cleaned_nodes.append(node)
    
    # 删除相关的边
    cleaned_edges = []
    for edge in kg.get('edges', []):
        if edge['source'] in nodes_to_remove or edge['target'] in nodes_to_remove:
            continue
        cleaned_edges.append(edge)
    
    kg['nodes'] = cleaned_nodes
    kg['edges'] = cleaned_edges
    
    return kg


def process_kg_file(file_path: str):
    """处理单个KG文件"""
    print(f"\n{'='*80}")
    print(f"处理文件: {file_path.split('/')[-1]}")
    print(f"{'='*80}")
    
    kg = load_kg(file_path)
    cleaned_kg = clean_kg(kg)
    save_kg(cleaned_kg, file_path)
    
    print(f"  已保存清理后的KG")


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
    
    print("\n" + "="*80)
    print("开始清理知识图谱中与项目无直接关系的unit节点")
    print("="*80)
    
    for kg_file in kg_files:
        if kg_file.exists():
            process_kg_file(str(kg_file))
        else:
            print(f"\n警告: 文件不存在 - {kg_file}")
    
    print("\n" + "="*80)
    print("清理完成!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()


