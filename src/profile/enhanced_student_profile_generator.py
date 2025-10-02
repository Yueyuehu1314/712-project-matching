#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版学生档案生成系统
支持基于不同课程背景(IN20/IN27)生成学生档案
结合项目描述和课程大纲信息
"""

import json
import os
import glob
import requests
import time
import hashlib
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class EnhancedStudentProfile:
    """增强版学生档案数据结构"""
    name: str
    student_id: str
    learning_background: str
    completed_units: List[str]
    previous_projects: List[str]
    work_experience: str
    interests: List[str]
    skills: List[str]
    major: str
    year_of_study: int
    generated_for_project: str
    generation_time: str
    course_background: str  # "IN20" or "IN27"
    unit_outline_content: str  # 课程大纲内容


class OllamaClient:
    """Ollama客户端"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def generate(self, model: str, prompt: str, system_prompt: str = "") -> str:
        """生成文本"""
        try:
            url = f"{self.base_url}/api/generate"
            data = {
                "model": model,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False
            }
            
            response = self.session.post(url, json=data, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
            
        except Exception as e:
            print(f"Ollama生成失败: {e}")
            return ""


class ProjectAnalyzer:
    """项目分析器"""
    
    def extract_project_requirements(self, project_content: str) -> Dict:
        """提取项目需求"""
        requirements = {
            'title': '',
            'description': '',
            'technical_skills': [],
            'major': [],
            'difficulty_level': 'intermediate',
            'project_type': 'research'
        }
        
        # 简单的文本分析提取项目信息
        lines = project_content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 提取标题
            if line.startswith('#') and not requirements['title']:
                requirements['title'] = line.replace('#', '').strip()
            
            # 提取技术技能关键词
            tech_keywords = ['python', 'machine learning', 'data analysis', 'statistics', 
                           'programming', 'database', 'visualization', 'algorithm']
            for keyword in tech_keywords:
                if keyword.lower() in line.lower():
                    if keyword not in requirements['technical_skills']:
                        requirements['technical_skills'].append(keyword)
        
        return requirements


class EnhancedStudentProfileGenerator:
    """增强版学生档案生成器"""
    
    def __init__(self, ollama_client: OllamaClient):
        self.ollama = ollama_client
        self.project_analyzer = ProjectAnalyzer()
        self.in20_content = self._load_unit_content("IN20")
        self.in27_content = self._load_unit_content("IN27")
    
    def _load_unit_content(self, course_code: str) -> str:
        """加载课程单元内容"""
        if course_code == "IN20":
            unit_file = "/Users/lynn/Documents/GitHub/ProjectMatching/unit_md/qut_IN20_39851_int_cms_unit.md"
        elif course_code == "IN27":
            unit_file = "/Users/lynn/Documents/GitHub/ProjectMatching/unit_md/qut_IN27_44569.md"
        else:
            return ""
        
        try:
            with open(unit_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"警告: 无法加载课程单元文件 {course_code}: {e}")
            return ""
    
    def _generate_student_name(self, project_title: str, student_index: int = 0, course_background: str = "IN20") -> str:
        """生成学生姓名"""
        hash_input = f"{project_title}_{student_index}_{course_background}".encode()
        hash_value = hashlib.md5(hash_input).hexdigest()
        
        first_names = [
            "Alex", "Jordan", "Taylor", "Casey", "Morgan", "Riley", "Avery", "Quinn",
            "Jamie", "Blake", "Drew", "Sage", "River", "Phoenix", "Skylar", "Rowan",
            "Cameron", "Devon", "Emery", "Finley", "Harper", "Hayden", "Kendall", "Logan",
            "Madison", "Parker", "Peyton", "Reagan", "Reese", "Rory", "Sydney", "Tyler"
        ]
        
        last_names = [
            "Anderson", "Brown", "Chen", "Davis", "Garcia", "Hernandez", "Johnson", "Jones",
            "Lee", "Lopez", "Martinez", "Miller", "Rodriguez", "Smith", "Thompson", "Williams",
            "Wilson", "Moore", "Taylor", "Jackson", "White", "Harris", "Martin", "Young",
            "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores"
        ]
        
        first_idx = int(hash_value[:2], 16) % len(first_names)
        last_idx = int(hash_value[2:4], 16) % len(last_names)
        
        return f"{first_names[first_idx]} {last_names[last_idx]}"
    
    def _generate_student_id(self, project_title: str, student_index: int, course_background: str) -> str:
        """生成学生ID"""
        hash_input = f"{project_title}_{student_index}_{course_background}".encode()
        hash_value = hashlib.md5(hash_input).hexdigest()
        return f"n{hash_value[:8]}"
    
    def _extract_relevant_units(self, requirements: Dict, course_background: str) -> List[str]:
        """根据课程背景提取相关课程单元"""
        if course_background == "IN20":
            # IN20 (Computer Science) 相关课程
            base_units = [
                "IFN712 - Research Project",
                "IFN701 - Research Methods",
                "IFN702 - Advanced Programming",
                "IFN703 - Software Engineering",
                "IFN704 - Database Systems"
            ]
        else:  # IN27 (Data Analytics)
            # IN27 (Data Analytics) 相关课程
            base_units = [
                "IFN712 - Research Project", 
                "IFN701 - Research Methods",
                "IFN705 - Data Analytics Fundamentals",
                "IFN706 - Statistical Methods",
                "IFN707 - Machine Learning",
                "IFN708 - Data Visualization"
            ]
        
        # 根据项目需求添加相关课程
        if any(keyword in str(requirements.get('technical_skills', [])).lower() 
               for keyword in ['machine learning', 'ai', 'neural']):
            base_units.append("IFN709 - Advanced Machine Learning")
        
        if any(keyword in str(requirements.get('technical_skills', [])).lower() 
               for keyword in ['database', 'sql', 'data']):
            base_units.append("IFN710 - Big Data Technologies")
        
        return base_units[:8]  # 限制课程数量
    
    def generate_enhanced_profile_markdown(self, project_file: str, student_index: int = 0, 
                                         course_background: str = "IN20", model: str = "qwen3:32b") -> str:
        """生成增强版学生档案Markdown"""
        if not os.path.exists(project_file):
            raise FileNotFoundError(f"项目文件不存在: {project_file}")
        
        # 读取项目内容
        with open(project_file, 'r', encoding='utf-8') as f:
            project_content = f.read()
        
        # 分析项目需求
        requirements = self.project_analyzer.extract_project_requirements(project_content)
        
        # 生成学生基本信息
        student_name = self._generate_student_name(requirements.get('title', 'Unknown'), student_index, course_background)
        student_id = self._generate_student_id(requirements.get('title', 'Unknown'), student_index, course_background)
        
        # 根据课程背景确定专业
        if course_background == "IN20":
            major = "Computer Science"
        else:  # IN27
            major = "Data Analytics"
        
        # 提取相关课程
        completed_units = self._extract_relevant_units(requirements, course_background)
        
        # 获取课程大纲内容
        unit_content = self.in20_content if course_background == "IN20" else self.in27_content
        
        # 构建系统提示
        system_prompt = f"""You are a professional student profile generator. Based on given project requirements and course information, generate a realistic but fictional student profile.

The student has a {course_background} background ({major} major) and should have the necessary skills and background to complete the project, while reflecting realistic student characteristics.

Please strictly follow this markdown format for the student profile (OUTPUT IN ENGLISH):

# Student Profile

## Basic Information
- **Name**: [Student Name]
- **Student ID**: [Student ID]
- **Major**: {major}
- **Year**: [Year Level]
- **Course Background**: {course_background}

## Academic Background
[Detailed academic background description, 150-200 words, emphasizing {course_background} background]

## Completed Courses
- [Course 1]
- [Course 2]
- [Course 3]
...

## Project Experience
### [Project Name 1]
[Project description, around 50 words]

### [Project Name 2]
[Project description, around 50 words]

### [Project Name 3]
[Project description, around 50 words]

## Work Experience
[Work experience description, within 100 words]

## Interests
- [Interest 1]
- [Interest 2]
- [Interest 3]
- [Interest 4]
- [Interest 5]

## Technical Skills
- [Skill 1]
- [Skill 2]
- [Skill 3]
- [Skill 4]
- [Skill 5]
- [Skill 6]
- [Skill 7]
- [Skill 8]

## Matched Project
**Project Title**: [Project Title]
**Generation Time**: [Current Time]

Ensure the profile is highly relevant to the project requirements and realistic for a {course_background} background student."""
        
        user_prompt = f"""
Please generate a suitable student profile for the following project:

**Project Information:**
- Project Title: {requirements.get('title', 'Unknown')}
- Project Description: {requirements.get('description', '')[:500]}...
- Required Majors: {', '.join(requirements.get('major', []))}
- Technical Skills: {', '.join(requirements.get('technical_skills', []))}

**Student Basic Information:**
- Name: {student_name}
- Student ID: {student_id}
- Course Background: {course_background}
- Completed Courses: {', '.join(completed_units)}

**Course Outline Information ({course_background}):**
{unit_content[:1000]}...

Please strictly follow the above markdown format to generate a complete student profile, ensuring content matches project requirements and reflects {course_background} background. OUTPUT EVERYTHING IN ENGLISH.
"""
        
        response = self.ollama.generate(model, user_prompt, system_prompt)
        
        if not response or response.strip() == "":
            raise Exception("LLM生成失败，返回空内容")
        
        return response
    
    def generate_mixed_student_profiles(self, project_file: str, total_students: int = 10, model: str = "qwen3:32b") -> List[str]:
        """为项目生成混合背景的学生档案"""
        # 50% IN20背景学生，50% IN27背景学生
        in20_count = total_students // 2
        in27_count = total_students - in20_count
        
        generated_files = []
        
        print(f"正在为项目生成 {total_students} 个学生档案 (IN20: {in20_count}, IN27: {in27_count})")
        
        # 生成IN20背景学生
        for i in range(in20_count):
            print(f"  [{i+1}/{in20_count}] 生成IN20背景学生档案...")
            try:
                markdown_content = self.generate_enhanced_profile_markdown(
                    project_file, i, "IN20", model
                )
                
                filepath = self._save_profile_markdown(project_file, markdown_content, f"IN20_{i}")
                generated_files.append(filepath)
                
                # 提取学生姓名用于显示
                import re
                name_match = re.search(r'\*\*Name\*\*:\s*([^\n]+)', markdown_content)
                student_name = name_match.group(1).strip() if name_match else "Unknown Student"
                print(f"    ✓ 已生成IN20学生: {student_name}")
                
            except Exception as e:
                print(f"    ✗ IN20学生生成失败: {str(e)}")
                continue
        
        # 生成IN27背景学生
        for i in range(in27_count):
            print(f"  [{i+1}/{in27_count}] 生成IN27背景学生档案...")
            try:
                markdown_content = self.generate_enhanced_profile_markdown(
                    project_file, i, "IN27", model
                )
                
                filepath = self._save_profile_markdown(project_file, markdown_content, f"IN27_{i}")
                generated_files.append(filepath)
                
                # 提取学生姓名用于显示
                import re
                name_match = re.search(r'\*\*Name\*\*:\s*([^\n]+)', markdown_content)
                student_name = name_match.group(1).strip() if name_match else "Unknown Student"
                print(f"    ✓ 已生成IN27学生: {student_name}")
                
            except Exception as e:
                print(f"    ✗ IN27学生生成失败: {str(e)}")
                continue
        
        print(f"✓ 项目完成，共生成 {len(generated_files)} 个学生档案")
        return generated_files
    
    def _save_profile_markdown(self, project_file: str, markdown_content: str, 
                              student_suffix: str, base_dir: str = "enhanced_profile_md") -> str:
        """保存学生档案Markdown文件"""
        # 创建输出目录
        os.makedirs(base_dir, exist_ok=True)
        
        # 生成文件名
        project_name = os.path.splitext(os.path.basename(project_file))[0]
        filename = f"{project_name}_{student_suffix}.md"
        filepath = os.path.join(base_dir, filename)
        
        # 保存文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return filepath


class EnhancedProjectMatchingSystem:
    """增强版项目匹配系统"""
    
    def __init__(self):
        self.ollama = OllamaClient()
        self.generator = EnhancedStudentProfileGenerator(self.ollama)
        self.profiles = {}
    
    def initialize(self) -> bool:
        """初始化系统"""
        try:
            # 测试Ollama连接
            response = self.ollama.generate("qwen3:32b", "Hello", "You are a helpful assistant.")
            if not response:
                print("❌ Ollama连接失败")
                return False
            
            print("✅ 增强版项目匹配系统初始化成功")
            return True
            
        except Exception as e:
            print(f"❌ 系统初始化失败: {e}")
            return False
    
    def generate_students_for_project(self, project_file: str, num_students: int = 10, model: str = "qwen3:32b") -> List[str]:
        """为指定项目生成混合背景的学生档案"""
        if not os.path.exists(project_file):
            print(f"错误: 项目文件不存在: {project_file}")
            return []
        
        print(f"正在为项目生成 {num_students} 个混合背景学生档案: {os.path.basename(project_file)}")
        return self.generator.generate_mixed_student_profiles(project_file, num_students, model)


def main():
    """主函数"""
    print("🚀 增强版学生档案生成系统")
    print("=" * 50)
    
    # 初始化系统
    system = EnhancedProjectMatchingSystem()
    if not system.initialize():
        return
    
    # 获取项目文件列表
    project_files = glob.glob("project_md/*.md")
    if not project_files:
        print("❌ 未找到项目文件")
        return
    
    print(f"📁 找到 {len(project_files)} 个项目文件")
    
    # 为每个项目生成学生档案
    for project_file in project_files[:2]:  # 先处理前2个项目作为测试
        print(f"\n📋 处理项目: {os.path.basename(project_file)}")
        try:
            generated_files = system.generate_students_for_project(project_file, 6)  # 每个项目生成6个学生
            print(f"✅ 项目完成，生成 {len(generated_files)} 个学生档案")
        except Exception as e:
            print(f"❌ 项目处理失败: {e}")
    
    print("\n🎉 增强版学生档案生成完成！")


if __name__ == "__main__":
    main()
