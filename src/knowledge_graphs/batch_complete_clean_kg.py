#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量完整清洁知识图谱生成器
为所有项目生成PD∩UO交集的清洁知识图谱，每个项目一个文件夹
"""

import os
import json
import re
import string
import matplotlib.pyplot as plt
import matplotlib
import networkx as nx
matplotlib.use('Agg')
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple, Optional

class BatchCompleteCleanKGExtractor:
    """批量完整清洁知识图谱提取器"""
    
    def __init__(self):
        # 精确的同义词映射
        self.synonyms = {
            # AI/ML 核心概念
            "ai": "artificial intelligence",
            "artificial intelligence": "machine learning",
            "ml": "machine learning", 
            "deep learning": "machine learning",
            "neural network": "machine learning",
            "pattern recognition": "machine learning",
            "computer vision": "machine learning",
            "data mining": "machine learning",
            
            # 网络和通信
            "wifi": "networking",
            "wireless": "networking",
            "network": "networking", 
            "networking": "networking",
            "protocol": "networking",
            "csi": "signal processing",  # Channel State Information
            "channel state information": "signal processing",
            
            # 数据科学
            "data science": "data analytics",
            "data analysis": "data analytics", 
            "data exploration": "data analytics",
            "analytics": "data analytics",
            "visualization": "data analytics",
            
            # 开发技术
            "web development": "web development",
            "mobile development": "mobile development",
            "programming": "programming",
            "software engineering": "programming",
            
            # 用户体验
            "ux": "user experience",
            "ui": "user interface",
            "hci": "human computer interaction",
            "human computer interaction": "user experience",
            
            # 安全
            "cybersecurity": "cybersecurity",
            "security": "cybersecurity",
            
            # 数据库
            "database": "database",
            "sql": "database"
        }
        
        # 有效技能白名单
        self.valid_skills = {
            "machine learning", "artificial intelligence", "data analytics", 
            "web development", "mobile development", "programming",
            "networking", "cybersecurity", "database", "user experience",
            "user interface", "human computer interaction", "signal processing",
            "image processing", "natural language processing", "cloud computing",
            "algorithm", "software engineering", "data visualization",
            "statistical analysis", "pattern recognition", "computer vision",
            "business analysis", "project management", "system design",
            "optimization", "simulation", "robotics", "blockchain"
        }
        
        # QUT程序映射
        self.program_mapping = {
            'IFN': 'Master of Information Technology',
            'CAB': 'Bachelor of Information Technology', 
            'IAB': 'Bachelor of Information Systems',
            'INB': 'Bachelor of Business Information Systems',
            'INN': 'Bachelor of Innovation',
            'ENN': 'Bachelor of Engineering',
            'MGN': 'Master of Business Administration',
            # 添加缺失的映射
            'QFN': 'QUT Foundation Program',
            'IGB': 'International Business Program',
            'MGZ': 'Management Program'
        }
        
        # 单元代码模式
        self.unit_pattern = r'\b[A-Z]{3}\d{3}\b'
        
        # 参数设置
        self.M = 5  # PD技能top数量
        self.K = 3  # 每个UNIT技能top数量
    
    def normalize_skill(self, skill: str) -> Optional[str]:
        """标准化技能名称"""
        if not skill:
            return None
        
        skill_lower = skill.lower().strip()
        
        # 过滤过短和包含数字的术语
        if len(skill_lower) < 3 or any(char.isdigit() for char in skill_lower):
            return None
        
        # 过滤包含特殊字符的无效术语
        if any(char in skill_lower for char in ['|', '<', '>', '(', ')', '[', ']']):
            return None
        
        # 检查同义词映射
        if skill_lower in self.synonyms:
            return self.synonyms[skill_lower]
        
        # 检查是否在有效技能列表中
        if skill_lower in self.valid_skills:
            return skill_lower
        
        # 部分匹配检查
        for valid_skill in self.valid_skills:
            if skill_lower in valid_skill or valid_skill in skill_lower:
                return valid_skill
        
        return None
    
    def extract_units_from_text(self, text: str) -> List[Tuple[str, str]]:
        """从文本中提取单元代码和名称"""
        units = []
        
        # 查找单元代码
        unit_codes = re.findall(self.unit_pattern, text)
        
        for code in set(unit_codes):
            # 查找对应的单元名称
            pattern = rf'{code}[^\n]*'
            matches = re.findall(pattern, text)
            
            if matches:
                full_text = matches[0]
                # 提取单元名称
                name_part = re.sub(rf'^{code}\s*', '', full_text).strip()
                
                # 清理名称
                name_part = re.sub(r'<[^>]*>', '', name_part)  # 移除HTML标签
                name_part = re.sub(r'\|.*$', '', name_part)    # 移除表格分隔符后内容
                name_part = name_part.strip()
                
                if name_part and len(name_part) > 3:
                    units.append((code, name_part[:50]))
                else:
                    units.append((code, f"Unit {code}"))
            else:
                units.append((code, f"Unit {code}"))
        
        return units
    
    def extract_project_skills(self, project_text: str) -> List[Tuple[str, float]]:
        """从项目描述中提取技能"""
        
        text_lower = project_text.lower()
        skill_scores = {}
        
        # 直接关键词检测
        for skill in self.valid_skills:
            score = 0
            skill_words = skill.split()
            
            # 完整匹配
            if skill in text_lower:
                score += 5
            
            # 词汇匹配
            for word in skill_words:
                score += text_lower.count(word)
            
            # 同义词匹配
            for synonym, canonical in self.synonyms.items():
                if canonical == skill and synonym in text_lower:
                    score += 3
            
            # 上下文加权
            contexts = ['using', 'with', 'implement', 'develop', 'apply', 'technique', 'method']
            for context in contexts:
                for word in skill_words:
                    if f"{context} {word}" in text_lower:
                        score += 2
            
            if score > 0:
                skill_scores[skill] = score
        
        # 排序并返回top-M
        sorted_skills = sorted(skill_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_skills[:self.M]
    
    def extract_unit_skills(self, unit_text: str, unit_code: str) -> List[Tuple[str, float]]:
        """从单元大纲中提取技能"""
        
        # 基于QUT单元代码的精确技能映射
        unit_skill_mapping = {
            'IFN680': ['machine learning', 'artificial intelligence', 'data analytics'],
            'IFN509': ['data analytics', 'machine learning', 'data visualization'],
            'IFN554': ['database', 'data analytics'],
            'IFN666': ['web development', 'mobile development', 'programming'],
            'IFN507': ['networking', 'programming'],
            'IFN541': ['cybersecurity', 'networking'],
            'IFN557': ['web development', 'programming'],
            'IFN563': ['programming', 'software engineering'],
            'IFN555': ['programming'],
            'IFN591': ['user experience', 'user interface'],
            'CAB432': ['cloud computing', 'networking'],
            'CAB340': ['algorithm', 'programming'],
            'IFN619': ['data analytics', 'machine learning'],
            'IFN647': ['data analytics', 'web development'],
            'IFN648': ['cybersecurity', 'programming'],
            'IFN649': ['networking', 'cybersecurity'],
            'IFN644': ['networking', 'cybersecurity'],
            'IFN623': ['user experience', 'human computer interaction'],
            'IFN652': ['programming', 'data analytics'],
            'IFN657': ['cybersecurity', 'programming'],
            'IFN662': ['programming', 'software engineering'],
            'IFN664': ['algorithm', 'programming'],
            'IFN515': ['business analysis', 'project management'],
            'IFN552': ['system design', 'programming'],
            'IFN528': ['project management', 'system design'],
            'IFN562': ['business analysis', 'data analytics'],
            'IFN631': ['project management', 'system design'],
            'IFN653': ['programming', 'business analysis'],
            'IFN712': ['programming', 'data analytics'],
            'IFN711': ['programming', 'project management'],
            'IFN701': ['programming', 'project management'],
            'IFN702': ['programming', 'project management']
        }
        
        # 获取预定义技能
        skills = unit_skill_mapping.get(unit_code, [])
        
        # 从文本中验证和补充技能
        text_lower = unit_text.lower()
        skill_scores = {}
        
        for skill in skills:
            score = 5.0  # 预定义技能基础分数
            
            # 文本验证加分
            if skill in text_lower:
                score += 2
            
            skill_scores[skill] = score
        
        # 从文本中发现其他技能
        for skill in self.valid_skills:
            if skill not in skill_scores:
                score = 0
                if skill in text_lower:
                    score += 1
                
                # 学习目标相关
                learning_contexts = ['learn', 'understand', 'develop', 'design', 'implement']
                for context in learning_contexts:
                    if f"{context} {skill}" in text_lower:
                        score += 1
                
                if score > 0:
                    skill_scores[skill] = score
        
        # 排序并返回top-K
        sorted_skills = sorted(skill_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_skills[:self.K]
    
    def extract_clean_kg(self, project_file: str, unit_dir: str = "unit_md") -> Tuple[Dict, List[str]]:
        """提取清洁知识图谱"""
        
        # 读取项目描述
        with open(project_file, 'r', encoding='utf-8') as f:
            project_content = f.read()
        
        project_name = self._extract_project_title(project_content)
        project_id = f"project_{os.path.splitext(os.path.basename(project_file))[0]}"
        
        # 提取项目技能
        project_skills_scored = self.extract_project_skills(project_content)
        project_skills = [skill for skill, score in project_skills_scored]
        
        # 处理单元大纲
        unit_data = {}
        unit_skills_map = {}
        
        if os.path.exists(unit_dir):
            unit_files = [f for f in os.listdir(unit_dir) if f.endswith('.md')]
            
            for unit_file in unit_files:
                unit_path = os.path.join(unit_dir, unit_file)
                with open(unit_path, 'r', encoding='utf-8') as f:
                    unit_content = f.read()
                
                units_in_file = self.extract_units_from_text(unit_content)
                
                for unit_code, unit_name in units_in_file:
                    unit_skills_scored = self.extract_unit_skills(unit_content, unit_code)
                    unit_skills = [skill for skill, score in unit_skills_scored]
                    
                    if unit_skills:  # 只保留有技能的单元
                        unit_data[unit_code] = {
                            'name': unit_name,
                            'skills': unit_skills,
                            'scores': dict(unit_skills_scored)
                        }
                        unit_skills_map[unit_code] = unit_skills
        
        # 找出交集技能
        project_skill_set = set(project_skills)
        all_unit_skills = set()
        for skills in unit_skills_map.values():
            all_unit_skills.update(skills)
        intersection_skills = project_skill_set & all_unit_skills
        
        if not intersection_skills:
            return {"nodes": [], "edges": []}, []
        
        # 构建知识图谱
        nodes = []
        edges = []
        triples = []
        
        # 1. 添加项目节点
        nodes.append({
            "id": project_id,
            "type": "PROJECT", 
            "name": project_name
        })
        
        # 2. 添加交集技能节点和项目→技能关系
        project_skill_scores = dict(project_skills_scored)
        for skill in intersection_skills:
            skill_id = f"skill_{skill.replace(' ', '_')}"
            
            # 添加技能节点
            nodes.append({
                "id": skill_id,
                "type": "SKILL",
                "name": skill
            })
            
            # 添加项目→技能关系
            weight = project_skill_scores.get(skill, 1.0)
            edges.append({
                "source": project_id,
                "target": skill_id,
                "relation": "requires",
                "weight": weight
            })
            
            triples.append(f"{project_name} requires {skill}")
        
        # 3. 添加单元节点和关系
        programs_added = set()
        
        for unit_code, unit_info in unit_data.items():
            unit_id = f"unit_{unit_code}"
            unit_name = f"{unit_code} {unit_info['name']}"
            
            # 检查该单元是否教授交集技能
            unit_intersection_skills = set(unit_info['skills']) & intersection_skills
            if not unit_intersection_skills:
                continue
            
            # 添加单元节点
            nodes.append({
                "id": unit_id,
                "type": "UNIT",
                "name": unit_name
            })
            
            # 添加程序节点和单元→程序关系
            unit_prefix = unit_code[:3]
            program_name = self.program_mapping.get(unit_prefix, f"{unit_prefix} Program")
            program_id = f"program_{unit_prefix}"
            
            if program_id not in programs_added:
                nodes.append({
                    "id": program_id,
                    "type": "PROGRAM",
                    "name": program_name
                })
                programs_added.add(program_id)
            
            # 单元→程序关系
            edges.append({
                "source": unit_id,
                "target": program_id,
                "relation": "belongs_to", 
                "weight": 1.0
            })
            
            triples.append(f"{unit_name} belongs_to {program_name}")
            
            # 添加单元→技能关系
            unit_skill_scores = unit_info['scores']
            
            for skill in unit_intersection_skills:
                skill_id = f"skill_{skill.replace(' ', '_')}"
                weight = unit_skill_scores.get(skill, 1.0)
                
                edges.append({
                    "source": unit_id,
                    "target": skill_id,
                    "relation": "teaches",
                    "weight": weight
                })
                
                triples.append(f"{unit_name} teaches {skill}")
        
        # 构建最终图结构
        kg_data = {
            "nodes": nodes,
            "edges": edges
        }
        
        return kg_data, triples
    
    def create_visualization(self, kg_data: Dict, project_name: str, output_file: str):
        """创建知识图谱可视化"""
        
        try:
            # 创建NetworkX图
            G = nx.DiGraph()
            
            # 添加节点
            for node in kg_data["nodes"]:
                G.add_node(node["id"], name=node["name"], type=node["type"])
            
            # 添加边
            for edge in kg_data["edges"]:
                G.add_edge(edge["source"], edge["target"], 
                          relation=edge["relation"], weight=edge["weight"])
            
            # 创建可视化
            plt.figure(figsize=(16, 12))
            
            # 3层布局：PROJECT (左) → SKILL (中) → UNIT (右)
            pos = self._create_three_layer_layout(G)
            
            # 定义颜色
            colors = {
                'PROJECT': '#FF6B6B',      # 红色
                'SKILL': '#FFD93D',        # 黄色
                'UNIT': '#4ECDC4',         # 青色
                'PROGRAM': '#9B59B6'       # 紫色
            }
            
            # 按类型绘制节点
            for node_type, color in colors.items():
                nodes = [n for n, d in G.nodes(data=True) if d.get('type') == node_type]
                if nodes:
                    if node_type == 'PROJECT':
                        size = 2000
                    elif node_type == 'SKILL':
                        size = 1500
                    elif node_type == 'UNIT':
                        size = 1000
                    else:  # PROGRAM
                        size = 800
                    
                    nx.draw_networkx_nodes(G, pos, nodelist=nodes,
                                         node_color=color, node_size=size,
                                         alpha=0.8, edgecolors='black', linewidths=1)
            
            # 按关系类型绘制边
            requires_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('relation') == 'requires']
            teaches_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('relation') == 'teaches']
            belongs_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('relation') == 'belongs_to']
            
            if requires_edges:
                nx.draw_networkx_edges(G, pos, edgelist=requires_edges,
                                     edge_color='red', width=3, alpha=0.7, arrows=True, arrowsize=20)
            
            if teaches_edges:
                nx.draw_networkx_edges(G, pos, edgelist=teaches_edges,
                                     edge_color='blue', width=2, alpha=0.7, arrows=True, arrowsize=15)
            
            if belongs_edges:
                nx.draw_networkx_edges(G, pos, edgelist=belongs_edges,
                                     edge_color='purple', width=1.5, alpha=0.5, arrows=True, arrowsize=10)
            
            # 添加标签
            labels = {}
            for node in G.nodes():
                name = G.nodes[node].get('name', node)
                if len(name) > 20:
                    name = name[:17] + "..."
                labels[node] = name
            
            nx.draw_networkx_labels(G, pos, labels, font_size=8, font_weight='bold')
            
            # 设置标题
            plt.title(f'Clean Knowledge Graph: PD ∩ UO\n{project_name}', 
                     fontsize=16, fontweight='bold', pad=20)
            
            # 创建图例
            legend_elements = [
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=colors['PROJECT'], 
                          markersize=15, label='PROJECT'),
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=colors['SKILL'], 
                          markersize=12, label='SKILL'),
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=colors['UNIT'], 
                          markersize=10, label='UNIT'),
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=colors['PROGRAM'], 
                          markersize=8, label='PROGRAM'),
                plt.Line2D([0], [0], color='red', linewidth=3, label='requires'),
                plt.Line2D([0], [0], color='blue', linewidth=2, label='teaches'),
                plt.Line2D([0], [0], color='purple', linewidth=1.5, label='belongs_to')
            ]
            
            plt.legend(handles=legend_elements, loc='upper right')
            
            plt.axis('off')
            plt.tight_layout()
            
            # 保存图片
            plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            return True
            
        except Exception as e:
            print(f"❌ 可视化失败: {e}")
            plt.close()
            return False
    
    def _create_three_layer_layout(self, G) -> Dict:
        """创建3层布局"""
        pos = {}
        
        # 按类型分组
        project_nodes = [n for n, d in G.nodes(data=True) if d.get('type') == 'PROJECT']
        skill_nodes = [n for n, d in G.nodes(data=True) if d.get('type') == 'SKILL']
        unit_nodes = [n for n, d in G.nodes(data=True) if d.get('type') == 'UNIT']
        program_nodes = [n for n, d in G.nodes(data=True) if d.get('type') == 'PROGRAM']
        
        # PROJECT在左侧
        for i, node in enumerate(project_nodes):
            pos[node] = (0, i - len(project_nodes)/2)
        
        # SKILL在中央
        for i, node in enumerate(skill_nodes):
            pos[node] = (2, (i - len(skill_nodes)/2) * 0.8)
        
        # UNIT在右侧
        for i, node in enumerate(unit_nodes):
            pos[node] = (4, (i - len(unit_nodes)/2) * 0.5)
        
        # PROGRAM在最右侧
        for i, node in enumerate(program_nodes):
            pos[node] = (5, (i - len(program_nodes)/2) * 1.5)
        
        return pos
    
    def _extract_project_title(self, content: str) -> str:
        """提取项目标题"""
        lines = content.split('\n')
        
        # 查找表格格式标题
        for line in lines:
            if 'project title' in line.lower() and '|' in line:
                parts = line.split('|')
                if len(parts) >= 3:
                    title = parts[-2].strip()
                    if title and len(title) > 3:
                        return title
        
        return "Unknown Project"
    
    def export_triples(self, triples: List[str], output_file: str):
        """导出三元组格式"""
        with open(output_file, 'w', encoding='utf-8') as f:
            for triple in triples:
                f.write(f"{triple}\n")
    
    def export_json(self, kg_data: Dict, output_file: str):
        """导出JSON格式"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(kg_data, f, ensure_ascii=False, indent=2)
    
    def process_project(self, project_file: str, output_dir: str = None):
        """处理单个项目"""
        
        project_name = os.path.splitext(os.path.basename(project_file))[0]
        
        try:
            # 提取知识图谱
            kg_data, triples = self.extract_clean_kg(project_file)
            
            if not kg_data["nodes"]:
                print(f"  ⚠️  无技能交集，跳过")
                return False
            
            # 设置输出目录
            if not output_dir:
                output_dir = f"complete_clean_kg_output/{project_name}"
            os.makedirs(output_dir, exist_ok=True)
            
            # 导出文件
            self.export_triples(triples, os.path.join(output_dir, f"{project_name}_triples.txt"))
            self.export_json(kg_data, os.path.join(output_dir, f"{project_name}_kg.json"))
            
            # 生成可视化
            vis_file = os.path.join(output_dir, f"{project_name}_kg.png")
            self.create_visualization(kg_data, project_name, vis_file)
            
            # 生成统计
            stats = {
                "project": project_name,
                "nodes": len(kg_data["nodes"]),
                "edges": len(kg_data["edges"]),
                "triples": len(triples),
                "node_types": Counter(node["type"] for node in kg_data["nodes"]),
                "relation_types": Counter(edge["relation"] for edge in kg_data["edges"])
            }
            
            with open(os.path.join(output_dir, f"{project_name}_stats.json"), 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
            
            print(f"  ✅ {stats['nodes']} 节点, {stats['edges']} 边, {stats['triples']} 三元组")
            return True
            
        except Exception as e:
            print(f"  ❌ 处理失败: {e}")
            return False
    
    def process_all_projects(self, project_dir: str = "project_md"):
        """处理所有项目"""
        
        print("🧠 批量完整清洁知识图谱生成器")
        print("=" * 60)
        print("📋 功能: PD∩UO交集 + 高质量技能提取 + 可视化")
        print("🎯 输出: 每个项目一个文件夹在 complete_clean_kg_output/")
        print("=" * 60)
        
        if not os.path.exists(project_dir):
            print(f"❌ 项目目录不存在: {project_dir}")
            return
        
        project_files = [f for f in os.listdir(project_dir) if f.endswith('.md')]
        print(f"📁 找到 {len(project_files)} 个项目文件")
        
        success_count = 0
        skip_count = 0
        
        for i, project_file in enumerate(project_files, 1):
            project_path = os.path.join(project_dir, project_file)
            print(f"\n[{i}/{len(project_files)}] {project_file}")
            
            result = self.process_project(project_path)
            if result:
                success_count += 1
            else:
                skip_count += 1
        
        print(f"\n📊 批量处理完成!")
        print(f"  ✅ 成功生成: {success_count} 个")
        print(f"  ⚠️  跳过(无交集): {skip_count} 个")
        print(f"  📁 输出目录: complete_clean_kg_output/")
        
        # 生成总结报告
        summary = {
            "total_projects": len(project_files),
            "successful_generations": success_count,
            "skipped_no_intersection": skip_count,
            "success_rate": f"{success_count/len(project_files)*100:.1f}%"
        }
        
        with open("complete_clean_kg_output/batch_summary.json", 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"  📄 总结报告: complete_clean_kg_output/batch_summary.json")

def main():
    """主函数"""
    extractor = BatchCompleteCleanKGExtractor()
    extractor.process_all_projects()
    
    print("\n🎉 批量处理完成!")

if __name__ == "__main__":
    main()
