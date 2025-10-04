#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成详细的unit关联报告
"""

import json
from pathlib import Path
from typing import Dict, Set
from collections import defaultdict


def load_kg(file_path: str) -> Dict:
    """加载知识图谱JSON文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_report(kg: Dict, project_name: str):
    """生成unit关联报告"""
    
    # 找出项目节点
    project_id = None
    project_title = ""
    for node in kg.get('nodes', []):
        if node['type'] == 'PROJECT':
            project_id = node['id']
            project_title = node['name']
            break
    
    if not project_id:
        return
    
    print(f"\n{'='*100}")
    print(f"项目: {project_title}")
    print(f"{'='*100}")
    
    # 找出项目需要的技能和专业
    project_skills = {}
    project_majors = set()
    
    for edge in kg.get('edges', []):
        if edge['source'] == project_id:
            if edge['relation'] == 'REQUIRES_SKILL':
                skill_name = next((n['name'] for n in kg['nodes'] if n['id'] == edge['target']), edge['target'])
                project_skills[edge['target']] = {
                    'name': skill_name,
                    'weight': edge.get('weight', 0),
                    'source_type': edge.get('source_type', 'Unknown')
                }
            elif edge['relation'] == 'SUITABLE_FOR_MAJOR':
                project_majors.add(edge['target'])
    
    print(f"\n项目需要的技能 ({len(project_skills)}):")
    for skill_id, skill_info in sorted(project_skills.items(), 
                                       key=lambda x: x[1]['weight'], 
                                       reverse=True):
        print(f"  - {skill_info['name']} (权重: {skill_info['weight']}, 来源: {skill_info['source_type']})")
    
    print(f"\n项目适合的专业 ({len(project_majors)}):")
    for major_id in project_majors:
        major_name = next((n['name'] for n in kg['nodes'] if n['id'] == major_id), major_id)
        print(f"  - {major_name}")
    
    # 统计每个技能关联的unit数量
    skill_units = defaultdict(set)
    major_units = defaultdict(set)
    
    for edge in kg.get('edges', []):
        if edge['relation'] == 'TAUGHT_IN':
            if edge['source'] in project_skills and edge['target'].startswith('unit_'):
                skill_units[edge['source']].add(edge['target'])
        
        if edge['relation'] == 'REQUIRES_UNIT':
            if edge['source'] in project_majors and edge['target'].startswith('unit_'):
                major_units[edge['source']].add(edge['target'])
    
    print(f"\n各技能关联的unit数量:")
    total_skill_units = set()
    for skill_id, units in sorted(skill_units.items(), 
                                   key=lambda x: len(x[1]), 
                                   reverse=True):
        skill_name = project_skills[skill_id]['name']
        print(f"  - {skill_name}: {len(units)} 个unit")
        total_skill_units.update(units)
    
    if major_units:
        print(f"\n各专业要求的unit数量:")
        total_major_units = set()
        for major_id, units in sorted(major_units.items(), 
                                       key=lambda x: len(x[1]), 
                                       reverse=True):
            major_name = next((n['name'] for n in kg['nodes'] if n['id'] == major_id), major_id)
            print(f"  - {major_name}: {len(units)} 个unit")
            total_major_units.update(units)
    else:
        total_major_units = set()
    
    # 统计先决条件
    all_direct_units = total_skill_units | total_major_units
    
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
    
    all_units_with_prereq = set(all_direct_units)
    for unit in all_direct_units:
        find_prerequisites(unit, all_units_with_prereq)
    
    prerequisite_units = all_units_with_prereq - all_direct_units
    
    print(f"\n总结:")
    print(f"  - 直接被技能教授的unit: {len(total_skill_units)}")
    print(f"  - 直接被专业要求的unit: {len(total_major_units)}")
    print(f"  - 去重后的直接相关unit: {len(all_direct_units)}")
    print(f"  - 作为先决条件的unit: {len(prerequisite_units)}")
    print(f"  - 总相关unit数: {len(all_units_with_prereq)}")
    
    # 统计总的unit数
    total_units = sum(1 for n in kg['nodes'] if n['type'] == 'UNIT')
    print(f"  - KG中总unit数: {total_units}")
    print(f"  - 未使用的unit数: {total_units - len(all_units_with_prereq)}")


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
    
    print("\n" + "="*100)
    print("知识图谱Unit关联详细报告")
    print("="*100)
    
    for project_name, kg_file in kg_files:
        if kg_file.exists():
            kg = load_kg(str(kg_file))
            generate_report(kg, project_name)
        else:
            print(f"\n警告: 文件不存在 - {kg_file}")
    
    print(f"\n{'='*100}\n")


if __name__ == "__main__":
    main()


