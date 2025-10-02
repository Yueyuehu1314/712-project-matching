#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目匹配知识图谱系统 - 构建项目和学生的知识图谱
功能：
1. 从项目文件和学生档案构建知识图谱
2. 分析项目-学生匹配关系
3. 可视化知识网络
4. 提供查询和推荐功能
"""

import json
import os
import re
import glob
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from collections import defaultdict, Counter
import numpy as np


@dataclass
class KnowledgeNode:
    """知识图谱节点"""
    id: str
    type: str  # 'concept', 'skill', 'technology', 'domain', 'course', 'project'
    label: str
    weight: float = 1.0
    attributes: Dict = None
    
    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}


@dataclass
class KnowledgeEdge:
    """知识图谱边"""
    source: str
    target: str
    relation: str  # 'requires', 'relates_to', 'part_of', 'prerequisite', 'similar_to'
    weight: float = 1.0
    attributes: Dict = None
    
    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}


@dataclass
class KnowledgeGraph:
    """知识图谱数据结构"""
    name: str
    nodes: List[KnowledgeNode]
    edges: List[KnowledgeEdge]
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {
                'created_at': datetime.now().isoformat(),
                'node_count': len(self.nodes),
                'edge_count': len(self.edges)
            }


class ConceptExtractor:
    """概念提取器 - 从文本中提取关键概念和技能"""
    
    def __init__(self):
        # 技术关键词字典
        self.tech_keywords = {
            'machine_learning': ['machine learning', 'ml', 'deep learning', 'neural network', 'tensorflow', 'pytorch', 'scikit-learn'],
            'web_development': ['web development', 'html', 'css', 'javascript', 'react', 'angular', 'vue', 'node.js'],
            'data_science': ['data science', 'data analysis', 'python', 'pandas', 'numpy', 'visualization', 'statistics'],
            'cybersecurity': ['cybersecurity', 'security', 'encryption', 'firewall', 'penetration testing', 'vulnerability'],
            'mobile_development': ['mobile development', 'android', 'ios', 'app development', 'flutter', 'react native'],
            'database': ['database', 'sql', 'mysql', 'postgresql', 'mongodb', 'nosql', 'data modeling'],
            'networking': ['networking', 'tcp/ip', 'wifi', 'routing', 'network security', 'protocols'],
            'ai': ['artificial intelligence', 'ai', 'computer vision', 'nlp', 'natural language processing'],
            'software_engineering': ['software engineering', 'agile', 'scrum', 'devops', 'testing', 'deployment'],
            'bioinformatics': ['bioinformatics', 'genomics', 'crispr', 'dna', 'protein', 'sequence analysis']
        }
        
        # 学术概念字典
        self.academic_concepts = {
            'algorithms': ['algorithm', 'complexity', 'optimization', 'sorting', 'searching', 'graph theory'],
            'systems': ['operating systems', 'distributed systems', 'parallel computing', 'cloud computing'],
            'mathematics': ['linear algebra', 'calculus', 'statistics', 'probability', 'discrete mathematics'],
            'business': ['business analysis', 'requirements engineering', 'stakeholder management', 'project management']
        }
        
        # 课程单元关键词映射
        self.unit_keywords = {
            'IFN551': ['computer systems', 'fundamentals', 'hardware', 'software'],
            'IFN552': ['systems analysis', 'design', 'modeling', 'requirements'],
            'IFN554': ['database', 'sql', 'data modeling', 'normalization'],
            'IFN555': ['programming', 'basics', 'algorithms', 'problem solving'],
            'IFN556': ['object oriented', 'oop', 'java', 'design patterns'],
            'IFN563': ['algorithms', 'complexity', 'data structures', 'optimization'],
            'IFN564': ['machine learning', 'ai', 'data mining', 'pattern recognition'],
            'IFN666': ['web technologies', 'html', 'css', 'javascript', 'web development'],
            'IFN619': ['data analytics', 'visualization', 'business intelligence'],
            'IFN623': ['cybersecurity', 'network security', 'encryption']
        }
    
    def extract_concepts(self, text: str) -> List[Tuple[str, str, float]]:
        """从文本中提取概念 
        Returns: List of (concept_id, concept_label, weight)
        """
        text_lower = text.lower()
        concepts = []
        
        # 提取技术概念
        for category, keywords in self.tech_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    weight = text_lower.count(keyword) * 0.5
                    concepts.append((f"tech_{category}", category.replace('_', ' ').title(), weight))
                    break  # 每个类别只添加一次
        
        # 提取学术概念
        for category, keywords in self.academic_concepts.items():
            for keyword in keywords:
                if keyword in text_lower:
                    weight = text_lower.count(keyword) * 0.3
                    concepts.append((f"academic_{category}", category.replace('_', ' ').title(), weight))
                    break
        
        return concepts
    
    def extract_units(self, unit_list: List[str]) -> List[Tuple[str, str, float]]:
        """从课程列表中提取概念"""
        concepts = []
        for unit in unit_list:
            unit_code = unit.split()[0] if unit else ""
            if unit_code in self.unit_keywords:
                keywords = self.unit_keywords[unit_code]
                for keyword in keywords:
                    concept_id = f"unit_{keyword.replace(' ', '_')}"
                    concepts.append((concept_id, keyword.title(), 1.0))
        return concepts


class ProjectKGGenerator:
    """项目知识图谱生成器"""
    
    def __init__(self):
        self.extractor = ConceptExtractor()
    
    def generate_project_kg(self, project_content: str, project_title: str) -> KnowledgeGraph:
        """生成仅基于项目描述的知识图谱 (RQ1 baseline)"""
        nodes = []
        edges = []
        
        # 添加项目节点
        project_node = KnowledgeNode(
            id=f"project_{project_title.replace(' ', '_')}",
            type="project",
            label=project_title,
            weight=1.0,
            attributes={"description": project_content[:200]}
        )
        nodes.append(project_node)
        
        # 提取概念
        concepts = self.extractor.extract_concepts(project_content)
        
        # 添加概念节点和边
        for concept_id, concept_label, weight in concepts:
            concept_node = KnowledgeNode(
                id=concept_id,
                type="concept",
                label=concept_label,
                weight=weight
            )
            nodes.append(concept_node)
            
            # 项目需要该概念
            edge = KnowledgeEdge(
                source=project_node.id,
                target=concept_id,
                relation="requires",
                weight=weight
            )
            edges.append(edge)
        
        return KnowledgeGraph(
            name=f"Project_KG_{project_title}",
            nodes=nodes,
            edges=edges,
            metadata={
                'type': 'project_only',
                'project_title': project_title,
                'created_at': datetime.now().isoformat()
            }
        )
    
    def generate_project_unit_kg(self, project_content: str, project_title: str, 
                                unit_content: str) -> KnowledgeGraph:
        """生成项目+课程单元的知识图谱 (RQ1 enhanced)"""
        nodes = []
        edges = []
        
        # 添加项目节点
        project_node = KnowledgeNode(
            id=f"project_{project_title.replace(' ', '_')}",
            type="project", 
            label=project_title,
            weight=1.0,
            attributes={"description": project_content[:200]}
        )
        nodes.append(project_node)
        
        # 添加课程单元节点
        unit_node = KnowledgeNode(
            id="qut_unit_outline",
            type="unit",
            label="QUT Unit Outline",
            weight=1.0,
            attributes={"content": unit_content[:200]}
        )
        nodes.append(unit_node)
        
        # 提取项目概念
        project_concepts = self.extractor.extract_concepts(project_content)
        
        # 提取课程概念
        unit_concepts = self.extractor.extract_concepts(unit_content)
        
        # 合并概念并去重
        all_concepts = {}
        for concept_id, concept_label, weight in project_concepts + unit_concepts:
            if concept_id in all_concepts:
                all_concepts[concept_id] = (concept_label, max(all_concepts[concept_id][1], weight))
            else:
                all_concepts[concept_id] = (concept_label, weight)
        
        # 添加概念节点和边
        for concept_id, (concept_label, weight) in all_concepts.items():
            concept_node = KnowledgeNode(
                id=concept_id,
                type="concept",
                label=concept_label,
                weight=weight
            )
            nodes.append(concept_node)
            
            # 检查概念来源并建立边
            is_in_project = any(c[0] == concept_id for c in project_concepts)
            is_in_unit = any(c[0] == concept_id for c in unit_concepts)
            
            if is_in_project:
                edge = KnowledgeEdge(
                    source=project_node.id,
                    target=concept_id,
                    relation="requires",
                    weight=weight
                )
                edges.append(edge)
            
            if is_in_unit:
                edge = KnowledgeEdge(
                    source=unit_node.id,
                    target=concept_id,
                    relation="teaches",
                    weight=weight
                )
                edges.append(edge)
        
        # 建立项目和课程单元之间的关系
        project_unit_edge = KnowledgeEdge(
            source=project_node.id,
            target=unit_node.id,
            relation="supported_by",
            weight=0.8
        )
        edges.append(project_unit_edge)
        
        return KnowledgeGraph(
            name=f"Project_Unit_KG_{project_title}",
            nodes=nodes,
            edges=edges,
            metadata={
                'type': 'project_with_unit',
                'project_title': project_title,
                'created_at': datetime.now().isoformat()
            }
        )


class StudentKGGenerator:
    """学生知识图谱生成器"""
    
    def __init__(self):
        self.extractor = ConceptExtractor()
        self.paraphraser = TextParaphraser()
    
    def generate_student_kg(self, student_profile: Dict, paraphrase_ratio: float = 0.1) -> KnowledgeGraph:
        """生成学生知识图谱 (RQ2)
        
        Args:
            student_profile: 学生档案信息
            paraphrase_ratio: 改写比例 (≈10%)
        """
        nodes = []
        edges = []
        
        # 添加学生节点
        student_node = KnowledgeNode(
            id=f"student_{student_profile.get('student_id', 'unknown')}",
            type="student",
            label=student_profile.get('name', 'Unknown Student'),
            weight=1.0,
            attributes={
                'student_id': student_profile.get('student_id'),
                'major': student_profile.get('major'),
                'year': student_profile.get('year_of_study')
            }
        )
        nodes.append(student_node)
        
        # 处理已完成课程 (RQ2: 只保留课程信息)
        completed_units = student_profile.get('completed_units', [])
        unit_concepts = self.extractor.extract_units(completed_units)
        
        # 处理项目经历 (RQ2: 只保留项目经历)
        project_experiences = student_profile.get('previous_projects', [])
        
        # 对项目经历文本进行轻度改写
        paraphrased_projects = []
        for project in project_experiences:
            if random.random() < paraphrase_ratio:
                paraphrased = self.paraphraser.paraphrase(project)
                paraphrased_projects.append(paraphrased)
            else:
                paraphrased_projects.append(project)
        
        # 从改写后的项目经历中提取概念
        project_text = " ".join(paraphrased_projects)
        project_concepts = self.extractor.extract_concepts(project_text)
        
        # 合并所有概念
        all_concepts = {}
        for concept_id, concept_label, weight in unit_concepts + project_concepts:
            if concept_id in all_concepts:
                all_concepts[concept_id] = (concept_label, all_concepts[concept_id][1] + weight)
            else:
                all_concepts[concept_id] = (concept_label, weight)
        
        # 添加概念节点和边
        for concept_id, (concept_label, weight) in all_concepts.items():
            concept_node = KnowledgeNode(
                id=concept_id,
                type="skill",
                label=concept_label,
                weight=weight
            )
            nodes.append(concept_node)
            
            # 学生掌握该概念
            edge = KnowledgeEdge(
                source=student_node.id,
                target=concept_id,
                relation="masters",
                weight=weight
            )
            edges.append(edge)
        
        return KnowledgeGraph(
            name=f"Student_KG_{student_profile.get('student_id')}",
            nodes=nodes,
            edges=edges,
            metadata={
                'type': 'student',
                'student_id': student_profile.get('student_id'),
                'paraphrase_ratio': paraphrase_ratio,
                'created_at': datetime.now().isoformat()
            }
        )


class TextParaphraser:
    """文本改写器 - 用于RQ2的轻度同义改写"""
    
    def __init__(self):
        # 同义词字典 (简化版本，实际可以使用更复杂的NLP模型)
        self.synonyms = {
            'develop': ['create', 'build', 'implement', 'design'],
            'analyze': ['examine', 'study', 'investigate', 'evaluate'],
            'project': ['work', 'assignment', 'task', 'initiative'],
            'system': ['platform', 'application', 'solution', 'framework'],
            'data': ['information', 'dataset', 'records', 'content'],
            'web': ['online', 'internet', 'digital', 'web-based'],
            'application': ['app', 'software', 'program', 'tool'],
            'database': ['data store', 'repository', 'data system'],
            'algorithm': ['method', 'approach', 'technique', 'procedure'],
            'machine learning': ['ML', 'automated learning', 'AI learning'],
            'programming': ['coding', 'development', 'software creation'],
            'optimization': ['improvement', 'enhancement', 'refinement']
        }
    
    def paraphrase(self, text: str) -> str:
        """对文本进行轻度同义改写"""
        words = text.split()
        paraphrased_words = []
        
        for word in words:
            word_lower = word.lower().strip('.,!?;:')
            
            # 检查是否有同义词
            if word_lower in self.synonyms and random.random() < 0.3:  # 30%概率改写
                synonym = random.choice(self.synonyms[word_lower])
                # 保持原始单词的大小写格式
                if word[0].isupper():
                    synonym = synonym.capitalize()
                paraphrased_words.append(synonym)
            else:
                paraphrased_words.append(word)
        
        return " ".join(paraphrased_words)


class CoverageScoreCalculator:
    """覆盖度评分计算器 - 用于评估项目-学生匹配质量"""
    
    def __init__(self):
        pass
    
    def calculate_coverage_score(self, project_kg: KnowledgeGraph, 
                                student_kg: KnowledgeGraph) -> float:
        """计算覆盖度分数
        
        覆盖度 = (学生掌握的项目所需概念数 / 项目所需概念总数)
        """
        # 提取项目所需的概念
        project_concepts = set()
        for edge in project_kg.edges:
            if edge.relation == "requires":
                project_concepts.add(edge.target)
        
        # 提取学生掌握的概念
        student_concepts = set()
        for edge in student_kg.edges:
            if edge.relation == "masters":
                student_concepts.add(edge.target)
        
        # 计算覆盖度
        if not project_concepts:
            return 0.0
        
        covered_concepts = project_concepts.intersection(student_concepts)
        coverage_score = len(covered_concepts) / len(project_concepts)
        
        return coverage_score
    
    def calculate_weighted_coverage_score(self, project_kg: KnowledgeGraph,
                                        student_kg: KnowledgeGraph) -> float:
        """计算加权覆盖度分数 (考虑概念重要性)"""
        # 提取项目概念及其权重
        project_concept_weights = {}
        for edge in project_kg.edges:
            if edge.relation == "requires":
                project_concept_weights[edge.target] = edge.weight
        
        # 提取学生概念及其权重
        student_concept_weights = {}
        for edge in student_kg.edges:
            if edge.relation == "masters":
                student_concept_weights[edge.target] = edge.weight
        
        # 计算加权覆盖度
        total_weight = sum(project_concept_weights.values())
        if total_weight == 0:
            return 0.0
        
        covered_weight = 0.0
        for concept, weight in project_concept_weights.items():
            if concept in student_concept_weights:
                # 使用学生和项目权重的最小值
                covered_weight += min(weight, student_concept_weights[concept])
        
        return covered_weight / total_weight


class KnowledgeGraphPersistence:
    """知识图谱持久化管理"""
    
    @staticmethod
    def save_kg(kg: KnowledgeGraph, filepath: str):
        """保存知识图谱到JSON文件"""
        kg_dict = {
            'name': kg.name,
            'nodes': [asdict(node) for node in kg.nodes],
            'edges': [asdict(edge) for edge in kg.edges],
            'metadata': kg.metadata
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(kg_dict, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def load_kg(filepath: str) -> KnowledgeGraph:
        """从JSON文件加载知识图谱"""
        with open(filepath, 'r', encoding='utf-8') as f:
            kg_dict = json.load(f)
        
        nodes = [KnowledgeNode(**node_data) for node_data in kg_dict['nodes']]
        edges = [KnowledgeEdge(**edge_data) for edge_data in kg_dict['edges']]
        
        return KnowledgeGraph(
            name=kg_dict['name'],
            nodes=nodes,
            edges=edges,
            metadata=kg_dict.get('metadata', {})
        )
    
    @staticmethod
    def export_to_networkx(kg: KnowledgeGraph) -> nx.Graph:
        """导出为NetworkX图用于可视化"""
        G = nx.Graph()
        
        # 添加节点
        for node in kg.nodes:
            G.add_node(node.id, 
                      label=node.label,
                      type=node.type,
                      weight=node.weight,
                      **node.attributes)
        
        # 添加边
        for edge in kg.edges:
            G.add_edge(edge.source, edge.target,
                      relation=edge.relation,
                      weight=edge.weight,
                      **edge.attributes)
        
        return G


# 示例使用函数
def demonstrate_kg_generation():
    """演示知识图谱生成流程"""
    print("知识图谱生成演示")
    print("="*50)
    
    # 模拟项目数据
    project_title = "Zero-Day Attack Detection Using Machine Learning"
    project_content = """
    This project aims to develop a machine learning-based approach to detect zero-day 
    cyberattacks by identifying anomalous patterns in network behavior. Using public datasets 
    containing both normal and known attack traffic, the project will train unsupervised and 
    semi-supervised machine learning models capable of learning normal behavior and flagging deviations.
    """
    
    # 模拟课程单元内容
    unit_content = """
    This unit covers cybersecurity fundamentals, network security protocols, machine learning 
    applications in security, and hands-on experience with security tools and frameworks.
    """
    
    # 模拟学生档案
    student_profile = {
        'name': 'Alex Chen',
        'student_id': 'n12345678',
        'major': 'Computer Science',
        'year_of_study': 3,
        'completed_units': [
            'IFN551 Computer Systems Fundamentals',
            'IFN564 Machine Learning', 
            'IFN623 Cyber Security'
        ],
        'previous_projects': [
            'Network traffic analysis system',
            'Machine learning anomaly detection',
            'Web application security testing'
        ]
    }
    
    # 生成知识图谱
    project_generator = ProjectKGGenerator()
    student_generator = StudentKGGenerator()
    
    # RQ1: 生成项目KG (baseline)
    project_kg = project_generator.generate_project_kg(project_content, project_title)
    print(f"项目KG节点数: {len(project_kg.nodes)}")
    print(f"项目KG边数: {len(project_kg.edges)}")
    
    # RQ1: 生成项目+课程单元KG (enhanced)
    project_unit_kg = project_generator.generate_project_unit_kg(
        project_content, project_title, unit_content
    )
    print(f"项目+单元KG节点数: {len(project_unit_kg.nodes)}")
    print(f"项目+单元KG边数: {len(project_unit_kg.edges)}")
    
    # RQ2: 生成学生KG (with paraphrasing)
    student_kg = student_generator.generate_student_kg(student_profile, paraphrase_ratio=0.1)
    print(f"学生KG节点数: {len(student_kg.nodes)}")
    print(f"学生KG边数: {len(student_kg.edges)}")
    
    # 计算覆盖度分数
    calculator = CoverageScoreCalculator()
    
    coverage1 = calculator.calculate_coverage_score(project_kg, student_kg)
    coverage2 = calculator.calculate_coverage_score(project_unit_kg, student_kg)
    
    print(f"\n覆盖度分数 (仅项目): {coverage1:.3f}")
    print(f"覆盖度分数 (项目+单元): {coverage2:.3f}")
    print(f"ΔAUC: {coverage2 - coverage1:.3f}")


class ProjectMatchingKnowledgeGraph:
    """项目匹配知识图谱主系统"""
    
    def __init__(self, project_dir: str = "project_md", 
                 student_dir: str = "profile_md", 
                 unit_file: str = "unit_md/qut_IN20_39851_int_cms_unit.md"):
        self.project_dir = project_dir
        self.student_dir = student_dir
        self.unit_file = unit_file
        
        self.extractor = ConceptExtractor()
        self.project_generator = ProjectKGGenerator()
        self.student_generator = StudentKGGenerator()
        
        # 存储所有图谱
        self.project_graphs = {}
        self.student_graphs = {}
        self.global_graph = nx.MultiDiGraph()
        
        # 实体和关系统计
        self.entities = {}
        self.relationships = []
    
    def build_complete_knowledge_graph(self):
        """构建完整的项目-学生知识图谱"""
        print("🔄 开始构建完整知识图谱...")
        
        # 1. 处理所有项目
        print("📁 处理项目文件...")
        self._process_all_projects()
        
        # 2. 处理所有学生档案
        print("👥 处理学生档案...")
        self._process_all_students()
        
        # 3. 构建项目-学生匹配关系
        print("🔗 构建匹配关系...")
        self._build_matching_relationships()
        
        # 4. 生成统计信息
        print("📊 生成统计信息...")
        self._generate_statistics()
        
        print("✅ 知识图谱构建完成！")
    
    def _process_all_projects(self):
        """处理所有项目文件"""
        project_files = glob.glob(os.path.join(self.project_dir, "*.md"))
        
        for i, project_file in enumerate(project_files, 1):
            project_name = os.path.splitext(os.path.basename(project_file))[0]
            print(f"  [{i}/{len(project_files)}] {project_name}")
            
            try:
                # 读取项目内容
                with open(project_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 解析项目信息
                project_info = self._parse_project_file(content)
                
                # 添加项目节点到全局图
                project_id = f"project_{project_name}"
                self.global_graph.add_node(
                    project_id,
                    type="PROJECT",
                    name=project_info['title'],
                    description=project_info['description'],
                    majors=project_info['majors'],
                    supervisor=project_info['supervisor'],
                    file_path=project_file
                )
                
                self.entities[project_id] = {
                    'type': 'PROJECT',
                    'name': project_info['title'],
                    'properties': project_info
                }
                
                # 添加技能和技术节点
                self._add_project_concepts(project_id, project_info)
                
            except Exception as e:
                print(f"    ❌ 处理失败: {e}")


def main():
    """主函数 - 构建完整的项目匹配知识图谱"""
    print("🎯 项目匹配知识图谱构建系统")
    print("=" * 60)
    
    # 创建知识图谱系统
    kg_system = ProjectMatchingKnowledgeGraph()
    
    # 构建完整知识图谱
    kg_system.build_complete_knowledge_graph()
    
    # 保存知识图谱
    kg_system.save_knowledge_graph()
    
    print(f"\n🎉 知识图谱构建完成！")
    print(f"📂 输出目录: knowledge_graph_output/")


if __name__ == "__main__":
    main()
