#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目进度量化器
量化数据收集、档案生成、图构建等各个阶段的指标
"""

import os
import json
import glob
import re
from typing import Dict, List, Tuple
from collections import Counter, defaultdict
import statistics

class ProjectProgressQuantifier:
    """项目进度量化器"""
    
    def __init__(self):
        self.stats = {
            'data_collection': {},
            'profile_generation': {},
            'graph_construction': {},
            'enhanced_features': {}
        }
    
    def quantify_data_collection(self) -> Dict:
        """量化数据收集阶段"""
        print("📊 量化数据收集阶段...")
        
        # 项目描述处理
        project_files = glob.glob("project_md/*.md")
        total_projects = len(project_files)
        
        # 提取实体统计
        all_entities = {
            'skills': [],
            'technologies': [],
            'requirements': [],
            'majors': [],
            'supervisors': [],
            'other': []
        }
        
        total_words = 0
        
        for project_file in project_files:
            try:
                with open(project_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    total_words += len(content.split())
                    
                    # 提取技能
                    skills = self._extract_skills_from_text(content)
                    all_entities['skills'].extend(skills)
                    
                    # 提取技术
                    technologies = self._extract_technologies_from_text(content)
                    all_entities['technologies'].extend(technologies)
                    
                    # 提取专业要求
                    majors = self._extract_majors_from_text(content)
                    all_entities['majors'].extend(majors)
                    
                    # 提取导师
                    supervisors = self._extract_supervisors_from_text(content)
                    all_entities['supervisors'].extend(supervisors)
                    
            except Exception as e:
                print(f"  警告: 无法处理 {project_file}: {e}")
        
        # 统计去重后的实体
        unique_entities = {
            'skills': len(set(all_entities['skills'])),
            'technologies': len(set(all_entities['technologies'])),
            'majors': len(set(all_entities['majors'])),
            'supervisors': len(set(all_entities['supervisors']))
        }
        
        total_entities = sum(unique_entities.values())
        
        self.stats['data_collection'] = {
            'projects_processed': total_projects,
            'total_entities_extracted': total_entities,
            'entity_breakdown': unique_entities,
            'total_words_processed': total_words,
            'avg_words_per_project': total_words / total_projects if total_projects > 0 else 0
        }
        
        return self.stats['data_collection']
    
    def quantify_profile_generation(self) -> Dict:
        """量化档案生成阶段"""
        print("👥 量化档案生成阶段...")
        
        profile_files = []
        for root, dirs, files in os.walk("profile_md"):
            for file in files:
                if file.endswith('.md'):
                    profile_files.append(os.path.join(root, file))
        
        total_profiles = len(profile_files)
        profile_lengths = []
        total_courses = []
        total_skills = []
        total_projects = []
        
        for profile_file in profile_files[:50]:  # 采样50个档案避免处理太久
            try:
                with open(profile_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # 统计字数
                    word_count = len(content.split())
                    profile_lengths.append(word_count)
                    
                    # 统计课程数量
                    courses = self._extract_courses_from_profile(content)
                    total_courses.append(len(courses))
                    
                    # 统计技能数量
                    skills = self._extract_skills_from_profile(content)
                    total_skills.append(len(skills))
                    
                    # 统计项目经验数量
                    projects = self._extract_project_experience_from_profile(content)
                    total_projects.append(len(projects))
                    
            except Exception as e:
                print(f"  警告: 无法处理 {profile_file}: {e}")
        
        self.stats['profile_generation'] = {
            'total_profiles_created': total_profiles,
            'sampled_profiles_analyzed': len(profile_lengths),
            'avg_profile_length_words': statistics.mean(profile_lengths) if profile_lengths else 0,
            'median_profile_length_words': statistics.median(profile_lengths) if profile_lengths else 0,
            'avg_courses_per_student': statistics.mean(total_courses) if total_courses else 0,
            'avg_skills_per_student': statistics.mean(total_skills) if total_skills else 0,
            'avg_projects_per_student': statistics.mean(total_projects) if total_projects else 0
        }
        
        return self.stats['profile_generation']
    
    def quantify_graph_construction(self) -> Dict:
        """量化图构建阶段"""
        print("🕸️ 量化图构建阶段...")
        
        # 项目知识图谱统计
        project_kg_stats = self._analyze_kg_directory("individual_kg/projects")
        
        # 学生知识图谱统计
        student_kg_stats = self._analyze_kg_directory("individual_kg/students")
        
        self.stats['graph_construction'] = {
            'project_kgs': project_kg_stats,
            'student_kgs': student_kg_stats
        }
        
        return self.stats['graph_construction']
    
    def _analyze_kg_directory(self, kg_dir: str) -> Dict:
        """分析知识图谱目录"""
        if not os.path.exists(kg_dir):
            return {'total_graphs': 0, 'avg_nodes': 0, 'avg_edges': 0}
        
        stats_files = glob.glob(os.path.join(kg_dir, "*_stats.json"))
        
        total_graphs = len(stats_files)
        node_counts = []
        edge_counts = []
        entity_type_counts = defaultdict(list)
        relation_type_counts = defaultdict(list)
        
        for stats_file in stats_files:
            try:
                with open(stats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    node_counts.append(data.get('total_entities', 0))
                    edge_counts.append(data.get('total_relationships', 0))
                    
                    # 统计实体类型
                    entity_types = data.get('entity_types', {})
                    for entity_type, count in entity_types.items():
                        entity_type_counts[entity_type].append(count)
                    
                    # 统计关系类型
                    relation_types = data.get('relation_types', {})
                    for relation_type, count in relation_types.items():
                        relation_type_counts[relation_type].append(count)
                        
            except Exception as e:
                print(f"  警告: 无法处理 {stats_file}: {e}")
        
        # 计算平均值
        avg_entity_types = {}
        for entity_type, counts in entity_type_counts.items():
            avg_entity_types[entity_type] = statistics.mean(counts) if counts else 0
        
        avg_relation_types = {}
        for relation_type, counts in relation_type_counts.items():
            avg_relation_types[relation_type] = statistics.mean(counts) if counts else 0
        
        return {
            'total_graphs': total_graphs,
            'avg_nodes': statistics.mean(node_counts) if node_counts else 0,
            'avg_edges': statistics.mean(edge_counts) if edge_counts else 0,
            'median_nodes': statistics.median(node_counts) if node_counts else 0,
            'median_edges': statistics.median(edge_counts) if edge_counts else 0,
            'avg_entity_types': avg_entity_types,
            'avg_relation_types': avg_relation_types
        }
    
    def quantify_enhanced_features(self) -> Dict:
        """量化增强功能"""
        print("✨ 量化增强功能...")
        
        # 检查课程-技能连接
        teaches_skill_count = 0
        total_kg_files = 0
        
        for kg_dir in ["individual_kg/students", "individual_kg/projects"]:
            if os.path.exists(kg_dir):
                relationship_files = glob.glob(os.path.join(kg_dir, "*_relationships.json"))
                total_kg_files += len(relationship_files)
                
                for rel_file in relationship_files:
                    try:
                        with open(rel_file, 'r', encoding='utf-8') as f:
                            relationships = json.load(f)
                            for rel in relationships:
                                if rel.get('relation_type') == 'TEACHES_SKILL':
                                    teaches_skill_count += 1
                    except Exception as e:
                        continue
        
        # 检查可视化文件
        visualization_count = len(glob.glob("individual_kg/*/*.png"))
        
        self.stats['enhanced_features'] = {
            'course_skill_connections': teaches_skill_count,
            'total_kg_files_checked': total_kg_files,
            'visualization_files_generated': visualization_count,
            'enhanced_kg_enabled': teaches_skill_count > 0
        }
        
        return self.stats['enhanced_features']
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """从文本中提取技能"""
        skills = []
        text_lower = text.lower()
        
        skill_patterns = [
            'machine learning', 'web development', 'data science', 'cybersecurity',
            'mobile development', 'database', 'networking', 'programming',
            'artificial intelligence', 'blockchain', 'cloud computing'
        ]
        
        for skill in skill_patterns:
            if skill in text_lower:
                skills.append(skill)
        
        return skills
    
    def _extract_technologies_from_text(self, text: str) -> List[str]:
        """从文本中提取技术"""
        technologies = []
        text_lower = text.lower()
        
        tech_patterns = [
            'python', 'java', 'javascript', 'react', 'tensorflow', 'sql',
            'mongodb', 'mysql', 'docker', 'kubernetes', 'aws'
        ]
        
        for tech in tech_patterns:
            if tech in text_lower:
                technologies.append(tech)
        
        return technologies
    
    def _extract_majors_from_text(self, text: str) -> List[str]:
        """从文本中提取专业"""
        majors = []
        
        major_patterns = [
            r'Computer Science', r'Data Science', r'Software Development',
            r'Business Analysis', r'Cyber Security', r'Enterprise Systems'
        ]
        
        for pattern in major_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                majors.append(pattern)
        
        return majors
    
    def _extract_supervisors_from_text(self, text: str) -> List[str]:
        """从文本中提取导师"""
        supervisors = []
        
        # 查找导师模式
        supervisor_pattern = r'Academic Supervisor[^|]*\|[^|]*\|([^|]+)'
        matches = re.findall(supervisor_pattern, text, re.IGNORECASE)
        
        for match in matches:
            supervisor = match.strip()
            if supervisor and supervisor != '':
                supervisors.append(supervisor)
        
        return supervisors
    
    def _extract_courses_from_profile(self, content: str) -> List[str]:
        """从学生档案中提取课程"""
        courses = []
        lines = content.split('\n')
        
        in_courses_section = False
        for line in lines:
            if '## Completed Courses' in line:
                in_courses_section = True
                continue
            elif line.startswith('##'):
                in_courses_section = False
            elif in_courses_section and line.strip().startswith('-'):
                course = line.strip().lstrip('- ').strip()
                if course:
                    courses.append(course)
        
        return courses
    
    def _extract_skills_from_profile(self, content: str) -> List[str]:
        """从学生档案中提取技能"""
        skills = []
        lines = content.split('\n')
        
        in_skills_section = False
        for line in lines:
            if '## Technical Skills' in line:
                in_skills_section = True
                continue
            elif line.startswith('##'):
                in_skills_section = False
            elif in_skills_section and line.strip().startswith('-'):
                skill = line.strip().lstrip('- ').strip()
                if skill:
                    skills.append(skill)
        
        return skills
    
    def _extract_project_experience_from_profile(self, content: str) -> List[str]:
        """从学生档案中提取项目经验"""
        projects = []
        lines = content.split('\n')
        
        in_projects_section = False
        for line in lines:
            if '## Project Experience' in line:
                in_projects_section = True
                continue
            elif line.startswith('##'):
                in_projects_section = False
            elif in_projects_section and line.strip().startswith('###'):
                project = line.strip().lstrip('### ').strip()
                if project:
                    projects.append(project)
        
        return projects
    
    def generate_progress_report(self) -> str:
        """生成进度报告"""
        print("\n📋 生成综合进度报告...")
        
        # 收集所有统计数据
        data_collection = self.quantify_data_collection()
        profile_generation = self.quantify_profile_generation()
        graph_construction = self.quantify_graph_construction()
        enhanced_features = self.quantify_enhanced_features()
        
        # 生成报告
        report = f"""
# 项目匹配系统 - 进度量化报告

## 📊 数据收集阶段 (Data Collection)
- **项目描述处理**: {data_collection['projects_processed']} project descriptions processed
- **实体提取总数**: {data_collection['total_entities_extracted']} entities extracted
  - Skills: {data_collection['entity_breakdown']['skills']}
  - Technologies: {data_collection['entity_breakdown']['technologies']} 
  - Majors: {data_collection['entity_breakdown']['majors']}
  - Supervisors: {data_collection['entity_breakdown']['supervisors']}
- **文本处理**: {data_collection['total_words_processed']:,} words processed
- **平均项目长度**: {data_collection['avg_words_per_project']:.0f} words per project

## 👥 档案生成阶段 (Profile Generation)
- **学生档案创建**: {profile_generation['total_profiles_created']} synthetic student profiles created
- **平均档案长度**: {profile_generation['avg_profile_length_words']:.0f} words per profile
- **档案质量指标**:
  - Average courses per student: {profile_generation['avg_courses_per_student']:.1f}
  - Average skills per student: {profile_generation['avg_skills_per_student']:.1f}
  - Average projects per student: {profile_generation['avg_projects_per_student']:.1f}

## 🕸️ 图构建阶段 (Graph Construction)

### 项目知识图谱 (Project KGs)
- **项目图谱数量**: {graph_construction['project_kgs']['total_graphs']} project KGs constructed
- **平均节点数**: {graph_construction['project_kgs']['avg_nodes']:.1f} nodes per project
- **平均边数**: {graph_construction['project_kgs']['avg_edges']:.1f} edges per project

### 学生知识图谱 (Student KGs)  
- **学生图谱数量**: {graph_construction['student_kgs']['total_graphs']} student KGs built
- **平均节点数**: {graph_construction['student_kgs']['avg_nodes']:.1f} nodes per student
- **平均边数**: {graph_construction['student_kgs']['avg_edges']:.1f} edges per student
"""

        # 添加实体类型分布
        if graph_construction['student_kgs']['avg_entity_types']:
            report += "\n### 学生图谱实体分布:\n"
            for entity_type, avg_count in graph_construction['student_kgs']['avg_entity_types'].items():
                if avg_count > 0:
                    report += f"  - {entity_type}: {avg_count:.1f} average per student\n"

        # 添加增强功能统计
        report += f"""
## ✨ 增强功能阶段 (Enhanced Features)
- **课程-技能连接**: {enhanced_features['course_skill_connections']} TEACHES_SKILL relationships created
- **可视化文件**: {enhanced_features['visualization_files_generated']} visualization files generated
- **增强KG状态**: {'✅ Enabled' if enhanced_features['enhanced_kg_enabled'] else '❌ Not enabled'}

## 📈 总体进展摘要
- ✅ **数据收集**: {data_collection['projects_processed']} projects, {data_collection['total_entities_extracted']} entities
- ✅ **档案生成**: {profile_generation['total_profiles_created']} profiles, avg {profile_generation['avg_profile_length_words']:.0f} words
- ✅ **图构建**: {graph_construction['project_kgs']['total_graphs']} project KGs + {graph_construction['student_kgs']['total_graphs']} student KGs
- {'✅' if enhanced_features['enhanced_kg_enabled'] else '🔄'} **增强功能**: Course→Skill connections {'implemented' if enhanced_features['enhanced_kg_enabled'] else 'in progress'}

---
*报告生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return report

def main():
    """主函数"""
    print("🎯 项目进度量化器")
    print("=" * 60)
    
    quantifier = ProjectProgressQuantifier()
    report = quantifier.generate_progress_report()
    
    # 保存报告
    with open("progress_report.md", 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(report)
    print(f"\n💾 详细报告已保存到: progress_report.md")

if __name__ == "__main__":
    main()








