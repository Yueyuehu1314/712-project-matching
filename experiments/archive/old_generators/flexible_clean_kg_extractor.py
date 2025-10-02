#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵活清洁知识图谱信息提取代理
放宽匹配条件，增强PD与UO技能交集检测
"""

import os
import json
import re
import string
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple, Optional

class FlexibleCleanKGExtractor:
    """灵活清洁知识图谱提取器"""
    
    def __init__(self):
        # 扩展同义词映射表
        self.synonyms = {
            # AI/ML 相关
            "ai": "machine learning",
            "artificial intelligence": "machine learning",
            "ml": "machine learning",
            "deep learning": "machine learning",
            "neural network": "machine learning",
            "pattern recognition": "machine learning",
            "computer vision": "machine learning",
            "data mining": "machine learning",
            
            # 网络相关
            "wifi": "networking",
            "wireless": "networking", 
            "network": "networking",
            "internet": "networking",
            "protocol": "networking",
            "wifi channel": "networking",
            "csi": "networking",  # Channel State Information
            
            # 数据相关
            "data exploration": "data science",
            "data analysis": "data science",
            "data visualization": "data science",
            "analytics": "data science",
            "big data": "data science",
            
            # 开发相关
            "web dev": "web development",
            "frontend": "web development",
            "backend": "web development",
            "mobile": "mobile development",
            "app": "mobile development",
            
            # 接口相关
            "ux": "user experience",
            "ui": "user interface",
            "hci": "human computer interaction",
            "human computer interaction": "user experience",
            
            # 安全相关
            "cyber security": "cybersecurity",
            "information security": "cybersecurity",
            "security": "cybersecurity",
            
            # 数据库相关
            "db": "database",
            "sql": "database",
            "data management": "database",
            
            # 其他技术
            "iot": "internet of things",
            "api": "programming",
            "algorithm": "programming",
            "coding": "programming"
        }
        
        # 减少过度泛化术语列表，保留更多有用词汇
        self.generic_terms = {
            "computer", "software", "technology", "system", "application",
            "course", "unit", "subject", "study", "student", "learning"
        }
        
        # 停用词
        self.stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "is", "are", "was", "were", "be", "been", "have",
            "has", "had", "will", "would", "could", "should", "may", "might"
        }
        
        # QUT程序映射
        self.program_mapping = {
            'IFN': 'Master of Information Technology',
            'CAB': 'Bachelor of Information Technology', 
            'IAB': 'Bachelor of Information Systems',
            'INB': 'Bachelor of Business Information Systems',
            'INN': 'Bachelor of Innovation',
            'ENN': 'Bachelor of Engineering',
            'MGN': 'Master of Business Administration',
            # 添加缺失的映射
            'QFN': 'QUT Foundation Program',
            'IGB': 'International Business Program',
            'MGZ': 'Management Program'
        }
        
        # 单元代码模式
        self.unit_pattern = r'\b[A-Z]{3}\d{3}\b'
        
        # 放宽参数设置
        self.M = 8  # PD技能top数量 (增加)
        self.K = 5  # 每个UNIT技能top数量 (增加)
    
    def normalize_skill(self, skill: str) -> Optional[str]:
        """灵活标准化技能名称"""
        if not skill:
            return None
        
        skill_lower = skill.lower().strip()
        
        # 过滤过短术语
        if len(skill_lower) < 2:  # 放宽到2个字符
            return None
        
        # 检查同义词映射 (支持部分匹配)
        for original, canonical in self.synonyms.items():
            if original in skill_lower or skill_lower in original:
                return canonical
        
        # 移除标点符号
        skill_clean = skill_lower.translate(str.maketrans('', '', string.punctuation))
        
        # 过滤泛化术语 (只过滤完全匹配)
        if skill_clean in self.generic_terms:
            return None
        
        # 保留有意义的技术术语
        if len(skill_clean) >= 2:
            return skill_clean
        
        return None
    
    def extract_units_from_text(self, text: str) -> List[Tuple[str, str]]:
        """从文本中提取单元代码和名称"""
        units = []
        
        # 查找单元代码
        unit_codes = re.findall(self.unit_pattern, text)
        
        for code in set(unit_codes):
            # 查找对应的单元名称
            pattern = rf'{code}[^\n]*'
            matches = re.findall(pattern, text)
            
            if matches:
                full_text = matches[0]
                # 提取单元名称
                name_part = re.sub(rf'^{code}\s*', '', full_text).strip()
                
                # 清理名称
                name_part = re.sub(r'<[^>]*>', '', name_part)  # 移除HTML标签
                name_part = re.sub(r'\|.*$', '', name_part)    # 移除表格分隔符后内容
                name_part = name_part.strip()
                
                if name_part and len(name_part) > 3:
                    units.append((code, name_part[:50]))
                else:
                    units.append((code, f"Unit {code}"))
            else:
                units.append((code, f"Unit {code}"))
        
        return units
    
    def extract_skills_from_text(self, text: str, context: str = "general") -> Set[str]:
        """从文本中提取技能关键词"""
        skills = set()
        text_lower = text.lower()
        
        # 技术关键词模式 (更宽松)
        tech_patterns = [
            # 编程语言和工具
            r'\b(python|java|javascript|c\+\+|sql|html|css|react|angular|nodejs|tensorflow|pytorch|matlab|r)\b',
            # 技术概念
            r'\b(\w+)\s+(?:learning|recognition|detection|analysis|processing|development|programming|mining|vision)\b',
            # 使用某技术
            r'\b(?:using|with|through|via|implement|develop|design|build|apply|utilize)\s+(\w+(?:\s+\w+){0,2})\b',
            # 学习目标
            r'\b(?:learn|understand|master|acquire|develop)\s+(\w+(?:\s+\w+){0,2})\b',
            # 技能描述
            r'\b(\w+(?:\s+\w+){0,2})\s+(?:skills?|techniques?|methods?|approaches?)\b',
            # 专业术语
            r'\b(machine\s+learning|deep\s+learning|data\s+mining|computer\s+vision|natural\s+language|human\s+computer|web\s+development|mobile\s+development)\b',
            # 缩写
            r'\b(ai|ml|nlp|hci|ux|ui|iot|api|sql|html|css|js)\b'
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if isinstance(match, tuple):
                    for m in match:
                        if m:
                            normalized = self.normalize_skill(m)
                            if normalized:
                                skills.add(normalized)
                else:
                    if match:
                        normalized = self.normalize_skill(match)
                        if normalized:
                            skills.add(normalized)
        
        # 从单词组合中提取技能
        words = re.findall(r'\b\w+\b', text_lower)
        for i in range(len(words)):
            # 单词
            skill = self.normalize_skill(words[i])
            if skill:
                skills.add(skill)
            
            # 双词组合
            if i < len(words) - 1:
                phrase = f"{words[i]} {words[i+1]}"
                skill = self.normalize_skill(phrase)
                if skill:
                    skills.add(skill)
            
            # 三词组合
            if i < len(words) - 2:
                phrase = f"{words[i]} {words[i+1]} {words[i+2]}"
                skill = self.normalize_skill(phrase)
                if skill:
                    skills.add(skill)
        
        return skills
    
    def extract_project_skills(self, project_text: str) -> List[Tuple[str, float]]:
        """从项目描述中提取技能"""
        
        # 提取所有技能
        skills = self.extract_skills_from_text(project_text, "project")
        
        # 计算技能分数
        text_lower = project_text.lower()
        skill_scores = []
        
        for skill in skills:
            score = 0
            skill_words = skill.split()
            
            # 基础频率分数
            for word in skill_words:
                score += text_lower.count(word)
            
            # 位置加权 (标题和开头更重要)
            first_200 = text_lower[:200]
            if any(word in first_200 for word in skill_words):
                score *= 2
            
            # 关键词加权
            important_contexts = ['using', 'with', 'implement', 'develop', 'design', 'apply']
            for context in important_contexts:
                if any(f"{context} {word}" in text_lower for word in skill_words):
                    score += 2
            
            if score > 0:
                skill_scores.append((skill, score))
        
        # 排序并返回top-M
        skill_scores.sort(key=lambda x: x[1], reverse=True)
        return skill_scores[:self.M]
    
    def extract_unit_skills(self, unit_text: str, unit_code: str) -> List[Tuple[str, float]]:
        """从单元大纲中提取技能"""
        
        # 扩展的单元技能映射
        unit_skill_mapping = {
            'IFN680': ['machine learning', 'data science', 'programming'],
            'IFN509': ['data science', 'machine learning', 'programming'],
            'IFN554': ['database', 'programming', 'data science'],
            'IFN666': ['web development', 'mobile development', 'programming'],
            'IFN507': ['networking', 'programming'],
            'IFN541': ['cybersecurity', 'networking'],
            'IFN557': ['web development', 'programming'],
            'IFN563': ['programming', 'software engineering'],
            'IFN555': ['programming'],
            'IFN591': ['user experience', 'web development'],
            'CAB432': ['networking', 'programming'],
            'CAB340': ['programming', 'machine learning'],
            'IFN619': ['data science', 'machine learning'],
            'IFN647': ['data science', 'web development'],
            'IFN648': ['cybersecurity', 'programming'],
            'IFN649': ['networking', 'cybersecurity'],
            'IFN644': ['networking', 'cybersecurity'],
            'IFN623': ['user experience', 'web development'],
            'IFN652': ['programming', 'data science'],
            'IFN657': ['cybersecurity', 'programming'],
            'IFN662': ['programming', 'data science'],
            'IFN664': ['programming', 'machine learning']
        }
        
        # 获取预定义技能
        predefined_skills = unit_skill_mapping.get(unit_code, [])
        
        # 从文本中提取技能
        extracted_skills = self.extract_skills_from_text(unit_text, "unit")
        
        # 合并技能
        all_skills = set(predefined_skills) | extracted_skills
        
        # 计算技能分数
        skill_scores = []
        text_lower = unit_text.lower()
        
        for skill in all_skills:
            # 基础分数：预定义技能分数更高
            base_score = 5.0 if skill in predefined_skills else 1.0
            
            # 文本频率分数
            skill_words = skill.split()
            frequency_score = 0
            for word in skill_words:
                frequency_score += text_lower.count(word)
            
            # 学习目标加权
            learning_contexts = ['learn', 'understand', 'develop', 'design', 'implement', 'apply']
            for context in learning_contexts:
                if any(f"{context} {word}" in text_lower for word in skill_words):
                    frequency_score += 1
            
            total_score = base_score + frequency_score
            
            if total_score > 0:
                skill_scores.append((skill, total_score))
        
        # 排序并返回top-K
        skill_scores.sort(key=lambda x: x[1], reverse=True)
        return skill_scores[:self.K]
    
    def find_intersection_skills(self, project_skills: List[str], 
                               unit_skills_map: Dict[str, List[str]]) -> Set[str]:
        """找出PD与UO的技能交集 (使用灵活匹配)"""
        project_skill_set = set(project_skills)
        
        all_unit_skills = set()
        for unit_skills in unit_skills_map.values():
            all_unit_skills.update(unit_skills)
        
        # 直接交集
        direct_intersection = project_skill_set & all_unit_skills
        
        # 灵活交集 (通过同义词)
        flexible_intersection = set()
        
        for p_skill in project_skill_set:
            for u_skill in all_unit_skills:
                # 检查是否有词汇重叠
                p_words = set(p_skill.split())
                u_words = set(u_skill.split())
                
                if p_words & u_words:  # 有共同词汇
                    flexible_intersection.add(p_skill)
                    flexible_intersection.add(u_skill)
        
        # 合并交集
        total_intersection = direct_intersection | flexible_intersection
        
        return total_intersection
    
    def extract_clean_kg(self, project_file: str, unit_dir: str = "unit_md") -> Tuple[Dict, List[str]]:
        """提取清洁知识图谱"""
        
        # 读取项目描述
        with open(project_file, 'r', encoding='utf-8') as f:
            project_content = f.read()
        
        project_name = self._extract_project_title(project_content)
        project_id = f"project_{os.path.splitext(os.path.basename(project_file))[0]}"
        
        # 提取项目技能
        project_skills_scored = self.extract_project_skills(project_content)
        project_skills = [skill for skill, score in project_skills_scored]
        
        print(f"项目技能 ({len(project_skills)}): {project_skills}")
        
        # 处理单元大纲
        unit_data = {}
        unit_skills_map = {}
        
        if os.path.exists(unit_dir):
            unit_files = [f for f in os.listdir(unit_dir) if f.endswith('.md')]
            
            for unit_file in unit_files:
                unit_path = os.path.join(unit_dir, unit_file)
                with open(unit_path, 'r', encoding='utf-8') as f:
                    unit_content = f.read()
                
                units_in_file = self.extract_units_from_text(unit_content)
                
                for unit_code, unit_name in units_in_file:
                    unit_skills_scored = self.extract_unit_skills(unit_content, unit_code)
                    unit_skills = [skill for skill, score in unit_skills_scored]
                    
                    unit_data[unit_code] = {
                        'name': unit_name,
                        'skills': unit_skills,
                        'scores': dict(unit_skills_scored)
                    }
                    unit_skills_map[unit_code] = unit_skills
        
        print(f"单元数量: {len(unit_data)}")
        all_unit_skills = set()
        for skills in unit_skills_map.values():
            all_unit_skills.update(skills)
        print(f"唯一单元技能: {len(all_unit_skills)}")
        print(f"示例单元技能: {list(all_unit_skills)[:10]}")
        
        # 找出交集技能
        intersection_skills = self.find_intersection_skills(project_skills, unit_skills_map)
        print(f"交集技能 ({len(intersection_skills)}): {list(intersection_skills)}")
        
        if not intersection_skills:
            print("⚠️ 仍然没有发现PD与UO的技能交集")
            print("🔍 尝试分析原因...")
            print(f"项目技能示例: {project_skills[:3]}")
            print(f"单元技能示例: {list(all_unit_skills)[:5]}")
            return {"nodes": [], "edges": []}, []
        
        # 构建知识图谱
        nodes = []
        edges = []
        triples = []
        
        # 1. 添加项目节点
        nodes.append({
            "id": project_id,
            "type": "PROJECT", 
            "name": project_name
        })
        
        # 2. 添加交集技能节点和项目→技能关系
        project_skill_scores = dict(project_skills_scored)
        for skill in intersection_skills:
            skill_id = f"skill_{skill.replace(' ', '_')}"
            
            # 添加技能节点
            nodes.append({
                "id": skill_id,
                "type": "SKILL",
                "name": skill
            })
            
            # 添加项目→技能关系
            weight = project_skill_scores.get(skill, 1.0)
            edges.append({
                "source": project_id,
                "target": skill_id,
                "relation": "requires",
                "weight": weight
            })
            
            triples.append(f"{project_name} requires {skill}")
        
        # 3. 添加单元节点和关系
        programs_added = set()
        
        for unit_code, unit_info in unit_data.items():
            unit_id = f"unit_{unit_code}"
            unit_name = f"{unit_code} {unit_info['name']}"
            
            # 检查该单元是否教授交集技能
            unit_intersection_skills = set(unit_info['skills']) & intersection_skills
            if not unit_intersection_skills:
                continue
            
            # 添加单元节点
            nodes.append({
                "id": unit_id,
                "type": "UNIT",
                "name": unit_name
            })
            
            # 添加程序节点和单元→程序关系
            unit_prefix = unit_code[:3]
            program_name = self.program_mapping.get(unit_prefix, f"{unit_prefix} Program")
            program_id = f"program_{unit_prefix}"
            
            if program_id not in programs_added:
                nodes.append({
                    "id": program_id,
                    "type": "PROGRAM",
                    "name": program_name
                })
                programs_added.add(program_id)
            
            # 单元→程序关系
            edges.append({
                "source": unit_id,
                "target": program_id,
                "relation": "belongs_to", 
                "weight": 1.0
            })
            
            triples.append(f"{unit_name} belongs_to {program_name}")
            
            # 添加单元→技能关系
            unit_skill_scores = unit_info['scores']
            
            for skill in unit_intersection_skills:
                skill_id = f"skill_{skill.replace(' ', '_')}"
                weight = unit_skill_scores.get(skill, 1.0)
                
                edges.append({
                    "source": unit_id,
                    "target": skill_id,
                    "relation": "teaches",
                    "weight": weight
                })
                
                triples.append(f"{unit_name} teaches {skill}")
        
        # 构建最终图结构
        kg_data = {
            "nodes": nodes,
            "edges": edges
        }
        
        return kg_data, triples
    
    def _extract_project_title(self, content: str) -> str:
        """提取项目标题"""
        lines = content.split('\n')
        
        # 查找表格格式标题
        for line in lines:
            if 'project title' in line.lower() and '|' in line:
                parts = line.split('|')
                if len(parts) >= 3:
                    title = parts[-2].strip()
                    if title and len(title) > 3:
                        return title
        
        # 查找Markdown标题
        for line in lines:
            if line.startswith('# '):
                return line[2:].strip()
        
        return "Unknown Project"
    
    def export_triples(self, triples: List[str], output_file: str):
        """导出三元组格式"""
        with open(output_file, 'w', encoding='utf-8') as f:
            for triple in triples:
                f.write(f"{triple}\n")
        print(f"✅ 三元组导出: {output_file}")
    
    def export_json(self, kg_data: Dict, output_file: str):
        """导出JSON格式"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(kg_data, f, ensure_ascii=False, indent=2)
        print(f"✅ JSON导出: {output_file}")
    
    def process_project(self, project_file: str, output_dir: str = None):
        """处理单个项目"""
        
        project_name = os.path.splitext(os.path.basename(project_file))[0]
        print(f"\n🔍 处理项目: {project_name}")
        
        try:
            # 提取知识图谱
            kg_data, triples = self.extract_clean_kg(project_file)
            
            if not kg_data["nodes"]:
                print("⚠️ 没有生成有效的知识图谱（无技能交集）")
                return False
            
            # 设置输出目录
            if not output_dir:
                output_dir = f"flexible_clean_kg_output/{project_name}"
            os.makedirs(output_dir, exist_ok=True)
            
            # 导出文件
            self.export_triples(triples, os.path.join(output_dir, f"{project_name}_triples.txt"))
            self.export_json(kg_data, os.path.join(output_dir, f"{project_name}_kg.json"))
            
            # 生成统计
            stats = {
                "project": project_name,
                "nodes": len(kg_data["nodes"]),
                "edges": len(kg_data["edges"]),
                "triples": len(triples),
                "node_types": Counter(node["type"] for node in kg_data["nodes"]),
                "relation_types": Counter(edge["relation"] for edge in kg_data["edges"])
            }
            
            with open(os.path.join(output_dir, f"{project_name}_stats.json"), 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 成功生成: {stats['nodes']} 节点, {stats['edges']} 边, {stats['triples']} 三元组")
            return True
            
        except Exception as e:
            print(f"❌ 处理失败: {e}")
            return False

def main():
    """主函数"""
    print("🧠 灵活清洁知识图谱信息提取代理")
    print("=" * 60)
    print("📋 改进: 放宽匹配条件，增强交集检测")
    print("🎯 输出: 三元组 + JSON")
    print("=" * 60)
    
    extractor = FlexibleCleanKGExtractor()
    
    # 处理示例项目
    test_project = "project_md/HAR_WiFi_Proposal_Zhenguo-1.md"
    
    if os.path.exists(test_project):
        extractor.process_project(test_project)
    else:
        print(f"❌ 示例项目文件不存在: {test_project}")
    
    print("\n🎉 处理完成!")

if __name__ == "__main__":
    main()
