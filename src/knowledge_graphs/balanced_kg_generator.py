#!/usr/bin/env python3
"""
平衡的知识图谱生成器
- 保留PD中的重要技能（即使UO中没有直接对应）
- 同时显示UO中支撑的技能
- 区分"核心技能"和"扩展技能"
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
class BalancedKGNode:
    id: str
    name: str
    type: str
    score: float = 0.0
    category: str = "core"  # supported, extended, core

@dataclass
class BalancedKGEdge:
    source: str
    target: str
    relation: str
    weight: float = 1.0
    category: str = "core"

class BalancedKGGenerator:
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
    
    def load_pd_only_data(self, project_name: str) -> List[Dict]:
        """加载PD-only数据"""
        pd_path = f"/Users/lynn/Documents/GitHub/ProjectMatching/clean_kg_output/{project_name}/{project_name}_clean_entities.json"
        
        if not os.path.exists(pd_path):
            return []
        
        try:
            with open(pd_path, 'r', encoding='utf-8') as f:
                entities = json.load(f)
            return [e for e in entities if e.get('entity_type') == 'SKILL']
        except:
            return []
    
    def load_pd_uo_data(self, project_name: str) -> Tuple[List[Dict], List[Dict]]:
        """加载PD+UO数据"""
        uo_path = f"/Users/lynn/Documents/GitHub/ProjectMatching/complete_clean_kg_output/{project_name}/{project_name}_kg.json"
        
        if not os.path.exists(uo_path):
            return [], []
        
        try:
            with open(uo_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('nodes', []), data.get('edges', [])
        except:
            return [], []
    
    def create_balanced_kg(self, project_name: str) -> Tuple[List[BalancedKGNode], List[BalancedKGEdge]]:
        """创建平衡的知识图谱 - 修复技能分类逻辑"""
        # 加载两种数据
        pd_skills = self.load_pd_only_data(project_name)
        uo_nodes, uo_edges = self.load_pd_uo_data(project_name)
        
        if not uo_nodes:  # 如果没有UO数据，使用PD数据
            return self._create_pd_only_kg(project_name, pd_skills)
        
        balanced_nodes = []
        balanced_edges = []
        
        # 获取各类型节点
        project_nodes = [n for n in uo_nodes if n['type'] == 'PROJECT']
        uo_skills = [n for n in uo_nodes if n['type'] == 'SKILL']
        units = [n for n in uo_nodes if n['type'] == 'UNIT'][:12]  # 限制UNIT数量
        programs = [n for n in uo_nodes if n['type'] == 'PROGRAM']
        
        # 添加项目节点
        for p in project_nodes:
            balanced_nodes.append(BalancedKGNode(
                id=p['id'], name=p['name'], type=p['type'], category="core"
            ))
        
        # 🔧 修复：正确分析技能支撑情况
        uo_skill_names = {self.normalize_skill(s['name']): s for s in uo_skills}
        pd_skill_dict = {self.normalize_skill(s['name']): s for s in pd_skills} if pd_skills else {}
        
        all_skills = {}
        
        # 1. 首先处理PD中的所有重要技能（评分>=2.5）
        if pd_skills:
            for pd_skill in pd_skills:
                normalized = self.normalize_skill(pd_skill['name'])
                if pd_skill.get('relevance_score', 0) >= 2.5:
                    
                    # 检查该技能是否在UO中有支撑
                    if normalized in uo_skill_names:
                        # 有UO支撑 - 使用UO的ID，但保留PD的评分
                        uo_skill = uo_skill_names[normalized]
                        all_skills[normalized] = {
                            'node': BalancedKGNode(
                                id=uo_skill['id'], name=uo_skill['name'], type='SKILL',
                                score=pd_skill.get('relevance_score', 3.0), category="supported"
                            ),
                            'source': 'both',
                            'pd_score': pd_skill.get('relevance_score', 3.0)
                        }
                    else:
                        # 无UO支撑 - 纯PD技能
                        skill_id = f"skill_{normalized.replace(' ', '_')}"
                        all_skills[normalized] = {
                            'node': BalancedKGNode(
                                id=skill_id, name=pd_skill['name'], type='SKILL',
                                score=pd_skill.get('relevance_score', 2.5), category="extended"
                            ),
                            'source': 'pd_only',
                            'pd_score': pd_skill.get('relevance_score', 2.5)
                        }
        
        # 2. 添加UO中独有的技能（PD中没有但UO中有的）
        for normalized_name, uo_skill in uo_skill_names.items():
            if normalized_name not in all_skills:
                all_skills[normalized_name] = {
                    'node': BalancedKGNode(
                        id=uo_skill['id'], name=uo_skill['name'], type='SKILL',
                        score=2.0, category="supported"
                    ),
                    'source': 'uo_only'
                }
        
        # 限制技能总数，优先保留supported技能和高分技能
        sorted_skills = sorted(all_skills.items(), 
                             key=lambda x: (x[1]['node'].category == 'supported', x[1]['node'].score), 
                             reverse=True)[:8]
        
        # 添加技能节点
        for skill_name, skill_data in sorted_skills:
            balanced_nodes.append(skill_data['node'])
        
        # 添加项目->技能边
        for project in project_nodes:
            for skill_name, skill_data in sorted_skills:
                edge_category = skill_data['node'].category
                weight = 2.0 if edge_category == "supported" else 1.5
                
                balanced_edges.append(BalancedKGEdge(
                    source=project['id'], target=skill_data['node'].id,
                    relation="requires", weight=weight, category=edge_category
                ))
        
        # 添加UNIT和PROGRAM节点
        for unit in units:
            balanced_nodes.append(BalancedKGNode(
                id=unit['id'], name=unit['name'], type='UNIT', category="core"
            ))
        
        for program in programs:
            balanced_nodes.append(BalancedKGNode(
                id=program['id'], name=program['name'], type='PROGRAM', category="core"
            ))
        
        # 添加UO边（只针对现有节点）
        existing_node_ids = {n.id for n in balanced_nodes}
        for edge in uo_edges:
            if edge['source'] in existing_node_ids and edge['target'] in existing_node_ids:
                balanced_edges.append(BalancedKGEdge(
                    source=edge['source'], target=edge['target'],
                    relation=edge['relation'], weight=edge.get('weight', 1.0),
                    category="supported"
                ))
        
        return balanced_nodes, balanced_edges
    
    def _create_pd_only_kg(self, project_name: str, pd_skills: List[Dict]) -> Tuple[List[BalancedKGNode], List[BalancedKGEdge]]:
        """为只有PD数据的项目创建KG"""
        if not pd_skills:
            return [], []
        
        nodes = []
        edges = []
        
        # 项目节点
        project_node = BalancedKGNode(
            id=f"project_{project_name}", name=project_name, type='PROJECT', category="core"
        )
        nodes.append(project_node)
        
        # 技能节点（取前6个）
        top_skills = sorted(pd_skills, key=lambda x: x.get('relevance_score', 0), reverse=True)[:6]
        
        for skill in top_skills:
            skill_node = BalancedKGNode(
                id=skill['id'], name=skill['name'], type='SKILL',
                score=skill.get('relevance_score', 1.0), category="extended"
            )
            nodes.append(skill_node)
            
            # 项目->技能边
            edges.append(BalancedKGEdge(
                source=project_node.id, target=skill_node.id,
                relation="requires", weight=skill.get('relevance_score', 1.0),
                category="extended"
            ))
        
        return nodes, edges
    
    def create_balanced_visualization(self, nodes: List[BalancedKGNode], edges: List[BalancedKGEdge], 
                                    project_name: str, output_path: str):
        """创建平衡的可视化"""
        G = nx.DiGraph()
        
        # 添加节点
        for node in nodes:
            G.add_node(node.id, **asdict(node))
        
        # 添加边
        for edge in edges:
            if edge.source in G.nodes and edge.target in G.nodes:
                G.add_edge(edge.source, edge.target, **asdict(edge))
        
        # 创建布局
        pos = self._create_balanced_layout(G, nodes)
        
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
        
        # 绘制边 - 区分类型
        edge_styles = {
            'supported': {'color': '#32CD32', 'width': 3, 'alpha': 0.8, 'style': '-'},
            'extended': {'color': '#FF8C00', 'width': 2.5, 'alpha': 0.7, 'style': '--'},
            'core': {'color': '#9B59B6', 'width': 2, 'alpha': 0.6, 'style': '-'}
        }
        
        # 按边的重要性排序绘制
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
        labels = self._create_smart_labels(G, nodes)
        
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
        
        # 增强图例
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#FF6B6B', 
                      markersize=18, label='PROJECT', markeredgecolor='white', markeredgewidth=2),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#32CD32', 
                      markersize=15, label='SKILL (UO Supported)', markeredgecolor='darkgreen', markeredgewidth=2),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#FFB347', 
                      markersize=15, label='SKILL (PD Extended)', markeredgecolor='darkorange', markeredgewidth=2),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#4ECDC4', 
                      markersize=12, label='UNIT', markeredgecolor='darkblue', markeredgewidth=1),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#DDA0DD', 
                      markersize=14, label='PROGRAM', markeredgecolor='darkviolet', markeredgewidth=1),
            plt.Line2D([0], [0], color='#32CD32', linewidth=3, label='Course Supported'),
            plt.Line2D([0], [0], color='#FF8C00', linewidth=2.5, linestyle='--', label='Extended Need'),
            plt.Line2D([0], [0], color='#9B59B6', linewidth=2, label='Structure')
        ]
        
        plt.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.18, 1),
                  fontsize=11, framealpha=0.95, fancybox=True, shadow=True)
        
        plt.title(f'Balanced Knowledge Graph: Complete Skills + Course Support\n{project_name}', 
                 fontsize=16, fontweight='bold', pad=25)
        
        plt.axis('off')
        plt.tight_layout()
        
        plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none', pad_inches=0.3)
        plt.close()
    
    def _create_smart_labels(self, G: nx.DiGraph, nodes: List[BalancedKGNode]) -> Dict:
        """创建智能标签"""
        labels = {}
        
        for node in nodes:
            name = node.name
            node_type = node.type
            
            if node_type == 'PROJECT':
                # 项目名称简化
                if len(name) > 35:
                    # 保留关键词
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
                # 技能名称美化
                skill_name = name.title().replace('_', ' ')
                if node.category == 'supported':
                    labels[node.id] = f"✓ {skill_name}"  # 有课程支撑的技能加勾
                else:
                    labels[node.id] = f"+ {skill_name}"  # 扩展技能加加号
            elif node_type == 'UNIT':
                # 提取单元代码
                code_match = re.search(r'\b[A-Z]{2,4}\d{3,4}\b', name)
                labels[node.id] = code_match.group() if code_match else name[:8]
            else:  # PROGRAM
                # 程序名称简化
                if 'master' in name.lower():
                    labels[node.id] = 'Master Program'
                elif 'bachelor' in name.lower():
                    labels[node.id] = 'Bachelor Program'
                else:
                    labels[node.id] = name[:18] + "..." if len(name) > 18 else name
        
        return labels
    
    def _create_balanced_layout(self, G: nx.DiGraph, nodes: List[BalancedKGNode]) -> Dict:
        """创建平衡布局"""
        pos = {}
        
        projects = [n for n in nodes if n.type == 'PROJECT']
        skills = [n for n in nodes if n.type == 'SKILL']
        units = [n for n in nodes if n.type == 'UNIT']
        programs = [n for n in nodes if n.type == 'PROGRAM']
        
        # 按技能类型分组
        supported_skills = [n for n in skills if n.category == 'supported']
        extended_skills = [n for n in skills if n.category == 'extended']
        
        # 项目层 (最左侧)
        for i, project in enumerate(projects):
            pos[project.id] = (0, 0)
        
        # 技能层 - 分两列
        all_skills = supported_skills + extended_skills
        for i, skill in enumerate(all_skills):
            x_pos = 6 if skill.category == 'supported' else 8
            y_offset = (i - len(all_skills)/2) * 2.5
            pos[skill.id] = (x_pos, y_offset)
        
        # UNIT层 - 紧凑网格
        unit_count = len(units)
        cols = 3
        for i, unit in enumerate(units):
            col = i % cols
            row = i // cols
            x = 14 + col * 2.5
            y = (row - unit_count/(2*cols)) * 2
            pos[unit.id] = (x, y)
        
        # PROGRAM层 (最右侧)
        for i, program in enumerate(programs):
            y_offset = (i - len(programs)/2) * 3
            pos[program.id] = (22, y_offset)
        
        return pos
    
    def process_all_projects(self):
        """处理所有项目"""
        input_dir = "/Users/lynn/Documents/GitHub/ProjectMatching/complete_clean_kg_output"
        output_dir = "/Users/lynn/Documents/GitHub/ProjectMatching/balanced_kg_output"
        
        os.makedirs(output_dir, exist_ok=True)
        
        # 获取所有项目
        project_dirs = [d for d in os.listdir(input_dir) 
                       if os.path.isdir(os.path.join(input_dir, d)) and d != '.DS_Store']
        
        results = []
        successful = 0
        failed = 0
        
        print(f"🚀 开始处理 {len(project_dirs)} 个项目...")
        print("=" * 70)
        
        for i, project_name in enumerate(project_dirs, 1):
            print(f"[{i:2d}/{len(project_dirs)}] 处理项目: {project_name[:50]}")
            
            project_output_dir = os.path.join(output_dir, project_name)
            os.makedirs(project_output_dir, exist_ok=True)
            
            try:
                # 创建平衡KG
                nodes, edges = self.create_balanced_kg(project_name)
                
                if not nodes:
                    print(f"         ⚠️  跳过 - 无有效数据")
                    failed += 1
                    continue
                
                # 生成可视化
                png_path = os.path.join(project_output_dir, f"{project_name}_balanced_kg.png")
                self.create_balanced_visualization(nodes, edges, project_name, png_path)
                
                # 保存JSON数据
                json_data = {
                    "nodes": [asdict(node) for node in nodes],
                    "edges": [asdict(edge) for edge in edges]
                }
                json_path = os.path.join(project_output_dir, f"{project_name}_balanced_kg.json")
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=2, ensure_ascii=False)
                
                # 统计信息
                supported_skills = len([n for n in nodes if n.type == 'SKILL' and n.category == 'supported'])
                extended_skills = len([n for n in nodes if n.type == 'SKILL' and n.category == 'extended'])
                
                stats = {
                    "project": project_name,
                    "total_nodes": len(nodes),
                    "total_edges": len(edges),
                    "supported_skills": supported_skills,
                    "extended_skills": extended_skills,
                    "units": len([n for n in nodes if n.type == 'UNIT']),
                    "programs": len([n for n in nodes if n.type == 'PROGRAM'])
                }
                
                stats_path = os.path.join(project_output_dir, f"{project_name}_balanced_stats.json")
                with open(stats_path, 'w', encoding='utf-8') as f:
                    json.dump(stats, f, indent=2, ensure_ascii=False)
                
                results.append({
                    "project": project_name,
                    "status": "success",
                    **stats
                })
                
                successful += 1
                print(f"         ✅ 成功 - 节点:{len(nodes)}, 支撑技能:{supported_skills}, 扩展技能:{extended_skills}")
                
            except Exception as e:
                print(f"         ❌ 失败: {str(e)[:50]}")
                failed += 1
                results.append({
                    "project": project_name,
                    "status": "failed",
                    "error": str(e)
                })
        
        # 保存总结
        summary = {
            "total_projects": len(project_dirs),
            "successful": successful,
            "failed": failed,
            "success_rate": f"{(successful/len(project_dirs)*100):.1f}%",
            "timestamp": datetime.now().isoformat(),
            "description": "平衡知识图谱：保留PD重要技能 + 标注UO支撑情况",
            "results": results
        }
        
        summary_path = os.path.join(output_dir, "balanced_summary.json")
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print("=" * 70)
        print(f"🎉 平衡知识图谱生成完成!")
        print(f"📊 总计: {len(project_dirs)} 个项目")
        print(f"✅ 成功: {successful} 个")
        print(f"❌ 失败: {failed} 个")
        print(f"📈 成功率: {(successful/len(project_dirs)*100):.1f}%")
        print(f"📁 输出目录: {output_dir}")
        print(f"🎯 特色: 绿色✓=有课程支撑, 橙色+=扩展需求")
        print("=" * 70)

def main():
    generator = BalancedKGGenerator()
    
    # 先测试单个项目
    project_name = "IFN712 Project Proposal Template_2025_Project matching"
    output_dir = "/Users/lynn/Documents/GitHub/ProjectMatching/balanced_kg_output_fixed"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"🔧 测试修复后的算法 - 项目: {project_name}")
    
    try:
        nodes, edges = generator.create_balanced_kg(project_name)
        
        if nodes:
            # 分析技能分类
            supported_skills = [(n.name, n.score) for n in nodes if n.type == 'SKILL' and n.category == 'supported']
            extended_skills = [(n.name, n.score) for n in nodes if n.type == 'SKILL' and n.category == 'extended']
            
            print(f"\n✅ 修复后的技能分类:")
            print(f"🟢 UO支撑技能 ({len(supported_skills)} 个):")
            for skill, score in supported_skills:
                print(f"   • {skill:<25} (评分: {score})")
            
            print(f"\n🟡 PD扩展技能 ({len(extended_skills)} 个):")
            for skill, score in extended_skills:
                print(f"   • {skill:<25} (评分: {score})")
            
            # 生成测试图像
            project_output_dir = os.path.join(output_dir, project_name)
            os.makedirs(project_output_dir, exist_ok=True)
            
            png_path = os.path.join(project_output_dir, f"{project_name}_fixed_kg.png")
            generator.create_balanced_visualization(nodes, edges, project_name, png_path)
            
            print(f"\n📊 测试图像已生成: {png_path}")
            print("🔍 请检查 machine learning、database 等技能是否正确连接到对应课程")
        else:
            print("❌ 未生成节点")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    # 如果测试成功，询问是否继续处理所有项目
    print(f"\n💡 如果测试结果正确，可以继续处理所有项目")
    # generator.process_all_projects()

if __name__ == "__main__":
    main()
