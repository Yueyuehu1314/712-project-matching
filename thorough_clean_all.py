#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from pathlib import Path
from collections import defaultdict

def thorough_clean_kg(kg_data, max_units_per_skill=10):
    """彻底清理KG，确保每个技能最多关联max_units_per_skill个unit"""
    
    # 1. 获取项目需要的技能
    project_node = next(n for n in kg_data['nodes'] if n['type'] == 'PROJECT')
    project_id = project_node['id']
    
    project_skills = set()
    for edge in kg_data['edges']:
        if edge['source'] == project_id and edge['target'].startswith('skill_'):
            project_skills.add(edge['target'])
    
    # 2. 统计每个技能当前关联的unit及其权重
    skill_units = defaultdict(list)
    for edge in kg_data['edges']:
        if edge['source'] in project_skills and edge['target'].startswith('unit_'):
            if edge['relation'] == 'TAUGHT_IN':
                skill_units[edge['source']].append({
                    'unit_id': edge['target'],
                    'weight': edge.get('weight', 1.0)
                })
    
    # 3. 对于关联过多unit的技能，只保留权重最高的N个
    units_to_keep_from_skills = set()
    units_to_remove = set()
    
    for skill_id, units in skill_units.items():
        if len(units) > max_units_per_skill:
            # 按权重排序，保留前N个
            sorted_units = sorted(units, key=lambda x: x['weight'], reverse=True)
            keep = sorted_units[:max_units_per_skill]
            remove = sorted_units[max_units_per_skill:]
            
            print(f"  技能 '{skill_id}': {len(units)}个unit -> 保留{max_units_per_skill}个，删除{len(remove)}个")
            
            for u in keep:
                units_to_keep_from_skills.add(u['unit_id'])
            for u in remove:
                units_to_remove.add(u['unit_id'])
        else:
            # 保留所有
            for u in units:
                units_to_keep_from_skills.add(u['unit_id'])
    
    # 4. 添加major要求的unit
    units_from_majors = set()
    for edge in kg_data['edges']:
        if edge['source'].startswith('major_') and edge['target'].startswith('unit_'):
            if edge['relation'] == 'REQUIRES_UNIT':
                units_from_majors.add(edge['target'])
    
    # 5. 只添加保留unit的先决条件（不递归添加要删除unit的先决条件）
    def collect_prerequisites_of_kept_units(kept_unit_ids):
        """只收集要保留unit的先决条件"""
        all_units_to_keep = set(kept_unit_ids)
        to_process = list(kept_unit_ids)
        
        while to_process:
            current_unit = to_process.pop()
            
            for edge in kg_data['edges']:
                if edge['relation'] == 'PREREQUISITE_FOR':
                    # 如果current_unit需要某个先决条件
                    if edge['target'] == current_unit and edge['source'].startswith('unit_'):
                        if edge['source'] not in all_units_to_keep:
                            all_units_to_keep.add(edge['source'])
                            to_process.append(edge['source'])
        
        return all_units_to_keep
    
    # 收集所有要保留的unit及其先决条件
    units_to_keep = units_to_keep_from_skills | units_from_majors
    units_with_prereqs = collect_prerequisites_of_kept_units(units_to_keep)
    
    # 6. 最终确定要删除的unit
    all_units = {n['id'] for n in kg_data['nodes'] if n['type'] == 'UNIT'}
    final_units_to_remove = all_units - units_with_prereqs
    
    original_count = len(all_units)
    
    # 7. 删除不需要的unit节点
    kg_data['nodes'] = [n for n in kg_data['nodes'] 
                        if n['type'] != 'UNIT' or n['id'] not in final_units_to_remove]
    
    # 8. 删除相关的边
    kg_data['edges'] = [e for e in kg_data['edges']
                        if not (e['source'] in final_units_to_remove or 
                               e['target'] in final_units_to_remove)]
    
    new_count = len(units_with_prereqs)
    
    return {
        'original_count': original_count,
        'new_count': new_count,
        'removed_count': len(final_units_to_remove)
    }

def main():
    base_dir = Path('/Users/lynn/Documents/GitHub/ProjectMatching/outputs/knowledge_graphs/enhanced_in20_in27')
    
    print("\n" + "="*100)
    print("彻底清理所有项目的知识图谱 (不限制unit总数)")
    print("="*100 + "\n")
    
    processed = 0
    
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
            unit_count = sum(1 for n in kg_data['nodes'] if n['type'] == 'UNIT')
            
            print(f"🔧 处理: {project_title}")
            print(f"  清理前: {unit_count} 个unit")
            
            # 清理
            stats = thorough_clean_kg(kg_data, max_units_per_skill=10)
            
            if stats['removed_count'] > 0:
                # 保存
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(kg_data, f, ensure_ascii=False, indent=2)
                
                print(f"  清理后: {stats['new_count']} 个unit")
                print(f"  删除了: {stats['removed_count']} 个unit ({stats['removed_count']/stats['original_count']*100:.1f}%)")
                print(f"  ✅ 已保存\n")
                processed += 1
            else:
                print(f"  ✅ 无需处理（已经符合要求）\n")
            
        except Exception as e:
            print(f"❌ 处理文件出错: {json_file}")
            print(f"   错误: {e}\n")
            continue
    
    print("="*100)
    print(f"完成! 实际处理了 {processed} 个项目")
    print("="*100 + "\n")

if __name__ == '__main__':
    main()

