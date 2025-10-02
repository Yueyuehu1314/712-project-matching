#!/usr/bin/env python3
"""
优化的清洁知识图谱提取器
- 减少UNIT数量，只保留最相关的
- 改进布局算法
- 增强可视化清晰度
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

matplotlib.use('Agg')
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

@dataclass
class CleanKGNode:
    id: str
    name: str
    type: str
    score: float = 0.0

@dataclass
class CleanKGEdge:
    source: str
    target: str
    relation: str
    weight: float = 1.0

class OptimizedCleanKGExtractor:
    def __init__(self):
        self.synonyms = {
            'ai': 'artificial intelligence',
            'ml': 'machine learning',
            'dl': 'deep learning',
            'nlp': 'natural language processing',
            'cv': 'computer vision',
            'web dev': 'web development',
            'app dev': 'application development',
            'mobile dev': 'mobile development',
            'db': 'database',
            'api': 'application programming interface',
            'ui': 'user interface',
            'ux': 'user experience',
            'qa': 'quality assurance',
            'devops': 'development operations',
            'cybersecurity': 'cyber security',
            'infosec': 'information security',
            'it': 'information technology',
            'iot': 'internet of things',
            'ar': 'augmented reality',
            'vr': 'virtual reality'
        }
        
        self.generic_terms = {
            'programming', 'software development', 'computer', 'technology',
            'system', 'application', 'development', 'analysis', 'design',
            'implementation', 'testing', 'research', 'study', 'learning',
            'knowledge', 'skill', 'ability', 'understanding', 'experience'
        }

    def normalize_skill(self, skill: str) -> str:
        """标准化技能名称"""
        skill = skill.lower().strip()
        skill = re.sub(r'[^\w\s]', '', skill)
        skill = re.sub(r'\s+', ' ', skill)
        
        # 应用同义词映射
        for short, full in self.synonyms.items():
            skill = re.sub(r'\b' + short + r'\b', full, skill)
        
        return skill

    def extract_skills_from_text(self, text: str) -> List[Tuple[str, float]]:
        """从文本中提取技能及其权重"""
        text = text.lower()
        
        # 技能模式匹配
        skill_patterns = [
            r'\b(?:artificial intelligence|machine learning|deep learning|neural networks?)\b',
            r'\b(?:python|java|javascript|c\+\+|sql|html|css|react|angular|vue)\b',
            r'\b(?:data analytics?|data science|data mining|big data|statistics)\b',
            r'\b(?:web development|mobile development|software engineering)\b',
            r'\b(?:database|mongodb|mysql|postgresql|nosql)\b',
            r'\b(?:cloud computing|aws|azure|docker|kubernetes)\b',
            r'\b(?:cyber security|information security|network security)\b',
            r'\b(?:project management|agile|scrum|devops)\b',
            r'\b(?:networking|computer networks|network protocols)\b',
            r'\b(?:data visualization|business intelligence|reporting)\b'
        ]
        
        skills_with_scores = []
        for pattern in skill_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                normalized = self.normalize_skill(match)
                if normalized not in self.generic_terms:
                    # 计算TF-IDF风格的权重
                    count = len(re.findall(pattern, text))
                    score = math.log(1 + count) * 2.0  # 权重增强
                    skills_with_scores.append((normalized, score))
        
        # 去重并合并分数
        skill_scores = defaultdict(float)
        for skill, score in skills_with_scores:
            skill_scores[skill] += score
        
        return list(skill_scores.items())

    def filter_top_units(self, units: List[Dict], skills: Set[str], max_units: int = 15) -> List[Dict]:
        """筛选最相关的单元，减少图的复杂度"""
        unit_scores = []
        
        for unit in units:
            unit_text = f"{unit.get('title', '')} {unit.get('description', '')} {' '.join(unit.get('skills', []))}"
            unit_skills = self.extract_skills_from_text(unit_text)
            
            # 计算与项目技能的重叠度
            overlap_score = 0
            for skill, score in unit_skills:
                if skill in skills:
                    overlap_score += score
            
            if overlap_score > 0:
                unit_scores.append((unit, overlap_score))
        
        # 按分数排序，取前N个
        unit_scores.sort(key=lambda x: x[1], reverse=True)
        return [unit for unit, score in unit_scores[:max_units]]

    def extract_clean_kg(self, project_md_path: str, unit_md_path: str) -> Tuple[List[CleanKGNode], List[CleanKGEdge]]:
        """提取清洁的知识图谱"""
        # 读取项目描述
        with open(project_md_path, 'r', encoding='utf-8') as f:
            project_content = f.read()
        
        project_name = os.path.basename(project_md_path).replace('.md', '')
        
        # 读取单元信息
        with open(unit_md_path, 'r', encoding='utf-8') as f:
            unit_content = f.read()
        
        # 提取项目技能
        project_skills = self.extract_skills_from_text(project_content)
        project_skills.sort(key=lambda x: x[1], reverse=True)
        
        # 只保留前5个最重要的技能
        top_project_skills = dict(project_skills[:5])
        
        # 解析单元信息
        units = self._parse_units_from_markdown(unit_content)
        
        # 筛选相关单元
        relevant_units = self.filter_top_units(units, set(top_project_skills.keys()), max_units=15)
        
        # 构建图节点和边
        nodes = []
        edges = []
        
        # 添加项目节点
        project_node = CleanKGNode(f"PROJECT_{project_name}", project_name, "PROJECT")
        nodes.append(project_node)
        
        # 添加技能节点和项目->技能边
        for skill, score in top_project_skills.items():
            skill_node = CleanKGNode(f"SKILL_{skill}", skill, "SKILL", score)
            nodes.append(skill_node)
            
            edge = CleanKGEdge(project_node.id, skill_node.id, "requires", score)
            edges.append(edge)
        
        # 处理单元和程序
        programs = set()
        for unit in relevant_units:
            # 添加单元节点
            unit_id = f"UNIT_{unit['code']}"
            unit_node = CleanKGNode(unit_id, unit['title'], "UNIT")
            nodes.append(unit_node)
            
            # 添加程序节点
            program = unit.get('program', 'Unknown Program')
            program_id = f"PROGRAM_{program}"
            programs.add((program_id, program))
            
            # 单元->程序边
            edge = CleanKGEdge(unit_id, program_id, "belongs_to", 1.0)
            edges.append(edge)
            
            # 单元技能
            unit_skills = self.extract_skills_from_text(f"{unit['title']} {unit.get('description', '')}")
            
            # 只连接与项目技能相交的技能
            for skill, score in unit_skills:
                if skill in top_project_skills:
                    skill_id = f"SKILL_{skill}"
                    edge = CleanKGEdge(unit_id, skill_id, "teaches", score)
                    edges.append(edge)
        
        # 添加程序节点
        for program_id, program_name in programs:
            program_node = CleanKGNode(program_id, program_name, "PROGRAM")
            nodes.append(program_node)
        
        return nodes, edges

    def _parse_units_from_markdown(self, content: str) -> List[Dict]:
        """从markdown内容解析单元信息"""
        units = []
        sections = content.split('\n## ')
        
        for section in sections[1:]:  # 跳过第一个空部分
            lines = section.split('\n')
            title = lines[0].strip()
            
            unit_info = {
                'code': title.split()[0] if title else 'UNKNOWN',
                'title': title,
                'description': '',
                'program': 'Unknown Program',
                'skills': []
            }
            
            for line in lines[1:]:
                if line.startswith('**Program:**'):
                    unit_info['program'] = line.replace('**Program:**', '').strip()
                elif line.startswith('**Description:**'):
                    unit_info['description'] = line.replace('**Description:**', '').strip()
            
            units.append(unit_info)
        
        return units

    def create_optimized_visualization(self, nodes: List[CleanKGNode], edges: List[CleanKGEdge], 
                                    project_name: str, output_path: str):
        """创建优化的可视化"""
        G = nx.DiGraph()
        
        # 添加节点
        for node in nodes:
            G.add_node(node.id, name=node.name, type=node.type, score=node.score)
        
        # 添加边
        for edge in edges:
            if edge.source in G.nodes and edge.target in G.nodes:
                G.add_edge(edge.source, edge.target, relation=edge.relation, weight=edge.weight)
        
        # 创建分层布局
        pos = self._create_layered_layout(G, nodes)
        
        # 绘图设置
        plt.figure(figsize=(16, 12))
        plt.clf()
        
        # 节点颜色和大小
        node_colors = []
        node_sizes = []
        for node_id in G.nodes():
            node_type = G.nodes[node_id]['type']
            if node_type == 'PROJECT':
                node_colors.append('#FF6B6B')
                node_sizes.append(3000)
            elif node_type == 'SKILL':
                node_colors.append('#FFD93D')
                node_sizes.append(2000)
            elif node_type == 'UNIT':
                node_colors.append('#6BCF7F')
                node_sizes.append(1200)
            else:  # PROGRAM
                node_colors.append('#A8E6CF')
                node_sizes.append(1500)
        
        # 绘制边
        edge_colors = {'requires': '#FF6B6B', 'teaches': '#4ECDC4', 'belongs_to': '#45B7D1'}
        for relation in ['belongs_to', 'teaches', 'requires']:
            edges_of_type = [(u, v) for u, v, d in G.edges(data=True) if d['relation'] == relation]
            if edges_of_type:
                nx.draw_networkx_edges(G, pos, edgelist=edges_of_type, 
                                     edge_color=edge_colors[relation], 
                                     alpha=0.6, width=1.5, arrows=True, 
                                     arrowsize=15, arrowstyle='->')
        
        # 绘制节点
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                             node_size=node_sizes, alpha=0.8)
        
        # 绘制标签（只显示核心节点的标签）
        labels = {}
        for node_id in G.nodes():
            node_type = G.nodes[node_id]['type']
            name = G.nodes[node_id]['name']
            if node_type in ['PROJECT', 'SKILL']:
                labels[node_id] = name
            elif node_type == 'UNIT' and len(name) < 30:  # 只显示短名称的单元
                labels[node_id] = name[:20] + "..." if len(name) > 20 else name
        
        nx.draw_networkx_labels(G, pos, labels, font_size=10, font_weight='bold')
        
        # 图例
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#FF6B6B', 
                      markersize=15, label='PROJECT'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#FFD93D', 
                      markersize=12, label='SKILL'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#6BCF7F', 
                      markersize=10, label='UNIT'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#A8E6CF', 
                      markersize=11, label='PROGRAM'),
            plt.Line2D([0], [0], color='#FF6B6B', linewidth=3, label='requires'),
            plt.Line2D([0], [0], color='#4ECDC4', linewidth=3, label='teaches'),
            plt.Line2D([0], [0], color='#45B7D1', linewidth=3, label='belongs_to')
        ]
        
        plt.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.15, 1))
        
        plt.title(f'Optimized Clean Knowledge Graph: PD ∩ UO\n{project_name}', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.axis('off')
        plt.tight_layout()
        
        # 保存图像
        plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()

    def _create_layered_layout(self, G: nx.DiGraph, nodes: List[CleanKGNode]) -> Dict:
        """创建分层布局"""
        pos = {}
        
        # 按类型分组
        projects = [n for n in nodes if n.type == 'PROJECT']
        skills = [n for n in nodes if n.type == 'SKILL']
        units = [n for n in nodes if n.type == 'UNIT']
        programs = [n for n in nodes if n.type == 'PROGRAM']
        
        # 项目层 (左侧)
        for i, project in enumerate(projects):
            pos[project.id] = (0, i * 2)
        
        # 技能层 (中左)
        for i, skill in enumerate(skills):
            pos[skill.id] = (3, i * 1.5 - len(skills) * 0.75)
        
        # 单元层 (中右) - 使用更紧凑的布局
        unit_rows = math.ceil(len(units) / 3)  # 3列布局
        for i, unit in enumerate(units):
            col = i % 3
            row = i // 3
            pos[unit.id] = (6 + col * 1.5, row * 1.2 - unit_rows * 0.6)
        
        # 程序层 (右侧)
        for i, program in enumerate(programs):
            pos[program.id] = (10, i * 1.5 - len(programs) * 0.75)
        
        return pos

def main():
    extractor = OptimizedCleanKGExtractor()
    
    # 测试单个项目
    project_md_dir = "/Users/lynn/Documents/GitHub/ProjectMatching/project_md"
    unit_md_path = "/Users/lynn/Documents/GitHub/ProjectMatching/unit_md/qut_IN20_39851_int_cms_unit.md"
    output_dir = "/Users/lynn/Documents/GitHub/ProjectMatching/optimized_clean_kg_output"
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 为 HAR_WiFi_Proposal_Zhenguo-1 项目创建优化版本
    project_file = "HAR_WiFi_Proposal_Zhenguo-1.md"
    project_path = os.path.join(project_md_dir, project_file)
    
    if os.path.exists(project_path):
        print(f"为项目 {project_file} 生成优化的清洁知识图谱...")
        
        project_name = project_file.replace('.md', '')
        project_output_dir = os.path.join(output_dir, project_name)
        os.makedirs(project_output_dir, exist_ok=True)
        
        try:
            nodes, edges = extractor.extract_clean_kg(project_path, unit_md_path)
            
            # 保存可视化
            png_path = os.path.join(project_output_dir, f"{project_name}_optimized_kg.png")
            extractor.create_optimized_visualization(nodes, edges, project_name, png_path)
            
            # 保存JSON数据
            json_data = {
                "nodes": [asdict(node) for node in nodes],
                "edges": [asdict(edge) for edge in edges]
            }
            json_path = os.path.join(project_output_dir, f"{project_name}_optimized_kg.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            # 保存三元组
            triples_path = os.path.join(project_output_dir, f"{project_name}_optimized_triples.txt")
            with open(triples_path, 'w', encoding='utf-8') as f:
                for edge in edges:
                    source_name = next(n.name for n in nodes if n.id == edge.source)
                    target_name = next(n.name for n in nodes if n.id == edge.target)
                    f.write(f"{source_name} {edge.relation} {target_name}\n")
            
            print(f"✅ 优化版本已生成: {png_path}")
            print(f"   节点数: {len(nodes)}")
            print(f"   边数: {len(edges)}")
            
        except Exception as e:
            print(f"❌ 生成失败: {e}")

if __name__ == "__main__":
    main()
