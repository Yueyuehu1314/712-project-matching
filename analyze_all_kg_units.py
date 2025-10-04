#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from pathlib import Path
from collections import defaultdict

def analyze_unit_connections(kg_data):
    """分析unit节点的连接情况"""
    # 获取所有unit节点
    unit_nodes = {node['id'] for node in kg_data['nodes'] if node['type'] == 'UNIT'}
    
    # 分析unit的连接
    connected_units = set()  # 与skill/major/project有连接的unit
    prerequisite_only_units = set()  # 只有prerequisite连接的unit
    isolated_units = set()  # 完全孤立的unit
    
    # 统计每个unit的连接类型
    unit_connections = defaultdict(lambda: {
        'to_skill': [],
        'to_major': [],
        'to_project': [],
        'prerequisite': [],
        'from_skill': [],
        'from_major': []
    })
    
    for edge in kg_data['edges']:
        source = edge['source']
        target = edge['target']
        relation = edge['relation']
        
        # 检查skill -> unit的连接
        if source.startswith('skill_') and target in unit_nodes:
            if relation == 'TAUGHT_IN':
                unit_connections[target]['from_skill'].append(source)
                connected_units.add(target)
        
        # 检查major -> unit的连接
        if source.startswith('major_') and target in unit_nodes:
            if relation == 'REQUIRES_UNIT':
                unit_connections[target]['from_major'].append(source)
                connected_units.add(target)
        
        # 检查unit -> unit的prerequisite连接
        if source in unit_nodes and target in unit_nodes:
            if relation == 'PREREQUISITE_FOR':
                unit_connections[source]['prerequisite'].append(target)
                unit_connections[target]['prerequisite'].append(source)
    
    # 确定每个unit的状态
    for unit_id in unit_nodes:
        conns = unit_connections[unit_id]
        has_meaningful_connection = (
            len(conns['from_skill']) > 0 or 
            len(conns['from_major']) > 0
        )
        has_prerequisite = len(conns['prerequisite']) > 0
        
        if has_meaningful_connection:
            connected_units.add(unit_id)
        elif has_prerequisite:
            prerequisite_only_units.add(unit_id)
        else:
            isolated_units.add(unit_id)
    
    return {
        'total_units': len(unit_nodes),
        'connected_units': connected_units,
        'prerequisite_only_units': prerequisite_only_units,
        'isolated_units': isolated_units,
        'unit_connections': unit_connections
    }

def main():
    base_dir = Path('/Users/lynn/Documents/GitHub/ProjectMatching/outputs/knowledge_graphs/enhanced_in20_in27')
    
    print("\n" + "="*100)
    print("知识图谱Unit连接情况全面分析")
    print("="*100 + "\n")
    
    # 遍历所有项目目录
    all_results = []
    
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
            analysis = analyze_unit_connections(kg_data)
            
            all_results.append({
                'project': project_title,
                'file': json_file,
                'analysis': analysis
            })
            
        except Exception as e:
            print(f"❌ 处理文件出错: {json_file}")
            print(f"   错误: {e}\n")
            continue
    
    # 按孤立unit数量排序
    all_results.sort(key=lambda x: len(x['analysis']['isolated_units']), reverse=True)
    
    # 打印结果
    for idx, result in enumerate(all_results, 1):
        project = result['project']
        analysis = result['analysis']
        
        total = analysis['total_units']
        connected = len(analysis['connected_units'])
        prerequisite_only = len(analysis['prerequisite_only_units'])
        isolated = len(analysis['isolated_units'])
        
        print(f"{idx}. 项目: {project}")
        print(f"   总unit数: {total}")
        print(f"   ✅ 有意义连接的unit: {connected} ({connected/total*100:.1f}%)")
        print(f"   ⚠️  只有先决条件连接的unit: {prerequisite_only} ({prerequisite_only/total*100:.1f}%)")
        print(f"   ❌ 完全孤立的unit: {isolated} ({isolated/total*100:.1f}%)")
        
        if isolated > 0:
            print(f"   需要清理!")
            # 显示几个孤立unit的例子
            isolated_list = list(analysis['isolated_units'])[:5]
            for unit_id in isolated_list:
                # 查找unit名称
                unit_node = next((n for n in kg_data['nodes'] if n['id'] == unit_id), None)
                if unit_node:
                    print(f"      - {unit_id}: {unit_node['name']}")
            if len(analysis['isolated_units']) > 5:
                print(f"      ... 还有 {len(analysis['isolated_units']) - 5} 个")
        
        print()
    
    # 统计摘要
    print("\n" + "="*100)
    print("统计摘要")
    print("="*100)
    
    needs_cleaning = [r for r in all_results if len(r['analysis']['isolated_units']) > 0]
    already_clean = [r for r in all_results if len(r['analysis']['isolated_units']) == 0]
    
    print(f"\n需要清理的项目: {len(needs_cleaning)}/{len(all_results)}")
    for r in needs_cleaning:
        print(f"  - {r['project']}: {len(r['analysis']['isolated_units'])} 个孤立unit")
    
    print(f"\n已经清理好的项目: {len(already_clean)}/{len(all_results)}")
    for r in already_clean:
        print(f"  - {r['project']}")
    
    print("\n" + "="*100 + "\n")

if __name__ == '__main__':
    main()


