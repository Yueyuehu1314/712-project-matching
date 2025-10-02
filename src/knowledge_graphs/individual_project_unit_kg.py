#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Individual Project + Unit Outline Knowledge Graph Builder
为每个项目生成包含 Unit Outline 信息的个体知识图谱
"""

import os
import json
import glob
import re
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict, Counter


@dataclass
class ProjectUnitEntity:
    """项目+Unit 个体知识图谱实体"""
    id: str
    name: str
    entity_type: str
    properties: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}


@dataclass
class ProjectUnitRelationship:
    """项目+Unit 个体知识图谱关系"""
    source_id: str
    target_id: str
    relation_type: str
    weight: float = 1.0
    properties: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}


class IndividualProjectUnitKGBuilder:
    """个体项目+Unit知识图谱构建器"""
    
    def __init__(self):
        self.entity_types = {
            'PROJECT': 'Project',
            'UNIT': 'Unit',
            'SKILL': 'Skill',
            'COURSE': 'Course',
            'MAJOR': 'Major',
            'TECHNOLOGY': 'Technology',
            'SUPERVISOR': 'Supervisor',
            'LEARNING_OUTCOME': 'LearningOutcome',
            'PREREQUISITE': 'Prerequisite'
        }
        
        self.relation_types = {
            'REQUIRES_SKILL': 'requires_skill',
            'REQUIRES_MAJOR': 'requires_major',
            'USES_TECHNOLOGY': 'uses_technology',
            'SUPERVISED_BY': 'supervised_by',
            'RELATES_TO_UNIT': 'relates_to_unit',
            'ACHIEVES_OUTCOME': 'achieves_outcome',
            'HAS_PREREQUISITE': 'has_prerequisite',
            'SUPPORTS_SKILL': 'supports_skill',
            'ENABLES_TECHNOLOGY': 'enables_technology'
        }
        
        # 加载 Unit Outline 数据
        self.unit_data = self._load_unit_outlines()
        
    def _load_unit_outlines(self, unit_dir: str = "unit_md") -> Dict:
        """加载 Unit Outline 数据"""
        print(f"📚 加载 Unit Outline 数据...")
        
        unit_data = {}
        if not os.path.exists(unit_dir):
            print(f"⚠️ Unit 目录不存在: {unit_dir}")
            return unit_data
        
        unit_files = glob.glob(os.path.join(unit_dir, "*.md"))
        
        for unit_file in unit_files:
            try:
                with open(unit_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                unit_info = self._parse_unit_content(content)
                unit_id = os.path.splitext(os.path.basename(unit_file))[0]
                unit_data[unit_id] = unit_info
                
            except Exception as e:
                print(f"  ❌ 加载 Unit 失败 {unit_file}: {e}")
        
        print(f"✅ 共加载 {len(unit_data)} 个 Unit Outline")
        return unit_data
    
    def _parse_unit_content(self, content: str) -> Dict[str, Any]:
        """解析 Unit Outline 内容"""
        info = {
            'title': 'Master of Information Technology',
            'majors': [],
            'units': [],
            'skills': [],
            'technologies': [],
            'learning_outcomes': [],
            'prerequisites': []
        }
        
        # 提取专业信息
        major_patterns = [
            'Business Analysis',
            'Computer Science', 
            'Data Science',
            'Software Development',
            'Cyber Security and Networks',
            'Enterprise Systems',
            'Executive IT'
        ]
        
        content_lower = content.lower()
        for pattern in major_patterns:
            if pattern.lower() in content_lower:
                info['majors'].append(pattern)
        
        # 提取课程单元 (IFN codes等)
        unit_pattern = r'\b(IFN\d{3}|CAB\d{3}|ENN\d{3}|IAB\d{3}|MGN\d{3})\b'
        units_found = set(re.findall(unit_pattern, content, re.IGNORECASE))
        info['units'] = list(units_found)
        
        # 从单元描述中提取技能和技术
        self._extract_skills_from_unit_descriptions(content, info)
        
        # 提取学习成果
        info['learning_outcomes'] = self._extract_learning_outcomes(content)
        
        # 提取先修课程
        info['prerequisites'] = self._extract_prerequisites(content)
        
        return info
    
    def _extract_skills_from_unit_descriptions(self, content: str, info: Dict):
        """从 Unit 描述中提取技能和技术"""
        content_lower = content.lower()
        
        # 技能关键词库
        skill_keywords = {
            'machine learning': ['machine learning', 'ml', 'artificial intelligence', 'ai'],
            'data science': ['data science', 'data mining', 'data analytics', 'data exploration'],
            'web development': ['web development', 'web application', 'html', 'css', 'javascript'],
            'cybersecurity': ['security', 'cyber security', 'cryptography', 'network security'],
            'business analysis': ['business analysis', 'business process', 'enterprise systems'],
            'software engineering': ['software development', 'programming', 'algorithms'],
            'database management': ['database', 'sql', 'data management'],
            'networking': ['network', 'tcp/ip', 'network systems'],
            'cloud computing': ['cloud', 'cloud computing'],
            'project management': ['project management', 'it governance'],
            'user experience': ['user experience', 'ux', 'interaction design']
        }
        
        for skill, keywords in skill_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                if skill not in info['skills']:
                    info['skills'].append(skill)
        
        # 技术关键词
        tech_keywords = {
            'Python': ['python'],
            'Java': ['java'],
            'JavaScript': ['javascript'],
            'React': ['react'],
            'SQL': ['sql'],
            'TensorFlow': ['tensorflow'],
            'SAP': ['sap'],
            'C#': ['c#'],
            'Flask': ['flask'],
            'MongoDB': ['mongodb']
        }
        
        for tech, keywords in tech_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                if tech not in info['technologies']:
                    info['technologies'].append(tech)
    
    def _extract_learning_outcomes(self, content: str) -> List[str]:
        """提取学习成果"""
        outcomes = []
        
        capability_patterns = [
            r'you will learn ([^.]+)',
            r'students will ([^.]+)',
            r'this unit ([^.]+)',
            r'provides ([^.]+)'
        ]
        
        for pattern in capability_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if 20 < len(match) < 150:
                    outcomes.append(match.strip())
        
        return outcomes[:8]
    
    def _extract_prerequisites(self, content: str) -> List[str]:
        """提取先修课程"""
        prereq_pattern = r'Pre-requisites[^|]*\|[^|]*\|([^|]+)'
        matches = re.findall(prereq_pattern, content, re.IGNORECASE)
        
        prerequisites = []
        for match in matches:
            codes = re.findall(r'\b(IFN\d{3}|CAB\d{3}|ENN\d{3}|IAB\d{3}|MGN\d{3})\b', match)
            prerequisites.extend(codes)
        
        return list(set(prerequisites))
    
    def create_project_unit_knowledge_graph(self, project_file: str, 
                                          output_dir: str = "individual_kg/projects_uo") -> Optional[Dict]:
        """为单个项目创建包含Unit信息的知识图谱"""
        
        if not os.path.exists(project_file):
            print(f"❌ 项目文件不存在: {project_file}")
            return None
        
        # 解析项目信息
        with open(project_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        project_info = self._parse_project_content(content)
        project_name = os.path.splitext(os.path.basename(project_file))[0]
        project_title = project_info.get('title', project_name)
        
        print(f"📋 创建项目+Unit知识图谱: {project_title}")
        
        # 创建图
        entities = {}
        relationships = []
        G = nx.MultiDiGraph()
        
        # 添加项目主实体
        project_entity_id = f"project_{project_name.replace(' ', '_')}"
        entities[project_entity_id] = ProjectUnitEntity(
            id=project_entity_id,
            name=project_title,
            entity_type='PROJECT',
            properties={
                'description': project_info.get('description', ''),
                'supervisor': project_info.get('supervisor', ''),
                'file_path': project_file
            }
        )
        
        G.add_node(project_entity_id, name=project_title, type='PROJECT',
                   **entities[project_entity_id].properties)
        
        # 添加项目直接的专业、技能、技术要求
        self._add_project_requirements(project_entity_id, project_info, entities, relationships, G)
        
        # 集成 Unit Outline 信息
        self._integrate_unit_outline_info(project_entity_id, project_info, entities, relationships, G)
        
        # 保存结果
        stats = self._save_project_unit_kg(project_entity_id, project_title, entities, 
                                         relationships, G, output_dir)
        
        return stats
    
    def _parse_project_content(self, content: str) -> Dict[str, Any]:
        """解析项目内容"""
        info = {
            'title': '',
            'description': '',
            'majors': [],
            'supervisor': '',
            'skills': [],
            'technologies': []
        }
        
        lines = content.split('\n')
        
        # 提取项目标题
        for line in lines:
            if 'Project title' in line:
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 3:
                        info['title'] = parts[-2].strip()
                break
        
        # 提取专业要求
        for line in lines:
            if 'Information Technology major' in line or 'major' in line.lower():
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 3:
                        majors_text = parts[-2].strip()
                        if majors_text:
                            info['majors'] = [m.strip() for m in majors_text.split(',')]
                break
        
        # 提取导师
        for line in lines:
            if 'Academic Supervisor' in line or 'Supervisor' in line:
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 3:
                        info['supervisor'] = parts[-2].strip()
                break
        
        # 提取描述
        description_lines = []
        in_description = False
        for line in lines:
            if 'Brief description' in line or 'Description' in line:
                in_description = True
                continue
            if in_description and line.strip():
                if line.startswith('|') and line.count('|') >= 3:
                    parts = line.split('|')
                    if len(parts) >= 3:
                        description_lines.append(parts[-2].strip())
                elif not line.startswith('+'):
                    description_lines.append(line.strip())
        
        info['description'] = ' '.join(description_lines)
        
        # 从描述中提取技能和技术
        self._extract_concepts_from_text(info['description'], info)
        
        return info
    
    def _extract_concepts_from_text(self, text: str, info: Dict):
        """从文本中提取概念"""
        text_lower = text.lower()
        
        skill_keywords = {
            'machine learning': ['machine learning', 'ml', 'deep learning', 'ai'],
            'web development': ['web', 'html', 'css', 'javascript', 'react'],
            'data science': ['data science', 'python', 'analysis', 'visualization'],
            'cybersecurity': ['security', 'cyber', 'encryption', 'firewall'],
            'mobile development': ['mobile', 'android', 'ios', 'app'],
            'database': ['database', 'sql', 'mysql', 'mongodb'],
            'networking': ['network', 'tcp/ip', 'wifi', 'routing']
        }
        
        for skill, keywords in skill_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                if skill not in info['skills']:
                    info['skills'].append(skill)
        
        tech_keywords = {
            'Python': ['python'],
            'Java': ['java'],
            'JavaScript': ['javascript'],
            'React': ['react'],
            'TensorFlow': ['tensorflow'],
            'SQL': ['sql']
        }
        
        for tech, keywords in tech_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                if tech not in info['technologies']:
                    info['technologies'].append(tech)
    
    def _add_project_requirements(self, project_id: str, project_info: Dict,
                                entities: Dict, relationships: List, G: nx.MultiDiGraph):
        """添加项目的直接要求"""
        
        # 添加专业要求
        for major in project_info.get('majors', []):
            major_id = f"major_{major.replace(' ', '_').lower()}"
            if major_id not in entities:
                entities[major_id] = ProjectUnitEntity(major_id, major, 'MAJOR')
                G.add_node(major_id, name=major, type='MAJOR')
            
            rel = ProjectUnitRelationship(project_id, major_id, 'REQUIRES_MAJOR')
            relationships.append(rel)
            G.add_edge(project_id, major_id, relation='REQUIRES_MAJOR', weight=1.0)
        
        # 添加技能要求
        for skill in project_info.get('skills', []):
            skill_id = f"skill_{skill.replace(' ', '_').lower()}"
            if skill_id not in entities:
                entities[skill_id] = ProjectUnitEntity(skill_id, skill, 'SKILL')
                G.add_node(skill_id, name=skill, type='SKILL')
            
            rel = ProjectUnitRelationship(project_id, skill_id, 'REQUIRES_SKILL')
            relationships.append(rel)
            G.add_edge(project_id, skill_id, relation='REQUIRES_SKILL', weight=1.0)
        
        # 添加技术要求
        for tech in project_info.get('technologies', []):
            tech_id = f"tech_{tech.replace(' ', '_').lower()}"
            if tech_id not in entities:
                entities[tech_id] = ProjectUnitEntity(tech_id, tech, 'TECHNOLOGY')
                G.add_node(tech_id, name=tech, type='TECHNOLOGY')
            
            rel = ProjectUnitRelationship(project_id, tech_id, 'USES_TECHNOLOGY')
            relationships.append(rel)
            G.add_edge(project_id, tech_id, relation='USES_TECHNOLOGY', weight=1.0)
        
        # 添加导师
        supervisor = project_info.get('supervisor', '')
        if supervisor:
            supervisor_id = f"supervisor_{supervisor.replace(' ', '_').lower()}"
            if supervisor_id not in entities:
                entities[supervisor_id] = ProjectUnitEntity(supervisor_id, supervisor, 'SUPERVISOR')
                G.add_node(supervisor_id, name=supervisor, type='SUPERVISOR')
            
            rel = ProjectUnitRelationship(project_id, supervisor_id, 'SUPERVISED_BY')
            relationships.append(rel)
            G.add_edge(project_id, supervisor_id, relation='SUPERVISED_BY', weight=1.0)
    
    def _integrate_unit_outline_info(self, project_id: str, project_info: Dict,
                                   entities: Dict, relationships: List, G: nx.MultiDiGraph):
        """集成 Unit Outline 信息"""
        
        project_majors = project_info.get('majors', [])
        project_skills = project_info.get('skills', [])
        
        # 遍历所有 Unit 数据，找到相关的 Unit
        for unit_id, unit_info in self.unit_data.items():
            unit_majors = unit_info.get('majors', [])
            unit_skills = unit_info.get('skills', [])
            
            # 检查 Unit 是否与项目相关
            major_overlap = any(pm in um for pm in project_majors for um in unit_majors)
            skill_overlap = any(ps in us for ps in project_skills for us in unit_skills)
            
            if major_overlap or skill_overlap:
                # 添加相关的 Unit
                unit_entity_id = f"unit_{unit_id}"
                if unit_entity_id not in entities:
                    entities[unit_entity_id] = ProjectUnitEntity(
                        unit_entity_id,
                        unit_info.get('title', unit_id),
                        'UNIT',
                        {
                            'unit_id': unit_id,
                            'majors': unit_majors,
                            'skills': unit_skills
                        }
                    )
                    G.add_node(unit_entity_id, name=unit_info.get('title', unit_id), 
                              type='UNIT', **entities[unit_entity_id].properties)
                
                # 连接项目与 Unit
                rel = ProjectUnitRelationship(project_id, unit_entity_id, 'RELATES_TO_UNIT', 
                                            weight=0.8)
                relationships.append(rel)
                G.add_edge(project_id, unit_entity_id, relation='RELATES_TO_UNIT', weight=0.8)
                
                # 添加 Unit 的技能，并连接到项目
                for skill in unit_skills:
                    skill_id = f"skill_{skill.replace(' ', '_').lower()}"
                    if skill_id not in entities:
                        entities[skill_id] = ProjectUnitEntity(skill_id, skill, 'SKILL')
                        G.add_node(skill_id, name=skill, type='SKILL')
                    
                    # Unit 支持技能
                    rel = ProjectUnitRelationship(unit_entity_id, skill_id, 'SUPPORTS_SKILL')
                    relationships.append(rel)
                    G.add_edge(unit_entity_id, skill_id, relation='SUPPORTS_SKILL', weight=1.0)
                
                # 添加 Unit 的技术
                for tech in unit_info.get('technologies', []):
                    tech_id = f"tech_{tech.replace(' ', '_').lower()}"
                    if tech_id not in entities:
                        entities[tech_id] = ProjectUnitEntity(tech_id, tech, 'TECHNOLOGY')
                        G.add_node(tech_id, name=tech, type='TECHNOLOGY')
                    
                    # Unit 启用技术
                    rel = ProjectUnitRelationship(unit_entity_id, tech_id, 'ENABLES_TECHNOLOGY')
                    relationships.append(rel)
                    G.add_edge(unit_entity_id, tech_id, relation='ENABLES_TECHNOLOGY', weight=1.0)
                
                # 添加学习成果
                for i, outcome in enumerate(unit_info.get('learning_outcomes', [])[:3]):  # 限制数量
                    outcome_id = f"outcome_{unit_id}_{i}"
                    outcome_name = outcome[:50] + "..." if len(outcome) > 50 else outcome
                    entities[outcome_id] = ProjectUnitEntity(outcome_id, outcome_name, 'LEARNING_OUTCOME')
                    G.add_node(outcome_id, name=outcome_name, type='LEARNING_OUTCOME')
                    
                    rel = ProjectUnitRelationship(unit_entity_id, outcome_id, 'ACHIEVES_OUTCOME')
                    relationships.append(rel)
                    G.add_edge(unit_entity_id, outcome_id, relation='ACHIEVES_OUTCOME', weight=1.0)
    
    def _save_project_unit_kg(self, entity_id: str, name: str, entities: Dict,
                            relationships: List, graph: nx.MultiDiGraph, output_dir: str) -> Dict:
        """保存项目+Unit知识图谱"""
        
        # 创建项目特定的输出目录
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_name = safe_name.replace(' ', '_')[:50]
        
        project_output_dir = os.path.join(output_dir, f"{entity_id}_{safe_name}")
        os.makedirs(project_output_dir, exist_ok=True)
        
        base_filename = f"{entity_id}_{safe_name}"
        
        # 保存实体数据
        entities_data = [asdict(entity) for entity in entities.values()]
        with open(os.path.join(project_output_dir, f"{base_filename}_entities.json"), 'w', encoding='utf-8') as f:
            json.dump(entities_data, f, ensure_ascii=False, indent=2)
        
        # 保存关系数据
        relationships_data = [asdict(rel) for rel in relationships]
        with open(os.path.join(project_output_dir, f"{base_filename}_relationships.json"), 'w', encoding='utf-8') as f:
            json.dump(relationships_data, f, ensure_ascii=False, indent=2)
        
        # 保存图文件
        nx.write_gexf(graph, os.path.join(project_output_dir, f"{base_filename}_graph.gexf"))
        
        # 创建可视化
        self._create_project_unit_visualization(graph, name, project_output_dir, base_filename)
        
        # 保存统计信息
        stats = {
            'entity_id': entity_id,
            'name': name,
            'total_entities': len(entities),
            'total_relationships': len(relationships),
            'entity_types': dict(Counter(e.entity_type for e in entities.values())),
            'relation_types': dict(Counter(r.relation_type for r in relationships)),
            'created_at': datetime.now().isoformat(),
            'output_dir': project_output_dir
        }
        
        with open(os.path.join(project_output_dir, f"{base_filename}_stats.json"), 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print(f"  ✅ 已保存到: {project_output_dir}")
        print(f"      实体: {len(entities)}, 关系: {len(relationships)}")
        
        return stats
    
    def _create_project_unit_visualization(self, graph: nx.MultiDiGraph, name: str, 
                                         output_dir: str, base_filename: str):
        """创建项目+Unit知识图谱可视化"""
        
        plt.figure(figsize=(16, 12))
        plt.clf()
        
        # 计算布局
        pos = nx.spring_layout(graph, k=3, iterations=100, seed=42)
        
        # 颜色映射
        node_colors = {
            'PROJECT': '#FF6B6B',           # 红色 - 项目
            'UNIT': '#FF9FF3',              # 粉紫色 - Unit
            'SKILL': '#45B7D1',             # 蓝色 - 技能
            'MAJOR': '#96CEB4',             # 绿色 - 专业
            'TECHNOLOGY': '#FFEAA7',        # 黄色 - 技术
            'SUPERVISOR': '#98D8C8',        # 浅绿 - 导师
            'LEARNING_OUTCOME': '#FFB84D',  # 橙色 - 学习成果
            'COURSE': '#DDA0DD',            # 紫色 - 课程
        }
        
        # 按类型绘制节点
        for node_type, color in node_colors.items():
            nodes = [n for n, d in graph.nodes(data=True) if d.get('type') == node_type]
            if nodes:
                if node_type == 'PROJECT':
                    node_size = 1500  # 项目节点最大
                elif node_type == 'UNIT':
                    node_size = 800   # Unit 节点较大
                elif node_type in ['SKILL', 'MAJOR', 'TECHNOLOGY']:
                    node_size = 500   # 关键概念中等
                else:
                    node_size = 300   # 其他节点较小
                
                alpha = 0.9 if node_type in ['PROJECT', 'UNIT'] else 0.7
                
                nx.draw_networkx_nodes(graph, pos, nodelist=nodes,
                                     node_color=color, node_size=node_size,
                                     alpha=alpha, edgecolors='black', linewidths=1)
        
        # 绘制边，区分不同类型
        unit_edges = [(u, v) for u, v, d in graph.edges(data=True) 
                     if d.get('relation') in ['RELATES_TO_UNIT', 'SUPPORTS_SKILL', 'ENABLES_TECHNOLOGY']]
        other_edges = [(u, v) for u, v, d in graph.edges(data=True) 
                      if d.get('relation') not in ['RELATES_TO_UNIT', 'SUPPORTS_SKILL', 'ENABLES_TECHNOLOGY']]
        
        # 普通边
        nx.draw_networkx_edges(graph, pos, edgelist=other_edges, 
                              alpha=0.5, width=1, edge_color='gray')
        
        # Unit 相关边（更突出）
        nx.draw_networkx_edges(graph, pos, edgelist=unit_edges, 
                              alpha=0.8, width=2, edge_color='purple', style='dashed')
        
        # 添加标签
        labels = {}
        for node in graph.nodes():
            node_name = graph.nodes[node].get('name', node)
            if len(node_name) > 20:
                node_name = node_name[:17] + "..."
            labels[node] = node_name
        
        nx.draw_networkx_labels(graph, pos, labels, font_size=8, font_weight='bold')
        
        # 设置标题
        plt.title(f'Project + Unit Outline Knowledge Graph\n{name}', 
                 fontsize=14, fontweight='bold')
        plt.axis('off')
        
        # 添加图例
        legend_elements = []
        for node_type, color in node_colors.items():
            if any(d.get('type') == node_type for n, d in graph.nodes(data=True)):
                legend_elements.append(plt.Line2D([0], [0], marker='o', color='w',
                                                markerfacecolor=color, markersize=10, 
                                                label=node_type.replace('_', ' ')))
        
        if legend_elements:
            plt.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0, 1))
        
        plt.tight_layout()
        
        # 保存图片
        output_file = os.path.join(output_dir, f"{base_filename}_kg.png")
        plt.savefig(output_file, dpi=300, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        plt.close()
    
    def build_all_project_unit_kgs(self, project_dir: str = "project_md", 
                                  output_dir: str = "individual_kg/projects_uo") -> Dict:
        """为所有项目构建项目+Unit知识图谱"""
        
        print("🚀 开始构建所有项目+Unit知识图谱...")
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 获取所有项目文件
        project_files = glob.glob(os.path.join(project_dir, "*.md"))
        print(f"找到 {len(project_files)} 个项目文件")
        
        results = {
            'projects': [],
            'summary': {}
        }
        
        # 处理每个项目
        for i, project_file in enumerate(project_files, 1):
            print(f"\n[{i}/{len(project_files)}] 处理项目: {os.path.basename(project_file)}")
            try:
                stats = self.create_project_unit_knowledge_graph(project_file, output_dir)
                if stats:
                    results['projects'].append(stats)
            except Exception as e:
                print(f"    ❌ 失败: {e}")
                continue
        
        # 生成总结
        if results['projects']:
            results['summary'] = {
                'total_projects': len(results['projects']),
                'total_entities': sum(p['total_entities'] for p in results['projects']),
                'total_relationships': sum(p['total_relationships'] for p in results['projects']),
                'avg_entities_per_project': sum(p['total_entities'] for p in results['projects']) / len(results['projects']),
                'avg_relationships_per_project': sum(p['total_relationships'] for p in results['projects']) / len(results['projects']),
                'created_at': datetime.now().isoformat()
            }
        
        # 保存总结报告
        with open(os.path.join(output_dir, "summary_report.json"), 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # 打印统计信息
        print(f"\n📊 项目+Unit知识图谱构建完成!")
        if results['projects']:
            print(f"  成功项目: {results['summary']['total_projects']} 个")
            print(f"  总实体数: {results['summary']['total_entities']}")
            print(f"  总关系数: {results['summary']['total_relationships']}")
            print(f"  平均每项目实体数: {results['summary']['avg_entities_per_project']:.1f}")
            print(f"  平均每项目关系数: {results['summary']['avg_relationships_per_project']:.1f}")
        
        print(f"\n📂 输出目录: {output_dir}/")
        print(f"  每个项目都有独立的文件夹，包含实体、关系、图形文件和可视化")
        
        return results


def main():
    """主函数"""
    print("🎯 Individual Project + Unit Outline Knowledge Graph Builder")
    print("=" * 70)
    
    builder = IndividualProjectUnitKGBuilder()
    results = builder.build_all_project_unit_kgs()
    
    print("\n🎉 所有项目+Unit知识图谱构建完成!")


if __name__ == "__main__":
    main()
