#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from pathlib import Path
from collections import defaultdict

def analyze_skill_units(json_file):
    """详细分析技能关联的unit"""
    with open(json_file, 'r', encoding='utf-8') as f:
        kg_data = json.load(f)
    
    project_title = kg_data.get('project_title', '')
    
    # 找出项目的技能
    project_id = next((n['id'] for n in kg_data['nodes'] if n['type'] == 'PROJECT'), None)
    project_skills = {}
    
    for edge in kg_data['edges']:
        if edge['source'] == project_id and edge['target'].startswith('skill_'):
            skill_name = next((n['name'] for n in kg_data['nodes'] if n['id'] == edge['target']), edge['target'])
            project_skills[edge['target']] = skill_name
    
    # 统计每个技能关联的unit
    skill_units = defaultdict(list)
    for edge in kg_data['edges']:
        if edge['source'] in project_skills and edge['target'].startswith('unit_'):
            if edge['relation'] == 'TAUGHT_IN':
                skill_units[edge['source']].append({
                    'unit_id': edge['target'],
                    'weight': edge.get('weight', 1.0),
                    'source_type': edge.get('source_type', 'unknown')
                })
    
    # 检查是否有技能关联超过10个unit
    problem_skills = {}
    for skill_id, units in skill_units.items():
        if len(units) > 10:
            problem_skills[skill_id] = {
                'name': project_skills[skill_id],
                'count': len(units),
                'units': sorted(units, key=lambda x: x['weight'], reverse=True)
            }
    
    return project_title, problem_skills

def main():
    base_dir = Path('/Users/lynn/Documents/GitHub/ProjectMatching/outputs/knowledge_graphs/enhanced_in20_in27')
    
    problem_projects = [
        'AI-Driven Project-Student Matching under Data Scarcity and Privacy Constraints',
        'JZhang_IFN712 Project Proposal 1_2025_CS ',
        'Assessing the IT Skill Requirements Expected from Graduates Among Various Industry Professionals',
        'Smart Intersection Localization for Pedestrians Using Bluetooth and Deep learning',
        'IoT-Based Spectral Sensing and Machine Learning for Plant Health Monitoring',
        'VitalID_ Smartphone-Based Identity Authentication Using Heart Rate and Breathing Signals'
    ]
    
    print("\n" + "="*100)
    print("分析问题项目")
    print("="*100 + "\n")
    
    for project_dir in sorted(base_dir.iterdir()):
        if not project_dir.is_dir():
            continue
        
        json_files = list(project_dir.glob('*_enhanced_kg.json'))
        if not json_files:
            continue
        
        json_file = json_files[0]
        
        try:
            project_title, problem_skills = analyze_skill_units(json_file)
            
            if problem_skills:
                print(f"📊 项目: {project_title}")
                print(f"   文件: {json_file.name}")
                
                for skill_id, info in problem_skills.items():
                    print(f"\n   ❌ 技能 '{info['name']}' ({skill_id}): {info['count']} 个unit")
                    print(f"      前15个unit:")
                    for i, unit in enumerate(info['units'][:15], 1):
                        print(f"        {i}. {unit['unit_id']} (weight: {unit['weight']}, source: {unit['source_type']})")
                    if len(info['units']) > 15:
                        print(f"        ... 还有 {len(info['units']) - 15} 个")
                
                print("\n" + "-"*100 + "\n")
        
        except Exception as e:
            print(f"❌ 处理文件出错: {json_file}: {e}")
            continue
    
    print("="*100 + "\n")

if __name__ == '__main__':
    main()


