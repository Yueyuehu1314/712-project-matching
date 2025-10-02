#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
个体知识图谱命令行工具
用于查看和管理个体学生和项目的知识图谱
"""

import os
import json
import argparse
from typing import List, Dict
import glob

class IndividualKGManager:
    """个体知识图谱管理器"""
    
    def __init__(self, base_dir: str = "individual_kg"):
        self.base_dir = base_dir
        self.students_dir = os.path.join(base_dir, "students")
        self.projects_dir = os.path.join(base_dir, "projects")
        self.summary_file = os.path.join(base_dir, "summary_report.json")
    
    def list_students(self, limit: int = None) -> List[Dict]:
        """列出所有学生知识图谱"""
        if not os.path.exists(self.students_dir):
            print("❌ 学生知识图谱目录不存在")
            return []
        
        # 查找所有学生统计文件
        stats_files = glob.glob(os.path.join(self.students_dir, "*_stats.json"))
        students = []
        
        for stats_file in stats_files:
            try:
                with open(stats_file, 'r', encoding='utf-8') as f:
                    stats = json.load(f)
                students.append(stats)
            except Exception as e:
                print(f"❌ 读取文件失败: {stats_file} - {e}")
        
        # 按学生ID排序
        students.sort(key=lambda x: x.get('entity_id', ''))
        
        if limit:
            students = students[:limit]
        
        return students
    
    def list_projects(self, limit: int = None) -> List[Dict]:
        """列出所有项目知识图谱"""
        if not os.path.exists(self.projects_dir):
            print("❌ 项目知识图谱目录不存在")
            return []
        
        # 查找所有项目统计文件
        stats_files = glob.glob(os.path.join(self.projects_dir, "*_stats.json"))
        projects = []
        
        for stats_file in stats_files:
            try:
                with open(stats_file, 'r', encoding='utf-8') as f:
                    stats = json.load(f)
                projects.append(stats)
            except Exception as e:
                print(f"❌ 读取文件失败: {stats_file} - {e}")
        
        # 按项目名称排序
        projects.sort(key=lambda x: x.get('name', ''))
        
        if limit:
            projects = projects[:limit]
        
        return projects
    
    def show_student_details(self, student_id: str):
        """显示学生详细信息"""
        # 查找匹配的学生文件
        pattern = os.path.join(self.students_dir, f"student_{student_id}_*_stats.json")
        stats_files = glob.glob(pattern)
        
        if not stats_files:
            print(f"❌ 未找到学生ID为 {student_id} 的知识图谱")
            return
        
        stats_file = stats_files[0]
        base_name = stats_file.replace("_stats.json", "")
        
        try:
            # 读取统计信息
            with open(stats_file, 'r', encoding='utf-8') as f:
                stats = json.load(f)
            
            # 读取实体信息
            entities_file = base_name + "_entities.json"
            with open(entities_file, 'r', encoding='utf-8') as f:
                entities = json.load(f)
            
            # 读取关系信息
            relationships_file = base_name + "_relationships.json"
            with open(relationships_file, 'r', encoding='utf-8') as f:
                relationships = json.load(f)
            
            self._display_individual_details(stats, entities, relationships, "student")
            
        except Exception as e:
            print(f"❌ 读取学生详细信息失败: {e}")
    
    def show_project_details(self, project_name: str):
        """显示项目详细信息"""
        # 查找匹配的项目文件
        pattern = os.path.join(self.projects_dir, f"project_{project_name}*_stats.json")
        stats_files = glob.glob(pattern)
        
        if not stats_files:
            print(f"❌ 未找到项目名称包含 '{project_name}' 的知识图谱")
            return
        
        if len(stats_files) > 1:
            print(f"🔍 找到多个匹配的项目:")
            for i, file in enumerate(stats_files):
                basename = os.path.basename(file).replace("_stats.json", "")
                print(f"  {i+1}. {basename}")
            choice = input("请选择项目序号: ")
            try:
                stats_file = stats_files[int(choice)-1]
            except (ValueError, IndexError):
                print("❌ 无效的选择")
                return
        else:
            stats_file = stats_files[0]
        
        base_name = stats_file.replace("_stats.json", "")
        
        try:
            # 读取统计信息
            with open(stats_file, 'r', encoding='utf-8') as f:
                stats = json.load(f)
            
            # 读取实体信息
            entities_file = base_name + "_entities.json"
            with open(entities_file, 'r', encoding='utf-8') as f:
                entities = json.load(f)
            
            # 读取关系信息
            relationships_file = base_name + "_relationships.json"
            with open(relationships_file, 'r', encoding='utf-8') as f:
                relationships = json.load(f)
            
            self._display_individual_details(stats, entities, relationships, "project")
            
        except Exception as e:
            print(f"❌ 读取项目详细信息失败: {e}")
    
    def _display_individual_details(self, stats: Dict, entities: List[Dict], 
                                   relationships: List[Dict], kg_type: str):
        """显示个体详细信息"""
        print("=" * 60)
        print(f"🎯 {kg_type.upper()} 知识图谱详情")
        print("=" * 60)
        
        print(f"📋 基本信息:")
        print(f"  名称: {stats['name']}")
        print(f"  ID: {stats['entity_id']}")
        print(f"  类型: {stats['type']}")
        print(f"  创建时间: {stats['created_at']}")
        
        print(f"\n📊 统计信息:")
        print(f"  实体总数: {stats['total_entities']}")
        print(f"  关系总数: {stats['total_relationships']}")
        
        print(f"\n🏷️ 实体类型分布:")
        for entity_type, count in stats['entity_types'].items():
            print(f"  {entity_type}: {count}")
        
        print(f"\n🔗 关系类型分布:")
        for relation_type, count in stats['relation_types'].items():
            print(f"  {relation_type}: {count}")
        
        print(f"\n📄 实体详情:")
        for entity in entities:
            if entity['entity_type'] != kg_type.upper():
                print(f"  - {entity['name']} ({entity['entity_type']})")
        
        print(f"\n🔗 关系详情:")
        for rel in relationships[:10]:  # 只显示前10个关系
            source_name = self._get_entity_name(rel['source_id'], entities)
            target_name = self._get_entity_name(rel['target_id'], entities)
            print(f"  {source_name} --{rel['relation_type']}--> {target_name}")
        
        if len(relationships) > 10:
            print(f"  ... 还有 {len(relationships) - 10} 个关系")
        
        # 显示文件信息
        print(f"\n📂 相关文件:")
        base_name = stats['entity_id'] + "_" + stats['name'].replace(' ', '_').replace('/', '_')
        kg_dir = self.students_dir if kg_type == "student" else self.projects_dir
        print(f"  知识图谱可视化: {kg_dir}/{base_name}_kg.png")
        print(f"  实体数据: {kg_dir}/{base_name}_entities.json")
        print(f"  关系数据: {kg_dir}/{base_name}_relationships.json")
    
    def _get_entity_name(self, entity_id: str, entities: List[Dict]) -> str:
        """获取实体名称"""
        for entity in entities:
            if entity['id'] == entity_id:
                return entity['name']
        return entity_id
    
    def show_summary(self):
        """显示总结报告"""
        if not os.path.exists(self.summary_file):
            print("❌ 总结报告文件不存在")
            return
        
        try:
            with open(self.summary_file, 'r', encoding='utf-8') as f:
                summary = json.load(f)
            
            print("=" * 60)
            print("📊 个体知识图谱总结报告")
            print("=" * 60)
            
            print(f"🎓 学生知识图谱:")
            print(f"  总数: {summary['summary']['total_students']}")
            print(f"  实体总数: {summary['summary']['total_student_entities']}")
            print(f"  关系总数: {summary['summary']['total_student_relationships']}")
            print(f"  平均实体数: {summary['summary']['total_student_entities'] / summary['summary']['total_students']:.1f}")
            print(f"  平均关系数: {summary['summary']['total_student_relationships'] / summary['summary']['total_students']:.1f}")
            
            print(f"\n📋 项目知识图谱:")
            print(f"  总数: {summary['summary']['total_projects']}")
            print(f"  实体总数: {summary['summary']['total_project_entities']}")
            print(f"  关系总数: {summary['summary']['total_project_relationships']}")
            print(f"  平均实体数: {summary['summary']['total_project_entities'] / summary['summary']['total_projects']:.1f}")
            print(f"  平均关系数: {summary['summary']['total_project_relationships'] / summary['summary']['total_projects']:.1f}")
            
            print(f"\n📅 创建时间: {summary['summary']['created_at']}")
            
            # 显示最大和最小的知识图谱
            students = summary['students']
            projects = summary['projects']
            
            if students:
                max_student = max(students, key=lambda x: x['entities'])
                min_student = min(students, key=lambda x: x['entities'])
                print(f"\n🏆 学生知识图谱:")
                print(f"  最大: {max_student['student_name']} ({max_student['entities']} 实体)")
                print(f"  最小: {min_student['student_name']} ({min_student['entities']} 实体)")
            
            if projects:
                max_project = max(projects, key=lambda x: x['entities'])
                min_project = min(projects, key=lambda x: x['entities'])
                print(f"\n🏆 项目知识图谱:")
                print(f"  最大: {max_project['project_title']} ({max_project['entities']} 实体)")
                print(f"  最小: {min_project['project_title']} ({min_project['entities']} 实体)")
            
        except Exception as e:
            print(f"❌ 读取总结报告失败: {e}")
    
    def search_by_keyword(self, keyword: str, kg_type: str = "all"):
        """根据关键词搜索知识图谱"""
        results = []
        
        if kg_type in ["all", "student"]:
            students = self.list_students()
            for student in students:
                if keyword.lower() in student['name'].lower() or keyword in student['entity_id']:
                    results.append(("student", student))
        
        if kg_type in ["all", "project"]:
            projects = self.list_projects()
            for project in projects:
                if keyword.lower() in project['name'].lower():
                    results.append(("project", project))
        
        if not results:
            print(f"❌ 未找到包含关键词 '{keyword}' 的知识图谱")
            return
        
        print(f"🔍 搜索结果 (关键词: '{keyword}'):")
        print("-" * 50)
        
        for i, (kg_type, kg_info) in enumerate(results, 1):
            icon = "🎓" if kg_type == "student" else "📋"
            print(f"{i}. {icon} {kg_info['name']} ({kg_info['entity_id']})")
            print(f"   实体: {kg_info['total_entities']}, 关系: {kg_info['total_relationships']}")

def main():
    parser = argparse.ArgumentParser(description="个体知识图谱管理工具")
    parser.add_argument("command", choices=['list', 'show', 'summary', 'search'], 
                       help="操作命令")
    parser.add_argument("--type", choices=['student', 'project', 'all'], default='all',
                       help="知识图谱类型")
    parser.add_argument("--id", help="学生ID或项目名称")
    parser.add_argument("--keyword", help="搜索关键词")
    parser.add_argument("--limit", type=int, help="限制显示数量")
    
    args = parser.parse_args()
    
    manager = IndividualKGManager()
    
    if args.command == "list":
        if args.type in ["all", "student"]:
            print("🎓 学生知识图谱列表:")
            print("-" * 50)
            students = manager.list_students(args.limit)
            for i, student in enumerate(students, 1):
                print(f"{i:3d}. {student['name']} ({student['entity_id']}) - "
                      f"{student['total_entities']} 实体, {student['total_relationships']} 关系")
        
        if args.type in ["all", "project"]:
            print("\n📋 项目知识图谱列表:")
            print("-" * 50)
            projects = manager.list_projects(args.limit)
            for i, project in enumerate(projects, 1):
                print(f"{i:3d}. {project['name']} - "
                      f"{project['total_entities']} 实体, {project['total_relationships']} 关系")
    
    elif args.command == "show":
        if not args.id:
            print("❌ 请提供 --id 参数")
            return
        
        if args.type == "student":
            manager.show_student_details(args.id)
        elif args.type == "project":
            manager.show_project_details(args.id)
        else:
            print("❌ 请指定 --type student 或 --type project")
    
    elif args.command == "summary":
        manager.show_summary()
    
    elif args.command == "search":
        if not args.keyword:
            print("❌ 请提供 --keyword 参数")
            return
        manager.search_by_keyword(args.keyword, args.type)

if __name__ == "__main__":
    main()
