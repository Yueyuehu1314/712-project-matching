#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from pathlib import Path
from collections import defaultdict

def clean_kg_units(kg_data, max_units_per_skill=10):
    """清理KG中每个技能关联过多的unit"""
    
    # 1. 获取项目需要的技能
    project_node = next(n for n in kg_data['nodes'] if n['type'] == 'PROJECT')
    project_id = project_node['id']
    
    project_skills = set()
    for edge in kg_data['edges']:
        if edge['source'] == project_id and edge['target'].startswith('skill_'):
            project_skills.add(edge['target'])
    
    # 2. 统计每个技能关联的unit及其权重
    skill_units = defaultdict(list)
    for edge in kg_data['edges']:
        if edge['source'] in project_skills and edge['target'].startswith('unit_'):
            if edge['relation'] == 'TAUGHT_IN':
                skill_units[edge['source']].append({
                    'unit_id': edge['target'],
                    'weight': edge.get('weight', 1.0)
                })
    
    # 3. 对于关联过多unit的技能，只保留权重最高的N个
    units_to_keep = set()
    units_to_remove = set()
    
    for skill_id, units in skill_units.items():
        if len(units) > max_units_per_skill:
            # 按权重排序，保留前N个
            sorted_units = sorted(units, key=lambda x: x['weight'], reverse=True)
            keep = sorted_units[:max_units_per_skill]
            remove = sorted_units[max_units_per_skill:]
            
            for u in keep:
                units_to_keep.add(u['unit_id'])
            for u in remove:
                units_to_remove.add(u['unit_id'])
        else:
            # 保留所有
            for u in units:
                units_to_keep.add(u['unit_id'])
    
    # 4. 添加先决条件链中的unit
    def add_prerequisites(unit_id, visited=None):
        if visited is None:
            visited = set()
        if unit_id in visited:
            return
        visited.add(unit_id)
        
        # 查找这个unit的先决条件
        for edge in kg_data['edges']:
            if edge['relation'] == 'PREREQUISITE_FOR':
                if edge['source'] == unit_id:
                    prereq = edge['target']
                    if prereq.startswith('unit_'):
                        units_to_keep.add(prereq)
                        add_prerequisites(prereq, visited)
                elif edge['target'] == unit_id:
                    prereq = edge['source']
                    if prereq.startswith('unit_'):
                        units_to_keep.add(prereq)
                        add_prerequisites(prereq, visited)
    
    for unit_id in list(units_to_keep):
        add_prerequisites(unit_id)
    
    # 5. 从要删除的集合中移除要保留的unit
    units_to_remove = units_to_remove - units_to_keep
    
    # 6. 添加major要求的unit
    for edge in kg_data['edges']:
        if edge['source'].startswith('major_') and edge['target'].startswith('unit_'):
            if edge['relation'] == 'REQUIRES_UNIT':
                units_to_keep.add(edge['target'])
                if edge['target'] in units_to_remove:
                    units_to_remove.remove(edge['target'])
    
    # 7. 删除不需要的unit节点
    original_count = sum(1 for n in kg_data['nodes'] if n['type'] == 'UNIT')
    kg_data['nodes'] = [n for n in kg_data['nodes'] 
                        if n['type'] != 'UNIT' or n['id'] in units_to_keep]
    
    # 8. 删除相关的边
    kg_data['edges'] = [e for e in kg_data['edges']
                        if not (e['source'] in units_to_remove or e['target'] in units_to_remove)]
    
    new_count = sum(1 for n in kg_data['nodes'] if n['type'] == 'UNIT')
    
    return {
        'original_count': original_count,
        'new_count': new_count,
        'removed_count': len(units_to_remove),
        'project_skills_count': len(project_skills)
    }

def main():
    base_dir = Path('/Users/lynn/Documents/GitHub/ProjectMatching/outputs/knowledge_graphs/enhanced_in20_in27')
    
    print("\n" + "="*100)
    print("批量清理所有项目的知识图谱")
    print("="*100 + "\n")
    
    # 遍历所有项目目录
    processed = 0
    skipped = 0
    
    for project_dir in sorted(base_dir.iterdir()):
        if not project_dir.is_dir():
            continue
        
        # 查找JSON文件
        json_files = list(project_dir.glob('*_enhanced_kg.json'))
        if not json_files:
            continue
        
        json_file = json_files[0]
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                kg_data = json.load(f)
            
            project_title = kg_data.get('project_title', project_dir.name)
            
            # 检查是否需要清理
            unit_count = sum(1 for n in kg_data['nodes'] if n['type'] == 'UNIT')
            
            # 如果unit数量少于50，认为已经清理过了，跳过
            if unit_count < 50:
                print(f"⏭️  跳过: {project_title}")
                print(f"   (已有 {unit_count} 个unit，无需清理)\n")
                skipped += 1
                continue
            
            print(f"🔧 处理: {project_title}")
            print(f"   清理前: {unit_count} 个unit")
            
            # 清理
            stats = clean_kg_units(kg_data, max_units_per_skill=10)
            
            # 保存
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(kg_data, f, ensure_ascii=False, indent=2)
            
            print(f"   清理后: {stats['new_count']} 个unit")
            print(f"   删除了: {stats['removed_count']} 个unit ({stats['removed_count']/stats['original_count']*100:.1f}%)")
            print(f"   ✅ 已保存\n")
            
            processed += 1
            
        except Exception as e:
            print(f"❌ 处理文件出错: {json_file}")
            print(f"   错误: {e}\n")
            continue
    
    print("="*100)
    print(f"完成! 处理了 {processed} 个项目, 跳过了 {skipped} 个项目")
    print("="*100 + "\n")

if __name__ == '__main__':
    main()


