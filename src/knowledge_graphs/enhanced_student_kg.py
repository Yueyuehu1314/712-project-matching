#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版学生知识图谱生成器

新的多层结构：
1. 学生 (中心节点)
2. 学生的属性：
   - 专业 (STUDIED_MAJOR)
   - 修过的课程 (COMPLETED_COURSE)
   - 项目经历 (PARTICIPATED_IN_PROJECT)
   - 工作经历 (WORKED_AT)
   - 研究兴趣 (INTERESTED_IN)
3. 课程的技能：
   - 课程 → 技能 (TEACHES_SKILL) - 从IN20/IN27数据提取
4. 项目经历的技能：
   - 项目经历 → 技能 (REQUIRES_SKILL) - 从项目描述提取
5. 技能层：
   - 学生通过课程获得的技能
   - 学生通过项目获得的技能
   - 学生自学的技能
"""

import os
import json
import glob
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict, Counter
import re

@dataclass
class EnhancedEntity:
    """增强版实体"""
    id: str
    name: str
    entity_type: str
    properties: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}

@dataclass
class EnhancedRelationship:
    """增强版关系"""
    source_id: str
    target_id: str
    relation_type: str
    weight: float = 1.0
    properties: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}

class EnhancedStudentKGBuilder:
    """增强版学生知识图谱构建器"""
    
    def __init__(self, in20_data_path: str = None, in27_data_path: str = None):
        """
        初始化
        
        Args:
            in20_data_path: IN20数据路径（JSON格式）
            in27_data_path: IN27数据路径（JSON格式）
        """
        self.in20_data = None
        self.in27_data = None
        
        # 加载IN20和IN27数据以获取课程-技能映射
        if in20_data_path and os.path.exists(in20_data_path):
            with open(in20_data_path, 'r', encoding='utf-8') as f:
                self.in20_data = json.load(f)
                print(f"✅ 加载IN20数据: {len(self.in20_data.get('nodes', []))} 节点")
        
        if in27_data_path and os.path.exists(in27_data_path):
            with open(in27_data_path, 'r', encoding='utf-8') as f:
                self.in27_data = json.load(f)
                print(f"✅ 加载IN27数据")
        
        # 构建课程-技能映射
        self.course_skill_mapping = self._build_course_skill_mapping()
        
        # 实体类型定义
        self.entity_types = {
            'STUDENT': 'Student',
            'MAJOR': 'Major',
            'COURSE': 'Course',
            'SKILL': 'Skill',
            'PROJECT_EXPERIENCE': 'ProjectExperience',
            'WORK_EXPERIENCE': 'WorkExperience',
            'INTEREST': 'Interest'
        }
        
        # 关系类型定义
        self.relation_types = {
            'STUDIED_MAJOR': 'studied_major',
            'COMPLETED_COURSE': 'completed_course',
            'TEACHES_SKILL': 'teaches_skill',  # 课程教授技能
            'PARTICIPATED_IN_PROJECT': 'participated_in_project',
            'REQUIRES_SKILL': 'requires_skill',  # 项目需要技能
            'WORKED_AT': 'worked_at',
            'HAS_SKILL': 'has_skill',  # 学生拥有技能
            'INTERESTED_IN': 'interested_in'
        }
    
    def _build_course_skill_mapping(self) -> Dict[str, List[str]]:
        """从IN20/IN27数据构建课程-技能映射"""
        mapping = {}
        
        if self.in20_data:
            # 从IN20数据提取 UNIT → SKILL 映射
            edges = self.in20_data.get('edges', [])
            for edge in edges:
                if edge.get('type') == 'TAUGHT_IN':
                    skill = edge.get('source')  # SKILL节点
                    unit = edge.get('target')    # UNIT节点
                    
                    if unit not in mapping:
                        mapping[unit] = []
                    mapping[unit].append(skill)
        
        # 添加一些通用的课程-技能映射（备用）
        default_mapping = {
            'IFN564': ['Machine Learning', 'Data Science', 'Artificial Intelligence'],
            'IFN555': ['Programming', 'Problem Solving', 'Algorithms'],
            'IFN556': ['Object-Oriented Programming', 'Software Design'],
            'IFN619': ['Data Visualization', 'Statistical Analysis', 'Data Science'],
            'IFN632': ['Advanced Analytics', 'Machine Learning', 'Data Mining'],
            'IFN551': ['Computer Systems', 'Hardware Understanding'],
            'IFN552': ['Systems Analysis', 'System Design'],
            'IFN553': ['Networking', 'Network Security'],
            'IFN563': ['Algorithms', 'Computational Complexity'],
            'IFN565': ['Advanced Programming', 'Software Engineering'],
            'IFN666': ['Web Development', 'JavaScript', 'HTML/CSS'],
            'IFN670': ['Mobile Development', 'App Development'],
            'IFN623': ['Cybersecurity', 'Network Security']
        }
        
        # 合并默认映射（如果还没有的话）
        for course, skills in default_mapping.items():
            if course not in mapping:
                mapping[course] = skills
        
        print(f"📚 构建课程-技能映射: {len(mapping)} 个课程")
        return mapping
    
    def _extract_course_code(self, course_name: str) -> str:
        """从课程名称提取课程代码"""
        # 提取如 IFN555, IFN619 等课程代码
        match = re.search(r'(IFN|CAB|IAB|ITN|INN|EGB)\d{3}', course_name.upper())
        if match:
            return match.group(0)
        return None
    
    def _get_skills_for_course(self, course_name: str) -> List[str]:
        """获取课程教授的技能"""
        skills = []
        
        # 尝试提取课程代码
        course_code = self._extract_course_code(course_name)
        
        # 1. 从映射中查找
        if course_code and course_code in self.course_skill_mapping:
            skills.extend(self.course_skill_mapping[course_code])
        
        # 2. 从完整课程名称查找
        if course_name in self.course_skill_mapping:
            skills.extend(self.course_skill_mapping[course_name])
        
        # 3. 基于关键词的推断
        course_lower = course_name.lower()
        if 'machine learning' in course_lower or 'ml' in course_lower:
            skills.extend(['Machine Learning', 'Data Science'])
        if 'web' in course_lower:
            skills.extend(['Web Development'])
        if 'mobile' in course_lower or 'app' in course_lower:
            skills.extend(['Mobile Development'])
        if 'security' in course_lower or 'cyber' in course_lower:
            skills.extend(['Cybersecurity'])
        if 'database' in course_lower:
            skills.extend(['Database Management', 'SQL'])
        if 'programming' in course_lower:
            skills.extend(['Programming'])
        if 'data' in course_lower and 'visual' in course_lower:
            skills.extend(['Data Visualization'])
        if 'network' in course_lower:
            skills.extend(['Networking'])
        
        return list(set(skills))  # 去重
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """从文本中提取技能关键词"""
        skills = []
        text_lower = text.lower()
        
        # 技能关键词库
        skill_keywords = {
            'Machine Learning': ['machine learning', 'ml', 'deep learning'],
            'Data Science': ['data science', 'data analysis'],
            'Python': ['python'],
            'Java': ['java'],
            'JavaScript': ['javascript', 'js'],
            'Web Development': ['web development', 'web app', 'html', 'css'],
            'Mobile Development': ['mobile', 'android', 'ios', 'app development'],
            'Cybersecurity': ['security', 'cybersecurity', 'encryption'],
            'Database Management': ['database', 'sql', 'mysql', 'mongodb'],
            'Networking': ['network', 'tcp/ip', 'wifi'],
            'Natural Language Processing': ['nlp', 'natural language'],
            'Computer Vision': ['computer vision', 'image processing'],
            'API Development': ['api', 'rest', 'restful'],
            'Cloud Computing': ['cloud', 'aws', 'azure', 'gcp']
        }
        
        for skill, keywords in skill_keywords.items():
            if any(kw in text_lower for kw in keywords):
                skills.append(skill)
        
        return list(set(skills))
    
    def create_enhanced_student_kg(self, student_file: str, output_dir: str = "outputs/knowledge_graphs/individual/enhanced_student_kg"):
        """创建增强版学生知识图谱"""
        
        if not os.path.exists(student_file):
            print(f"❌ 学生文件不存在: {student_file}")
            return None
        
        # 解析学生信息
        with open(student_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        student_info = self._parse_student_content(content)
        student_id = student_info.get('student_id', 'unknown')
        student_name = student_info.get('name', 'Unknown Student')
        
        print(f"🎓 创建增强学生知识图谱: {student_name} ({student_id})")
        
        # 创建图结构
        entities = {}
        relationships = []
        G = nx.MultiDiGraph()
        
        # ============= 第1层: 学生主实体 =============
        student_entity_id = f"student_{student_id}"
        entities[student_entity_id] = EnhancedEntity(
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
        G.add_node(student_entity_id, name=student_name, type='STUDENT',
                   **entities[student_entity_id].properties)
        
        # ============= 第2层: 专业 =============
        major = student_info.get('major', '')
        if major:
            major_id = f"major_{major.replace(' ', '_').lower()}"
            if major_id not in entities:
                entities[major_id] = EnhancedEntity(major_id, major, 'MAJOR')
                G.add_node(major_id, name=major, type='MAJOR')
            
            rel = EnhancedRelationship(student_entity_id, major_id, 'STUDIED_MAJOR')
            relationships.append(rel)
            G.add_edge(student_entity_id, major_id, relation='STUDIED_MAJOR', weight=1.0)
        
        # ============= 第2层: 课程 + 第3层: 课程→技能 =============
        course_taught_skills = set()  # 记录通过课程获得的技能
        
        for course in student_info.get('courses', []):
            course_clean = course.strip()
            course_id = f"course_{course_clean.replace(' ', '_').lower().replace('/', '_')}"
            
            # 添加课程节点
            if course_id not in entities:
                entities[course_id] = EnhancedEntity(course_id, course_clean, 'COURSE')
                G.add_node(course_id, name=course_clean, type='COURSE')
            
            # 学生完成课程
            rel = EnhancedRelationship(student_entity_id, course_id, 'COMPLETED_COURSE', weight=1.0)
            relationships.append(rel)
            G.add_edge(student_entity_id, course_id, relation='COMPLETED_COURSE', weight=1.0)
            
            # 获取课程教授的技能
            taught_skills = self._get_skills_for_course(course_clean)
            
            for skill in taught_skills:
                skill_id = f"skill_{skill.replace(' ', '_').lower()}"
                
                # 添加技能节点
                if skill_id not in entities:
                    entities[skill_id] = EnhancedEntity(skill_id, skill, 'SKILL')
                    G.add_node(skill_id, name=skill, type='SKILL')
                
                # 课程 → 技能
                rel = EnhancedRelationship(course_id, skill_id, 'TEACHES_SKILL', weight=0.9)
                relationships.append(rel)
                G.add_edge(course_id, skill_id, relation='TEACHES_SKILL', weight=0.9)
                
                # 学生通过课程 → 技能
                if not G.has_edge(student_entity_id, skill_id):
                    rel = EnhancedRelationship(student_entity_id, skill_id, 'HAS_SKILL', 
                                              weight=0.8, 
                                              properties={'source': 'course'})
                    relationships.append(rel)
                    G.add_edge(student_entity_id, skill_id, relation='HAS_SKILL', weight=0.8, source='course')
                
                course_taught_skills.add(skill_id)
        
        # ============= 第2层: 项目经历 + 第3层: 项目→技能 =============
        project_skills = set()
        
        for i, project_desc in enumerate(student_info.get('projects', [])):
            project_exp_id = f"project_exp_{student_id}_{i}"
            
            # 添加项目经历节点
            project_name = project_desc[:50] + "..." if len(project_desc) > 50 else project_desc
            entities[project_exp_id] = EnhancedEntity(
                project_exp_id,
                project_name,
                'PROJECT_EXPERIENCE',
                {'description': project_desc, 'index': i}
            )
            G.add_node(project_exp_id, name=project_name, type='PROJECT_EXPERIENCE')
            
            # 学生参与项目
            rel = EnhancedRelationship(student_entity_id, project_exp_id, 'PARTICIPATED_IN_PROJECT', weight=1.0)
            relationships.append(rel)
            G.add_edge(student_entity_id, project_exp_id, relation='PARTICIPATED_IN_PROJECT', weight=1.0)
            
            # 从项目描述提取技能
            extracted_skills = self._extract_skills_from_text(project_desc)
            
            for skill in extracted_skills:
                skill_id = f"skill_{skill.replace(' ', '_').lower()}"
                
                # 添加技能节点
                if skill_id not in entities:
                    entities[skill_id] = EnhancedEntity(skill_id, skill, 'SKILL')
                    G.add_node(skill_id, name=skill, type='SKILL')
                
                # 项目 → 技能
                rel = EnhancedRelationship(project_exp_id, skill_id, 'REQUIRES_SKILL', weight=0.7)
                relationships.append(rel)
                G.add_edge(project_exp_id, skill_id, relation='REQUIRES_SKILL', weight=0.7)
                
                # 学生通过项目 → 技能
                if not G.has_edge(student_entity_id, skill_id):
                    rel = EnhancedRelationship(student_entity_id, skill_id, 'HAS_SKILL',
                                              weight=0.75,
                                              properties={'source': 'project'})
                    relationships.append(rel)
                    G.add_edge(student_entity_id, skill_id, relation='HAS_SKILL', weight=0.75, source='project')
                
                project_skills.add(skill_id)
        
        # ============= 第2层: 直接技能（自学/其他途径） =============
        for skill in student_info.get('skills', []):
            skill_clean = skill.strip()
            skill_id = f"skill_{skill_clean.replace(' ', '_').lower().replace('/', '_').replace('(', '').replace(')', '')}"
            
            # 添加技能节点
            if skill_id not in entities:
                entities[skill_id] = EnhancedEntity(skill_id, skill_clean, 'SKILL')
                G.add_node(skill_id, name=skill_clean, type='SKILL')
            
            # 如果这个技能既不是通过课程也不是通过项目获得，则标记为"自学"
            if skill_id not in course_taught_skills and skill_id not in project_skills:
                if not G.has_edge(student_entity_id, skill_id):
                    rel = EnhancedRelationship(student_entity_id, skill_id, 'HAS_SKILL',
                                              weight=0.6,
                                              properties={'source': 'self-taught'})
                    relationships.append(rel)
                    G.add_edge(student_entity_id, skill_id, relation='HAS_SKILL', weight=0.6, source='self-taught')
        
        # ============= 第2层: 研究兴趣 =============
        for interest in student_info.get('interests', []):
            interest_id = f"interest_{interest.replace(' ', '_').lower().replace('-', '_')}"
            
            if interest_id not in entities:
                entities[interest_id] = EnhancedEntity(interest_id, interest, 'INTEREST')
                G.add_node(interest_id, name=interest, type='INTEREST')
            
            rel = EnhancedRelationship(student_entity_id, interest_id, 'INTERESTED_IN', weight=1.0)
            relationships.append(rel)
            G.add_edge(student_entity_id, interest_id, relation='INTERESTED_IN', weight=1.0)
        
        # ============= 保存结果 =============
        self._save_enhanced_kg(student_entity_id, student_name, entities, relationships, G, output_dir)
        
        # 统计信息
        stats = {
            'total_entities': len(entities),
            'total_relationships': len(relationships),
            'courses': len([e for e in entities.values() if e.entity_type == 'COURSE']),
            'skills': len([e for e in entities.values() if e.entity_type == 'SKILL']),
            'projects': len([e for e in entities.values() if e.entity_type == 'PROJECT_EXPERIENCE']),
            'interests': len([e for e in entities.values() if e.entity_type == 'INTEREST']),
            'skills_from_courses': len(course_taught_skills),
            'skills_from_projects': len(project_skills)
        }
        
        print(f"  📊 统计: {stats['total_entities']} 实体, {stats['total_relationships']} 关系")
        print(f"     - 课程: {stats['courses']}, 技能: {stats['skills']}, 项目: {stats['projects']}")
        
        return stats
    
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
            if '**Name**:' in line or 'Name:' in line:
                info['name'] = line.split(':')[-1].strip().replace('**', '')
            elif '**Student ID**:' in line or 'Student ID:' in line:
                info['student_id'] = line.split(':')[-1].strip().replace('**', '')
            elif '**Major**:' in line or 'Major:' in line:
                info['major'] = line.split(':')[-1].strip().replace('**', '')
            elif '**Year**:' in line or 'Year:' in line:
                info['year'] = line.split(':')[-1].strip().replace('**', '')
        
        # 提取列表信息和项目
        current_section = None
        current_project_title = None
        current_project_desc = []
        
        for i, line in enumerate(lines):
            if '## Completed Courses' in line or '## Completed Units' in line:
                # 保存之前的项目
                if current_project_title and current_project_desc:
                    info['projects'].append(f"{current_project_title}: {' '.join(current_project_desc)}")
                    current_project_title = None
                    current_project_desc = []
                current_section = 'courses'
            elif '## Technical Skills' in line or '## Skills' in line:
                if current_project_title and current_project_desc:
                    info['projects'].append(f"{current_project_title}: {' '.join(current_project_desc)}")
                    current_project_title = None
                    current_project_desc = []
                current_section = 'skills'
            elif '## Interests' in line or '## Research Interests' in line:
                if current_project_title and current_project_desc:
                    info['projects'].append(f"{current_project_title}: {' '.join(current_project_desc)}")
                    current_project_title = None
                    current_project_desc = []
                current_section = 'interests'
            elif '## Previous Projects' in line or '## Project Experience' in line:
                current_section = 'projects'
            elif line.startswith('##') and not line.startswith('###'):
                # 遇到其他二级标题，保存项目并清空section
                if current_project_title and current_project_desc:
                    info['projects'].append(f"{current_project_title}: {' '.join(current_project_desc)}")
                    current_project_title = None
                    current_project_desc = []
                current_section = None
            elif current_section == 'projects' and line.strip().startswith('###'):
                # 保存之前的项目
                if current_project_title and current_project_desc:
                    info['projects'].append(f"{current_project_title}: {' '.join(current_project_desc)}")
                # 开始新项目
                current_project_title = line.strip().lstrip('### ').strip()
                current_project_desc = []
            elif current_section == 'projects' and current_project_title and line.strip() and not line.startswith('#'):
                # 项目描述行
                current_project_desc.append(line.strip())
            elif current_section in ['courses', 'skills', 'interests'] and line.strip().startswith('-'):
                item = line.strip().lstrip('- ').strip()
                if item:
                    info[current_section].append(item)
        
        # 保存最后一个项目
        if current_project_title and current_project_desc:
            info['projects'].append(f"{current_project_title}: {' '.join(current_project_desc)}")
        
        return info
    
    def _save_enhanced_kg(self, entity_id: str, name: str, entities: Dict,
                         relationships: List, graph: nx.MultiDiGraph, output_dir: str):
        """保存增强版知识图谱"""
        
        os.makedirs(output_dir, exist_ok=True)
        
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_name = safe_name.replace(' ', '_')[:50]
        base_filename = f"{entity_id}_{safe_name}"
        
        # 保存JSON数据
        kg_data = {
            'entities': [asdict(e) for e in entities.values()],
            'relationships': [asdict(r) for r in relationships],
            'metadata': {
                'student_id': entity_id,
                'student_name': name,
                'created_at': datetime.now().isoformat(),
                'version': '2.0_enhanced'
            }
        }
        
        json_path = os.path.join(output_dir, f"{base_filename}_enhanced_kg.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(kg_data, f, ensure_ascii=False, indent=2)
        
        # 创建可视化
        self._create_enhanced_visualization(graph, entity_id, name, output_dir, base_filename)
        
        print(f"  ✅ 已保存: {base_filename}")
    
    def _create_enhanced_visualization(self, graph: nx.MultiDiGraph, entity_id: str,
                                      name: str, output_dir: str, base_filename: str,
                                      show_edge_weights: bool = True):
        """
        创建增强版可视化
        
        Args:
            show_edge_weights: 是否显示边的权重标签
        """
        
        plt.figure(figsize=(16, 12))
        plt.clf()
        
        # 使用spring_layout但增加节点间距
        pos = nx.spring_layout(graph, k=3, iterations=100, seed=42)
        
        # 颜色映射
        node_colors = {
            'STUDENT': '#4ECDC4',           # 青色 - 学生
            'MAJOR': '#96CEB4',             # 绿色 - 专业
            'COURSE': '#DDA0DD',            # 紫色 - 课程
            'SKILL': '#45B7D1',             # 蓝色 - 技能
            'PROJECT_EXPERIENCE': '#FF6B6B', # 红色 - 项目经历
            'INTEREST': '#F7DC6F'           # 黄色 - 兴趣
        }
        
        # 按类型绘制节点
        for node_type, color in node_colors.items():
            nodes = [n for n, d in graph.nodes(data=True) if d.get('type') == node_type]
            if nodes:
                if node_type == 'STUDENT':
                    node_size = 2000
                    alpha = 1.0
                elif node_type in ['COURSE', 'PROJECT_EXPERIENCE']:
                    node_size = 800
                    alpha = 0.85
                else:
                    node_size = 600
                    alpha = 0.75
                
                nx.draw_networkx_nodes(graph, pos, nodelist=nodes,
                                     node_color=color, node_size=node_size,
                                     alpha=alpha, edgecolors='black', linewidths=2)
        
        # 绘制不同类型的边
        edge_styles = {
            'TEACHES_SKILL': {'color': 'purple', 'width': 3, 'style': 'dashed', 'alpha': 0.9},
            'REQUIRES_SKILL': {'color': 'red', 'width': 2.5, 'style': 'dotted', 'alpha': 0.8},
            'COMPLETED_COURSE': {'color': 'green', 'width': 2, 'style': 'solid', 'alpha': 0.7},
            'PARTICIPATED_IN_PROJECT': {'color': 'orange', 'width': 2, 'style': 'solid', 'alpha': 0.7},
            'HAS_SKILL': {'color': 'blue', 'width': 1.5, 'style': 'solid', 'alpha': 0.6},
            'STUDIED_MAJOR': {'color': 'darkgreen', 'width': 2.5, 'style': 'solid', 'alpha': 0.8},
            'INTERESTED_IN': {'color': 'gold', 'width': 1.5, 'style': 'solid', 'alpha': 0.6}
        }
        
        for relation_type, style in edge_styles.items():
            edges = [(u, v) for u, v, d in graph.edges(data=True) if d.get('relation') == relation_type]
            if edges:
                nx.draw_networkx_edges(graph, pos, edgelist=edges,
                                     edge_color=style['color'],
                                     width=style['width'],
                                     style=style['style'],
                                     alpha=style['alpha'],
                                     arrows=True,
                                     arrowsize=15)
        
        # 添加标签
        labels = {}
        for node in graph.nodes():
            node_name = graph.nodes[node].get('name', node)
            if len(node_name) > 20:
                node_name = node_name[:17] + "..."
            labels[node] = node_name
        
        nx.draw_networkx_labels(graph, pos, labels, font_size=8, font_weight='bold')
        
        # 添加边的权重标签（如果启用）
        if show_edge_weights:
            edge_labels = {}
            for u, v, data in graph.edges(data=True):
                weight = data.get('weight', 1.0)
                # 只显示权重不为1.0的边，避免图过于拥挤
                if weight != 1.0:
                    edge_labels[(u, v)] = f"{weight:.2f}"
            
            if edge_labels:
                nx.draw_networkx_edge_labels(graph, pos, edge_labels, 
                                            font_size=6, font_color='darkred',
                                            bbox=dict(boxstyle='round,pad=0.3', 
                                                     facecolor='white', 
                                                     edgecolor='none', 
                                                     alpha=0.7))
        
        # 标题
        plt.title(f"Student Knowledge Graph\n{name}", fontsize=16, fontweight='bold', pad=20)
        plt.axis('off')
        
        # 图例 - 分为节点和边两部分
        # 节点类型图例
        node_legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#4ECDC4', 
                      markersize=12, label='Student', markeredgecolor='black', markeredgewidth=1.5),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#96CEB4',
                      markersize=10, label='Major', markeredgecolor='black', markeredgewidth=1.5),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#DDA0DD',
                      markersize=10, label='Course', markeredgecolor='black', markeredgewidth=1.5),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#45B7D1',
                      markersize=10, label='Skill', markeredgecolor='black', markeredgewidth=1.5),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#FF6B6B',
                      markersize=10, label='Project Experience', markeredgecolor='black', markeredgewidth=1.5),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#F7DC6F',
                      markersize=10, label='Interest', markeredgecolor='black', markeredgewidth=1.5)
        ]
        
        # 边类型图例
        edge_legend_elements = [
            plt.Line2D([0], [0], color='darkgreen', linewidth=2.5, linestyle='-',
                      label='Student → Major'),
            plt.Line2D([0], [0], color='green', linewidth=2, linestyle='-',
                      label='Student → Course'),
            plt.Line2D([0], [0], color='purple', linewidth=3, linestyle='--',
                      label='Course → Skill'),
            plt.Line2D([0], [0], color='orange', linewidth=2, linestyle='-',
                      label='Student → Project'),
            plt.Line2D([0], [0], color='red', linewidth=2.5, linestyle=':',
                      label='Project → Skill'),
            plt.Line2D([0], [0], color='blue', linewidth=1.5, linestyle='-',
                      label='Student → Skill'),
            plt.Line2D([0], [0], color='gold', linewidth=1.5, linestyle='-',
                      label='Student → Interest')
        ]
        
        # 创建两个图例
        legend1 = plt.legend(handles=node_legend_elements, loc='upper left', 
                            fontsize=9, title='Node Types', title_fontsize=10, framealpha=0.9)
        plt.gca().add_artist(legend1)  # 添加第一个图例
        
        plt.legend(handles=edge_legend_elements, loc='upper right', 
                  fontsize=8, title='Relationships', title_fontsize=10, framealpha=0.9)
        
        plt.tight_layout()
        
        # 保存
        output_file = os.path.join(output_dir, f"{base_filename}_kg.png")
        plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
    
    def build_all_enhanced_student_kgs(self, student_dir: str = "data/processed/profiles_md"):
        """批量构建所有学生的增强知识图谱"""
        
        print("🚀 开始批量构建增强学生知识图谱...")
        
        # 查找所有学生文件
        student_files = []
        for root, dirs, files in os.walk(student_dir):
            for file in files:
                if file.endswith('.md') and not file.startswith('.'):
                    student_files.append(os.path.join(root, file))
        
        print(f"找到 {len(student_files)} 个学生档案")
        
        results = []
        for i, student_file in enumerate(student_files, 1):
            print(f"\n[{i}/{len(student_files)}] {os.path.basename(student_file)}")
            try:
                result = self.create_enhanced_student_kg(student_file)
                if result:
                    results.append(result)
            except Exception as e:
                print(f"  ❌ 失败: {e}")
        
        # 生成总结
        summary = {
            'total_students': len(results),
            'total_entities': sum(r['total_entities'] for r in results),
            'total_relationships': sum(r['total_relationships'] for r in results),
            'avg_skills_per_student': sum(r['skills'] for r in results) / len(results) if results else 0,
            'created_at': datetime.now().isoformat()
        }
        
        output_dir = "outputs/knowledge_graphs/individual/enhanced_student_kg"
        with open(os.path.join(output_dir, 'summary.json'), 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 完成! 共处理 {len(results)} 个学生")
        print(f"   总实体: {summary['total_entities']}, 总关系: {summary['total_relationships']}")
        
        return results

def main():
    """主函数"""
    print("=" * 60)
    print("增强版学生知识图谱生成器")
    print("=" * 60)
    
    # 初始化（可选加载IN20/IN27数据）
    in20_path = "outputs/knowledge_graphs/enhanced_in20_in27/AI-Based Human Activity Recognition Using WiFi Channel State Information/AI-Based Human Activity Recognition Using WiFi Channel State Information_enhanced_kg.json"
    
    builder = EnhancedStudentKGBuilder(in20_data_path=in20_path if os.path.exists(in20_path) else None)
    
    # 批量构建
    builder.build_all_enhanced_student_kgs()
    
    print("\n🎉 所有增强学生知识图谱构建完成!")

if __name__ == "__main__":
    main()

