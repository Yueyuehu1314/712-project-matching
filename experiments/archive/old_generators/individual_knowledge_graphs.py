#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版个体知识图谱构建系统
为每个学生和每个项目创建独立的知识图谱

主要特性：
- 学生档案的个体知识图谱生成
- 项目信息的个体知识图谱生成
- 课程到技能的连接关系 (TEACHES_SKILL)
- 增强的可视化效果

修复了原有问题：
- 技能现在正确地从课程连接出来
- 可以追踪技能的来源（课程 vs 自学）
"""

import os
import json
import glob
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict, Counter

@dataclass
class IndividualEntity:
    """个体知识图谱实体"""
    id: str
    name: str
    entity_type: str
    properties: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}

@dataclass
class IndividualRelationship:
    """个体知识图谱关系"""
    source_id: str
    target_id: str
    relation_type: str
    weight: float = 1.0
    properties: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}

class IndividualKnowledgeGraphBuilder:
    """个体知识图谱构建器"""
    
    def __init__(self):
        self.entity_types = {
            'STUDENT': 'Student',
            'PROJECT': 'Project', 
            'SKILL': 'Skill',
            'COURSE': 'Course',
            'MAJOR': 'Major',
            'TECHNOLOGY': 'Technology',
            'SUPERVISOR': 'Supervisor',
            'INTEREST': 'Interest',
            'COMPANY': 'Company',
            'WORK_EXPERIENCE': 'WorkExperience',
            'PROJECT_EXPERIENCE': 'ProjectExperience'
        }
        
        self.relation_types = {
            'HAS_SKILL': 'has_skill',
            'COMPLETED_COURSE': 'completed_course',
            'STUDIED_MAJOR': 'studied_major',
            'INTERESTED_IN': 'interested_in',
            'WORKED_AT': 'worked_at',
            'PARTICIPATED_IN': 'participated_in',
            'REQUIRES_SKILL': 'requires_skill',
            'USES_TECHNOLOGY': 'uses_technology',
            'SUPERVISED_BY': 'supervised_by',
            'REQUIRES_MAJOR': 'requires_major',
            'TEACHES_SKILL': 'teaches_skill',  # 新增：课程教授技能
            'SUPPORTS_PROJECT': 'supports_project'  # 新增：课程支持项目
        }
        
        # 课程到技能的映射
        self.course_skill_mapping = {
            'IFN564 Machine Learning': ['machine learning', 'data science', 'artificial intelligence'],
            'IFN666 Web Technologies': ['web development', 'javascript', 'html/css'],
            'IFN670 Mobile Application Development': ['mobile development', 'app development'],
            'IFN623 Cyber Security': ['cybersecurity', 'network security', 'encryption'],
            'IFN554 Databases': ['database management', 'sql', 'data modeling'],
            'IFN555 Introduction to Programming': ['programming', 'problem solving', 'algorithms'],
            'IFN556 Object Oriented Programming': ['object-oriented programming', 'software design'],
            'IFN619 Data Analytics and Visualisation': ['data science', 'data visualization', 'statistical analysis'],
            'IFN632 Advanced Data Analytics': ['advanced analytics', 'machine learning', 'data mining'],
            'IFN565 Advanced Programming': ['advanced programming', 'software engineering'],
            'IFN668 Advanced Software Engineering': ['software engineering', 'software architecture'],
            'IFN563 Algorithms and Complexity': ['algorithms', 'computational complexity', 'optimization'],
            'IFN614 Business Process Modelling': ['business analysis', 'process modeling'],
            'IFN616 Requirements Engineering': ['requirements analysis', 'stakeholder management'],
            'IFN617 Business Intelligence Systems': ['business intelligence', 'data warehousing'],
            'IFN551 Computer Systems Fundamentals': ['computer systems', 'hardware understanding'],
            'IFN552 Systems Analysis and Design': ['systems analysis', 'system design'],
            'IFN553 Introduction to Security and Networking': ['networking', 'network security']
        }
    
    def create_student_knowledge_graph(self, student_file: str, output_dir: str = "individual_kg/students"):
        """为单个学生创建知识图谱"""
        
        if not os.path.exists(student_file):
            print(f"❌ 学生文件不存在: {student_file}")
            return None
        
        # 解析学生信息
        with open(student_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        student_info = self._parse_student_content(content)
        student_id = student_info.get('student_id', 'unknown')
        student_name = student_info.get('name', 'Unknown Student')
        
        print(f"🎓 创建学生知识图谱: {student_name} ({student_id})")
        
        # 创建图
        entities = {}
        relationships = []
        G = nx.MultiDiGraph()
        
        # 添加学生主实体
        student_entity_id = f"student_{student_id}"
        entities[student_entity_id] = IndividualEntity(
            id=student_entity_id,
            name=student_name,
            entity_type='STUDENT',
            properties={
                'student_id': student_id,
                'major': student_info.get('major', ''),
                'year': student_info.get('year', ''),
                'file_path': student_file
            }
        )
        
        G.add_node(student_entity_id, 
                   name=student_name, 
                   type='STUDENT',
                   **entities[student_entity_id].properties)
        
        # 添加专业
        major = student_info.get('major', '')
        if major:
            major_id = f"major_{major.replace(' ', '_').lower()}"
            if major_id not in entities:
                entities[major_id] = IndividualEntity(major_id, major, 'MAJOR')
                G.add_node(major_id, name=major, type='MAJOR')
            
            rel = IndividualRelationship(student_entity_id, major_id, 'STUDIED_MAJOR')
            relationships.append(rel)
            G.add_edge(student_entity_id, major_id, relation='STUDIED_MAJOR', weight=1.0)
        
        # 添加课程并建立课程到技能的连接
        course_taught_skills = set()  # 记录通过课程获得的技能
        for course in student_info.get('courses', []):
            course_clean = course.strip()
            course_id = f"course_{course_clean.replace(' ', '_').lower()}"
            if course_id not in entities:
                entities[course_id] = IndividualEntity(course_id, course_clean, 'COURSE')
                G.add_node(course_id, name=course_clean, type='COURSE')
            
            # 学生完成课程
            rel = IndividualRelationship(student_entity_id, course_id, 'COMPLETED_COURSE')
            relationships.append(rel)
            G.add_edge(student_entity_id, course_id, relation='COMPLETED_COURSE', weight=1.0)
            
            # 课程教授的技能
            taught_skills = self._get_skills_taught_by_course(course_clean)
            for skill in taught_skills:
                skill_id = f"skill_{skill.replace(' ', '_').lower()}"
                
                # 添加技能实体
                if skill_id not in entities:
                    entities[skill_id] = IndividualEntity(skill_id, skill, 'SKILL')
                    G.add_node(skill_id, name=skill, type='SKILL')
                
                # 课程教授技能
                rel = IndividualRelationship(course_id, skill_id, 'TEACHES_SKILL', weight=0.8)
                relationships.append(rel)
                G.add_edge(course_id, skill_id, relation='TEACHES_SKILL', weight=0.8)
                
                # 学生通过课程获得技能
                rel = IndividualRelationship(student_entity_id, skill_id, 'HAS_SKILL', weight=0.9)
                relationships.append(rel)
                G.add_edge(student_entity_id, skill_id, relation='HAS_SKILL', weight=0.9)
                
                course_taught_skills.add(skill_id)
        
        # 添加直接技能（不通过课程获得的）
        for skill in student_info.get('skills', []):
            skill_clean = skill.strip()
            skill_id = f"skill_{skill_clean.replace(' ', '_').lower()}"
            
            # 如果技能还没有通过课程添加，则作为直接技能添加
            if skill_id not in course_taught_skills:
                if skill_id not in entities:
                    entities[skill_id] = IndividualEntity(skill_id, skill_clean, 'SKILL')
                    G.add_node(skill_id, name=skill_clean, type='SKILL')
                
                rel = IndividualRelationship(student_entity_id, skill_id, 'HAS_SKILL', weight=0.7)
                relationships.append(rel)
                G.add_edge(student_entity_id, skill_id, relation='HAS_SKILL', weight=0.7)
        
        # 添加兴趣
        for interest in student_info.get('interests', []):
            interest_id = f"interest_{interest.replace(' ', '_').lower()}"
            if interest_id not in entities:
                entities[interest_id] = IndividualEntity(interest_id, interest, 'INTEREST')
                G.add_node(interest_id, name=interest, type='INTEREST')
            
            rel = IndividualRelationship(student_entity_id, interest_id, 'INTERESTED_IN')
            relationships.append(rel)
            G.add_edge(student_entity_id, interest_id, relation='INTERESTED_IN', weight=1.0)
        
        # 添加项目经验
        for i, project in enumerate(student_info.get('projects', [])):
            project_exp_id = f"project_exp_{student_id}_{i}"
            entities[project_exp_id] = IndividualEntity(
                project_exp_id, 
                project[:50] + "..." if len(project) > 50 else project, 
                'PROJECT_EXPERIENCE',
                {'description': project}
            )
            G.add_node(project_exp_id, name=project[:30], type='PROJECT_EXPERIENCE')
            
            rel = IndividualRelationship(student_entity_id, project_exp_id, 'PARTICIPATED_IN')
            relationships.append(rel)
            G.add_edge(student_entity_id, project_exp_id, relation='PARTICIPATED_IN', weight=1.0)
        
        # 保存结果
        self._save_individual_kg(student_entity_id, student_name, entities, relationships, G, output_dir, 'student')
        
        return {
            'entities': len(entities),
            'relationships': len(relationships),
            'student_id': student_id,
            'student_name': student_name
        }
    
    def create_project_knowledge_graph(self, project_file: str, output_dir: str = "individual_kg/projects"):
        """为单个项目创建知识图谱"""
        
        if not os.path.exists(project_file):
            print(f"❌ 项目文件不存在: {project_file}")
            return None
        
        # 解析项目信息
        with open(project_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        project_info = self._parse_project_content(content)
        project_name = os.path.splitext(os.path.basename(project_file))[0]
        project_title = project_info.get('title', project_name)
        
        print(f"📋 创建项目知识图谱: {project_title}")
        
        # 创建图
        entities = {}
        relationships = []
        G = nx.MultiDiGraph()
        
        # 添加项目主实体
        project_entity_id = f"project_{project_name.replace(' ', '_')}"
        entities[project_entity_id] = IndividualEntity(
            id=project_entity_id,
            name=project_title,
            entity_type='PROJECT',
            properties={
                'description': project_info.get('description', ''),
                'supervisor': project_info.get('supervisor', ''),
                'file_path': project_file
            }
        )
        
        G.add_node(project_entity_id, 
                   name=project_title, 
                   type='PROJECT',
                   **entities[project_entity_id].properties)
        
        # 添加专业要求
        for major in project_info.get('majors', []):
            major_id = f"major_{major.replace(' ', '_').lower()}"
            if major_id not in entities:
                entities[major_id] = IndividualEntity(major_id, major, 'MAJOR')
                G.add_node(major_id, name=major, type='MAJOR')
            
            rel = IndividualRelationship(project_entity_id, major_id, 'REQUIRES_MAJOR')
            relationships.append(rel)
            G.add_edge(project_entity_id, major_id, relation='REQUIRES_MAJOR', weight=1.0)
        
        # 添加技能要求
        for skill in project_info.get('skills', []):
            skill_id = f"skill_{skill.replace(' ', '_').lower()}"
            if skill_id not in entities:
                entities[skill_id] = IndividualEntity(skill_id, skill, 'SKILL')
                G.add_node(skill_id, name=skill, type='SKILL')
            
            rel = IndividualRelationship(project_entity_id, skill_id, 'REQUIRES_SKILL')
            relationships.append(rel)
            G.add_edge(project_entity_id, skill_id, relation='REQUIRES_SKILL', weight=1.0)
        
        # 添加技术要求
        for tech in project_info.get('technologies', []):
            tech_id = f"tech_{tech.replace(' ', '_').lower()}"
            if tech_id not in entities:
                entities[tech_id] = IndividualEntity(tech_id, tech, 'TECHNOLOGY')
                G.add_node(tech_id, name=tech, type='TECHNOLOGY')
            
            rel = IndividualRelationship(project_entity_id, tech_id, 'USES_TECHNOLOGY')
            relationships.append(rel)
            G.add_edge(project_entity_id, tech_id, relation='USES_TECHNOLOGY', weight=1.0)
        
        # 添加导师
        supervisor = project_info.get('supervisor', '')
        if supervisor:
            supervisor_id = f"supervisor_{supervisor.replace(' ', '_').lower()}"
            if supervisor_id not in entities:
                entities[supervisor_id] = IndividualEntity(supervisor_id, supervisor, 'SUPERVISOR')
                G.add_node(supervisor_id, name=supervisor, type='SUPERVISOR')
            
            rel = IndividualRelationship(project_entity_id, supervisor_id, 'SUPERVISED_BY')
            relationships.append(rel)
            G.add_edge(project_entity_id, supervisor_id, relation='SUPERVISED_BY', weight=1.0)
        
        # 保存结果
        self._save_individual_kg(project_entity_id, project_title, entities, relationships, G, output_dir, 'project')
        
        return {
            'entities': len(entities),
            'relationships': len(relationships),
            'project_name': project_name,
            'project_title': project_title
        }
    
    def _parse_student_content(self, content: str) -> Dict[str, Any]:
        """解析学生档案内容"""
        info = {
            'name': '',
            'student_id': '',
            'major': '',
            'year': '',
            'courses': [],
            'skills': [],
            'interests': [],
            'projects': []
        }
        
        lines = content.split('\n')
        
        # 提取基本信息
        for line in lines:
            if '**Name**:' in line:
                info['name'] = line.split('**Name**:')[1].strip()
            elif '**Student ID**:' in line:
                info['student_id'] = line.split('**Student ID**:')[1].strip()
            elif '**Major**:' in line:
                info['major'] = line.split('**Major**:')[1].strip()
            elif '**Year**:' in line:
                info['year'] = line.split('**Year**:')[1].strip()
        
        # 提取列表信息
        current_section = None
        for line in lines:
            if '## Completed Courses' in line:
                current_section = 'courses'
            elif '## Technical Skills' in line:
                current_section = 'skills'
            elif '## Interests' in line:
                current_section = 'interests'
            elif '## Previous Projects' in line or '## Project Experience' in line:
                current_section = 'projects'
            elif line.startswith('##'):
                current_section = None
            elif current_section and line.strip().startswith('-'):
                item = line.strip().lstrip('- ').strip()
                if item:
                    info[current_section].append(item)
        
        return info
    
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
                        if majors_text and majors_text != '':
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
    
    def _get_skills_taught_by_course(self, course_name: str) -> List[str]:
        """获取课程教授的技能"""
        # 直接映射
        if course_name in self.course_skill_mapping:
            return self.course_skill_mapping[course_name]
        
        # 基于课程名称的模糊匹配
        skills = []
        course_lower = course_name.lower()
        
        if 'machine learning' in course_lower or 'ml' in course_lower:
            skills.extend(['machine learning', 'data science'])
        if 'web' in course_lower and 'technolog' in course_lower:
            skills.extend(['web development', 'javascript'])
        if 'mobile' in course_lower or 'app' in course_lower:
            skills.extend(['mobile development'])
        if 'security' in course_lower or 'cyber' in course_lower:
            skills.extend(['cybersecurity'])
        if 'database' in course_lower or 'db' in course_lower:
            skills.extend(['database management', 'sql'])
        if 'programming' in course_lower:
            skills.extend(['programming'])
        if 'data' in course_lower and ('analytic' in course_lower or 'visual' in course_lower):
            skills.extend(['data science', 'data visualization'])
        if 'network' in course_lower:
            skills.extend(['networking'])
        if 'business' in course_lower:
            skills.extend(['business analysis'])
        
        return list(set(skills))  # 去重
    
    def _extract_concepts_from_text(self, text: str, info: Dict):
        """从文本中提取概念"""
        text_lower = text.lower()
        
        # 技能关键词
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
        
        # 技术关键词
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
    
    def _save_individual_kg(self, entity_id: str, name: str, entities: Dict, 
                           relationships: List, graph: nx.MultiDiGraph, 
                           output_dir: str, kg_type: str):
        """保存个体知识图谱"""
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 安全的文件名
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_name = safe_name.replace(' ', '_')[:50]  # 限制长度
        
        base_filename = f"{entity_id}_{safe_name}"
        
        # 保存实体数据
        entities_data = [asdict(entity) for entity in entities.values()]
        with open(os.path.join(output_dir, f"{base_filename}_entities.json"), 'w', encoding='utf-8') as f:
            json.dump(entities_data, f, ensure_ascii=False, indent=2)
        
        # 保存关系数据
        relationships_data = [asdict(rel) for rel in relationships]
        with open(os.path.join(output_dir, f"{base_filename}_relationships.json"), 'w', encoding='utf-8') as f:
            json.dump(relationships_data, f, ensure_ascii=False, indent=2)
        
        # 创建可视化
        self._create_individual_visualization(graph, entity_id, name, output_dir, base_filename, kg_type)
        
        # 保存统计信息
        stats = {
            'entity_id': entity_id,
            'name': name,
            'type': kg_type,
            'total_entities': len(entities),
            'total_relationships': len(relationships),
            'entity_types': dict(Counter(e.entity_type for e in entities.values())),
            'relation_types': dict(Counter(r.relation_type for r in relationships)),
            'created_at': datetime.now().isoformat()
        }
        
        with open(os.path.join(output_dir, f"{base_filename}_stats.json"), 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print(f"  ✅ 已保存: {base_filename} ({len(entities)} 实体, {len(relationships)} 关系)")
    
    def _create_individual_visualization(self, graph: nx.MultiDiGraph, entity_id: str, 
                                       name: str, output_dir: str, base_filename: str, kg_type: str):
        """创建个体知识图谱可视化"""
        
        plt.figure(figsize=(12, 9))
        plt.clf()
        
        # 计算布局
        pos = nx.spring_layout(graph, k=2, iterations=50, seed=42)
        
        # 颜色映射
        node_colors = {
            'STUDENT': '#4ECDC4',      # 青色
            'PROJECT': '#FF6B6B',      # 红色
            'SKILL': '#45B7D1',        # 蓝色
            'MAJOR': '#96CEB4',        # 绿色
            'TECHNOLOGY': '#FFEAA7',   # 黄色
            'COURSE': '#DDA0DD',       # 紫色
            'SUPERVISOR': '#98D8C8',   # 浅绿
            'INTEREST': '#F7DC6F',     # 淡黄
            'PROJECT_EXPERIENCE': '#FFB6C1',  # 粉色
            'WORK_EXPERIENCE': '#F0E68C'      # 卡其色
        }
        
        # 按类型绘制节点
        for node_type, color in node_colors.items():
            nodes = [n for n, d in graph.nodes(data=True) if d.get('type') == node_type]
            if nodes:
                # 中心节点（学生或项目）用大尺寸
                node_size = 1000 if node_type in ['STUDENT', 'PROJECT'] else 400
                alpha = 0.9 if node_type in ['STUDENT', 'PROJECT'] else 0.7
                
                nx.draw_networkx_nodes(graph, pos, nodelist=nodes,
                                     node_color=color, node_size=node_size,
                                     alpha=alpha, edgecolors='black', linewidths=1)
        
        # 绘制不同类型的边
        # 课程教授技能的边（重点突出）
        teaches_edges = [(u, v) for u, v, d in graph.edges(data=True) 
                        if d.get('relation') == 'TEACHES_SKILL']
        if teaches_edges:
            nx.draw_networkx_edges(graph, pos, edgelist=teaches_edges, 
                                 edge_color='purple', width=3, style='dashed',
                                 alpha=0.8)
        
        # 学生完成课程的边
        course_edges = [(u, v) for u, v, d in graph.edges(data=True) 
                       if d.get('relation') == 'COMPLETED_COURSE']
        if course_edges:
            nx.draw_networkx_edges(graph, pos, edgelist=course_edges, 
                                 edge_color='green', width=2, style='solid',
                                 alpha=0.7)
        
        # 学生拥有技能的边
        skill_edges = [(u, v) for u, v, d in graph.edges(data=True) 
                      if d.get('relation') == 'HAS_SKILL']
        if skill_edges:
            nx.draw_networkx_edges(graph, pos, edgelist=skill_edges, 
                                 edge_color='blue', width=2, style='solid',
                                 alpha=0.6)
        
        # 其他边
        other_edges = [(u, v) for u, v, d in graph.edges(data=True) 
                      if d.get('relation') not in ['TEACHES_SKILL', 'COMPLETED_COURSE', 'HAS_SKILL']]
        nx.draw_networkx_edges(graph, pos, edgelist=other_edges, 
                              alpha=0.4, width=1, edge_color='gray')
        
        # 添加标签
        labels = {}
        for node in graph.nodes():
            node_name = graph.nodes[node].get('name', node)
            # 限制标签长度
            if len(node_name) > 15:
                node_name = node_name[:12] + "..."
            labels[node] = node_name
        
        nx.draw_networkx_labels(graph, pos, labels, font_size=9, font_weight='bold')
        
        # 设置标题
        title = f"Enhanced {kg_type.title()} Knowledge Graph\n{name}\n(With Course→Skill Connections)"
        plt.title(title, fontsize=14, fontweight='bold')
        plt.axis('off')
        
        # 添加图例
        legend_elements = []
        for node_type, color in node_colors.items():
            if any(d.get('type') == node_type for n, d in graph.nodes(data=True)):
                legend_elements.append(plt.Line2D([0], [0], marker='o', color='w',
                                                markerfacecolor=color, markersize=8, label=node_type))
        
        if legend_elements:
            plt.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0, 1))
        
        plt.tight_layout()
        
        # 保存图片
        output_file = os.path.join(output_dir, f"{base_filename}_kg.png")
        plt.savefig(output_file, dpi=300, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        plt.close()
    
    def build_all_individual_kgs(self, project_dir: str = "project_md", 
                                student_dir: str = "profile_md"):
        """构建所有个体知识图谱"""
        
        print("🚀 开始构建所有个体知识图谱...")
        
        # 创建输出目录
        os.makedirs("individual_kg/students", exist_ok=True)
        os.makedirs("individual_kg/projects", exist_ok=True)
        
        results = {
            'students': [],
            'projects': [],
            'summary': {}
        }
        
        # 处理所有学生
        print(f"\n👥 处理学生档案 (目录: {student_dir})")
        student_files = []
        for root, dirs, files in os.walk(student_dir):
            for file in files:
                if file.endswith('.md'):
                    student_files.append(os.path.join(root, file))
        
        print(f"找到 {len(student_files)} 个学生档案")
        
        for i, student_file in enumerate(student_files, 1):
            print(f"  [{i}/{len(student_files)}] {os.path.basename(student_file)}")
            try:
                result = self.create_student_knowledge_graph(student_file)
                if result:
                    results['students'].append(result)
            except Exception as e:
                print(f"    ❌ 失败: {e}")
        
        # 处理所有项目
        print(f"\n📋 处理项目文件 (目录: {project_dir})")
        project_files = glob.glob(os.path.join(project_dir, "*.md"))
        print(f"找到 {len(project_files)} 个项目文件")
        
        for i, project_file in enumerate(project_files, 1):
            print(f"  [{i}/{len(project_files)}] {os.path.basename(project_file)}")
            try:
                result = self.create_project_knowledge_graph(project_file)
                if result:
                    results['projects'].append(result)
            except Exception as e:
                print(f"    ❌ 失败: {e}")
        
        # 生成总结
        results['summary'] = {
            'total_students': len(results['students']),
            'total_projects': len(results['projects']),
            'total_student_entities': sum(r['entities'] for r in results['students']),
            'total_student_relationships': sum(r['relationships'] for r in results['students']),
            'total_project_entities': sum(r['entities'] for r in results['projects']),
            'total_project_relationships': sum(r['relationships'] for r in results['projects']),
            'created_at': datetime.now().isoformat()
        }
        
        # 保存总结报告
        with open("individual_kg/summary_report.json", 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # 打印统计信息
        print(f"\n📊 个体知识图谱构建完成!")
        print(f"  学生图谱: {results['summary']['total_students']} 个")
        print(f"  项目图谱: {results['summary']['total_projects']} 个")
        print(f"  学生实体总数: {results['summary']['total_student_entities']}")
        print(f"  学生关系总数: {results['summary']['total_student_relationships']}")
        print(f"  项目实体总数: {results['summary']['total_project_entities']}")
        print(f"  项目关系总数: {results['summary']['total_project_relationships']}")
        print(f"\n📂 输出目录:")
        print(f"  学生KG: individual_kg/students/")
        print(f"  项目KG: individual_kg/projects/")
        print(f"  总结报告: individual_kg/summary_report.json")
        
        return results

def main():
    """主函数"""
    print("🎯 个体知识图谱构建系统")
    print("=" * 50)
    
    builder = IndividualKnowledgeGraphBuilder()
    builder.build_all_individual_kgs()
    
    print("\n🎉 所有个体知识图谱构建完成!")

if __name__ == "__main__":
    main()
