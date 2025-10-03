#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于增强知识图谱的学生-项目匹配系统

匹配策略：
1. 技能匹配 (Skills Matching)
   - 学生的技能 vs 项目需要的技能
   - 考虑技能来源权重（课程 > 项目经验 > 自学）
   
2. 专业匹配 (Major Matching)
   - 学生的专业 vs 项目适合的专业
   
3. 课程匹配 (Course Matching)
   - 学生修过的课程 vs 项目相关的课程（通过UNITs）
   
4. 兴趣匹配 (Interest Matching)
   - 学生的研究兴趣 vs 项目主题

综合评分 = 技能分 * 0.5 + 专业分 * 0.2 + 课程分 * 0.2 + 兴趣分 * 0.1
"""

import os
import json
import glob
from typing import Dict, List, Tuple, Set
from collections import defaultdict
from dataclasses import dataclass, asdict
import re
from datetime import datetime


@dataclass
class MatchScore:
    """匹配分数详情"""
    student_id: str
    student_name: str
    project_name: str
    total_score: float
    skill_score: float
    major_score: float
    course_score: float
    interest_score: float
    matched_skills: List[str]
    matched_courses: List[str]
    matched_interests: List[str]
    details: Dict


class KGEnhancedMatcher:
    """基于增强知识图谱的匹配器"""
    
    def __init__(self, 
                 student_kg_dir: str = "outputs/knowledge_graphs/enhanced_student_kg",
                 project_kg_dir: str = "outputs/knowledge_graphs/enhanced_in20_in27",
                 output_dir: str = "outputs/matching/PD+UO_STUDENT_matching"):
        
        self.student_kg_dir = student_kg_dir
        self.project_kg_dir = project_kg_dir
        self.output_dir = output_dir
        
        # 权重配置
        self.weights = {
            'skill': 0.5,
            'major': 0.2,
            'course': 0.2,
            'interest': 0.1
        }
        
        # 技能来源权重（学生KG中的技能权重）
        self.skill_source_weights = {
            'course': 0.8,      # 课程获得的技能
            'project': 0.7,     # 项目获得的技能
            'self-taught': 0.6  # 自学的技能
        }
        
        os.makedirs(output_dir, exist_ok=True)
        
    def normalize_name(self, name: str) -> str:
        """标准化名称（用于匹配）"""
        # 转小写，移除特殊字符，移除多余空格
        name = name.lower()
        name = re.sub(r'[^\w\s]', ' ', name)
        name = re.sub(r'\s+', ' ', name)
        return name.strip()
    
    def load_student_kg(self, json_file: str) -> Dict:
        """加载学生知识图谱"""
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_project_kg(self, json_file: str) -> Dict:
        """加载项目知识图谱"""
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def extract_student_info(self, student_kg: Dict) -> Dict:
        """从学生KG提取信息"""
        info = {
            'id': '',
            'name': '',
            'major': '',
            'skills': {},  # skill_name -> weight
            'courses': set(),
            'interests': set()
        }
        
        # 创建实体映射
        entity_map = {e['id']: e for e in student_kg['entities']}
        
        # 找到学生节点
        student_node = None
        for entity in student_kg['entities']:
            if entity['entity_type'] == 'STUDENT':
                student_node = entity
                info['id'] = entity['properties'].get('student_id', '')
                info['name'] = entity['name']
                info['major'] = entity['properties'].get('major', '')
                break
        
        if not student_node:
            return info
        
        student_id = student_node['id']
        
        # 提取技能、课程、兴趣
        for rel in student_kg['relationships']:
            if rel['source_id'] == student_id:
                target = entity_map.get(rel['target_id'])
                if not target:
                    continue
                
                # 学生的技能
                if rel['relation_type'] == 'HAS_SKILL':
                    skill_name = self.normalize_name(target['name'])
                    weight = rel.get('weight', 0.6)
                    # 考虑技能来源
                    source = rel.get('properties', {}).get('source', 'self-taught')
                    source_weight = self.skill_source_weights.get(source, 0.6)
                    info['skills'][skill_name] = weight * source_weight
                
                # 学生的课程
                elif rel['relation_type'] == 'COMPLETED_COURSE':
                    course_name = self.normalize_name(target['name'])
                    info['courses'].add(course_name)
                
                # 学生的兴趣
                elif rel['relation_type'] == 'INTERESTED_IN':
                    interest_name = self.normalize_name(target['name'])
                    info['interests'].add(interest_name)
        
        return info
    
    def extract_project_info(self, project_kg: Dict) -> Dict:
        """从项目KG提取信息"""
        info = {
            'name': project_kg.get('project', ''),
            'title': project_kg.get('project_title', ''),
            'skills': {},  # skill_name -> weight
            'majors': set(),
            'units': set()
        }
        
        # 创建节点映射
        node_map = {n['id']: n for n in project_kg['nodes']}
        
        # 找到项目节点
        project_node = None
        for node in project_kg['nodes']:
            if node['type'] == 'PROJECT':
                project_node = node
                break
        
        if not project_node:
            return info
        
        project_id = project_node['id']
        
        # 提取技能、专业、课程
        for edge in project_kg['edges']:
            # 项目需要的技能
            if edge['source'] == project_id and edge['relation'] == 'REQUIRES_SKILL':
                target_node = node_map.get(edge['target'])
                if target_node and target_node['type'] == 'SKILL':
                    skill_name = self.normalize_name(target_node['name'])
                    weight = edge.get('weight', 1.0)
                    info['skills'][skill_name] = weight
            
            # 项目适合的专业
            elif edge['source'] == project_id and edge['relation'] == 'SUITABLE_FOR_MAJOR':
                target_node = node_map.get(edge['target'])
                if target_node and target_node['type'] == 'MAJOR':
                    major_name = self.normalize_name(target_node['name'])
                    info['majors'].add(major_name)
            
            # 提取UNIT信息（用于课程匹配）
            elif edge['relation'] in ['TAUGHT_IN', 'REQUIRES_UNIT']:
                target_node = node_map.get(edge['target'])
                if target_node and target_node['type'] == 'UNIT':
                    unit_name = self.normalize_name(target_node['name'])
                    info['units'].add(unit_name)
        
        return info
    
    def calculate_skill_match(self, student_skills: Dict[str, float], 
                             project_skills: Dict[str, float]) -> Tuple[float, List[str]]:
        """
        计算技能匹配分数
        返回: (分数, 匹配的技能列表)
        """
        if not project_skills:
            return 0.0, []
        
        matched_skills = []
        total_weight = 0.0
        matched_weight = 0.0
        
        for skill, proj_weight in project_skills.items():
            total_weight += proj_weight
            
            if skill in student_skills:
                # 匹配成功
                stud_weight = student_skills[skill]
                # 综合考虑学生权重和项目权重
                matched_weight += proj_weight * stud_weight
                matched_skills.append(skill)
        
        score = (matched_weight / total_weight) if total_weight > 0 else 0.0
        return score, matched_skills
    
    def calculate_major_match(self, student_major: str, project_majors: Set[str]) -> float:
        """计算专业匹配分数"""
        if not project_majors:
            return 0.0
        
        student_major_norm = self.normalize_name(student_major)
        
        # 完全匹配
        if student_major_norm in project_majors:
            return 1.0
        
        # 部分匹配（关键词匹配）
        student_keywords = set(student_major_norm.split())
        for proj_major in project_majors:
            proj_keywords = set(proj_major.split())
            overlap = student_keywords & proj_keywords
            if overlap:
                # 基于重叠关键词的相似度
                similarity = len(overlap) / max(len(student_keywords), len(proj_keywords))
                return similarity * 0.8  # 部分匹配最高0.8
        
        return 0.0
    
    def calculate_course_match(self, student_courses: Set[str], 
                               project_units: Set[str]) -> Tuple[float, List[str]]:
        """
        计算课程匹配分数（基于课程代码匹配）
        返回: (分数, 匹配的课程列表)
        """
        if not project_units:
            return 0.0, []
        
        matched_courses = []
        
        # 提取课程代码（如IFN668, CAB302等）
        def extract_course_codes(text: str) -> Set[str]:
            # 匹配类似 IFN668, CAB302 的模式
            pattern = r'\b[A-Z]{3}\d{3}\b'
            return set(re.findall(pattern, text.upper()))
        
        # 学生的课程代码
        student_codes = set()
        for course in student_courses:
            student_codes.update(extract_course_codes(course))
        
        # 项目的课程代码
        project_codes = set()
        for unit in project_units:
            project_codes.update(extract_course_codes(unit))
        
        if not project_codes:
            return 0.0, []
        
        # 计算匹配
        matched_codes = student_codes & project_codes
        matched_courses = list(matched_codes)
        
        score = len(matched_codes) / len(project_codes)
        return score, matched_courses
    
    def calculate_interest_match(self, student_interests: Set[str], 
                                 project_title: str) -> Tuple[float, List[str]]:
        """
        计算兴趣匹配分数
        返回: (分数, 匹配的兴趣列表)
        """
        if not student_interests:
            return 0.0, []
        
        project_title_norm = self.normalize_name(project_title)
        project_words = set(project_title_norm.split())
        
        matched_interests = []
        max_similarity = 0.0
        
        for interest in student_interests:
            interest_words = set(interest.split())
            overlap = interest_words & project_words
            
            if overlap:
                # 计算相似度
                similarity = len(overlap) / max(len(interest_words), len(project_words))
                max_similarity = max(max_similarity, similarity)
                matched_interests.append(interest)
        
        return max_similarity, matched_interests
    
    def match_student_to_project(self, student_info: Dict, project_info: Dict) -> MatchScore:
        """匹配单个学生到单个项目"""
        
        # 1. 技能匹配
        skill_score, matched_skills = self.calculate_skill_match(
            student_info['skills'], 
            project_info['skills']
        )
        
        # 2. 专业匹配
        major_score = self.calculate_major_match(
            student_info['major'], 
            project_info['majors']
        )
        
        # 3. 课程匹配
        course_score, matched_courses = self.calculate_course_match(
            student_info['courses'], 
            project_info['units']
        )
        
        # 4. 兴趣匹配
        interest_score, matched_interests = self.calculate_interest_match(
            student_info['interests'], 
            project_info['title']
        )
        
        # 综合评分
        total_score = (
            skill_score * self.weights['skill'] +
            major_score * self.weights['major'] +
            course_score * self.weights['course'] +
            interest_score * self.weights['interest']
        )
        
        return MatchScore(
            student_id=student_info['id'],
            student_name=student_info['name'],
            project_name=project_info['name'],
            total_score=total_score,
            skill_score=skill_score,
            major_score=major_score,
            course_score=course_score,
            interest_score=interest_score,
            matched_skills=matched_skills,
            matched_courses=matched_courses,
            matched_interests=matched_interests,
            details={
                'student_major': student_info['major'],
                'project_majors': list(project_info['majors']),
                'student_skill_count': len(student_info['skills']),
                'project_skill_count': len(project_info['skills']),
                'student_course_count': len(student_info['courses']),
                'project_unit_count': len(project_info['units'])
            }
        )
    
    def match_all(self):
        """执行全部匹配"""
        print("🚀 开始基于增强知识图谱的匹配...")
        print(f"学生KG目录: {self.student_kg_dir}")
        print(f"项目KG目录: {self.project_kg_dir}")
        print(f"输出目录: {self.output_dir}")
        print()
        
        # 加载所有项目KG
        project_kgs = {}
        project_dirs = [d for d in os.listdir(self.project_kg_dir) 
                       if os.path.isdir(os.path.join(self.project_kg_dir, d))]
        
        print(f"📁 找到 {len(project_dirs)} 个项目")
        for proj_dir in project_dirs:
            json_file = os.path.join(self.project_kg_dir, proj_dir, 
                                    f"{proj_dir}_enhanced_kg.json")
            if os.path.exists(json_file):
                project_kg = self.load_project_kg(json_file)
                project_info = self.extract_project_info(project_kg)
                project_kgs[proj_dir] = project_info
                print(f"  ✓ {proj_dir}")
        
        print(f"\n✅ 成功加载 {len(project_kgs)} 个项目KG")
        print()
        
        # 按项目组织匹配结果
        results_by_project = defaultdict(list)
        
        # 遍历所有学生KG
        student_count = 0
        for proj_dir in os.listdir(self.student_kg_dir):
            student_proj_dir = os.path.join(self.student_kg_dir, proj_dir)
            if not os.path.isdir(student_proj_dir):
                continue
            
            # 查找学生KG JSON文件
            json_files = glob.glob(os.path.join(student_proj_dir, "*_enhanced_kg.json"))
            
            for json_file in json_files:
                student_count += 1
                student_kg = self.load_student_kg(json_file)
                student_info = self.extract_student_info(student_kg)
                
                # 与每个项目匹配
                for proj_name, project_info in project_kgs.items():
                    match_score = self.match_student_to_project(student_info, project_info)
                    results_by_project[proj_name].append(match_score)
        
        print(f"👥 处理了 {student_count} 个学生")
        print()
        
        # 保存结果（按项目分类）
        print("💾 保存匹配结果...")
        for proj_name, matches in results_by_project.items():
            # 按总分排序
            matches.sort(key=lambda x: x.total_score, reverse=True)
            
            # 创建项目文件夹
            project_output_dir = os.path.join(self.output_dir, proj_name)
            os.makedirs(project_output_dir, exist_ok=True)
            
            # 保存JSON
            json_path = os.path.join(project_output_dir, "matching_results.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'project': proj_name,
                    'total_students': len(matches),
                    'generated_at': datetime.now().isoformat(),
                    'matching_method': 'KG_Enhanced',
                    'weights': self.weights,
                    'matches': [asdict(m) for m in matches]
                }, f, indent=2, ensure_ascii=False)
            
            # 保存可读的文本报告
            report_path = os.path.join(project_output_dir, "matching_report.txt")
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(f"项目匹配报告\n")
                f.write(f"=" * 80 + "\n")
                f.write(f"项目名称: {proj_name}\n")
                f.write(f"匹配学生数: {len(matches)}\n")
                f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"\n匹配权重配置:\n")
                f.write(f"  - 技能匹配: {self.weights['skill']*100}%\n")
                f.write(f"  - 专业匹配: {self.weights['major']*100}%\n")
                f.write(f"  - 课程匹配: {self.weights['course']*100}%\n")
                f.write(f"  - 兴趣匹配: {self.weights['interest']*100}%\n")
                f.write(f"\n" + "=" * 80 + "\n\n")
                
                # Top 20 学生
                f.write(f"Top 20 匹配学生:\n")
                f.write(f"-" * 80 + "\n\n")
                
                for i, match in enumerate(matches[:20], 1):
                    f.write(f"排名 #{i}\n")
                    f.write(f"学生: {match.student_name} ({match.student_id})\n")
                    f.write(f"综合得分: {match.total_score:.3f}\n")
                    f.write(f"  - 技能得分: {match.skill_score:.3f}\n")
                    f.write(f"  - 专业得分: {match.major_score:.3f}\n")
                    f.write(f"  - 课程得分: {match.course_score:.3f}\n")
                    f.write(f"  - 兴趣得分: {match.interest_score:.3f}\n")
                    f.write(f"匹配详情:\n")
                    f.write(f"  - 匹配技能 ({len(match.matched_skills)}): {', '.join(match.matched_skills[:10])}")
                    if len(match.matched_skills) > 10:
                        f.write(f" ... (共{len(match.matched_skills)}个)")
                    f.write(f"\n")
                    f.write(f"  - 匹配课程 ({len(match.matched_courses)}): {', '.join(match.matched_courses)}\n")
                    if match.matched_interests:
                        f.write(f"  - 匹配兴趣: {', '.join(match.matched_interests)}\n")
                    f.write(f"\n" + "-" * 80 + "\n\n")
            
            print(f"  ✓ {proj_name}: {len(matches)} 个学生匹配")
        
        # 生成总体汇总
        self.generate_summary(results_by_project)
        
        print()
        print(f"✅ 匹配完成！结果已保存到: {self.output_dir}")
    
    def generate_summary(self, results_by_project: Dict[str, List[MatchScore]]):
        """生成总体汇总报告"""
        summary_path = os.path.join(self.output_dir, "SUMMARY.txt")
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("增强知识图谱匹配系统 - 总体汇总\n")
            f.write("=" * 80 + "\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"项目总数: {len(results_by_project)}\n")
            f.write(f"\n" + "=" * 80 + "\n\n")
            
            # 每个项目的统计
            for proj_name, matches in sorted(results_by_project.items()):
                if not matches:
                    continue
                
                avg_score = sum(m.total_score for m in matches) / len(matches)
                top_score = matches[0].total_score
                top_student = matches[0].student_name
                
                f.write(f"项目: {proj_name}\n")
                f.write(f"  学生数: {len(matches)}\n")
                f.write(f"  平均得分: {avg_score:.3f}\n")
                f.write(f"  最高得分: {top_score:.3f} ({top_student})\n")
                f.write(f"  输出目录: {proj_name}/\n")
                f.write(f"\n")
        
        print(f"  ✓ 汇总报告: SUMMARY.txt")


def main():
    """主函数"""
    matcher = KGEnhancedMatcher(
        student_kg_dir="outputs/knowledge_graphs/enhanced_student_kg",
        project_kg_dir="outputs/knowledge_graphs/enhanced_in20_in27",
        output_dir="outputs/matching/PD+UO_STUDENT_matching"
    )
    
    matcher.match_all()


if __name__ == "__main__":
    main()

