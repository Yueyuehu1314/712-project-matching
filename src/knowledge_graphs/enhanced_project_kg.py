#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Project Knowledge Graph Builder
集成 QUT Unit Outline 信息的增强版项目知识图谱构建器
"""

print("📦 Starting enhanced_project_kg imports...")

import os
import json
import re
import glob
print("📦 Basic imports completed")

from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict, Counter
print("📦 Advanced imports completed")

try:
    import networkx as nx
    print("📦 networkx imported")
except ImportError as e:
    print(f"❌ Failed to import networkx: {e}")
    nx = None

try:
    import matplotlib.pyplot as plt
    print("📦 matplotlib imported")
except ImportError as e:
    print(f"❌ Failed to import matplotlib: {e}")
    
try:
    import pandas as pd
    print("📦 pandas imported")
except ImportError as e:
    print(f"❌ Failed to import pandas: {e}")
    
try:
    import numpy as np
    print("📦 numpy imported")
except ImportError as e:
    print(f"❌ Failed to import numpy: {e}")

try:
    from project_knowledge_graph import ProjectKnowledgeGraphBuilder, Entity, Relationship
    print("📦 project_knowledge_graph imports completed")
except ImportError as e:
    print(f"❌ Failed to import from project_knowledge_graph: {e}")

print("✅ enhanced_project_kg imports completed")


class EnhancedProjectKnowledgeGraphBuilder(ProjectKnowledgeGraphBuilder):
    """增强版项目知识图谱构建器 - 集成 Unit Outline 信息"""
    
    def __init__(self):
        super().__init__()
        
        # 添加新的实体类型
        self.entity_types.update({
            'UNIT': 'Unit',
            'LEARNING_OUTCOME': 'LearningOutcome',
            'PREREQUISITE': 'Prerequisite',
            'ASSESSMENT': 'Assessment'
        })
        
        # 添加新的关系类型
        self.relation_types.update({
            'RELATES_TO_UNIT': 'relates_to_unit',
            'HAS_PREREQUISITE': 'has_prerequisite',
            'ACHIEVES_OUTCOME': 'achieves_outcome',
            'ASSESSED_BY': 'assessed_by',
            'BUILDS_ON': 'builds_on'
        })
        
        # Unit outline 数据
        self.unit_data = {}
        
    def load_unit_outlines(self, unit_dir: str = "unit_md"):
        """加载 Unit Outline 数据"""
        print(f"📚 加载 Unit Outline 数据从: {unit_dir}")
        
        if not os.path.exists(unit_dir):
            print(f"⚠️ Unit 目录不存在: {unit_dir}")
            return
        
        unit_files = glob.glob(os.path.join(unit_dir, "*.md"))
        print(f"找到 {len(unit_files)} 个 Unit 文件")
        
        for unit_file in unit_files:
            try:
                with open(unit_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                unit_info = self._parse_unit_content(content)
                unit_id = os.path.splitext(os.path.basename(unit_file))[0]
                self.unit_data[unit_id] = unit_info
                
                print(f"  ✅ 已加载: {unit_id}")
                
            except Exception as e:
                print(f"  ❌ 加载失败 {unit_file}: {e}")
        
        print(f"✅ 共加载 {len(self.unit_data)} 个 Unit Outline")
    
    def _parse_unit_content(self, content: str) -> Dict[str, Any]:
        """解析 Unit Outline 内容"""
        info = {
            'title': '',
            'course_code': '',
            'majors': [],
            'units': [],
            'skills': [],
            'technologies': [],
            'learning_outcomes': [],
            'prerequisites': [],
            'assessments': []
        }
        
        lines = content.split('\n')
        
        # 提取课程标题
        for line in lines[:10]:  # 在前10行查找标题
            if line.startswith('# ') and 'Master of Information Technology' in line:
                info['title'] = line.strip('# ').strip()
                break
        
        # 提取专业信息
        major_patterns = [
            r'Business Analysis Major',
            r'Computer Science Major', 
            r'Data Science Major',
            r'Software Development Major',
            r'Cyber Security and Networks Major',
            r'Enterprise Systems Major',
            r'Executive IT Major'
        ]
        
        content_lower = content.lower()
        for pattern in major_patterns:
            if pattern.lower() in content_lower:
                major_name = pattern.replace(' Major', '')
                if major_name not in info['majors']:
                    info['majors'].append(major_name)
        
        # 提取课程单元 (IFN codes)
        unit_pattern = r'\b(IFN\d{3}|CAB\d{3}|ENN\d{3}|IAB\d{3}|MGN\d{3})\b'
        units_found = set(re.findall(unit_pattern, content, re.IGNORECASE))
        info['units'] = list(units_found)
        
        # 从单元描述中提取技能和技术
        self._extract_skills_from_unit_descriptions(content, info)
        
        # 提取学习成果 (从单元描述中)
        info['learning_outcomes'] = self._extract_learning_outcomes(content)
        
        # 提取先修课程信息
        info['prerequisites'] = self._extract_prerequisites(content)
        
        return info
    
    def _extract_skills_from_unit_descriptions(self, content: str, info: Dict):
        """从 Unit 描述中提取技能和技术"""
        content_lower = content.lower()
        
        # 扩展的技能关键词库
        skill_keywords = {
            'machine learning': ['machine learning', 'ml', 'artificial intelligence', 'ai', 'deep learning'],
            'data science': ['data science', 'data mining', 'data analytics', 'data exploration', 'big data'],
            'web development': ['web development', 'web application', 'html', 'css', 'javascript', 'react'],
            'cybersecurity': ['security', 'cyber security', 'cryptography', 'network security', 'information security'],
            'business analysis': ['business analysis', 'business process', 'enterprise systems', 'requirements analysis'],
            'software engineering': ['software development', 'programming', 'algorithms', 'data structures'],
            'database management': ['database', 'sql', 'data management', 'information systems'],
            'networking': ['network', 'tcp/ip', 'network systems', 'network engineering'],
            'cloud computing': ['cloud', 'cloud computing', 'distributed systems'],
            'project management': ['project management', 'it governance', 'consulting'],
            'user experience': ['user experience', 'ux', 'human computer interaction', 'interaction design']
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
            'C#': ['c#', 'c sharp'],
            'Flask': ['flask'],
            'Bootstrap': ['bootstrap'],
            'MongoDB': ['mongodb'],
            'MySQL': ['mysql']
        }
        
        for tech, keywords in tech_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                if tech not in info['technologies']:
                    info['technologies'].append(tech)
    
    def _extract_learning_outcomes(self, content: str) -> List[str]:
        """提取学习成果"""
        outcomes = []
        
        # 从单元描述中提取关键能力
        capability_patterns = [
            r'you will learn ([^.]+)',
            r'students will ([^.]+)',
            r'this unit ([^.]+)',
            r'provides ([^.]+)',
            r'introduces ([^.]+)'
        ]
        
        for pattern in capability_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if len(match) > 20 and len(match) < 200:  # 过滤合理长度
                    outcomes.append(match.strip())
        
        return outcomes[:10]  # 限制数量
    
    def _extract_prerequisites(self, content: str) -> List[str]:
        """提取先修课程"""
        prereq_pattern = r'Pre-requisites[^|]*\|[^|]*\|([^|]+)'
        matches = re.findall(prereq_pattern, content, re.IGNORECASE)
        
        prerequisites = []
        for match in matches:
            # 提取课程代码
            codes = re.findall(r'\b(IFN\d{3}|CAB\d{3}|ENN\d{3}|IAB\d{3}|MGN\d{3})\b', match)
            prerequisites.extend(codes)
        
        return list(set(prerequisites))
    
    def build_enhanced_from_files(self, project_dir: str = "project_md", 
                                 student_dir: str = "profile_md",
                                 unit_dir: str = "unit_md"):
        """构建增强版知识图谱"""
        print("🔄 开始构建增强版项目知识图谱...")
        
        # 首先加载 Unit Outline 数据
        self.load_unit_outlines(unit_dir)
        
        # 调用基础构建方法
        self.build_from_files(project_dir, student_dir)
        
        # 添加 Unit 相关的实体和关系
        print("🔗 添加 Unit Outline 相关信息...")
        self._add_unit_entities_and_relationships()
        
        print("✅ 增强版知识图谱构建完成！")
        self._print_enhanced_statistics()
    
    def _add_unit_entities_and_relationships(self):
        """添加 Unit 相关实体和关系"""
        for unit_id, unit_info in self.unit_data.items():
            # 添加 Unit 实体
            unit_entity_id = f"unit_{unit_id}"
            self.add_entity(
                unit_entity_id,
                unit_info.get('title', unit_id),
                'UNIT',
                {
                    'course_code': unit_id,
                    'majors': unit_info.get('majors', []),
                    'units': unit_info.get('units', [])
                }
            )
            
            # 添加学习成果实体
            for i, outcome in enumerate(unit_info.get('learning_outcomes', [])):
                outcome_id = f"outcome_{unit_id}_{i}"
                self.add_entity(outcome_id, outcome[:50] + "..." if len(outcome) > 50 else outcome, 'LEARNING_OUTCOME')
                self.add_relationship(unit_entity_id, outcome_id, 'ACHIEVES_OUTCOME')
            
            # 添加先修课程关系
            for prereq in unit_info.get('prerequisites', []):
                prereq_id = f"unit_{prereq}"
                if prereq_id not in self.entities:
                    self.add_entity(prereq_id, prereq, 'UNIT')
                self.add_relationship(unit_entity_id, prereq_id, 'HAS_PREREQUISITE')
            
            # 连接到专业
            for major in unit_info.get('majors', []):
                major_id = f"major_{major.replace(' ', '_').lower()}"
                if major_id in self.entities:
                    self.add_relationship(major_id, unit_entity_id, 'RELATES_TO_UNIT')
            
            # 连接到技能
            for skill in unit_info.get('skills', []):
                skill_id = f"skill_{skill.replace(' ', '_').lower()}"
                if skill_id in self.entities:
                    self.add_relationship(unit_entity_id, skill_id, 'RELATES_TO_UNIT')
                else:
                    # 如果技能不存在，创建它
                    self.add_entity(skill_id, skill, 'SKILL')
                    self.add_relationship(unit_entity_id, skill_id, 'RELATES_TO_UNIT')
            
            # 连接到技术
            for tech in unit_info.get('technologies', []):
                tech_id = f"tech_{tech.replace(' ', '_').lower()}"
                if tech_id in self.entities:
                    self.add_relationship(unit_entity_id, tech_id, 'RELATES_TO_UNIT')
                else:
                    self.add_entity(tech_id, tech, 'TECHNOLOGY')
                    self.add_relationship(unit_entity_id, tech_id, 'RELATES_TO_UNIT')
    
    def _calculate_enhanced_match_score(self, project_id: str, student_id: str) -> float:
        """增强版匹配分数计算 - 考虑 Unit Outline 信息"""
        # 基础匹配分数
        base_score = super()._calculate_match_score(project_id, student_id)
        
        # Unit 相关匹配增强
        unit_bonus = 0.0
        
        # 获取项目相关的 Unit
        project_units = set()
        for rel in self.relationships:
            if rel.source_id == project_id and rel.relation_type == 'RELATES_TO_UNIT':
                project_units.add(rel.target_id)
        
        # 获取学生完成的课程对应的 Unit
        student_courses = set()
        for rel in self.relationships:
            if rel.source_id == student_id and rel.relation_type == 'COMPLETED_COURSE':
                course_name = self.entities[rel.target_id].name.lower()
                # 尝试匹配课程与 Unit
                for unit_id, unit_info in self.unit_data.items():
                    for unit_code in unit_info.get('units', []):
                        if unit_code.lower() in course_name:
                            student_courses.add(f"unit_{unit_id}")
        
        # 计算 Unit 重叠度
        if project_units and student_courses:
            unit_overlap = len(project_units.intersection(student_courses))
            unit_bonus = (unit_overlap / len(project_units)) * 0.15  # 15% 权重给 Unit 匹配
        
        # 学习成果匹配
        outcome_bonus = 0.0
        project_outcomes = set()
        for rel in self.relationships:
            if rel.target_id in project_units:
                for rel2 in self.relationships:
                    if rel2.source_id == rel.target_id and rel2.relation_type == 'ACHIEVES_OUTCOME':
                        project_outcomes.add(rel2.target_id)
        
        if project_outcomes:
            # 简化的学习成果匹配逻辑
            outcome_bonus = 0.05  # 5% 额外奖励
        
        enhanced_score = base_score + unit_bonus + outcome_bonus
        return min(enhanced_score, 1.0)
    
    def _build_matches(self):
        """重写匹配构建方法以使用增强版匹配算法"""
        projects = [e for e in self.entities.values() if e.entity_type == 'PROJECT']
        students = [e for e in self.entities.values() if e.entity_type == 'STUDENT']
        
        for project in projects:
            for student in students:
                score = self._calculate_enhanced_match_score(project.id, student.id)
                if score > 0.2:  # 阈值过滤
                    self.add_relationship(
                        student.id, project.id, 'MATCHES', 
                        weight=score, 
                        properties={'score': score, 'enhanced': True}
                    )
    
    def _print_enhanced_statistics(self):
        """打印增强版统计信息"""
        entity_counts = Counter(e.entity_type for e in self.entities.values())
        relation_counts = Counter(r.relation_type for r in self.relationships)
        
        print(f"\n📊 增强版知识图谱统计:")
        print(f"   实体总数: {len(self.entities)}")
        print(f"   关系总数: {len(self.relationships)}")
        print(f"   实体类型分布: {dict(entity_counts)}")
        print(f"   关系类型分布: {dict(relation_counts)}")
        print(f"   Unit 数量: {entity_counts.get('UNIT', 0)}")
        print(f"   学习成果数量: {entity_counts.get('LEARNING_OUTCOME', 0)}")
    
    def create_enhanced_visualization(self, output_dir: str = "enhanced_kg_output"):
        """创建增强版可视化"""
        if not self.graph or not nx or not plt:
            print("❌ 无法创建可视化：缺少必要库")
            return
        
        plt.figure(figsize=(24, 18))
        
        # 使用 spring layout
        pos = nx.spring_layout(self.graph, k=3, iterations=100)
        
        # 扩展的颜色映射
        node_colors = {
            'PROJECT': '#FF6B6B',
            'STUDENT': '#4ECDC4',
            'SKILL': '#45B7D1', 
            'MAJOR': '#96CEB4',
            'TECHNOLOGY': '#FFEAA7',
            'COURSE': '#DDA0DD',
            'SUPERVISOR': '#98D8C8',
            'INTEREST': '#F7DC6F',
            'UNIT': '#FF9FF3',           # 新增: Unit 粉紫色
            'LEARNING_OUTCOME': '#FFB84D', # 新增: 学习成果 橙色
            'PREREQUISITE': '#A8E6CF'     # 新增: 先修课程 浅绿色
        }
        
        # 绘制不同类型的节点
        for entity_type, color in node_colors.items():
            nodes = [n for n, d in self.graph.nodes(data=True) if d.get('type') == entity_type]
            if nodes:
                # 根据类型设置节点大小
                if entity_type in ['PROJECT', 'STUDENT']:
                    node_size = 500
                elif entity_type == 'UNIT':
                    node_size = 300
                else:
                    node_size = 200
                    
                nx.draw_networkx_nodes(self.graph, pos, nodelist=nodes, 
                                     node_color=color, node_size=node_size, alpha=0.8)
        
        # 绘制边，根据关系类型设置不同样式
        enhanced_edges = [(u, v) for u, v, d in self.graph.edges(data=True) 
                         if d.get('relation') in ['RELATES_TO_UNIT', 'ACHIEVES_OUTCOME']]
        regular_edges = [(u, v) for u, v, d in self.graph.edges(data=True) 
                        if d.get('relation') not in ['RELATES_TO_UNIT', 'ACHIEVES_OUTCOME']]
        
        # 普通边
        nx.draw_networkx_edges(self.graph, pos, edgelist=regular_edges, 
                              alpha=0.3, width=0.5, edge_color='gray')
        
        # 增强边（Unit 相关）
        nx.draw_networkx_edges(self.graph, pos, edgelist=enhanced_edges, 
                              alpha=0.6, width=1.5, edge_color='purple', style='dashed')
        
        # 添加重要节点标签
        important_nodes = [n for n, d in self.graph.nodes(data=True) 
                          if d.get('type') in ['PROJECT', 'STUDENT', 'UNIT']]
        labels = {n: self.graph.nodes[n].get('name', n)[:15] for n in important_nodes[:30]}
        nx.draw_networkx_labels(self.graph, pos, labels, font_size=8)
        
        plt.title('增强版项目匹配知识图谱 (集成 Unit Outline)', fontsize=16, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()
        
        # 保存图片
        plt.savefig(os.path.join(output_dir, "enhanced_knowledge_graph.png"), 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 增强版可视化图片已保存: {output_dir}/enhanced_knowledge_graph.png")


def main():
    """主函数"""
    print("🎯 增强版项目知识图谱构建系统")
    print("=" * 60)
    
    print("🔧 初始化增强版构建器...")
    try:
        builder = EnhancedProjectKnowledgeGraphBuilder()
        print("✅ 增强版构建器初始化成功")
    except Exception as e:
        print(f"❌ 构建器初始化失败: {e}")
        return
    
    print("\n📊 开始构建增强版知识图谱...")
    try:
        # 构建增强版知识图谱
        builder.build_enhanced_from_files()
        print("✅ 增强版知识图谱构建成功")
    except Exception as e:
        print(f"❌ 增强版知识图谱构建失败: {e}")
        return
    
    print("\n💾 保存增强版结果...")
    try:
        # 创建输出目录
        output_dir = "enhanced_kg_output"
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存结果
        builder.save_graph(output_dir)
        print("✅ 增强版结果保存成功")
    except Exception as e:
        print(f"❌ 增强版结果保存失败: {e}")
        return
    
    print("\n🎨 创建增强版可视化...")
    try:
        # 创建可视化
        builder.create_enhanced_visualization(output_dir)
        print("✅ 增强版可视化创建成功")
    except Exception as e:
        print(f"❌ 增强版可视化创建失败: {e}")
    
    print(f"\n🎉 增强版知识图谱构建完成！")
    print(f"📂 输出目录: {output_dir}/")
    print(f"📄 查看文件: entities.json, relationships.json, enhanced_knowledge_graph.png")


if __name__ == "__main__":
    main()
