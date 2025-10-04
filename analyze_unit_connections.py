#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析知识图谱中unit节点的连接类型
"""

import json
from pathlib import Path
from typing import Dict, Set
from collections import defaultdict


def load_kg(file_path: str) -> Dict:
    """加载知识图谱JSON文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_unit_connections(kg: Dict):
    """分析unit节点的连接类型"""
    
    # 统计不同类型的连接
    units_taught_by_skills = set()  # 被技能教授的unit
    units_required_by_majors = set()  # 被专业要求的unit
    units_as_prerequisites = defaultdict(set)  # 作为先决条件的unit及其依赖
    units_with_prerequisites = set()  # 有先决条件的unit
    
    # 遍历所有边
    for edge in kg.get('edges', []):
        source = edge['source']
        target = edge['target']
        relation = edge['relation']
        
        # 技能 -> unit (TAUGHT_IN)
        if relation == 'TAUGHT_IN' and target.startswith('unit_'):
            units_taught_by_skills.add(target)
        
        # 专业 -> unit (REQUIRES_UNIT)
        if relation == 'REQUIRES_UNIT' and target.startswith('unit_'):
            units_required_by_majors.add(target)
        
        # unit -> unit (PREREQUISITE_FOR, 非自引用)
        if relation == 'PREREQUISITE_FOR':
            if source.startswith('unit_') and target.startswith('unit_'):
                if source != target:
                    units_as_prerequisites[source].add(target)
                    units_with_prerequisites.add(target)
    
    # 找出所有unit节点
    all_units = set()
    unit_names = {}
    for node in kg.get('nodes', []):
        if node['type'] == 'UNIT':
            all_units.add(node['id'])
            unit_names[node['id']] = node['name']
    
    # 分类分析
    print(f"\n总unit节点数: {len(all_units)}")
    print(f"被技能直接教授的unit: {len(units_taught_by_skills)}")
    print(f"被专业要求的unit: {len(units_required_by_majors)}")
    
    # 找出只通过先决条件关系连接的unit
    only_prerequisite_units = all_units - units_taught_by_skills - units_required_by_majors
    print(f"只通过先决条件连接的unit: {len(only_prerequisite_units)}")
    
    # 进一步分析:找出那些既不被技能教授,也不被专业要求,且只作为其他unit的远程先决条件的unit
    # 这些可能是不太相关的unit
    weakly_connected_units = set()
    
    # 递归查找从直接相关unit可达的所有先决条件unit
    directly_relevant_units = units_taught_by_skills | units_required_by_majors
    reachable_prerequisites = set()
    
    def find_prerequisites(unit_id: str, visited: Set[str]):
        """递归查找unit的所有先决条件"""
        if unit_id in visited:
            return
        visited.add(unit_id)
        
        # 查找unit_id作为目标的所有PREREQUISITE_FOR边的源节点
        for edge in kg.get('edges', []):
            if (edge['relation'] == 'PREREQUISITE_FOR' and 
                edge['target'] == unit_id and 
                edge['source'].startswith('unit_') and
                edge['source'] != unit_id):
                find_prerequisites(edge['source'], visited)
    
    # 从直接相关的unit开始,找出所有可达的先决条件
    for unit in directly_relevant_units:
        find_prerequisites(unit, reachable_prerequisites)
    
    # 找出那些不在先决条件链中的unit
    isolated_units = all_units - directly_relevant_units - reachable_prerequisites
    
    print(f"\n详细分类:")
    print(f"1. 直接相关的unit (被技能教授或被专业要求): {len(directly_relevant_units)}")
    print(f"2. 在先决条件链中的unit: {len(reachable_prerequisites)}")
    print(f"3. 孤立的unit (不在上述两类中): {len(isolated_units)}")
    
    if isolated_units:
        print(f"\n孤立的unit列表:")
        for unit_id in sorted(isolated_units):
            print(f"  - {unit_id}: {unit_names.get(unit_id, 'Unknown')}")
    
    # 检查这些unit是否只是自引用或与项目无关
    return isolated_units


def main():
    """主函数"""
    base_dir = Path("/Users/lynn/Documents/GitHub/ProjectMatching/outputs/knowledge_graphs/enhanced_in20_in27")
    
    kg_files = [
        ("AI-Driven Project Matching", 
         base_dir / "AI-Driven Project-Student Matching under Data Scarcity and Privacy Constraints" / 
         "AI-Driven Project-Student Matching under Data Scarcity and Privacy Constraints_enhanced_kg.json"),
        
        ("IT Skills Survey",
         base_dir / "Assessing the IT Skill Requirements Expected from Graduates Among Various Industry Professionals" /
         "Assessing the IT Skill Requirements Expected from Graduates Among Various Industry Professionals_enhanced_kg.json"),
        
        ("IoT Plant Monitoring",
         base_dir / "IoT-Based Spectral Sensing and Machine Learning for Plant Health Monitoring" /
         "IoT-Based Spectral Sensing and Machine Learning for Plant Health Monitoring_enhanced_kg.json"),
        
        ("JZhang Project",
         base_dir / "JZhang_IFN712 Project Proposal 1_2025_CS " /
         "JZhang_IFN712 Project Proposal 1_2025_CS _enhanced_kg.json"),
        
        ("Smart Intersection",
         base_dir / "Smart Intersection Localization for Pedestrians Using Bluetooth and Deep learning" /
         "Smart Intersection Localization for Pedestrians Using Bluetooth and Deep learning_enhanced_kg.json"),
        
        ("VitalID",
         base_dir / "VitalID_ Smartphone-Based Identity Authentication Using Heart Rate and Breathing Signals" /
         "VitalID_ Smartphone-Based Identity Authentication Using Heart Rate and Breathing Signals_enhanced_kg.json"),
    ]
    
    print("=" * 80)
    print("分析知识图谱中unit节点的连接类型")
    print("=" * 80)
    
    for project_name, kg_file in kg_files:
        if kg_file.exists():
            print(f"\n{'='*80}")
            print(f"项目: {project_name}")
            print(f"文件: {kg_file.name}")
            print(f"{'='*80}")
            
            kg = load_kg(str(kg_file))
            isolated_units = analyze_unit_connections(kg)
        else:
            print(f"\n警告: 文件不存在 - {kg_file}")


if __name__ == "__main__":
    main()


