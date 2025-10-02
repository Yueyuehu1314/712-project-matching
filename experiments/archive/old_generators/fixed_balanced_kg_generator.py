#!/usr/bin/env python3
"""
完全修复的平衡知识图谱生成器
- 正确识别PD技能是否有UO课程支撑
- 确保有课程支撑的技能连接到对应课程
- 区分真正的"扩展技能"和"支撑技能"
"""

import os
import json
import re
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, asdict
import math
from datetime import datetime

matplotlib.use('Agg')
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

@dataclass
class FixedKGNode:
    id: str
    name: str
    type: str
    score: float = 0.0
    category: str = "core"  # supported, extended, core

@dataclass
class FixedKGEdge:
    source: str
    target: str
    relation: str
    weight: float = 1.0
    category: str = "core"

class FixedBalancedKGGenerator:
    def __init__(self):
        self.synonyms = {
            'ai': 'artificial intelligence',
            'ml': 'machine learning',
            'dl': 'deep learning',
            'data science': 'data analytics',
            'big data': 'data analytics',
            'visualization': 'data visualization',
            'mobile dev': 'mobile development',
            'app dev': 'mobile development',
            'web dev': 'web development',
            'cybersecurity': 'cyber security',
            'network': 'networking',
            'databases': 'database',
            'db': 'database'
        }
    
    def normalize_skill(self, skill: str) -> str:
        """标准化技能名称"""
        skill = skill.lower().strip()
        skill = re.sub(r'[^\w\s]', '', skill)
        skill = re.sub(r'\s+', ' ', skill)
        
        for short, full in self.synonyms.items():
            skill = re.sub(r'\b' + short + r'\b', full, skill)
        
        return skill
    
    def load_pd_skills(self, project_name: str) -> List[Dict]:
        """加载PD技能数据"""
        pd_path = f"/Users/lynn/Documents/GitHub/ProjectMatching/clean_kg_output/{project_name}/{project_name}_clean_entities.json"
        
        if not os.path.exists(pd_path):
            return []
        
        try:
            with open(pd_path, 'r', encoding='utf-8') as f:
                entities = json.load(f)
            return [e for e in entities if e.get('entity_type') == 'SKILL']
        except:
            return []
    
    def load_uo_data(self, project_name: str) -> Tuple[List[Dict], List[Dict]]:
        """加载UO数据"""
        uo_path = f"/Users/lynn/Documents/GitHub/ProjectMatching/complete_clean_kg_output/{project_name}/{project_name}_kg.json"
        
        if not os.path.exists(uo_path):
            return [], []
        
        try:
            with open(uo_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('nodes', []), data.get('edges', [])
        except:
            return [], []
    
    def analyze_skill_support(self, pd_skills: List[Dict], uo_nodes: List[Dict], uo_edges: List[Dict]) -> Dict:
        """分析每个PD技能是否有UO课程支撑"""
        # 获取UO中的技能及其连接
        uo_skills = [n for n in uo_nodes if n['type'] == 'SKILL']
        uo_skill_map = {self.normalize_skill(s['name']): s for s in uo_skills}
        
        # 分析teaches关系
        teaches_edges = [e for e in uo_edges if e.get('relation') == 'teaches']
        skill_to_units = defaultdict(list)
        
        for edge in teaches_edges:
            target_skill_id = edge['target']
            source_unit_id = edge['source']
            
            # 找到对应的技能和单元
            skill_node = next((n for n in uo_nodes if n['id'] == target_skill_id), None)
            unit_node = next((n for n in uo_nodes if n['id'] == source_unit_id), None)
            
            if skill_node and unit_node:
                skill_name = self.normalize_skill(skill_node['name'])
                skill_to_units[skill_name].append({
                    'unit_id': source_unit_id,
                    'unit_name': unit_node['name'],
                    'weight': edge.get('weight', 1.0)
                })
        
        # 分析每个PD技能的支撑情况
        skill_analysis = {}
        
        for pd_skill in pd_skills:
            skill_name = pd_skill['name']
            normalized_name = self.normalize_skill(skill_name)
            pd_score = pd_skill.get('relevance_score', 0)
            
            if pd_score >= 2.5:  # 只考虑重要技能
                
                # 检查是否有UO支撑
                if normalized_name in skill_to_units:
                    # 有课程支撑
                    uo_skill = uo_skill_map.get(normalized_name)
                    skill_analysis[normalized_name] = {
                        'pd_skill': pd_skill,
                        'uo_skill': uo_skill,
                        'supporting_units': skill_to_units[normalized_name],
                        'category': 'supported',
                        'score': pd_score,
                        'final_name': skill_name,  # 使用PD中的名称
                        'final_id': uo_skill['id'] if uo_skill else f"skill_{normalized_name.replace(' ', '_')}"
                    }
                    print(f"✅ {skill_name} -> 有 {len(skill_to_units[normalized_name])} 个课程支撑")
                else:
                    # 无课程支撑
                    skill_analysis[normalized_name] = {
                        'pd_skill': pd_skill,
                        'uo_skill': None,
                        'supporting_units': [],
                        'category': 'extended',
                        'score': pd_score,
                        'final_name': skill_name,
                        'final_id': f"skill_{normalized_name.replace(' ', '_')}"
                    }
                    print(f"⚠️  {skill_name} -> 无课程支撑")
        
        # 添加UO独有的技能
        for normalized_name, uo_skill in uo_skill_map.items():
            if normalized_name not in skill_analysis and normalized_name in skill_to_units:
                skill_analysis[normalized_name] = {
                    'pd_skill': None,
                    'uo_skill': uo_skill,
                    'supporting_units': skill_to_units[normalized_name],
                    'category': 'supported',
                    'score': 2.0,
                    'final_name': uo_skill['name'],
                    'final_id': uo_skill['id']
                }
        
        return skill_analysis
    
    def create_fixed_kg(self, project_name: str) -> Tuple[List[FixedKGNode], List[FixedKGEdge]]:
        """创建修复的知识图谱"""
        print(f"\n🔧 分析项目: {project_name}")
        
        # 加载数据
        pd_skills = self.load_pd_skills(project_name)
        uo_nodes, uo_edges = self.load_uo_data(project_name)
        
        if not uo_nodes:
            print("   ❌ 无UO数据")
            return [], []
        
        print(f"   📊 PD技能: {len(pd_skills)}, UO节点: {len(uo_nodes)}, UO边: {len(uo_edges)}")
        
        # 分析技能支撑情况
        skill_analysis = self.analyze_skill_support(pd_skills, uo_nodes, uo_edges)
        
        # 创建节点和边
        nodes = []
        edges = []
        
        # 项目节点
        project_nodes = [n for n in uo_nodes if n['type'] == 'PROJECT']
        for p in project_nodes:
            nodes.append(FixedKGNode(
                id=p['id'], name=p['name'], type=p['type'], category="core"
            ))
        
        # 技能节点（按分数排序，取前8个）
        sorted_skills = sorted(skill_analysis.items(), 
                             key=lambda x: (x[1]['category'] == 'supported', x[1]['score']), 
                             reverse=True)[:8]
        
        for skill_name, skill_info in sorted_skills:
            nodes.append(FixedKGNode(
                id=skill_info['final_id'],
                name=skill_info['final_name'],
                type='SKILL',
                score=skill_info['score'],
                category=skill_info['category']
            ))
        
        # 项目->技能边
        for project in project_nodes:
            for skill_name, skill_info in sorted_skills:
                weight = 2.0 if skill_info['category'] == 'supported' else 1.5
                edges.append(FixedKGEdge(
                    source=project['id'],
                    target=skill_info['final_id'],
                    relation="requires",
                    weight=weight,
                    category=skill_info['category']
                ))
        
        # UNIT和PROGRAM节点（限制数量）
        units = [n for n in uo_nodes if n['type'] == 'UNIT'][:12]
        programs = [n for n in uo_nodes if n['type'] == 'PROGRAM']
        
        for unit in units:
            nodes.append(FixedKGNode(
                id=unit['id'], name=unit['name'], type='UNIT', category="core"
            ))
        
        for program in programs:
            nodes.append(FixedKGNode(
                id=program['id'], name=program['name'], type='PROGRAM', category="core"
            ))
        
        # 添加UO边（只保留现有节点间的连接）
        existing_node_ids = {n.id for n in nodes}
        for edge in uo_edges:
            if (edge['source'] in existing_node_ids and 
                edge['target'] in existing_node_ids):
                edges.append(FixedKGEdge(
                    source=edge['source'],
                    target=edge['target'],
                    relation=edge['relation'],
                    weight=edge.get('weight', 1.0),
                    category="supported"
                ))
        
        print(f"   ✅ 生成: {len(nodes)} 节点, {len(edges)} 边")
        
        return nodes, edges
    
    def create_visualization(self, nodes: List[FixedKGNode], edges: List[FixedKGEdge], 
                           project_name: str, output_path: str):
        """创建可视化"""
        G = nx.DiGraph()
        
        # 添加节点
        for node in nodes:
            G.add_node(node.id, **asdict(node))
        
        # 添加边
        for edge in edges:
            if edge.source in G.nodes and edge.target in G.nodes:
                G.add_edge(edge.source, edge.target, **asdict(edge))
        
        # 创建布局
        pos = self._create_layout(G, nodes)
        
        plt.figure(figsize=(18, 12))
        plt.clf()
        
        # 节点样式
        node_colors = []
        node_sizes = []
        
        for node_id in G.nodes():
            node = G.nodes[node_id]
            node_type = node['type']
            category = node.get('category', 'core')
            
            if node_type == 'PROJECT':
                node_colors.append('#FF6B6B')  # 红色
                node_sizes.append(4500)
            elif node_type == 'SKILL':
                if category == 'supported':
                    node_colors.append('#32CD32')  # 亮绿色 - UO支撑技能
                else:
                    node_colors.append('#FFB347')  # 橙色 - PD扩展技能
                node_sizes.append(3000)
            elif node_type == 'UNIT':
                node_colors.append('#4ECDC4')  # 青色
                node_sizes.append(1800)
            else:  # PROGRAM
                node_colors.append('#DDA0DD')  # 淡紫色
                node_sizes.append(2200)
        
        # 绘制边
        edge_styles = {
            'supported': {'color': '#32CD32', 'width': 3, 'alpha': 0.8, 'style': '-'},
            'extended': {'color': '#FF8C00', 'width': 2.5, 'alpha': 0.7, 'style': '--'},
            'core': {'color': '#9B59B6', 'width': 2, 'alpha': 0.6, 'style': '-'}
        }
        
        for category in ['core', 'extended', 'supported']:
            edges_of_category = []
            for u, v, d in G.edges(data=True):
                if d.get('category', 'core') == category:
                    edges_of_category.append((u, v))
            
            if edges_of_category:
                style = edge_styles[category]
                nx.draw_networkx_edges(
                    G, pos, edgelist=edges_of_category,
                    edge_color=style['color'],
                    width=style['width'],
                    alpha=style['alpha'],
                    style=style['style'],
                    arrows=True,
                    arrowsize=18,
                    arrowstyle='->',
                    connectionstyle="arc3,rad=0.05"
                )
        
        # 绘制节点
        nx.draw_networkx_nodes(
            G, pos, node_color=node_colors, node_size=node_sizes,
            alpha=0.9, linewidths=2.5, edgecolors='white'
        )
        
        # 智能标签
        labels = self._create_labels(G, nodes)
        
        # 分层绘制标签
        font_configs = {
            'PROJECT': {'size': 12, 'weight': 'bold', 'color': 'darkred'},
            'SKILL': {'size': 11, 'weight': 'bold', 'color': 'black'},
            'UNIT': {'size': 9, 'weight': 'normal', 'color': 'darkblue'},
            'PROGRAM': {'size': 10, 'weight': 'bold', 'color': 'darkviolet'}
        }
        
        for node_type, config in font_configs.items():
            type_labels = {nid: label for nid, label in labels.items() 
                          if G.nodes[nid]['type'] == node_type}
            if type_labels:
                nx.draw_networkx_labels(
                    G, pos, type_labels,
                    font_size=config['size'],
                    font_weight=config['weight'],
                    font_color=config['color']
                )
        
        # 图例
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#FF6B6B', 
                      markersize=18, label='PROJECT'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#32CD32', 
                      markersize=15, label='✓ SKILL (Course Supported)', markeredgecolor='darkgreen', markeredgewidth=2),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#FFB347', 
                      markersize=15, label='+ SKILL (Extended Need)', markeredgecolor='darkorange', markeredgewidth=2),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#4ECDC4', 
                      markersize=12, label='UNIT'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#DDA0DD', 
                      markersize=14, label='PROGRAM'),
            plt.Line2D([0], [0], color='#32CD32', linewidth=3, label='Course Teaches'),
            plt.Line2D([0], [0], color='#FF8C00', linewidth=2.5, linestyle='--', label='Extended Need'),
            plt.Line2D([0], [0], color='#9B59B6', linewidth=2, label='Structure')
        ]
        
        plt.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.18, 1),
                  fontsize=11, framealpha=0.95, fancybox=True, shadow=True)
        
        plt.title(f'Fixed Balanced Knowledge Graph: Correct Skill-Course Connections\n{project_name}', 
                 fontsize=16, fontweight='bold', pad=25)
        
        plt.axis('off')
        plt.tight_layout()
        
        plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none', pad_inches=0.3)
        plt.close()
    
    def _create_labels(self, G: nx.DiGraph, nodes: List[FixedKGNode]) -> Dict:
        """创建标签"""
        labels = {}
        
        for node in nodes:
            name = node.name
            node_type = node.type
            
            if node_type == 'PROJECT':
                if len(name) > 35:
                    keywords = ['AI', 'ML', 'Data', 'Web', 'Mobile', 'Security', 'Network']
                    for keyword in keywords:
                        if keyword.lower() in name.lower():
                            labels[node.id] = f"{keyword} Project"
                            break
                    else:
                        labels[node.id] = name[:32] + "..."
                else:
                    labels[node.id] = name
            elif node_type == 'SKILL':
                skill_name = name.title().replace('_', ' ')
                if node.category == 'supported':
                    labels[node.id] = f"✓ {skill_name}"
                else:
                    labels[node.id] = f"+ {skill_name}"
            elif node_type == 'UNIT':
                code_match = re.search(r'\b[A-Z]{2,4}\d{3,4}\b', name)
                labels[node.id] = code_match.group() if code_match else name[:8]
            else:  # PROGRAM
                if 'master' in name.lower():
                    labels[node.id] = 'Master Program'
                elif 'bachelor' in name.lower():
                    labels[node.id] = 'Bachelor Program'
                else:
                    labels[node.id] = name[:18] + "..." if len(name) > 18 else name
        
        return labels
    
    def _create_layout(self, G: nx.DiGraph, nodes: List[FixedKGNode]) -> Dict:
        """创建布局"""
        pos = {}
        
        projects = [n for n in nodes if n.type == 'PROJECT']
        skills = [n for n in nodes if n.type == 'SKILL']
        units = [n for n in nodes if n.type == 'UNIT']
        programs = [n for n in nodes if n.type == 'PROGRAM']
        
        # 按技能类型分组
        supported_skills = [n for n in skills if n.category == 'supported']
        extended_skills = [n for n in skills if n.category == 'extended']
        
        # 项目层
        for i, project in enumerate(projects):
            pos[project.id] = (0, 0)
        
        # 技能层 - 分两列
        all_skills = supported_skills + extended_skills
        for i, skill in enumerate(all_skills):
            x_pos = 6 if skill.category == 'supported' else 8
            y_offset = (i - len(all_skills)/2) * 2.5
            pos[skill.id] = (x_pos, y_offset)
        
        # UNIT层
        for i, unit in enumerate(units):
            col = i % 3
            row = i // 3
            x = 14 + col * 2.5
            y = (row - len(units)/(2*3)) * 2
            pos[unit.id] = (x, y)
        
        # PROGRAM层
        for i, program in enumerate(programs):
            y_offset = (i - len(programs)/2) * 3
            pos[program.id] = (22, y_offset)
        
        return pos

def main():
    generator = FixedBalancedKGGenerator()
    
    # 测试单个项目
    project_name = "IFN712 Project Proposal Template_2025_Project matching"
    output_dir = "/Users/lynn/Documents/GitHub/ProjectMatching/fixed_kg_output"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"🔧 测试完全修复的算法")
    print("=" * 60)
    
    try:
        nodes, edges = generator.create_fixed_kg(project_name)
        
        if nodes:
            # 分析结果
            supported_skills = [(n.name, n.score) for n in nodes if n.type == 'SKILL' and n.category == 'supported']
            extended_skills = [(n.name, n.score) for n in nodes if n.type == 'SKILL' and n.category == 'extended']
            
            print(f"\n📊 修复后的结果:")
            print(f"🟢 有课程支撑的技能 ({len(supported_skills)} 个):")
            for skill, score in supported_skills:
                print(f"   ✓ {skill:<25} (评分: {score})")
            
            print(f"\n🟡 需要扩展学习的技能 ({len(extended_skills)} 个):")
            for skill, score in extended_skills:
                print(f"   + {skill:<25} (评分: {score})")
            
            # 生成图像
            project_output_dir = os.path.join(output_dir, project_name)
            os.makedirs(project_output_dir, exist_ok=True)
            
            png_path = os.path.join(project_output_dir, f"{project_name}_fixed_kg.png")
            generator.create_visualization(nodes, edges, project_name, png_path)
            
            print(f"\n🎯 修复版图像: {png_path}")
            print("✅ 现在 machine learning、database 等应该正确连接到对应课程了！")
        else:
            print("❌ 未生成节点")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
