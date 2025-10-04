#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据质量检查工具
检查学生档案和项目描述的质量，生成诊断报告
"""

import json
import os
import re
from pathlib import Path
from collections import Counter
import numpy as np
from typing import Dict, List, Set, Any


class DataQualityChecker:
    """数据质量检查器"""
    
    def __init__(self, data_dir: str = "data/processed"):
        self.data_dir = Path(data_dir)
        self.students = []
        self.projects = []
        
    def load_student_profiles(self):
        """加载所有学生档案"""
        profile_dir = self.data_dir / "student_profiles"
        
        if not profile_dir.exists():
            print(f"⚠️  学生档案目录不存在: {profile_dir}")
            return
        
        for file in profile_dir.glob("*.json"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    student = json.load(f)
                    self.students.append(student)
            except Exception as e:
                print(f"⚠️  读取 {file} 失败: {e}")
        
        print(f"✅ 加载了 {len(self.students)} 个学生档案")
    
    def load_project_descriptions(self):
        """加载所有项目描述"""
        # 尝试多个可能的位置
        possible_locations = [
            self.data_dir / "enhanced_profiles_md",
            self.data_dir / "project_proposals_md",
            Path("enhanced_profile_md"),
        ]
        
        for loc in possible_locations:
            if loc.exists():
                for file in loc.glob("*.md"):
                    try:
                        with open(file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            self.projects.append({
                                "filename": file.name,
                                "content": content
                            })
                    except Exception as e:
                        print(f"⚠️  读取 {file} 失败: {e}")
        
        print(f"✅ 加载了 {len(self.projects)} 个项目描述")
    
    def extract_skills_from_student(self, student: Dict) -> Set[str]:
        """从学生档案中提取技能"""
        skills = set()
        
        # 从不同字段提取技能
        if isinstance(student, dict):
            # 技能字段
            if "skills" in student:
                if isinstance(student["skills"], list):
                    skills.update(student["skills"])
                elif isinstance(student["skills"], str):
                    skills.update(student["skills"].split(","))
            
            # 课程字段
            if "courses" in student:
                if isinstance(student["courses"], list):
                    skills.update(student["courses"])
            
            if "completed_courses" in student:
                if isinstance(student["completed_courses"], list):
                    skills.update(student["completed_courses"])
            
            # 从文本中提取（如果有profile字段）
            if "profile" in student:
                text_skills = self.extract_skills_from_text(student["profile"])
                skills.update(text_skills)
        
        return skills
    
    def extract_skills_from_project(self, project: Dict) -> Set[str]:
        """从项目描述中提取技能要求"""
        content = project["content"]
        skills = set()
        
        # 查找技能相关的部分
        skill_patterns = [
            r"(?i)skills?[:\s]+([^\n]+)",
            r"(?i)requirements?[:\s]+([^\n]+)",
            r"(?i)technologies?[:\s]+([^\n]+)",
            r"(?i)tools?[:\s]+([^\n]+)",
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                # 简单分词
                words = re.findall(r'\b[A-Za-z]+\b', match)
                skills.update(words)
        
        return skills
    
    def extract_skills_from_text(self, text: str) -> Set[str]:
        """从文本中提取可能的技能关键词"""
        # 常见的技术技能关键词
        tech_keywords = {
            "python", "java", "javascript", "c++", "sql", "machine learning",
            "deep learning", "neural network", "data science", "ai", "ml",
            "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn",
            "web development", "frontend", "backend", "database", "api",
            "cloud", "aws", "azure", "docker", "kubernetes", "git",
            "statistics", "probability", "algorithm", "data structure",
        }
        
        text_lower = text.lower()
        found_skills = set()
        
        for keyword in tech_keywords:
            if keyword in text_lower:
                found_skills.add(keyword)
        
        return found_skills
    
    def check_student_quality(self) -> Dict[str, Any]:
        """检查学生数据质量"""
        if not self.students:
            return {"error": "No student data loaded"}
        
        report = {
            "total_students": len(self.students),
            "students_with_skills": 0,
            "avg_skills_per_student": 0,
            "skill_vocabulary": set(),
            "skill_distribution": [],
            "text_lengths": [],
        }
        
        all_skills = []
        
        for student in self.students:
            skills = self.extract_skills_from_student(student)
            
            if skills:
                report["students_with_skills"] += 1
            
            all_skills.append(len(skills))
            report["skill_vocabulary"].update(skills)
            
            # 文本长度
            if isinstance(student, dict) and "profile" in student:
                report["text_lengths"].append(len(student["profile"]))
        
        report["avg_skills_per_student"] = np.mean(all_skills) if all_skills else 0
        report["std_skills_per_student"] = np.std(all_skills) if all_skills else 0
        report["skill_vocabulary_size"] = len(report["skill_vocabulary"])
        report["skill_distribution"] = all_skills
        
        if report["text_lengths"]:
            report["avg_text_length"] = np.mean(report["text_lengths"])
            report["std_text_length"] = np.std(report["text_lengths"])
        
        # 转换set为list以便JSON序列化
        report["skill_vocabulary"] = sorted(list(report["skill_vocabulary"]))
        
        return report
    
    def check_project_quality(self) -> Dict[str, Any]:
        """检查项目数据质量"""
        if not self.projects:
            return {"error": "No project data loaded"}
        
        report = {
            "total_projects": len(self.projects),
            "projects_with_skills": 0,
            "avg_requirements_per_project": 0,
            "requirement_vocabulary": set(),
            "requirement_distribution": [],
            "text_lengths": [],
        }
        
        all_requirements = []
        
        for project in self.projects:
            skills = self.extract_skills_from_project(project)
            
            if skills:
                report["projects_with_skills"] += 1
            
            all_requirements.append(len(skills))
            report["requirement_vocabulary"].update(skills)
            
            # 文本长度
            report["text_lengths"].append(len(project["content"]))
        
        report["avg_requirements_per_project"] = np.mean(all_requirements) if all_requirements else 0
        report["std_requirements_per_project"] = np.std(all_requirements) if all_requirements else 0
        report["requirement_vocabulary_size"] = len(report["requirement_vocabulary"])
        report["requirement_distribution"] = all_requirements
        
        if report["text_lengths"]:
            report["avg_text_length"] = np.mean(report["text_lengths"])
            report["std_text_length"] = np.std(report["text_lengths"])
        
        # 转换set为list
        report["requirement_vocabulary"] = sorted(list(report["requirement_vocabulary"]))
        
        return report
    
    def check_vocabulary_overlap(self, student_report: Dict, project_report: Dict) -> Dict[str, Any]:
        """检查学生技能和项目需求的词汇重叠"""
        student_vocab = set(student_report.get("skill_vocabulary", []))
        project_vocab = set(project_report.get("requirement_vocabulary", []))
        
        common = student_vocab & project_vocab
        student_only = student_vocab - project_vocab
        project_only = project_vocab - student_vocab
        total = student_vocab | project_vocab
        
        overlap_ratio = len(common) / len(total) if total else 0
        
        return {
            "common_terms": sorted(list(common)),
            "common_count": len(common),
            "student_only_terms": sorted(list(student_only)),
            "student_only_count": len(student_only),
            "project_only_terms": sorted(list(project_only)),
            "project_only_count": len(project_only),
            "total_vocabulary": len(total),
            "overlap_ratio": overlap_ratio,
        }
    
    def generate_report(self, output_file: str = "outputs/data_quality_report.json"):
        """生成完整的数据质量报告"""
        print("\n" + "="*60)
        print("📊 数据质量检查报告")
        print("="*60 + "\n")
        
        # 加载数据
        self.load_student_profiles()
        self.load_project_descriptions()
        
        # 检查质量
        student_report = self.check_student_quality()
        project_report = self.check_project_quality()
        overlap_report = self.check_vocabulary_overlap(student_report, project_report)
        
        # 打印摘要
        print("\n📚 学生档案质量:")
        print(f"  - 总学生数: {student_report.get('total_students', 0)}")
        print(f"  - 有技能信息的学生: {student_report.get('students_with_skills', 0)}")
        print(f"  - 平均技能数: {student_report.get('avg_skills_per_student', 0):.2f} ± {student_report.get('std_skills_per_student', 0):.2f}")
        print(f"  - 技能词汇量: {student_report.get('skill_vocabulary_size', 0)}")
        
        print("\n📁 项目描述质量:")
        print(f"  - 总项目数: {project_report.get('total_projects', 0)}")
        print(f"  - 有需求信息的项目: {project_report.get('projects_with_skills', 0)}")
        print(f"  - 平均需求数: {project_report.get('avg_requirements_per_project', 0):.2f} ± {project_report.get('std_requirements_per_project', 0):.2f}")
        print(f"  - 需求词汇量: {project_report.get('requirement_vocabulary_size', 0)}")
        
        print("\n🔗 词汇重叠分析:")
        print(f"  - 共同词汇: {overlap_report['common_count']}")
        print(f"  - 仅学生有: {overlap_report['student_only_count']}")
        print(f"  - 仅项目有: {overlap_report['project_only_count']}")
        print(f"  - 重叠率: {overlap_report['overlap_ratio']:.2%}")
        
        # 诊断
        print("\n🔍 诊断建议:")
        
        if overlap_report['overlap_ratio'] < 0.1:
            print("  ⚠️  词汇重叠率过低 (<10%)！这可能导致匹配困难。")
            print("     建议：使用语义相似度而非精确匹配")
        
        if student_report.get('avg_skills_per_student', 0) < 5:
            print("  ⚠️  学生平均技能数过少 (<5)！")
            print("     建议：增强学生档案，提取更多隐含技能")
        
        if project_report.get('avg_requirements_per_project', 0) < 5:
            print("  ⚠️  项目平均需求数过少 (<5)！")
            print("     建议：增强项目描述，明确列出技能要求")
        
        if student_report.get('students_with_skills', 0) < student_report.get('total_students', 1) * 0.5:
            print("  ⚠️  超过50%的学生档案缺少技能信息！")
            print("     建议：重新生成或补充学生档案")
        
        # 保存报告
        full_report = {
            "generated_at": str(np.datetime64('now')),
            "students": student_report,
            "projects": project_report,
            "overlap": overlap_report,
        }
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(full_report, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 报告已保存至: {output_path}")
        print("="*60 + "\n")
        
        return full_report


def main():
    """主函数"""
    checker = DataQualityChecker()
    report = checker.generate_report()
    
    # 返回重叠率，用于判断数据质量
    overlap_ratio = report["overlap"]["overlap_ratio"]
    
    if overlap_ratio < 0.1:
        print("\n⚠️  数据质量警告：词汇重叠率过低，建议优先改进数据或使用语义匹配方法！")
        return 1
    else:
        print("\n✅ 数据质量合格，可以继续进行实验。")
        return 0


if __name__ == "__main__":
    exit(main())


