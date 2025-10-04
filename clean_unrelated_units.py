#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理知识图谱中没有关联的unit节点
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Set


def load_kg(file_path: str) -> Dict:
    """加载知识图谱JSON文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_kg(kg: Dict, file_path: str):
    """保存知识图谱JSON文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(kg, f, indent=2, ensure_ascii=False)


def find_connected_units(kg: Dict) -> Set[str]:
    """
    找出所有有意义连接的unit节点
    
    有意义的连接包括:
    1. 被技能通过TAUGHT_IN关系连接
    2. 被专业通过REQUIRES_UNIT关系连接
    3. 作为其他unit的先决条件(PREREQUISITE_FOR,且不是自引用)
    4. 有其他unit作为先决条件
    """
    connected_units = set()
    
    # 遍历所有边
    for edge in kg.get('edges', []):
        source = edge['source']
        target = edge['target']
        relation = edge['relation']
        
        # 技能 -> unit (TAUGHT_IN)
        if relation == 'TAUGHT_IN' and target.startswith('unit_'):
            connected_units.add(target)
        
        # 专业 -> unit (REQUIRES_UNIT)
        if relation == 'REQUIRES_UNIT' and target.startswith('unit_'):
            connected_units.add(target)
        
        # unit -> unit (PREREQUISITE_FOR, 非自引用)
        if relation == 'PREREQUISITE_FOR':
            if source.startswith('unit_') and target.startswith('unit_'):
                if source != target:
                    connected_units.add(source)
                    connected_units.add(target)
    
    return connected_units


def clean_kg(kg: Dict) -> Dict:
    """清理知识图谱中没有关联的unit节点"""
    
    # 找出所有有连接的unit节点
    connected_units = find_connected_units(kg)
    
    # 找出所有unit节点
    all_units = set()
    for node in kg.get('nodes', []):
        if node['type'] == 'UNIT':
            all_units.add(node['id'])
    
    # 找出需要删除的unit节点
    units_to_remove = all_units - connected_units
    
    print(f"  总unit节点数: {len(all_units)}")
    print(f"  有连接的unit节点数: {len(connected_units)}")
    print(f"  需要删除的unit节点数: {len(units_to_remove)}")
    
    # 删除没有连接的unit节点
    cleaned_nodes = []
    for node in kg.get('nodes', []):
        if node['id'] not in units_to_remove:
            cleaned_nodes.append(node)
    
    # 删除与这些unit相关的边
    cleaned_edges = []
    for edge in kg.get('edges', []):
        source = edge['source']
        target = edge['target']
        
        # 如果边的source或target是要删除的unit,则跳过该边
        if source in units_to_remove or target in units_to_remove:
            continue
        
        cleaned_edges.append(edge)
    
    # 更新KG
    kg['nodes'] = cleaned_nodes
    kg['edges'] = cleaned_edges
    
    return kg


def process_kg_file(file_path: str):
    """处理单个KG文件"""
    print(f"\n处理文件: {file_path}")
    
    # 加载KG
    kg = load_kg(file_path)
    
    # 清理KG
    cleaned_kg = clean_kg(kg)
    
    # 保存清理后的KG
    save_kg(cleaned_kg, file_path)
    
    print(f"  已保存清理后的KG")


def main():
    """主函数"""
    # 定义要处理的文件列表
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
    
    print("开始清理知识图谱中没有关联的unit节点...")
    
    # 处理每个文件
    for kg_file in kg_files:
        if kg_file.exists():
            process_kg_file(str(kg_file))
        else:
            print(f"\n警告: 文件不存在 - {kg_file}")
    
    print("\n清理完成!")


if __name__ == "__main__":
    main()


