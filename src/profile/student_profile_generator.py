#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于Ollama的学生档案生成系统
根据项目需求生成最适合的学生资料，包括学习背景、修过的课程、项目经历等
"""

import json
import os
import glob
import requests
import time
import hashlib
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class StudentProfile:
    """学生档案数据结构"""
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


class OllamaClient:
    """Ollama客户端"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def is_available(self) -> bool:
        """检查Ollama是否可用"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def list_models(self) -> List[str]:
        """列出可用模型"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except Exception:
            return []
    
    def generate(self, model: str, prompt: str, system: str = None) -> str:
        """生成文本"""
        data = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        if system:
            data["system"] = system
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=data,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '')
            else:
                raise Exception(f"API调用失败: {response.status_code}")
                
        except Exception as e:
            raise Exception(f"生成文本失败: {str(e)}")


class ProjectAnalyzer:
    """项目分析器"""
    
    def __init__(self):
        pass
    
    def extract_project_requirements(self, project_content: str) -> Dict:
        """从项目内容中提取需求信息"""
        requirements = {
            'title': '',
            'major': [],
            'technical_skills': [],
            'domain_knowledge': [],
            'description': '',
            'complexity_level': 'medium'
        }
        
        lines = project_content.split('\n')
        
        # 提取项目标题
        for line in lines:
            if 'Project title' in line or 'title' in line.lower():
                # 寻找标题内容
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) > 2:
                        requirements['title'] = parts[-2].strip()
                break
        
        # 提取专业信息
        for line in lines:
            if 'Information Technology major' in line or 'major' in line.lower():
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) > 2:
                        majors_text = parts[-2].strip()
                        requirements['major'] = [m.strip() for m in majors_text.split(',')]
                break
        
        # 提取描述
        description_lines = []
        in_description = False
        for line in lines:
            if 'Brief description' in line or 'description' in line.lower():
                in_description = True
                continue
            if in_description and line.strip():
                if line.startswith('|') and line.count('|') > 2:
                    # 表格行
                    parts = line.split('|')
                    if len(parts) > 2:
                        description_lines.append(parts[-2].strip())
                elif not line.startswith('+') and not line.startswith('|'):
                    # 非表格行
                    description_lines.append(line.strip())
                    
        requirements['description'] = ' '.join(description_lines)
        
        # 分析技术技能需求
        content_lower = project_content.lower()
        technical_keywords = {
            'machine learning': ['machine learning', 'ml', 'deep learning', 'neural network'],
            'web development': ['web', 'html', 'css', 'javascript', 'react', 'angular'],
            'data science': ['data science', 'python', 'pandas', 'numpy', 'visualization'],
            'cybersecurity': ['security', 'encryption', 'firewall', 'vulnerability'],
            'mobile development': ['mobile', 'android', 'ios', 'app development'],
            'database': ['database', 'sql', 'mysql', 'postgresql', 'mongodb'],
            'networking': ['network', 'tcp/ip', 'wifi', 'routing'],
            'business analysis': ['business analysis', 'requirement', 'stakeholder']
        }
        
        for skill, keywords in technical_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                requirements['technical_skills'].append(skill)
        
        return requirements


class StudentProfileGenerator:
    """学生档案生成器"""
    
    def __init__(self, ollama_client: OllamaClient):
        self.ollama = ollama_client
        self.project_analyzer = ProjectAnalyzer()
        self.unit_content = self._load_unit_content()
    
    def _load_unit_content(self) -> str:
        """加载课程单元内容"""
        unit_file = "/Users/lynn/Documents/GitHub/ProjectMatching/unit_md/qut_IN20_39851_int_cms_unit.md"
        try:
            with open(unit_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"警告: 无法加载课程单元文件: {e}")
            return ""
    
    def _generate_student_name(self, project_title: str, student_index: int = 0) -> str:
        """生成学生姓名"""
        # 使用项目标题和学生索引生成不同的名字
        hash_input = f"{project_title}_{student_index}".encode()
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
    
    def _extract_relevant_units(self, requirements: Dict) -> List[str]:
        """根据项目需求提取相关课程单元"""
        majors = requirements.get('major', [])
        technical_skills = requirements.get('technical_skills', [])
        
        # 基础课程
        base_units = [
            "IFN551 Computer Systems Fundamentals",
            "IFN552 Systems Analysis and Design", 
            "IFN554 Databases",
            "IFN555 Introduction to Programming",
            "IFN556 Object Oriented Programming"
        ]
        
        # 根据专业选择相关课程
        major_units = []
        if any("Computer Science" in major for major in majors):
            major_units.extend([
                "IFN563 Algorithms and Complexity",
                "IFN564 Machine Learning",
                "IFN565 Advanced Programming"
            ])
        
        if any("Data Science" in major for major in majors):
            major_units.extend([
                "IFN619 Data Analytics and Visualisation",
                "IFN564 Machine Learning",
                "IFN632 Advanced Data Analytics"
            ])
        
        if any("Business Analysis" in major for major in majors):
            major_units.extend([
                "IFN614 Business Process Modelling",
                "IFN616 Requirements Engineering",
                "IFN617 Business Intelligence Systems"
            ])
        
        if any("Software Development" in major for major in majors):
            major_units.extend([
                "IFN666 Web Technologies",
                "IFN668 Advanced Software Engineering",
                "IFN670 Mobile Application Development"
            ])
        
        # 根据技术技能添加课程
        skill_units = []
        if "machine learning" in technical_skills:
            skill_units.append("IFN564 Machine Learning")
        if "web development" in technical_skills:
            skill_units.append("IFN666 Web Technologies")
        if "cybersecurity" in technical_skills:
            skill_units.extend([
                "IFN553 Introduction to Security and Networking",
                "IFN623 Cyber Security"
            ])
        
        # 合并并去重
        all_units = list(set(base_units + major_units + skill_units))
        return all_units[:8]  # 限制数量
    
    def generate_profile_markdown(self, project_file: str, student_index: int = 0, model: str = "llama3.2") -> str:
        """为特定项目生成学生档案的markdown内容"""
        
        # 读取项目文件
        with open(project_file, 'r', encoding='utf-8') as f:
            project_content = f.read()
        
        # 分析项目需求
        requirements = self.project_analyzer.extract_project_requirements(project_content)
        
        # 生成学生基本信息
        project_title = requirements.get('title', os.path.basename(project_file))
        student_name = self._generate_student_name(project_title, student_index)
        student_id = f"n{int(hashlib.md5(f'{student_name}_{student_index}'.encode()).hexdigest()[:6], 16):08d}"
        
        # 选择相关课程
        completed_units = self._extract_relevant_units(requirements)
        
        # 使用Ollama生成markdown格式的档案
        system_prompt = """You are a professional student profile generator. Based on given project requirements and course information, generate a realistic but fictional student profile.
The generated student should have the necessary skills and background to complete the project, while reflecting realistic student characteristics.

Please strictly follow this markdown format for the student profile (OUTPUT IN ENGLISH):

# Student Profile

## Basic Information
- **Name**: [Student Name]
- **Student ID**: [Student ID]
- **Major**: [Major Name]
- **Year**: [Year Level]

## Academic Background
[Detailed academic background description, 150-200 words]

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

Ensure the profile is highly relevant to the project requirements and realistic."""
        
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
- Completed Courses: {', '.join(completed_units)}

Please strictly follow the above markdown format to generate a complete student profile, ensuring content matches project requirements. OUTPUT EVERYTHING IN ENGLISH.
"""
        
        response = self.ollama.generate(model, user_prompt, system_prompt)
        
        # 如果生成失败，抛出异常而不是使用模板
        if not response or response.strip() == "":
            raise Exception("LLM生成失败，返回空内容")
        
        return response
    
    def save_profile_markdown(self, project_file: str, markdown_content: str, base_dir: str = "profile_md") -> str:
        """保存学生档案为markdown文件到指定目录结构"""
        
        # 获取项目名称（不包含扩展名）
        project_name = os.path.splitext(os.path.basename(project_file))[0]
        
        # 创建项目子目录
        project_dir = os.path.join(base_dir, project_name)
        os.makedirs(project_dir, exist_ok=True)
        
        # 从markdown内容中提取学生姓名和学号（现在是英文格式）
        import re
        name_match = re.search(r'\*\*Name\*\*:\s*([^\n]+)', markdown_content)
        id_match = re.search(r'\*\*Student ID\*\*:\s*([^\n]+)', markdown_content)
        
        student_name = name_match.group(1).strip() if name_match else "Unknown_Student"
        student_id = id_match.group(1).strip() if id_match else "Unknown_ID"
        
        # 生成文件名：学号_姓名.md
        safe_name = student_name.replace(' ', '_').replace('/', '_')
        filename = f"{student_id}_{safe_name}.md"
        filepath = os.path.join(project_dir, filename)
        
        # 保存markdown文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return filepath


class ConversationManager:
    """对话管理器 - 为每个项目创建独立的对话会话"""
    
    def __init__(self, ollama_client: OllamaClient):
        self.ollama = ollama_client
        self.conversations = {}  # project_id -> conversation_history
    
    def start_new_conversation_from_markdown(self, project_id: str, markdown_content: str) -> str:
        """为特定项目开始新的对话（基于markdown档案）"""
        conversation_id = f"{project_id}_{int(time.time())}"
        
        # 从markdown中提取学生信息
        import re
        name_match = re.search(r'\*\*Name\*\*:\s*([^\n]+)', markdown_content)
        id_match = re.search(r'\*\*Student ID\*\*:\s*([^\n]+)', markdown_content)
        
        student_name = name_match.group(1).strip() if name_match else "Unknown Student"
        student_id = id_match.group(1).strip() if id_match else "Unknown ID"
        
        # 初始化对话历史
        system_prompt = f"""You are now playing the role of student {student_name} (Student ID: {student_id}).

Here is your complete profile information:
{markdown_content}

Please strictly follow the above profile information to play this student role. When answering questions, you should match the background, skills, experience, and personality traits described in the profile. Maintain role consistency and answer questions in English."""

        self.conversations[conversation_id] = {
            'system_prompt': system_prompt,
            'history': [],
            'student_name': student_name,
            'student_id': student_id,
            'markdown_content': markdown_content,
            'created_at': datetime.now().isoformat()
        }
        
        return conversation_id
    
    def chat(self, conversation_id: str, user_message: str, model: str = "llama3.2") -> str:
        """在指定对话中进行聊天"""
        if conversation_id not in self.conversations:
            return "错误：对话不存在"
        
        conversation = self.conversations[conversation_id]
        
        # 构建完整的对话上下文
        context = ""
        for exchange in conversation['history']:
            context += f"User: {exchange['user']}\nStudent: {exchange['assistant']}\n\n"
        
        context += f"User: {user_message}\nStudent: "
        
        try:
            response = self.ollama.generate(
                model=model,
                prompt=context,
                system=conversation['system_prompt']
            )
            
            # 保存对话历史
            conversation['history'].append({
                'user': user_message,
                'assistant': response,
                'timestamp': datetime.now().isoformat()
            })
            
            return response
            
        except Exception as e:
            return f"生成回复失败: {str(e)}"
    
    def get_conversation_info(self, conversation_id: str) -> Dict:
        """获取对话信息"""
        if conversation_id not in self.conversations:
            return {}
        
        conv = self.conversations[conversation_id]
        return {
            'conversation_id': conversation_id,
            'student_name': conv['student_name'],
            'student_id': conv['student_id'],
            'created_at': conv['created_at'],
            'message_count': len(conv['history'])
        }


class ProjectMatchingSystem:
    """主系统类"""
    
    def __init__(self):
        self.ollama = OllamaClient()
        self.generator = StudentProfileGenerator(self.ollama)
        self.conversation_manager = ConversationManager(self.ollama)
        self.profiles = {}  # project_file -> StudentProfile
    
    def initialize(self) -> bool:
        """初始化系统"""
        if not self.ollama.is_available():
            print("错误: Ollama服务不可用。请确保Ollama正在运行。")
            print("启动命令: ollama serve")
            return False
        
        models = self.ollama.list_models()
        if not models:
            print("警告: 没有找到可用的模型。请下载模型，例如：")
            print("ollama pull llama3.2")
            return False
        
        print(f"✓ Ollama已连接，可用模型: {', '.join(models)}")
        return True
    
    def generate_students_for_project(self, project_file: str, num_students: int = 10, model: str = "llama3.2") -> List[str]:
        """为指定项目生成多个学生档案"""
        if not os.path.exists(project_file):
            print(f"错误: 项目文件不存在: {project_file}")
            return []
        
        print(f"正在为项目生成 {num_students} 个学生档案: {os.path.basename(project_file)}")
        generated_files = []
        
        for i in range(num_students):
            print(f"  [{i+1}/{num_students}] 生成学生档案...")
            
            try:
                markdown_content = self.generator.generate_profile_markdown(project_file, i, model)
                
                # 保存到markdown文件
                filepath = self.generator.save_profile_markdown(project_file, markdown_content)
                
                # 提取学生姓名用于显示
                import re
                name_match = re.search(r'\*\*Name\*\*:\s*([^\n]+)', markdown_content)
                student_name = name_match.group(1).strip() if name_match else "Unknown Student"
                
                print(f"    ✓ 已生成: {student_name}")
                generated_files.append(filepath)
                
                # 存储第一个学生的markdown内容用于对话演示
                if i == 0:
                    self.profiles[project_file] = markdown_content
                
            except Exception as e:
                print(f"    ✗ 生成失败: {str(e)}")
                continue
        
        print(f"✓ 项目 {os.path.basename(project_file)} 完成，共生成 {len(generated_files)} 个学生档案")
        return generated_files
    
    def generate_student_for_project(self, project_file: str, model: str = "llama3.2") -> Optional[str]:
        """为指定项目生成单个学生档案（向后兼容）"""
        results = self.generate_students_for_project(project_file, 1, model)
        return results[0] if results else None
    
    def start_conversation_with_student(self, project_file: str) -> Optional[str]:
        """与指定项目的学生开始对话"""
        if project_file not in self.profiles:
            print("请先为该项目生成学生档案")
            return None
        
        markdown_content = self.profiles[project_file]
        conversation_id = self.conversation_manager.start_new_conversation_from_markdown(
            os.path.basename(project_file), markdown_content
        )
        
        # 提取学生姓名用于显示
        import re
        name_match = re.search(r'\*\*Name\*\*:\s*([^\n]+)', markdown_content)
        student_name = name_match.group(1).strip() if name_match else "Unknown Student"
        
        print(f"✓ 已为学生 {student_name} 创建新对话: {conversation_id}")
        return conversation_id
    
    def chat_with_student(self, conversation_id: str, message: str, model: str = "llama3.2") -> str:
        """与学生聊天"""
        return self.conversation_manager.chat(conversation_id, message, model)
    
    def generate_all_profiles(self, num_students_per_project: int = 10, model: str = "llama3.2") -> List[str]:
        """为所有项目批量生成学生档案"""
        projects = self.list_available_projects()
        all_generated_files = []
        
        print(f"正在为 {len(projects)} 个项目各生成 {num_students_per_project} 个学生档案...")
        
        for i, project_file in enumerate(projects, 1):
            print(f"\n[{i}/{len(projects)}] 处理项目: {os.path.basename(project_file)}")
            generated_files = self.generate_students_for_project(project_file, num_students_per_project, model)
            all_generated_files.extend(generated_files)
        
        print(f"\n✓ 批量生成完成！共生成 {len(all_generated_files)} 个学生档案")
        print(f"  - 项目数量: {len(projects)}")
        print(f"  - 每项目学生数: {num_students_per_project}")
        print(f"  - 档案保存路径: profile_md/")
        return all_generated_files
    
    def list_available_projects(self) -> List[str]:
        """列出可用的项目文件"""
        project_dir = "/Users/lynn/Documents/GitHub/ProjectMatching/project_md"
        return glob.glob(os.path.join(project_dir, "*.md"))


def main():
    """主函数 - 演示系统使用"""
    system = ProjectMatchingSystem()
    
    if not system.initialize():
        return
    
    # 为所有项目生成学生档案
    generated_files = system.generate_all_profiles()
    
    print(f"\n✓ 所有学生档案已生成到 profile_md/ 目录")
    print("使用命令行工具进行更多操作:")
    print("  python cli.py list                # 查看项目列表")
    print("  python cli.py chat --project 项目文件  # 与学生对话")


if __name__ == "__main__":
    main()
