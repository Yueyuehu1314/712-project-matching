#!/usr/bin/env python3
"""
精细化清洁知识图谱生成器
- 基于existing complete_clean_kg_output 数据
- 保留前13个最相关的UNIT
- 排除bachelor相关的UNIT
- 生成结构清晰的可视化
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
class RefinedKGNode:
    id: str
    name: str
    type: str
    score: float = 0.0

@dataclass
class RefinedKGEdge:
    source: str
    target: str
    relation: str
    weight: float = 1.0

class RefinedCleanKGGenerator:
    def __init__(self):
        self.bachelor_keywords = {
            'bachelor', 'undergraduate', 'degree', 'beng', 'bsc', 'ba', 'bachelor of'
        }
        
    def load_existing_kg_data(self, project_dir: str) -> Tuple[List[Dict], List[Dict]]:
        """从existing complete_clean_kg_output加载数据"""
        kg_json_path = None
        for file in os.listdir(project_dir):
            if file.endswith('_kg.json'):
                kg_json_path = os.path.join(project_dir, file)
                break
        
        if not kg_json_path or not os.path.exists(kg_json_path):
            return [], []
        
        with open(kg_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data.get('nodes', []), data.get('edges', [])
    
    def filter_bachelor_units(self, nodes: List[Dict]) -> List[Dict]:
        """过滤掉bachelor相关的UNIT"""
        filtered_nodes = []
        
        for node in nodes:
            if node['type'] == 'UNIT':
                unit_name = node['name'].lower()
                # 检查是否包含bachelor关键词
                is_bachelor = any(keyword in unit_name for keyword in self.bachelor_keywords)
                if not is_bachelor:
                    filtered_nodes.append(node)
            else:
                filtered_nodes.append(node)
        
        return filtered_nodes
    
    def calculate_unit_relevance(self, unit_node: Dict, skill_nodes: List[Dict], 
                               edges: List[Dict]) -> float:
        """计算UNIT与项目技能的相关性分数"""
        unit_id = unit_node['id']
        skill_ids = {node['id'] for node in skill_nodes if node['type'] == 'SKILL'}
        
        relevance_score = 0.0
        connection_count = 0
        
        # 计算与技能的连接权重
        for edge in edges:
            if edge['source'] == unit_id and edge['target'] in skill_ids:
                if edge['relation'] == 'teaches':
                    relevance_score += edge.get('weight', 1.0) * 2.0  # teaches关系权重更高
                    connection_count += 1
        
        # 考虑连接数量的奖励
        if connection_count > 0:
            relevance_score *= (1 + connection_count * 0.3)
        
        return relevance_score
    
    def select_top_units(self, nodes: List[Dict], edges: List[Dict], max_units: int = 13) -> List[Dict]:
        """选择前N个最相关的UNIT"""
        # 分离不同类型的节点
        project_nodes = [n for n in nodes if n['type'] == 'PROJECT']
        skill_nodes = [n for n in nodes if n['type'] == 'SKILL']
        unit_nodes = [n for n in nodes if n['type'] == 'UNIT']
        program_nodes = [n for n in nodes if n['type'] == 'PROGRAM']
        
        # 过滤bachelor相关的UNIT
        unit_nodes = [n for n in unit_nodes if not any(
            keyword in n['name'].lower() for keyword in self.bachelor_keywords
        )]
        
        # 计算每个UNIT的相关性分数
        unit_scores = []
        for unit in unit_nodes:
            score = self.calculate_unit_relevance(unit, skill_nodes, edges)
            if score > 0:  # 只保留有连接的UNIT
                unit_scores.append((unit, score))
        
        # 按分数排序，取前max_units个
        unit_scores.sort(key=lambda x: x[1], reverse=True)
        selected_units = [unit for unit, score in unit_scores[:max_units]]
        
        return project_nodes + skill_nodes + selected_units + program_nodes
    
    def filter_relevant_edges(self, nodes: List[Dict], edges: List[Dict]) -> List[Dict]:
        """过滤相关的边"""
        node_ids = {node['id'] for node in nodes}
        
        filtered_edges = []
        for edge in edges:
            if edge['source'] in node_ids and edge['target'] in node_ids:
                filtered_edges.append(edge)
        
        return filtered_edges
    
    def create_refined_visualization(self, nodes: List[Dict], edges: List[Dict], 
                                   project_name: str, output_path: str):
        """创建精细化的可视化 - 结构清晰版本"""
        G = nx.DiGraph()
        
        # 添加节点
        for node in nodes:
            G.add_node(node['id'], **node)
        
        # 添加边
        for edge in edges:
            if edge['source'] in G.nodes and edge['target'] in G.nodes:
                G.add_edge(edge['source'], edge['target'], **edge)
        
        # 创建优化的分层布局
        pos = self._create_clean_layout(G, nodes)
        
        # 设置图形大小
        plt.figure(figsize=(20, 14))
        plt.clf()
        
        # 节点样式设置
        node_colors = []
        node_sizes = []
        
        for node_id in G.nodes():
            node_type = G.nodes[node_id]['type']
            if node_type == 'PROJECT':
                node_colors.append('#FF6B6B')  # 红色
                node_sizes.append(5000)
            elif node_type == 'SKILL':
                node_colors.append('#FFD93D')  # 黄色
                node_sizes.append(3000)
            elif node_type == 'UNIT':
                node_colors.append('#4ECDC4')  # 青色
                node_sizes.append(2000)
            else:  # PROGRAM
                node_colors.append('#C8A8E9')  # 紫色
                node_sizes.append(2500)
        
        # 绘制边 - 分层绘制避免重叠
        edge_styles = {
            'requires': {'color': '#FF6B6B', 'width': 4, 'alpha': 0.8, 'style': '-'},
            'teaches': {'color': '#4ECDC4', 'width': 2.5, 'alpha': 0.7, 'style': '-'},
            'belongs_to': {'color': '#9B59B6', 'width': 2, 'alpha': 0.6, 'style': '--'}
        }
        
        # 按关系类型绘制边
        for relation in ['belongs_to', 'teaches', 'requires']:
            edges_of_type = [(u, v) for u, v, d in G.edges(data=True) 
                           if d.get('relation') == relation]
            if edges_of_type:
                style = edge_styles[relation]
                nx.draw_networkx_edges(
                    G, pos, edgelist=edges_of_type,
                    edge_color=style['color'],
                    width=style['width'],
                    alpha=style['alpha'],
                    style=style['style'],
                    arrows=True,
                    arrowsize=25,
                    arrowstyle='->',
                    connectionstyle="arc3,rad=0.1"
                )
        
        # 绘制节点
        nx.draw_networkx_nodes(
            G, pos,
            node_color=node_colors,
            node_size=node_sizes,
            alpha=0.9,
            linewidths=3,
            edgecolors='white'
        )
        
        # 智能标签处理
        labels = self._create_smart_labels(G, nodes)
        
        # 分类型绘制标签，避免重叠
        font_configs = {
            'PROJECT': {'size': 12, 'weight': 'bold', 'color': 'black'},
            'SKILL': {'size': 11, 'weight': 'bold', 'color': 'black'},
            'UNIT': {'size': 9, 'weight': 'normal', 'color': 'darkgreen'},
            'PROGRAM': {'size': 10, 'weight': 'bold', 'color': 'purple'}
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
        
        # 创建清晰的图例
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#FF6B6B', 
                      markersize=20, label='PROJECT', markeredgecolor='white', markeredgewidth=2),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#FFD93D', 
                      markersize=16, label='SKILL', markeredgecolor='white', markeredgewidth=2),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#4ECDC4', 
                      markersize=14, label='UNIT', markeredgecolor='white', markeredgewidth=2),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#C8A8E9', 
                      markersize=16, label='PROGRAM', markeredgecolor='white', markeredgewidth=2),
            plt.Line2D([0], [0], color='#FF6B6B', linewidth=4, label='requires'),
            plt.Line2D([0], [0], color='#4ECDC4', linewidth=3, label='teaches'),
            plt.Line2D([0], [0], color='#9B59B6', linewidth=2, linestyle='--', label='belongs_to')
        ]
        
        plt.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.15, 1),
                  fontsize=12, framealpha=0.95, fancybox=True, shadow=True)
        
        # 设置标题
        plt.title(f'Clean Knowledge Graph: PD ∩ UO\n{project_name}', 
                 fontsize=18, fontweight='bold', pad=25)
        
        plt.axis('off')
        plt.tight_layout()
        
        # 保存高质量图像
        plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none',
                   pad_inches=0.5)
        plt.close()
    
    def _create_clean_layout(self, G: nx.DiGraph, nodes: List[Dict]) -> Dict:
        """创建清晰的分层布局"""
        pos = {}
        
        # 按类型分组
        projects = [n for n in nodes if n['type'] == 'PROJECT']
        skills = [n for n in nodes if n['type'] == 'SKILL']
        units = [n for n in nodes if n['type'] == 'UNIT']
        programs = [n for n in nodes if n['type'] == 'PROGRAM']
        
        # 项目层 (最左侧)
        for i, project in enumerate(projects):
            pos[project['id']] = (0, 0)  # 单个项目居中
        
        # 技能层 (中左侧)
        skill_count = len(skills)
        for i, skill in enumerate(skills):
            y_offset = (i - skill_count/2) * 3
            pos[skill['id']] = (6, y_offset)
        
        # UNIT层 (中右侧) - 使用网格布局
        unit_count = len(units)
        cols = 4  # 每行4个UNIT
        rows = math.ceil(unit_count / cols)
        
        for i, unit in enumerate(units):
            col = i % cols
            row = i // cols
            x = 12 + col * 3
            y = (row - rows/2) * 2.5
            pos[unit['id']] = (x, y)
        
        # 程序层 (最右侧)
        program_count = len(programs)
        for i, program in enumerate(programs):
            y_offset = (i - program_count/2) * 4
            pos[program['id']] = (25, y_offset)
        
        return pos
    
    def _create_smart_labels(self, G: nx.DiGraph, nodes: List[Dict]) -> Dict:
        """创建智能标签，避免过长文本"""
        labels = {}
        
        for node in nodes:
            node_id = node['id']
            name = node['name']
            node_type = node['type']
            
            if node_type == 'PROJECT':
                # 项目名称 - 保留关键词
                labels[node_id] = self._shorten_project_name(name)
            elif node_type == 'SKILL':
                # 技能名称 - 首字母大写
                labels[node_id] = name.title()
            elif node_type == 'UNIT':
                # 单元 - 显示代码
                labels[node_id] = self._extract_unit_code(name)
            else:  # PROGRAM
                # 程序名称 - 简化显示
                labels[node_id] = self._shorten_program_name(name)
        
        return labels
    
    def _shorten_project_name(self, name: str) -> str:
        """简化项目名称"""
        if len(name) <= 30:
            return name
        
        # 保留关键词
        keywords = ['AI', 'ML', 'Data', 'Web', 'Mobile', 'Security', 'Network']
        for keyword in keywords:
            if keyword.lower() in name.lower():
                return f"{keyword} Project"
        
        return name[:27] + "..."
    
    def _extract_unit_code(self, name: str) -> str:
        """提取单元代码"""
        # 查找单元代码模式 (如 IFN701, CAB432等)
        code_match = re.search(r'\b[A-Z]{2,4}\d{3,4}\b', name)
        if code_match:
            return code_match.group()
        
        # 如果没有标准代码，返回前10个字符
        return name[:10] + "..." if len(name) > 10 else name
    
    def _shorten_program_name(self, name: str) -> str:
        """简化程序名称"""
        if 'master' in name.lower():
            return 'Master Program'
        elif 'bachelor' in name.lower():
            return 'Bachelor Program'
        elif len(name) > 20:
            return name[:17] + "..."
        return name
    
    def process_project(self, project_name: str, input_dir: str, output_dir: str) -> Dict:
        """处理单个项目"""
        project_input_dir = os.path.join(input_dir, project_name)
        project_output_dir = os.path.join(output_dir, project_name)
        
        if not os.path.exists(project_input_dir):
            return {"status": "failed", "error": "Input directory not found"}
        
        os.makedirs(project_output_dir, exist_ok=True)
        
        try:
            # 加载现有数据
            nodes, edges = self.load_existing_kg_data(project_input_dir)
            
            if not nodes or not edges:
                return {"status": "failed", "error": "No data found"}
            
            # 选择前13个最相关的UNIT
            refined_nodes = self.select_top_units(nodes, edges, max_units=13)
            refined_edges = self.filter_relevant_edges(refined_nodes, edges)
            
            # 生成可视化
            png_path = os.path.join(project_output_dir, f"{project_name}_refined_kg.png")
            self.create_refined_visualization(refined_nodes, refined_edges, project_name, png_path)
            
            # 保存refined数据
            refined_data = {
                "nodes": refined_nodes,
                "edges": refined_edges
            }
            
            json_path = os.path.join(project_output_dir, f"{project_name}_refined_kg.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(refined_data, f, indent=2, ensure_ascii=False)
            
            # 保存统计信息
            stats = {
                "project": project_name,
                "total_nodes": len(refined_nodes),
                "total_edges": len(refined_edges),
                "node_types": {
                    "PROJECT": len([n for n in refined_nodes if n['type'] == 'PROJECT']),
                    "SKILL": len([n for n in refined_nodes if n['type'] == 'SKILL']),
                    "UNIT": len([n for n in refined_nodes if n['type'] == 'UNIT']),
                    "PROGRAM": len([n for n in refined_nodes if n['type'] == 'PROGRAM'])
                },
                "relation_types": {
                    "requires": len([e for e in refined_edges if e['relation'] == 'requires']),
                    "teaches": len([e for e in refined_edges if e['relation'] == 'teaches']),
                    "belongs_to": len([e for e in refined_edges if e['relation'] == 'belongs_to'])
                }
            }
            
            stats_path = os.path.join(project_output_dir, f"{project_name}_refined_stats.json")
            with open(stats_path, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
            
            return {
                "status": "success",
                "nodes": len(refined_nodes),
                "edges": len(refined_edges),
                "units": stats["node_types"]["UNIT"]
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def process_all_projects(self):
        """处理所有项目"""
        input_dir = "/Users/lynn/Documents/GitHub/ProjectMatching/complete_clean_kg_output"
        output_dir = "/Users/lynn/Documents/GitHub/ProjectMatching/refined_clean_kg_output"
        
        os.makedirs(output_dir, exist_ok=True)
        
        # 获取所有项目目录
        project_dirs = [d for d in os.listdir(input_dir) 
                       if os.path.isdir(os.path.join(input_dir, d)) and d != 'batch_summary.json']
        
        results = []
        successful = 0
        failed = 0
        
        print(f"开始处理 {len(project_dirs)} 个项目...")
        print("=" * 60)
        
        for i, project_name in enumerate(project_dirs, 1):
            print(f"[{i}/{len(project_dirs)}] 处理项目: {project_name}")
            
            result = self.process_project(project_name, input_dir, output_dir)
            result["project"] = project_name
            results.append(result)
            
            if result["status"] == "success":
                successful += 1
                print(f"   ✅ 成功 - 节点: {result['nodes']}, 边: {result['edges']}, UNITs: {result['units']}")
            else:
                failed += 1
                print(f"   ❌ 失败: {result['error']}")
        
        # 保存总结报告
        summary = {
            "total_projects": len(project_dirs),
            "successful": successful,
            "failed": failed,
            "success_rate": f"{(successful/len(project_dirs)*100):.1f}%",
            "timestamp": datetime.now().isoformat(),
            "details": results
        }
        
        summary_path = os.path.join(output_dir, "refined_summary.json")
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print("=" * 60)
        print(f"🎉 精细化处理完成!")
        print(f"📊 总计: {len(project_dirs)} 个项目")
        print(f"✅ 成功: {successful} 个")
        print(f"❌ 失败: {failed} 个") 
        print(f"📈 成功率: {(successful/len(project_dirs)*100):.1f}%")
        print(f"📁 输出目录: {output_dir}")
        print("🔍 每个项目保留最相关的13个UNIT，排除bachelor相关内容")
        print("=" * 60)

def main():
    generator = RefinedCleanKGGenerator()
    generator.process_all_projects()

if __name__ == "__main__":
    main()








