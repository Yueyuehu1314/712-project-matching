#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目知识图谱构建系统
将项目文件和学生档案转换为知识图谱，支持分析和可视化
"""

import os
import json
import re
import glob
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict, Counter

try:
    import networkx as nx
    import matplotlib.pyplot as plt
    import pandas as pd
    import numpy as np
except ImportError as e:
    print(f"警告: 缺少依赖库 {e}")
    print("请安装: pip install networkx matplotlib pandas numpy")
    nx = None


@dataclass
class Entity:
    """知识图谱实体"""
    id: str
    name: str
    entity_type: str
    properties: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}


@dataclass
class Relationship:
    """知识图谱关系"""
    source_id: str
    target_id: str
    relation_type: str
    weight: float = 1.0
    properties: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}


class ProjectKnowledgeGraphBuilder:
    """项目知识图谱构建器"""
    
    def __init__(self):
        self.entities = {}  # entity_id -> Entity
        self.relationships = []  # List[Relationship]
        self.graph = nx.MultiDiGraph() if nx else None
        
        # 实体类型定义
        self.entity_types = {
            'PROJECT': 'Project',
            'STUDENT': 'Student',
            'SKILL': 'Skill', 
            'COURSE': 'Course',
            'MAJOR': 'Major',
            'TECHNOLOGY': 'Technology',
            'SUPERVISOR': 'Supervisor',
            'COMPANY': 'Company',
            'INTEREST': 'Interest'
        }
        
        # 关系类型定义
        self.relation_types = {
            'MATCHES': 'matches',
            'HAS_SKILL': 'has_skill',
            'COMPLETED_COURSE': 'completed_course',
            'STUDIED_MAJOR': 'studied_major',
            'REQUIRES_SKILL': 'requires_skill',
            'USES_TECHNOLOGY': 'uses_technology',
            'SUPERVISED_BY': 'supervised_by',
            'WORKED_AT': 'worked_at',
            'INTERESTED_IN': 'interested_in'
        }
    
    def add_entity(self, entity_id: str, name: str, entity_type: str, properties: Dict = None) -> Entity:
        """添加实体"""
        if properties is None:
            properties = {}
            
        entity = Entity(
            id=entity_id,
            name=name,
            entity_type=entity_type,
            properties=properties
        )
        
        self.entities[entity_id] = entity
        
        # 添加到NetworkX图中
        if self.graph:
            self.graph.add_node(entity_id, 
                               name=name, 
                               type=entity_type, 
                               **properties)
        
        return entity
    
    def add_relationship(self, source_id: str, target_id: str, relation_type: str, 
                        weight: float = 1.0, properties: Dict = None) -> Relationship:
        """添加关系"""
        if properties is None:
            properties = {}
            
        relationship = Relationship(
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            weight=weight,
            properties=properties
        )
        
        self.relationships.append(relationship)
        
        # 添加到NetworkX图中
        if self.graph:
            self.graph.add_edge(source_id, target_id, 
                               relation=relation_type, 
                               weight=weight,
                               **properties)
        
        return relationship
    
    def build_from_files(self, project_dir: str = "project_md", 
                        student_dir: str = "profile_md"):
        """从文件构建知识图谱"""
        print("🔄 开始构建项目知识图谱...")
        print(f"📂 项目目录: {project_dir}")
        print(f"👥 学生目录: {student_dir}")
        
        # 检查目录是否存在
        if not os.path.exists(project_dir):
            print(f"❌ 错误: 项目目录不存在 - {project_dir}")
            return
        if not os.path.exists(student_dir):
            print(f"❌ 错误: 学生目录不存在 - {student_dir}")
            return
        
        print("✅ 目录检查通过")
        
        # 处理项目文件
        print("📁 开始处理项目文件...")
        try:
            self._process_projects(project_dir)
            print("✅ 项目文件处理完成")
        except Exception as e:
            print(f"❌ 项目文件处理失败: {e}")
            return
        
        # 处理学生档案
        print("👥 开始处理学生档案...")
        try:
            self._process_students(student_dir)
            print("✅ 学生档案处理完成")
        except Exception as e:
            print(f"❌ 学生档案处理失败: {e}")
            return
        
        # 构建匹配关系
        print("🔗 开始构建匹配关系...")
        try:
            self._build_matches()
            print("✅ 匹配关系构建完成")
        except Exception as e:
            print(f"❌ 匹配关系构建失败: {e}")
            return
        
        print("✅ 知识图谱构建完成！")
        self._print_statistics()
    
    def _process_projects(self, project_dir: str):
        """处理项目文件"""
        print(f"🔍 扫描项目目录: {project_dir}")
        project_files = glob.glob(os.path.join(project_dir, "*.md"))
        print(f"📁 找到 {len(project_files)} 个项目文件")
        
        if not project_files:
            print("⚠️ 没有找到项目文件")
            return
        
        for i, project_file in enumerate(project_files, 1):
            project_name = os.path.splitext(os.path.basename(project_file))[0]
            print(f"  [{i}/{len(project_files)}] 处理项目: {project_name}")
            
            try:
                print(f"    📖 读取文件: {project_file}")
                with open(project_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"    📄 文件长度: {len(content)} 字符")
                
                print("    🔍 解析项目内容...")
                project_info = self._parse_project_content(content)
                project_id = f"project_{project_name.replace(' ', '_')}"
                
                print(f"    📝 项目标题: {project_info.get('title', '未找到')}")
                print(f"    🎓 专业要求: {project_info.get('majors', [])}")
                print(f"    🔧 技能要求: {project_info.get('skills', [])}")
                
                # 添加项目实体
                self.add_entity(
                    project_id,
                    project_info.get('title', project_name),
                    'PROJECT',
                    {
                        'description': project_info.get('description', ''),
                        'majors': project_info.get('majors', []),
                        'supervisor': project_info.get('supervisor', ''),
                        'file_path': project_file
                    }
                )
                
                print("    🔗 添加相关概念...")
                # 添加相关概念
                self._add_project_concepts(project_id, project_info)
                print(f"    ✅ 项目 {project_name} 处理完成")
                
            except Exception as e:
                print(f"    ❌ 处理失败: {e}")
                import traceback
                traceback.print_exc()
    
    def _process_students(self, student_dir: str):
        """处理学生档案"""
        student_files = []
        for root, dirs, files in os.walk(student_dir):
            for file in files:
                if file.endswith('.md'):
                    student_files.append(os.path.join(root, file))
        
        for i, student_file in enumerate(student_files, 1):
            print(f"  [{i}/{len(student_files)}] {os.path.basename(student_file)}")
            
            try:
                with open(student_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                student_info = self._parse_student_content(content)
                student_id = f"student_{student_info.get('student_id', 'unknown')}"
                
                # 添加学生实体
                self.add_entity(
                    student_id,
                    student_info.get('name', 'Unknown Student'),
                    'STUDENT',
                    {
                        'student_id': student_info.get('student_id', ''),
                        'major': student_info.get('major', ''),
                        'year': student_info.get('year', ''),
                        'file_path': student_file
                    }
                )
                
                # 添加相关概念
                self._add_student_concepts(student_id, student_info)
                
            except Exception as e:
                print(f"    ❌ 处理失败: {e}")
    
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
            if 'Information Technology major' in line:
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 3:
                        majors_text = parts[-2].strip()
                        info['majors'] = [m.strip() for m in majors_text.split(',')]
                break
        
        # 提取导师
        for line in lines:
            if 'Academic Supervisor' in line:
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 3:
                        info['supervisor'] = parts[-2].strip()
                break
        
        # 提取描述
        description_lines = []
        in_description = False
        for line in lines:
            if 'Brief description' in line:
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
            elif line.startswith('##'):
                current_section = None
            elif current_section and line.strip().startswith('-'):
                item = line.strip().lstrip('- ').strip()
                if item:
                    info[current_section].append(item)
        
        return info
    
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
    
    def _add_project_concepts(self, project_id: str, project_info: Dict):
        """为项目添加相关概念"""
        # 添加专业
        for major in project_info.get('majors', []):
            major_id = f"major_{major.replace(' ', '_').lower()}"
            if major_id not in self.entities:
                self.add_entity(major_id, major, 'MAJOR')
            self.add_relationship(project_id, major_id, 'REQUIRES_MAJOR')
        
        # 添加技能
        for skill in project_info.get('skills', []):
            skill_id = f"skill_{skill.replace(' ', '_').lower()}"
            if skill_id not in self.entities:
                self.add_entity(skill_id, skill, 'SKILL')
            self.add_relationship(project_id, skill_id, 'REQUIRES_SKILL')
        
        # 添加技术
        for tech in project_info.get('technologies', []):
            tech_id = f"tech_{tech.replace(' ', '_').lower()}"
            if tech_id not in self.entities:
                self.add_entity(tech_id, tech, 'TECHNOLOGY')
            self.add_relationship(project_id, tech_id, 'USES_TECHNOLOGY')
        
        # 添加导师
        supervisor = project_info.get('supervisor', '')
        if supervisor:
            supervisor_id = f"supervisor_{supervisor.replace(' ', '_').lower()}"
            if supervisor_id not in self.entities:
                self.add_entity(supervisor_id, supervisor, 'SUPERVISOR')
            self.add_relationship(project_id, supervisor_id, 'SUPERVISED_BY')
    
    def _add_student_concepts(self, student_id: str, student_info: Dict):
        """为学生添加相关概念"""
        # 添加专业
        major = student_info.get('major', '')
        if major:
            major_id = f"major_{major.replace(' ', '_').lower()}"
            if major_id not in self.entities:
                self.add_entity(major_id, major, 'MAJOR')
            self.add_relationship(student_id, major_id, 'STUDIED_MAJOR')
        
        # 添加课程
        for course in student_info.get('courses', []):
            course_id = f"course_{course.replace(' ', '_').lower()}"
            if course_id not in self.entities:
                self.add_entity(course_id, course, 'COURSE')
            self.add_relationship(student_id, course_id, 'COMPLETED_COURSE')
        
        # 添加技能
        for skill in student_info.get('skills', []):
            skill_id = f"skill_{skill.replace(' ', '_').lower()}"
            if skill_id not in self.entities:
                self.add_entity(skill_id, skill, 'SKILL')
            self.add_relationship(student_id, skill_id, 'HAS_SKILL')
        
        # 添加兴趣
        for interest in student_info.get('interests', []):
            interest_id = f"interest_{interest.replace(' ', '_').lower()}"
            if interest_id not in self.entities:
                self.add_entity(interest_id, interest, 'INTEREST')
            self.add_relationship(student_id, interest_id, 'INTERESTED_IN')
    
    def _build_matches(self):
        """构建项目-学生匹配关系"""
        projects = [e for e in self.entities.values() if e.entity_type == 'PROJECT']
        students = [e for e in self.entities.values() if e.entity_type == 'STUDENT']
        
        for project in projects:
            for student in students:
                score = self._calculate_match_score(project.id, student.id)
                if score > 0.2:  # 阈值过滤
                    self.add_relationship(
                        student.id, project.id, 'MATCHES', 
                        weight=score, 
                        properties={'score': score}
                    )
    
    def _calculate_match_score(self, project_id: str, student_id: str) -> float:
        """计算匹配分数"""
        score = 0.0
        
        # 获取项目需要的技能
        project_skills = set()
        project_majors = set()
        
        for rel in self.relationships:
            if rel.source_id == project_id:
                if rel.relation_type == 'REQUIRES_SKILL':
                    project_skills.add(rel.target_id)
                elif rel.relation_type == 'REQUIRES_MAJOR':
                    project_majors.add(rel.target_id)
        
        # 获取学生的技能和专业
        student_skills = set()
        student_majors = set()
        
        for rel in self.relationships:
            if rel.source_id == student_id:
                if rel.relation_type == 'HAS_SKILL':
                    student_skills.add(rel.target_id)
                elif rel.relation_type == 'STUDIED_MAJOR':
                    student_majors.add(rel.target_id)
        
        # 计算技能匹配度
        if project_skills:
            skill_overlap = len(project_skills.intersection(student_skills))
            score += (skill_overlap / len(project_skills)) * 0.6
        
        # 计算专业匹配度
        if project_majors and project_majors.intersection(student_majors):
            score += 0.3
        
        # 兴趣匹配
        student_interests = set()
        for rel in self.relationships:
            if rel.source_id == student_id and rel.relation_type == 'INTERESTED_IN':
                student_interests.add(rel.target_id)
        
        if project_skills.intersection(student_interests):
            score += 0.1
        
        return min(score, 1.0)
    
    def _print_statistics(self):
        """打印统计信息"""
        entity_counts = Counter(e.entity_type for e in self.entities.values())
        relation_counts = Counter(r.relation_type for r in self.relationships)
        
        print(f"\n📊 知识图谱统计:")
        print(f"   实体总数: {len(self.entities)}")
        print(f"   关系总数: {len(self.relationships)}")
        print(f"   实体类型分布: {dict(entity_counts)}")
        print(f"   关系类型分布: {dict(relation_counts)}")
    
    def save_graph(self, output_dir: str = "knowledge_graph_output"):
        """保存知识图谱"""
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存实体
        entities_data = []
        for entity in self.entities.values():
            entities_data.append(asdict(entity))
        
        with open(os.path.join(output_dir, "entities.json"), 'w', encoding='utf-8') as f:
            json.dump(entities_data, f, ensure_ascii=False, indent=2)
        
        # 保存关系
        relationships_data = []
        for rel in self.relationships:
            relationships_data.append(asdict(rel))
        
        with open(os.path.join(output_dir, "relationships.json"), 'w', encoding='utf-8') as f:
            json.dump(relationships_data, f, ensure_ascii=False, indent=2)
        
        # 保存NetworkX图
        if self.graph and nx:
            nx.write_gexf(self.graph, os.path.join(output_dir, "knowledge_graph.gexf"))
        
        # 生成统计报告
        stats = {
            'total_entities': len(self.entities),
            'total_relationships': len(self.relationships),
            'entity_types': dict(Counter(e.entity_type for e in self.entities.values())),
            'relation_types': dict(Counter(r.relation_type for r in self.relationships)),
            'created_at': datetime.now().isoformat()
        }
        
        with open(os.path.join(output_dir, "statistics.json"), 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 知识图谱已保存到: {output_dir}")
    
    def get_recommendations(self, entity_id: str, relation_type: str = 'MATCHES', 
                          top_k: int = 5) -> List[Tuple[str, float]]:
        """获取推荐"""
        recommendations = []
        
        for rel in self.relationships:
            if (rel.source_id == entity_id and rel.relation_type == relation_type) or \
               (rel.target_id == entity_id and rel.relation_type == relation_type):
                other_id = rel.target_id if rel.source_id == entity_id else rel.source_id
                score = rel.weight
                name = self.entities.get(other_id, {}).name if other_id in self.entities else other_id
                recommendations.append((name, score))
        
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:top_k]
    
    def create_simple_visualization(self, output_dir: str = "knowledge_graph_output"):
        """创建简单的可视化"""
        if not self.graph or not nx or not plt:
            print("❌ 无法创建可视化：缺少必要库")
            return
        
        plt.figure(figsize=(20, 15))
        
        # 使用spring layout
        pos = nx.spring_layout(self.graph, k=2, iterations=50)
        
        # 按类型设置颜色
        node_colors = {
            'PROJECT': '#FF6B6B',
            'STUDENT': '#4ECDC4',
            'SKILL': '#45B7D1', 
            'MAJOR': '#96CEB4',
            'TECHNOLOGY': '#FFEAA7',
            'COURSE': '#DDA0DD',
            'SUPERVISOR': '#98D8C8',
            'INTEREST': '#F7DC6F'
        }
        
        # 绘制不同类型的节点
        for entity_type, color in node_colors.items():
            nodes = [n for n, d in self.graph.nodes(data=True) if d.get('type') == entity_type]
            if nodes:
                nx.draw_networkx_nodes(self.graph, pos, nodelist=nodes, 
                                     node_color=color, node_size=300, alpha=0.8)
        
        # 绘制边
        nx.draw_networkx_edges(self.graph, pos, alpha=0.3, width=0.5)
        
        # 添加标签（仅显示部分以避免过于拥挤）
        important_nodes = [n for n, d in self.graph.nodes(data=True) 
                          if d.get('type') in ['PROJECT', 'STUDENT']]
        labels = {n: self.graph.nodes[n].get('name', n)[:10] for n in important_nodes[:20]}
        nx.draw_networkx_labels(self.graph, pos, labels, font_size=8)
        
        plt.title('项目匹配知识图谱', fontsize=16, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()
        
        # 保存图片
        plt.savefig(os.path.join(output_dir, "knowledge_graph.png"), 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 可视化图片已保存: {output_dir}/knowledge_graph.png")


class ProjectUnitKGGenerator:
    """项目+单元知识图谱生成器"""
    
    def __init__(self):
        self.unit_content = ""
        self.load_unit_content()
    
    def load_unit_content(self):
        """加载单元内容"""
        unit_file = "unit_md/qut_IN20_39851_int_cms_unit.md"
        try:
            with open(unit_file, 'r', encoding='utf-8') as f:
                self.unit_content = f.read()
            print(f"✅ 成功加载单元文件: {unit_file}")
        except Exception as e:
            print(f"❌ 加载单元文件失败: {e}")
    
    def create_project_unit_kg(self, project_file: str, output_dir: str):
        """为单个项目创建项目+单元知识图谱"""
        project_name = os.path.splitext(os.path.basename(project_file))[0]
        print(f"\n🔄 为项目 {project_name} 创建项目+单元知识图谱...")
        
        # 创建项目特定的构建器
        builder = ProjectKnowledgeGraphBuilder()
        
        try:
            # 读取项目内容
            with open(project_file, 'r', encoding='utf-8') as f:
                project_content = f.read()
            
            # 解析项目信息
            project_info = builder._parse_project_content(project_content)
            project_id = f"project_{project_name.replace(' ', '_')}"
            
            # 添加项目实体
            builder.add_entity(
                project_id,
                project_info.get('title', project_name),
                'PROJECT',
                {
                    'description': project_info.get('description', ''),
                    'majors': project_info.get('majors', []),
                    'supervisor': project_info.get('supervisor', ''),
                    'file_path': project_file
                }
            )
            
            # 添加单元实体
            unit_id = "qut_unit_outline"
            builder.add_entity(
                unit_id,
                "QUT Unit Outline",
                'UNIT',
                {
                    'content': self.unit_content[:500] + "..." if len(self.unit_content) > 500 else self.unit_content,
                    'file_path': "unit_md/qut_IN20_39851_int_cms_unit.md"
                }
            )
            
            # 添加项目概念
            builder._add_project_concepts(project_id, project_info)
            
            # 从单元内容中提取概念
            unit_info = {'skills': [], 'technologies': []}
            builder._extract_concepts_from_text(self.unit_content, unit_info)
            
            # 添加单元概念
            for skill in unit_info['skills']:
                skill_id = f"skill_{skill.replace(' ', '_').lower()}"
                if skill_id not in builder.entities:
                    builder.add_entity(skill_id, skill, 'SKILL')
                builder.add_relationship(unit_id, skill_id, 'TEACHES_SKILL')
                
                # 如果项目也需要这个技能，建立连接
                if skill_id in [rel.target_id for rel in builder.relationships 
                               if rel.source_id == project_id and rel.relation_type == 'REQUIRES_SKILL']:
                    builder.add_relationship(project_id, unit_id, 'SUPPORTED_BY', weight=0.8)
            
            for tech in unit_info['technologies']:
                tech_id = f"tech_{tech.replace(' ', '_').lower()}"
                if tech_id not in builder.entities:
                    builder.add_entity(tech_id, tech, 'TECHNOLOGY')
                builder.add_relationship(unit_id, tech_id, 'TEACHES_TECHNOLOGY')
            
            # 建立项目和单元之间的通用关系
            builder.add_relationship(project_id, unit_id, 'SUPPORTED_BY', weight=0.7)
            
            # 保存项目+单元知识图谱
            project_output_dir = os.path.join(output_dir, project_name.replace(' ', '_'))
            os.makedirs(project_output_dir, exist_ok=True)
            
            # 保存JSON文件
            entities_data = [asdict(entity) for entity in builder.entities.values()]
            with open(os.path.join(project_output_dir, f"{project_name}_entities.json"), 'w', encoding='utf-8') as f:
                json.dump(entities_data, f, ensure_ascii=False, indent=2)
            
            relationships_data = [asdict(rel) for rel in builder.relationships]
            with open(os.path.join(project_output_dir, f"{project_name}_relationships.json"), 'w', encoding='utf-8') as f:
                json.dump(relationships_data, f, ensure_ascii=False, indent=2)
            
            # 保存GEXF格式
            if builder.graph:
                nx.write_gexf(builder.graph, os.path.join(project_output_dir, f"{project_name}_kg.gexf"))
            
            # 生成可视化
            self._create_project_unit_visualization(builder, project_output_dir, project_name)
            
            # 生成统计信息
            stats = {
                'project_name': project_name,
                'project_title': project_info.get('title', project_name),
                'total_entities': len(builder.entities),
                'total_relationships': len(builder.relationships),
                'entity_types': {},
                'relation_types': {},
                'created_at': datetime.now().isoformat()
            }
            
            # 统计实体类型
            for entity in builder.entities.values():
                stats['entity_types'][entity.entity_type] = stats['entity_types'].get(entity.entity_type, 0) + 1
            
            # 统计关系类型
            for rel in builder.relationships:
                stats['relation_types'][rel.relation_type] = stats['relation_types'].get(rel.relation_type, 0) + 1
            
            with open(os.path.join(project_output_dir, f"{project_name}_statistics.json"), 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 项目 {project_name} 的项目+单元知识图谱已生成")
            print(f"   📂 输出目录: {project_output_dir}")
            print(f"   📊 实体数: {len(builder.entities)}, 关系数: {len(builder.relationships)}")
            
            return True
            
        except Exception as e:
            print(f"❌ 为项目 {project_name} 生成知识图谱失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _create_project_unit_visualization(self, builder, output_dir, project_name):
        """创建项目+单元知识图谱可视化"""
        try:
            if not builder.graph or not nx or not plt:
                print("❌ 无法创建可视化：缺少必要库")
                return
            
            plt.figure(figsize=(16, 12))
            
            # 使用spring layout
            pos = nx.spring_layout(builder.graph, k=3, iterations=50)
            
            # 节点颜色配置
            node_colors = {
                'PROJECT': '#FF6B6B',      # 红色 - 项目
                'UNIT': '#4ECDC4',         # 青色 - 单元  
                'SKILL': '#45B7D1',        # 蓝色 - 技能
                'MAJOR': '#96CEB4',        # 绿色 - 专业
                'TECHNOLOGY': '#FFEAA7',   # 黄色 - 技术
                'SUPERVISOR': '#98D8C8',   # 浅绿 - 导师
            }
            
            # 绘制不同类型的节点
            for entity_type, color in node_colors.items():
                nodes = [n for n, d in builder.graph.nodes(data=True) if d.get('type') == entity_type]
                if nodes:
                    # 设置节点大小
                    node_size = 800 if entity_type in ['PROJECT', 'UNIT'] else 400
                    nx.draw_networkx_nodes(builder.graph, pos, nodelist=nodes, 
                                         node_color=color, node_size=node_size, alpha=0.8)
            
            # 绘制边
            nx.draw_networkx_edges(builder.graph, pos, alpha=0.4, width=1, edge_color='gray')
            
            # 添加标签（只为重要节点）
            important_nodes = [n for n, d in builder.graph.nodes(data=True) 
                              if d.get('type') in ['PROJECT', 'UNIT']]
            labels = {n: builder.graph.nodes[n].get('name', n)[:15] + '...' 
                     if len(builder.graph.nodes[n].get('name', n)) > 15 
                     else builder.graph.nodes[n].get('name', n) 
                     for n in important_nodes}
            nx.draw_networkx_labels(builder.graph, pos, labels, font_size=10, font_weight='bold')
            
            # 添加技能标签（较小字体）
            skill_nodes = [n for n, d in builder.graph.nodes(data=True) if d.get('type') == 'SKILL'][:10]  # 只显示前10个技能
            skill_labels = {n: builder.graph.nodes[n].get('name', n)[:10] for n in skill_nodes}
            nx.draw_networkx_labels(builder.graph, pos, skill_labels, font_size=8, font_color='darkblue')
            
            plt.title(f'项目+单元知识图谱: {project_name}', fontsize=16, fontweight='bold', pad=20)
            
            # 添加图例
            legend_elements = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, 
                                        markersize=10, label=entity_type) 
                             for entity_type, color in node_colors.items()]
            plt.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.15, 1))
            
            plt.axis('off')
            plt.tight_layout()
            
            # 保存可视化
            plt.savefig(os.path.join(output_dir, f"{project_name}_project_unit_kg.png"), 
                       dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            print(f"📊 可视化已保存: {project_name}_project_unit_kg.png")
            
        except Exception as e:
            print(f"❌ 创建可视化失败: {e}")
    
    def generate_all_project_unit_kgs(self):
        """为所有项目生成项目+单元知识图谱"""
        print("🎯 开始为所有项目生成项目+单元知识图谱")
        print("=" * 60)
        
        # 创建输出目录
        base_output_dir = "individual_kg/projects_uo"
        os.makedirs(base_output_dir, exist_ok=True)
        print(f"📂 输出目录: {base_output_dir}")
        
        # 获取所有项目文件
        project_files = glob.glob("project_md/*.md")
        print(f"📁 找到 {len(project_files)} 个项目文件")
        
        if not project_files:
            print("⚠️ 没有找到项目文件")
            return
        
        success_count = 0
        failed_count = 0
        
        for i, project_file in enumerate(project_files, 1):
            project_name = os.path.splitext(os.path.basename(project_file))[0]
            print(f"\n[{i}/{len(project_files)}] 处理项目: {project_name}")
            
            if self.create_project_unit_kg(project_file, base_output_dir):
                success_count += 1
            else:
                failed_count += 1
        
        print(f"\n🎉 所有项目+单元知识图谱生成完成！")
        print(f"✅ 成功: {success_count} 个")
        print(f"❌ 失败: {failed_count} 个")
        print(f"📂 输出目录: {base_output_dir}")


def main():
    """主函数"""
    print("🎯 项目+单元知识图谱构建系统")
    print("=" * 50)
    
    # 创建项目+单元知识图谱生成器
    generator = ProjectUnitKGGenerator()
    
    # 为所有项目生成项目+单元知识图谱
    generator.generate_all_project_unit_kgs()


if __name__ == "__main__":
    main()

