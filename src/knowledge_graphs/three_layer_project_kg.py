#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3层结构项目知识图谱生成器

结构：
Layer 1: Project (项目)
Layer 2: Domain Categories (主题域/技能类别)
Layer 3: Specific Skills/Technologies/Majors (具体技能/技术/专业)

特点：
- 去除 Professor 节点
- 更清晰的层次结构
- 更好的知识组织
"""

import os
import json
import glob
import re
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict
from pathlib import Path

@dataclass
class KGEntity:
    """知识图谱实体"""
    id: str
    name: str
    entity_type: str  # PROJECT, DOMAIN, SKILL, TECHNOLOGY, MAJOR
    layer: int  # 1, 2, or 3
    properties: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}

@dataclass
class KGRelationship:
    """知识图谱关系"""
    source_id: str
    target_id: str
    relation_type: str
    weight: float = 1.0
    properties: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}


class ThreeLayerProjectKGGenerator:
    """3层项目知识图谱生成器"""
    
    def __init__(self, use_existing_weights=False):
        """
        初始化生成器
        
        Args:
            use_existing_weights: 是否从enhanced_in20_in27读取现有权重
        """
        self.use_existing_weights = use_existing_weights
        self.existing_weights = {}  # 存储从enhanced_in20_in27加载的权重
        
        if use_existing_weights:
            self._load_existing_weights()
        
        # 技能到领域的映射
        self.skill_to_domain = {
            # Machine Learning Domain
            'machine learning': 'Machine Learning & AI',
            'deep learning': 'Machine Learning & AI',
            'neural networks': 'Machine Learning & AI',
            'artificial intelligence': 'Machine Learning & AI',
            'computer vision': 'Machine Learning & AI',
            'natural language processing': 'Machine Learning & AI',
            'nlp': 'Machine Learning & AI',
            'reinforcement learning': 'Machine Learning & AI',
            'gan': 'Machine Learning & AI',
            'generative models': 'Machine Learning & AI',
            'model training': 'Machine Learning & AI',
            
            # Data Science Domain
            'data science': 'Data Science & Analytics',
            'data analytics': 'Data Science & Analytics',
            'data analysis': 'Data Science & Analytics',
            'data visualization': 'Data Science & Analytics',
            'statistical analysis': 'Data Science & Analytics',
            'data mining': 'Data Science & Analytics',
            'big data': 'Data Science & Analytics',
            'data warehousing': 'Data Science & Analytics',
            'business intelligence': 'Data Science & Analytics',
            
            # Web Development Domain
            'web development': 'Web Development',
            'frontend': 'Web Development',
            'backend': 'Web Development',
            'full stack': 'Web Development',
            'html': 'Web Development',
            'css': 'Web Development',
            'javascript': 'Web Development',
            'react': 'Web Development',
            'vue': 'Web Development',
            'angular': 'Web Development',
            'node.js': 'Web Development',
            'django': 'Web Development',
            
            # Mobile Development Domain
            'mobile development': 'Mobile Development',
            'android': 'Mobile Development',
            'ios': 'Mobile Development',
            'react native': 'Mobile Development',
            'flutter': 'Mobile Development',
            'swift': 'Mobile Development',
            'kotlin': 'Mobile Development',
            'app development': 'Mobile Development',
            
            # Cybersecurity Domain
            'cybersecurity': 'Cybersecurity',
            'network security': 'Cybersecurity',
            'information security': 'Cybersecurity',
            'encryption': 'Cybersecurity',
            'penetration testing': 'Cybersecurity',
            'security analysis': 'Cybersecurity',
            'threat detection': 'Cybersecurity',
            
            # Database Domain
            'database': 'Database Systems',
            'sql': 'Database Systems',
            'nosql': 'Database Systems',
            'mongodb': 'Database Systems',
            'postgresql': 'Database Systems',
            'mysql': 'Database Systems',
            'database design': 'Database Systems',
            'data modeling': 'Database Systems',
            
            # Networking Domain
            'networking': 'Networking & Communication',
            'network protocols': 'Networking & Communication',
            'tcp/ip': 'Networking & Communication',
            'wifi': 'Networking & Communication',
            'iot': 'Networking & Communication',
            'wireless communication': 'Networking & Communication',
            'network architecture': 'Networking & Communication',
            
            # Software Engineering Domain
            'software engineering': 'Software Engineering',
            'software design': 'Software Engineering',
            'software architecture': 'Software Engineering',
            'design patterns': 'Software Engineering',
            'agile': 'Software Engineering',
            'devops': 'Software Engineering',
            'ci/cd': 'Software Engineering',
            'testing': 'Software Engineering',
            'version control': 'Software Engineering',
            'git': 'Software Engineering',
            
            # Cloud Computing Domain
            'cloud computing': 'Cloud Computing',
            'aws': 'Cloud Computing',
            'azure': 'Cloud Computing',
            'google cloud': 'Cloud Computing',
            'docker': 'Cloud Computing',
            'kubernetes': 'Cloud Computing',
            'microservices': 'Cloud Computing',
            
            # Signal Processing Domain
            'signal processing': 'Signal Processing',
            'image processing': 'Signal Processing',
            'audio processing': 'Signal Processing',
            'digital signal processing': 'Signal Processing',
            'filtering': 'Signal Processing',
            'feature extraction': 'Signal Processing',
            
            # Programming Languages
            'python': 'Programming Languages',
            'java': 'Programming Languages',
            'c++': 'Programming Languages',
            'c#': 'Programming Languages',
            'r': 'Programming Languages',
            'matlab': 'Programming Languages',
            'scala': 'Programming Languages',
            
            # Business & Management
            'business analysis': 'Business & Management',
            'project management': 'Business & Management',
            'requirements engineering': 'Business & Management',
            'stakeholder management': 'Business & Management',
            'process modeling': 'Business & Management',
            
            # Hardware & Embedded
            'embedded systems': 'Hardware & Embedded Systems',
            'iot devices': 'Hardware & Embedded Systems',
            'raspberry pi': 'Hardware & Embedded Systems',
            'arduino': 'Hardware & Embedded Systems',
            'hardware design': 'Hardware & Embedded Systems',
            
            # Computer Vision & Sensing
            'computer vision': 'Computer Vision & Sensing',
            'image recognition': 'Computer Vision & Sensing',
            'object detection': 'Computer Vision & Sensing',
            'activity recognition': 'Computer Vision & Sensing',
            'sensor fusion': 'Computer Vision & Sensing',
            
            # GIS & Spatial Analysis
            'gis': 'GIS & Spatial Analysis',
            'remote sensing': 'GIS & Spatial Analysis',
            'spatial analysis': 'GIS & Spatial Analysis',
            'geospatial data': 'GIS & Spatial Analysis',
            'satellite imagery': 'GIS & Spatial Analysis',
        }
        
        # 技术到领域的映射
        self.tech_to_domain = {
            'tensorflow': 'Machine Learning & AI',
            'pytorch': 'Machine Learning & AI',
            'keras': 'Machine Learning & AI',
            'scikit-learn': 'Machine Learning & AI',
            'opencv': 'Computer Vision & Sensing',
            'pandas': 'Data Science & Analytics',
            'numpy': 'Data Science & Analytics',
            'matplotlib': 'Data Science & Analytics',
            'tableau': 'Data Science & Analytics',
            'power bi': 'Data Science & Analytics',
            'docker': 'Cloud Computing',
            'kubernetes': 'Cloud Computing',
            'aws': 'Cloud Computing',
            'azure': 'Cloud Computing',
            'react': 'Web Development',
            'vue': 'Web Development',
            'angular': 'Web Development',
            'node.js': 'Web Development',
            'django': 'Web Development',
            'flask': 'Web Development',
            'spring': 'Web Development',
        }
    
    def _load_existing_weights(self):
        """从enhanced_in20_in27加载项目权重数据"""
        enhanced_dir = Path("outputs/knowledge_graphs/enhanced_in20_in27")
        
        if not enhanced_dir.exists():
            print(f"⚠️  enhanced_in20_in27目录不存在，使用默认权重")
            return
        
        print(f"📥 从 enhanced_in20_in27 加载权重数据...")
        
        # 遍历所有项目的enhanced KG
        for project_dir in enhanced_dir.iterdir():
            if not project_dir.is_dir():
                continue
            
            # 查找JSON文件
            json_files = list(project_dir.glob("*_enhanced_kg.json"))
            if not json_files:
                continue
            
            kg_file = json_files[0]
            try:
                with open(kg_file, 'r', encoding='utf-8') as f:
                    kg_data = json.load(f)
                
                project_name = kg_data.get('project', '')
                if not project_name:
                    continue
                
                # 存储该项目的权重映射
                project_weights = {}
                
                # 提取 PROJECT -> SKILL 的权重
                for edge in kg_data.get('edges', []):
                    if edge.get('relation') == 'REQUIRES_SKILL':
                        skill_id = edge.get('target', '')
                        weight = edge.get('weight', 1.0)
                        
                        # 查找技能名称
                        skill_name = None
                        for node in kg_data.get('nodes', []):
                            if node.get('id') == skill_id:
                                skill_name = node.get('name', '').lower()
                                break
                        
                        if skill_name:
                            project_weights[skill_name] = weight
                
                # 存储到全局字典
                self.existing_weights[project_name] = project_weights
                
            except Exception as e:
                print(f"  ⚠️  加载失败 {kg_file.name}: {e}")
        
        print(f"  ✅ 已加载 {len(self.existing_weights)} 个项目的权重数据")
    
    def _normalize_weight(self, weight: float, min_val: float = 2.0, max_val: float = 20.0) -> float:
        """
        将enhanced_in20_in27的权重（通常2-20）归一化到0.5-1.0范围
        
        Args:
            weight: 原始权重（2-20）
            min_val: 最小权重值
            max_val: 最大权重值
            
        Returns:
            归一化后的权重（0.5-1.0）
        """
        # 线性归一化到0.5-1.0
        # 2.0 -> 0.5, 20.0 -> 1.0
        normalized = 0.5 + ((weight - min_val) / (max_val - min_val)) * 0.5
        
        # 确保在范围内
        return max(0.5, min(1.0, normalized))
    
    def _get_weight_for_skill(self, project_name: str, skill: str, default: float = 0.8) -> float:
        """
        获取项目-技能的权重
        
        Args:
            project_name: 项目名称
            skill: 技能名称
            default: 默认权重
            
        Returns:
            权重值
        """
        if not self.use_existing_weights:
            return default
        
        # 查找项目权重数据
        project_weights = self.existing_weights.get(project_name, {})
        if not project_weights:
            return default
        
        # 查找技能权重
        skill_lower = skill.lower()
        if skill_lower in project_weights:
            raw_weight = project_weights[skill_lower]
            return self._normalize_weight(raw_weight)
        
        return default
    
    def generate_project_kg(self, project_file: str, output_dir: str = "outputs/knowledge_graphs/individual/three_layer_projects") -> Optional[Dict]:
        """生成3层结构的项目知识图谱"""
        
        if not os.path.exists(project_file):
            print(f"❌ 项目文件不存在: {project_file}")
            return None
        
        # 解析项目信息
        with open(project_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        project_info = self._parse_project_content(content)
        project_name = os.path.splitext(os.path.basename(project_file))[0]
        project_title = project_info.get('title', project_name)
        
        print(f"📋 生成3层项目知识图谱: {project_title}")
        
        # 创建图
        entities = {}
        relationships = []
        G = nx.MultiDiGraph()
        
        # Layer 1: 项目节点
        project_id = f"project_{project_name.replace(' ', '_')}"
        entities[project_id] = KGEntity(
            id=project_id,
            name=project_title,
            entity_type='PROJECT',
            layer=1,
            properties={
                'description': project_info.get('description', '')[:200],
                'file_path': project_file
            }
        )
        
        G.add_node(project_id, name=project_title, type='PROJECT', layer=1,
                   **entities[project_id].properties)
        
        # 收集所有技能、技术、专业
        all_skills = project_info.get('skills', [])
        all_technologies = project_info.get('technologies', [])
        all_majors = project_info.get('majors', [])
        
        # Layer 2: 领域分类
        domain_skills = defaultdict(list)
        domain_technologies = defaultdict(list)
        
        # 将技能分配到领域
        for skill in all_skills:
            skill_lower = skill.lower().strip()
            domain = self._get_domain_for_skill(skill_lower)
            domain_skills[domain].append(skill)
        
        # 将技术分配到领域
        for tech in all_technologies:
            tech_lower = tech.lower().strip()
            domain = self._get_domain_for_tech(tech_lower)
            domain_technologies[domain].append(tech)
        
        # 专业归到特定领域
        for major in all_majors:
            domain = 'Academic Programs'
            if major not in domain_skills[domain]:
                domain_skills[domain].append(major)
        
        # 创建领域节点和关系
        for domain, skills in domain_skills.items():
            if not skills:
                continue
                
            domain_id = f"domain_{domain.replace(' ', '_').replace('&', 'and').lower()}"
            
            # 添加领域节点
            if domain_id not in entities:
                entities[domain_id] = KGEntity(
                    id=domain_id,
                    name=domain,
                    entity_type='DOMAIN',
                    layer=2,
                    properties={'skill_count': len(skills)}
                )
                
                G.add_node(domain_id, name=domain, type='DOMAIN', layer=2,
                          skill_count=len(skills))
                
                # 项目关联领域
                rel = KGRelationship(
                    source_id=project_id,
                    target_id=domain_id,
                    relation_type='REQUIRES_DOMAIN',
                    weight=1.0
                )
                relationships.append(rel)
                G.add_edge(project_id, domain_id, relation='REQUIRES_DOMAIN', weight=1.0)
            
            # Layer 3: 具体技能
            for skill in skills:
                skill_id = f"skill_{skill.replace(' ', '_').lower()}"
                
                if skill_id not in entities:
                    # 判断是专业还是技能
                    entity_type = 'MAJOR' if domain == 'Academic Programs' else 'SKILL'
                    
                    entities[skill_id] = KGEntity(
                        id=skill_id,
                        name=skill,
                        entity_type=entity_type,
                        layer=3,
                        properties={}
                    )
                    
                    G.add_node(skill_id, name=skill, type=entity_type, layer=3)
                    
                    # 领域包含技能 - 使用动态权重
                    skill_weight = self._get_weight_for_skill(project_name, skill, default=0.8)
                    
                    rel = KGRelationship(
                        source_id=domain_id,
                        target_id=skill_id,
                        relation_type='INCLUDES',
                        weight=skill_weight
                    )
                    relationships.append(rel)
                    G.add_edge(domain_id, skill_id, relation='INCLUDES', weight=skill_weight)
        
        # 处理技术节点
        for domain, techs in domain_technologies.items():
            if not techs:
                continue
                
            domain_id = f"domain_{domain.replace(' ', '_').replace('&', 'and').lower()}"
            
            # 确保领域节点存在
            if domain_id not in entities:
                entities[domain_id] = KGEntity(
                    id=domain_id,
                    name=domain,
                    entity_type='DOMAIN',
                    layer=2,
                    properties={'tech_count': len(techs)}
                )
                
                G.add_node(domain_id, name=domain, type='DOMAIN', layer=2,
                          tech_count=len(techs))
                
                # 项目关联领域
                rel = KGRelationship(
                    source_id=project_id,
                    target_id=domain_id,
                    relation_type='REQUIRES_DOMAIN',
                    weight=1.0
                )
                relationships.append(rel)
                G.add_edge(project_id, domain_id, relation='REQUIRES_DOMAIN', weight=1.0)
            
            # Layer 3: 具体技术
            for tech in techs:
                tech_id = f"tech_{tech.replace(' ', '_').lower()}"
                
                if tech_id not in entities:
                    entities[tech_id] = KGEntity(
                        id=tech_id,
                        name=tech,
                        entity_type='TECHNOLOGY',
                        layer=3,
                        properties={}
                    )
                    
                    G.add_node(tech_id, name=tech, type='TECHNOLOGY', layer=3)
                    
                    # 领域包含技术 - 使用动态权重（默认稍高于skill）
                    tech_weight = self._get_weight_for_skill(project_name, tech, default=0.9)
                    
                    rel = KGRelationship(
                        source_id=domain_id,
                        target_id=tech_id,
                        relation_type='USES_TECH',
                        weight=tech_weight
                    )
                    relationships.append(rel)
                    G.add_edge(domain_id, tech_id, relation='USES_TECH', weight=tech_weight)
        
        # 保存结果
        stats = self._save_three_layer_kg(
            project_id, project_title, entities, relationships, G, output_dir
        )
        
        return stats
    
    def _get_domain_for_skill(self, skill: str) -> str:
        """获取技能对应的领域"""
        skill_lower = skill.lower().strip()
        
        # 完全匹配
        if skill_lower in self.skill_to_domain:
            return self.skill_to_domain[skill_lower]
        
        # 部分匹配
        for key, domain in self.skill_to_domain.items():
            if key in skill_lower or skill_lower in key:
                return domain
        
        # 默认领域
        return 'General Skills'
    
    def _get_domain_for_tech(self, tech: str) -> str:
        """获取技术对应的领域"""
        tech_lower = tech.lower().strip()
        
        # 完全匹配
        if tech_lower in self.tech_to_domain:
            return self.tech_to_domain[tech_lower]
        
        # 部分匹配
        for key, domain in self.tech_to_domain.items():
            if key in tech_lower or tech_lower in key:
                return domain
        
        # 默认领域
        return 'General Technologies'
    
    def _parse_project_content(self, content: str) -> Dict[str, Any]:
        """解析项目内容"""
        info = {
            'title': '',
            'description': '',
            'majors': [],
            'skills': [],
            'technologies': []
        }
        
        lines = content.split('\n')
        
        # 提取项目标题
        for line in lines:
            if 'Project title' in line or '## Project Title' in line:
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 3:
                        info['title'] = parts[-2].strip()
                elif ':' in line:
                    info['title'] = line.split(':', 1)[1].strip()
                break
        
        # 提取专业要求
        for line in lines:
            if 'Information Technology major' in line or 'Major' in line:
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 3:
                        majors_text = parts[-2].strip()
                        if majors_text and majors_text != '-' and 'major' not in majors_text.lower():
                            info['majors'] = [m.strip() for m in majors_text.split(',') if m.strip()]
                break
        
        # 提取描述
        description_lines = []
        in_description = False
        for line in lines:
            if 'Brief description' in line or 'Description' in line:
                in_description = True
                continue
            if in_description:
                if line.startswith('|') and line.count('|') >= 3:
                    parts = line.split('|')
                    if len(parts) >= 3:
                        text = parts[-2].strip()
                        if text and text != '-':
                            description_lines.append(text)
                elif line.strip() and not line.startswith('+') and not line.startswith('|'):
                    description_lines.append(line.strip())
                    
                # 遇到新的表格行或章节标题，停止
                if ('Academic Supervisor' in line or 'Project context' in line or 
                    '##' in line or 'Required' in line):
                    break
        
        info['description'] = ' '.join(description_lines)
        
        # 从描述中提取技能和技术
        self._extract_skills_technologies(info['description'], info)
        
        return info
    
    def _extract_skills_technologies(self, text: str, info: Dict):
        """从文本中提取技能和技术"""
        text_lower = text.lower()
        
        # 常见技能关键词
        skill_keywords = [
            'machine learning', 'deep learning', 'data science', 'data analytics',
            'web development', 'mobile development', 'cybersecurity', 'network security',
            'database', 'sql', 'nosql', 'cloud computing', 'devops',
            'software engineering', 'programming', 'algorithms', 'data structures',
            'artificial intelligence', 'computer vision', 'nlp', 'natural language processing',
            'signal processing', 'image processing', 'iot', 'embedded systems',
            'business analysis', 'project management', 'agile', 'testing',
            'frontend', 'backend', 'full stack', 'api', 'microservices',
            'gis', 'remote sensing', 'spatial analysis'
        ]
        
        # 常见技术关键词
        tech_keywords = [
            'python', 'java', 'javascript', 'c++', 'c#', 'r', 'matlab',
            'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'opencv',
            'react', 'vue', 'angular', 'node.js', 'django', 'flask', 'spring',
            'aws', 'azure', 'google cloud', 'docker', 'kubernetes',
            'mongodb', 'postgresql', 'mysql', 'redis',
            'git', 'jenkins', 'ansible', 'terraform',
            'pandas', 'numpy', 'matplotlib', 'tableau', 'power bi'
        ]
        
        # 提取技能
        for skill in skill_keywords:
            if skill in text_lower and skill.title() not in info['skills']:
                info['skills'].append(skill.title())
        
        # 提取技术
        for tech in tech_keywords:
            if tech in text_lower:
                # 保持原始大小写
                tech_formatted = tech.upper() if tech in ['sql', 'api', 'iot', 'nlp', 'gis', 'aws'] else tech.title()
                if tech_formatted not in info['technologies']:
                    info['technologies'].append(tech_formatted)
    
    def _save_three_layer_kg(self, project_id: str, project_title: str,
                            entities: Dict, relationships: List,
                            G: nx.MultiDiGraph, output_dir: str) -> Dict:
        """保存3层知识图谱"""
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 清理文件名
        safe_title = "".join(c for c in project_title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title.replace(' ', '_')[:50]
        
        # 保存实体
        entities_file = os.path.join(output_dir, f"{safe_title}_entities.json")
        with open(entities_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(e) for e in entities.values()], f, indent=2, ensure_ascii=False)
        
        # 保存关系
        relationships_file = os.path.join(output_dir, f"{safe_title}_relationships.json")
        with open(relationships_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(r) for r in relationships], f, indent=2, ensure_ascii=False)
        
        # 保存可视化图
        self._visualize_three_layer_kg(G, project_title, output_dir, safe_title)
        
        # 统计信息
        layer_counts = defaultdict(int)
        type_counts = defaultdict(int)
        for entity in entities.values():
            layer_counts[entity.layer] += 1
            type_counts[entity.entity_type] += 1
        
        stats = {
            'project_id': project_id,
            'project_title': project_title,
            'total_entities': len(entities),
            'total_relationships': len(relationships),
            'layer_distribution': dict(layer_counts),
            'entity_types': dict(type_counts),
            'layers': {
                'layer_1': 'Project',
                'layer_2': 'Domains',
                'layer_3': 'Skills/Technologies/Majors'
            }
        }
        
        stats_file = os.path.join(output_dir, f"{safe_title}_stats.json")
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"  ✅ 实体: {len(entities)}, 关系: {len(relationships)}")
        print(f"  📊 层次分布: Layer1={layer_counts[1]}, Layer2={layer_counts[2]}, Layer3={layer_counts[3]}")
        
        return stats
    
    def _visualize_three_layer_kg(self, G: nx.MultiDiGraph, title: str, 
                                  output_dir: str, safe_title: str, 
                                  show_all_weights: bool = False):
        """可视化3层知识图谱（圆形同心圆布局）
        
        完全按照示意图的圆形布局：
        - Layer 1 (Project): 中心点
        - Layer 2 (Domain): 内圈同心圆
        - Layer 3 (Skills/Tech): 外圈同心圆
        - 虚线圆圈分隔每层
        
        Args:
            G: NetworkX图
            title: 项目标题
            output_dir: 输出目录
            safe_title: 安全的文件名
            show_all_weights: 是否显示所有权重（包括1.0）。默认False只显示非1.0权重
        """
        
        plt.figure(figsize=(24, 24), facecolor='#f8f9fa')
        ax = plt.gca()
        
        # 按层分组节点
        layer1_nodes = [n for n, d in G.nodes(data=True) if d.get('layer') == 1]
        layer2_nodes = [n for n, d in G.nodes(data=True) if d.get('layer') == 2]
        layer3_nodes = [n for n, d in G.nodes(data=True) if d.get('layer') == 3]
        
        # 圆形同心圆布局参数
        import math
        pos = {}
        
        # 半径设置（更紧凑）
        RADIUS_LAYER1 = 0        # Layer 1: 中心点
        RADIUS_LAYER2 = 1.5      # Layer 2: 内圈（更短的边）
        RADIUS_LAYER3 = 3.0      # Layer 3: 外圈（更短的边）
        
        # Layer 1: 项目节点在正中心 (0, 0)
        if layer1_nodes:
            pos[layer1_nodes[0]] = (0, 0)
        
        # Layer 2: 领域节点均匀分布在内圈
        layer2_count = len(layer2_nodes)
        if layer2_count > 0:
            for i, node in enumerate(layer2_nodes):
                angle = 2 * math.pi * i / layer2_count - math.pi / 2  # 从顶部开始
                x = RADIUS_LAYER2 * math.cos(angle)
                y = RADIUS_LAYER2 * math.sin(angle)
                pos[node] = (x, y)
        
        # Layer 3: 详细节点均匀分布在外圈
        # 按所属领域分组，每组节点围绕对应的领域节点排列
        domain_children = defaultdict(list)
        for edge in G.edges(data=True):
            if edge[1] in layer3_nodes:
                domain_children[edge[0]].append(edge[1])
        
        # Layer 3节点均匀分布策略：围绕对应的Domain节点放置
        for domain_idx, domain in enumerate(layer2_nodes):
            children = domain_children.get(domain, [])
            child_count = len(children)
            if child_count > 0:
                # 计算这个域的角度范围
                base_angle = 2 * math.pi * domain_idx / layer2_count - math.pi / 2
                angle_spread = (2 * math.pi / layer2_count) * 0.8  # 80%的扇形区域
                
                for i, child in enumerate(children):
                    # 在该域的角度范围内均匀分布
                    if child_count == 1:
                        angle = base_angle
                    else:
                        angle = base_angle + (i - (child_count - 1) / 2) * angle_spread / (child_count + 1)
                    
                    x = RADIUS_LAYER3 * math.cos(angle)
                    y = RADIUS_LAYER3 * math.sin(angle)
                    pos[child] = (x, y)
        
        # 节点颜色
        node_colors = []
        for node in G.nodes():
            node_type = G.nodes[node].get('type', '')
            if node_type == 'PROJECT':
                node_colors.append('#FF6B6B')  # 红色
            elif node_type == 'DOMAIN':
                node_colors.append('#4ECDC4')  # 青色
            elif node_type == 'MAJOR':
                node_colors.append('#95E1D3')  # 浅青色
            elif node_type == 'SKILL':
                node_colors.append('#FFA07A')  # 浅橙色
            elif node_type == 'TECHNOLOGY':
                node_colors.append('#DDA0DD')  # 浅紫色
            else:
                node_colors.append('#E0E0E0')  # 灰色
        
        # 节点大小（更大）
        node_sizes = []
        for node in G.nodes():
            layer = G.nodes[node].get('layer', 3)
            if layer == 1:
                node_sizes.append(8000)  # Project节点最大
            elif layer == 2:
                node_sizes.append(5000)  # Domain节点中等
            else:
                node_sizes.append(2500)  # Skills/Tech节点较小
        
        # 🎨 绘制虚线圆圈分隔层（先画背景）
        circle_layer2 = plt.Circle((0, 0), RADIUS_LAYER2, color='#cccccc', 
                                   fill=False, linestyle='--', linewidth=2, alpha=0.4)
        circle_layer3 = plt.Circle((0, 0), RADIUS_LAYER3, color='#cccccc', 
                                   fill=False, linestyle='--', linewidth=2, alpha=0.4)
        ax.add_patch(circle_layer2)
        ax.add_patch(circle_layer3)
        
        # 绘制边（使用不同颜色区分关系类型）
        edge_colors = []
        for u, v, data in G.edges(data=True):
            relation = data.get('relation', '')
            if relation == 'REQUIRES_DOMAIN':
                edge_colors.append('#666666')  # 深灰色：Project -> Domain
            elif relation in ['INCLUDES', 'USES_TECH']:
                edge_colors.append('#999999')  # 浅灰色：Domain -> Skills/Tech
            else:
                edge_colors.append('#cccccc')
        
        nx.draw_networkx_edges(G, pos, edge_color=edge_colors, arrows=True, 
                              arrowsize=20, alpha=0.6, width=2.0, 
                              connectionstyle='arc3,rad=0.1')
        
        # 绘制节点（在边之上）
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                              node_size=node_sizes, alpha=0.95, 
                              edgecolors='white', linewidths=2)
        
        # 绘制边的权重标签
        edge_labels = {}
        for u, v, data in G.edges(data=True):
            weight = data.get('weight', 1.0)
            # 根据参数决定是否显示所有权重
            if show_all_weights or weight != 1.0:
                edge_labels[(u, v)] = f"{weight:.1f}"
        
        if edge_labels:
            nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=7, 
                                        font_color='red', bbox=dict(boxstyle="round,pad=0.2", 
                                        facecolor='white', alpha=0.7, edgecolor='none'))
        
        # 节点标签（粗体显示）
        labels = {node: G.nodes[node].get('name', node)[:30] for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, font_size=10, font_weight='bold', 
                               font_family='sans-serif')
        
        # 🏷️ 添加层次标签（适应更紧凑的布局）
        plt.text(3.7, 0, 'Layer 3\n(Details)', fontsize=14, color='#FF8C00', 
                weight='bold', ha='left', va='center',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFF8DC', alpha=0.8))
        
        plt.text(0, 2.2, 'Layer 2\n(Domain)', fontsize=14, color='#4ECDC4', 
                weight='bold', ha='center', va='bottom',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='#E0F7FA', alpha=0.8))
        
        plt.text(0, -0.8, 'Layer 1', fontsize=14, color='#FF6B6B', 
                weight='bold', ha='center', va='top',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFE4E1', alpha=0.8))
        
        plt.title(f"3-Layer Project Knowledge Graph: {title}", fontsize=18, 
                 weight='bold', pad=30)
        
        # 图例（更详细）
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#FF6B6B', edgecolor='white', linewidth=2, label='Project (Layer 1)'),
            Patch(facecolor='#4ECDC4', edgecolor='white', linewidth=2, label='Domain (Layer 2)'),
            Patch(facecolor='#95E1D3', edgecolor='white', linewidth=2, label='Major (Layer 3)'),
            Patch(facecolor='#FFA07A', edgecolor='white', linewidth=2, label='Skill (Layer 3)'),
            Patch(facecolor='#DDA0DD', edgecolor='white', linewidth=2, label='Technology (Layer 3)')
        ]
        plt.legend(handles=legend_elements, loc='upper right', fontsize=11, 
                  framealpha=0.95, edgecolor='gray')
        
        plt.axis('equal')  # 保持圆形
        plt.axis('off')
        plt.tight_layout()
        
        output_file = os.path.join(output_dir, f"{safe_title}_kg.png")
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"  📊 可视化已保存: {output_file}")


def generate_all_three_layer_project_kgs(project_dir: str = "data/processed/projects_md",
                                         output_dir: str = "outputs/knowledge_graphs/individual/three_layer_projects",
                                         use_existing_weights: bool = False):
    """
    批量生成所有项目的3层知识图谱
    
    Args:
        project_dir: 项目Markdown文件目录
        output_dir: 输出目录
        use_existing_weights: 是否从enhanced_in20_in27读取现有权重并归一化
    """
    
    generator = ThreeLayerProjectKGGenerator(use_existing_weights=use_existing_weights)
    
    # 获取所有项目文件
    project_files = glob.glob(os.path.join(project_dir, "*.md"))
    
    if not project_files:
        print(f"❌ 未找到项目文件: {project_dir}")
        return
    
    print(f"🔄 开始生成3层项目知识图谱...")
    print(f"📁 项目目录: {project_dir}")
    print(f"📂 输出目录: {output_dir}")
    print(f"📋 找到 {len(project_files)} 个项目\n")
    
    results = []
    for i, project_file in enumerate(project_files, 1):
        project_name = os.path.basename(project_file)
        print(f"[{i}/{len(project_files)}] {project_name}")
        
        try:
            stats = generator.generate_project_kg(project_file, output_dir)
            if stats:
                results.append(stats)
        except Exception as e:
            print(f"  ❌ 失败: {e}")
            import traceback
            traceback.print_exc()
    
    # 保存总体报告
    if results:
        summary = {
            'total_projects': len(results),
            'generation_time': datetime.now().isoformat(),
            'output_directory': output_dir,
            'projects': results
        }
        
        summary_file = os.path.join(output_dir, "summary_report.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 完成！共生成 {len(results)} 个3层项目知识图谱")
        print(f"📄 总结报告: {summary_file}")
        
        return {
            'successful': len(results),
            'failed': len(project_files) - len(results),
            'total': len(project_files)
        }
    else:
        print("\n❌ 没有成功生成任何知识图谱")
        return {
            'successful': 0,
            'failed': len(project_files),
            'total': len(project_files)
        }


if __name__ == "__main__":
    generate_all_three_layer_project_kgs()

