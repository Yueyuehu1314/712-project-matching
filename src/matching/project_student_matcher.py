#!/usr/bin/env python3
"""
项目-学生匹配系统
基于项目描述(PD)和学生知识图谱进行匹配
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass, asdict
from collections import defaultdict
import pandas as pd
from datetime import datetime


@dataclass
class MatchResult:
    """匹配结果"""
    student_id: str
    student_name: str
    project_name: str
    match_score: float
    skill_match_score: float
    major_match_score: float
    interest_match_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    student_majors: List[str]
    project_required_majors: List[str]
    details: Dict


class ProjectStudentMatcher:
    """项目-学生匹配器"""
    
    def __init__(self, 
                 projects_dir: str = "data/processed/projects_md",
                 students_kg_dir: str = "outputs/knowledge_graphs/enhanced_student_kg"):
        self.projects_dir = Path(projects_dir)
        self.students_kg_dir = Path(students_kg_dir)
        
        # 技能同义词映射
        self.skill_synonyms = {
            'ai': 'artificial intelligence',
            'ml': 'machine learning',
            'dl': 'deep learning',
            'data science': 'data analytics',
            'big data': 'data analytics',
            'visualization': 'data visualization',
            'mobile dev': 'mobile development',
            'app dev': 'mobile development',
            'web dev': 'web development',
            'cybersecurity': 'cyber security',
            'network': 'networking',
            'databases': 'database',
            'db': 'database',
            'iot': 'internet of things'
        }
        
    def normalize_skill(self, skill: str) -> str:
        """标准化技能名称"""
        skill = skill.lower().strip()
        skill = re.sub(r'[^\w\s]', '', skill)
        skill = re.sub(r'\s+', ' ', skill)
        
        for short, full in self.skill_synonyms.items():
            skill = re.sub(r'\b' + short + r'\b', full, skill)
        
        return skill
    
    def extract_project_requirements(self, project_md_file: Path) -> Dict:
        """从项目MD文件提取需求"""
        with open(project_md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        project_info = {
            'name': project_md_file.stem,
            'title': '',
            'required_skills': set(),
            'required_majors': set(),
            'description': ''
        }
        
        # 提取项目标题
        title_match = re.search(r'\|\s*Project title\s*\|\s*(.+?)\s*\|', content, re.IGNORECASE)
        if title_match:
            project_info['title'] = title_match.group(1).strip()
        
        # 提取专业要求
        major_match = re.search(r'\|\s*Information Technology major.*?\|\s*(.+?)\s*\|', content, re.IGNORECASE)
        if major_match:
            majors_text = major_match.group(1)
            majors = [m.strip() for m in re.split(r'[,;和&]', majors_text) if m.strip()]
            project_info['required_majors'] = set(self.normalize_skill(m) for m in majors)
        
        # 提取技能关键词 - 从整个项目描述中提取
        # 常见技能关键词
        skill_keywords = [
            'machine learning', 'deep learning', 'artificial intelligence', 'ai',
            'data science', 'data analytics', 'data visualization',
            'python', 'tensorflow', 'pytorch', 'scikit-learn',
            'web development', 'mobile development', 'mobile app',
            'cybersecurity', 'cyber security', 'security', 'networking',
            'database', 'sql', 'nosql',
            'iot', 'internet of things', 'wifi', 'csi',
            'signal processing', 'computer vision', 'nlp',
            'react', 'javascript', 'node.js', 'flask', 'django',
            'cloud computing', 'aws', 'azure', 'gcp',
            'gan', 'lstm', 'cnn', 'neural network'
        ]
        
        content_lower = content.lower()
        for keyword in skill_keywords:
            if keyword in content_lower:
                project_info['required_skills'].add(self.normalize_skill(keyword))
        
        # 提取简短描述（从Brief description部分）
        desc_match = re.search(r'Brief description.*?\|(.*?)\+---', content, re.DOTALL | re.IGNORECASE)
        if desc_match:
            desc_text = desc_match.group(1).strip()
            # 取前200个字符
            project_info['description'] = ' '.join(desc_text.split())[:200] + '...'
        
        return project_info
    
    def load_student_kg(self, student_kg_file: Path) -> Dict:
        """加载学生知识图谱"""
        with open(student_kg_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def extract_student_info(self, student_kg: Dict) -> Dict:
        """从学生KG提取信息"""
        student_info = {
            'id': '',
            'name': '',
            'majors': set(),
            'skills': set(),
            'interests': set(),
            'courses': []
        }
        
        # 从实体提取信息（注意：字段名是entities不是nodes）
        for entity in student_kg.get('entities', []):
            entity_type = entity.get('entity_type', '')
            if entity_type == 'STUDENT':
                student_info['id'] = entity['id'].replace('student_', '')
                student_info['name'] = entity['name']
            elif entity_type == 'MAJOR':
                student_info['majors'].add(self.normalize_skill(entity['name']))
            elif entity_type == 'SKILL':
                student_info['skills'].add(self.normalize_skill(entity['name']))
            elif entity_type == 'INTEREST':
                student_info['interests'].add(self.normalize_skill(entity['name']))
            elif entity_type == 'COURSE':
                student_info['courses'].append(entity['name'])
        
        return student_info
    
    def calculate_skill_match(self, project_skills: Set[str], student_skills: Set[str]) -> Tuple[float, List[str], List[str]]:
        """计算技能匹配度"""
        if not project_skills:
            return 0.0, [], []
        
        matched_skills = []
        for ps in project_skills:
            for ss in student_skills:
                # 精确匹配或包含关系
                if ps == ss or ps in ss or ss in ps:
                    matched_skills.append(ps)
                    break
        
        missing_skills = list(project_skills - set(matched_skills))
        match_ratio = len(matched_skills) / len(project_skills) if project_skills else 0.0
        
        return match_ratio, matched_skills, missing_skills
    
    def calculate_major_match(self, project_majors: Set[str], student_majors: Set[str]) -> float:
        """计算专业匹配度"""
        if not project_majors:
            return 0.5  # 没有专业要求时给中等分数
        
        # 检查是否有任何匹配
        for pm in project_majors:
            for sm in student_majors:
                if pm in sm or sm in pm:
                    return 1.0
        
        return 0.0
    
    def calculate_interest_match(self, project_skills: Set[str], student_interests: Set[str]) -> float:
        """计算兴趣匹配度"""
        if not student_interests:
            return 0.0
        
        matched = 0
        for ps in project_skills:
            for si in student_interests:
                if ps in si or si in ps:
                    matched += 1
                    break
        
        return matched / max(len(project_skills), 1)
    
    def match_project_student(self, project_info: Dict, student_info: Dict) -> MatchResult:
        """匹配单个项目和学生"""
        # 计算各项匹配分数
        skill_score, matched_skills, missing_skills = self.calculate_skill_match(
            project_info['required_skills'], 
            student_info['skills']
        )
        
        major_score = self.calculate_major_match(
            project_info['required_majors'],
            student_info['majors']
        )
        
        interest_score = self.calculate_interest_match(
            project_info['required_skills'],
            student_info['interests']
        )
        
        # 综合匹配分数（权重：技能60%，专业30%，兴趣10%）
        total_score = skill_score * 0.6 + major_score * 0.3 + interest_score * 0.1
        
        return MatchResult(
            student_id=student_info['id'],
            student_name=student_info['name'],
            project_name=project_info['name'],
            match_score=round(total_score, 3),
            skill_match_score=round(skill_score, 3),
            major_match_score=round(major_score, 3),
            interest_match_score=round(interest_score, 3),
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            student_majors=list(student_info['majors']),
            project_required_majors=list(project_info['required_majors']),
            details={
                'student_total_skills': len(student_info['skills']),
                'project_required_skills': len(project_info['required_skills']),
                'student_courses': len(student_info['courses'])
            }
        )
    
    def match_all_for_project(self, project_md_file: Path) -> List[MatchResult]:
        """为一个项目匹配所有学生"""
        print(f"\n📋 处理项目: {project_md_file.stem}")
        
        # 提取项目需求
        project_info = self.extract_project_requirements(project_md_file)
        print(f"   • 项目标题: {project_info['title']}")
        print(f"   • 需要技能: {len(project_info['required_skills'])} 个")
        print(f"   • 需要专业: {', '.join(project_info['required_majors']) if project_info['required_majors'] else 'Any'}")
        
        # 获取该项目的学生KG目录
        project_dir_name = project_md_file.stem
        students_dir = self.students_kg_dir / project_dir_name
        
        if not students_dir.exists():
            print(f"   ⚠️  未找到学生KG目录: {students_dir}")
            return []
        
        # 匹配所有学生
        results = []
        student_kg_files = list(students_dir.glob("student_*_enhanced_kg.json"))
        
        print(f"   • 找到 {len(student_kg_files)} 个学生")
        
        for student_file in student_kg_files:
            student_kg = self.load_student_kg(student_file)
            student_info = self.extract_student_info(student_kg)
            
            match_result = self.match_project_student(project_info, student_info)
            results.append(match_result)
        
        # 按匹配分数排序
        results.sort(key=lambda x: x.match_score, reverse=True)
        
        print(f"   ✅ 完成匹配，平均分数: {sum(r.match_score for r in results) / len(results):.3f}")
        
        return results
    
    def save_matching_results(self, project_name: str, results: List[MatchResult], output_dir: Path):
        """保存匹配结果"""
        project_output_dir = output_dir / project_name
        project_output_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. 保存JSON格式
        json_file = project_output_dir / "matching_results.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(r) for r in results], f, indent=2, ensure_ascii=False)
        
        # 2. 保存CSV格式（便于查看）
        csv_file = project_output_dir / "matching_results.csv"
        df = pd.DataFrame([
            {
                'Student ID': r.student_id,
                'Student Name': r.student_name,
                'Total Score': r.match_score,
                'Skill Score': r.skill_match_score,
                'Major Score': r.major_match_score,
                'Interest Score': r.interest_match_score,
                'Matched Skills': ', '.join(r.matched_skills[:5]),  # 只显示前5个
                'Missing Skills': ', '.join(r.missing_skills[:5]),
                'Student Majors': ', '.join(r.student_majors)
            }
            for r in results
        ])
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        
        # 3. 保存可读性强的文本报告
        report_file = project_output_dir / "matching_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"{'='*80}\n")
            f.write(f"项目-学生匹配报告\n")
            f.write(f"{'='*80}\n\n")
            f.write(f"项目名称: {project_name}\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"学生总数: {len(results)}\n\n")
            
            # 统计信息
            f.write(f"{'='*80}\n")
            f.write(f"匹配统计\n")
            f.write(f"{'='*80}\n\n")
            f.write(f"平均匹配分数: {sum(r.match_score for r in results) / len(results):.3f}\n")
            f.write(f"最高分数: {max(r.match_score for r in results):.3f}\n")
            f.write(f"最低分数: {min(r.match_score for r in results):.3f}\n")
            
            # 分数分布
            high_match = len([r for r in results if r.match_score >= 0.7])
            medium_match = len([r for r in results if 0.4 <= r.match_score < 0.7])
            low_match = len([r for r in results if r.match_score < 0.4])
            
            f.write(f"\n分数分布:\n")
            f.write(f"  • 高匹配 (≥0.7): {high_match} 人 ({high_match/len(results)*100:.1f}%)\n")
            f.write(f"  • 中匹配 (0.4-0.7): {medium_match} 人 ({medium_match/len(results)*100:.1f}%)\n")
            f.write(f"  • 低匹配 (<0.4): {low_match} 人 ({low_match/len(results)*100:.1f}%)\n")
            
            # Top 10 学生
            f.write(f"\n{'='*80}\n")
            f.write(f"Top 10 匹配学生\n")
            f.write(f"{'='*80}\n\n")
            
            for i, result in enumerate(results[:10], 1):
                f.write(f"{i}. {result.student_name} ({result.student_id})\n")
                f.write(f"   总分: {result.match_score:.3f} | ")
                f.write(f"技能: {result.skill_match_score:.3f} | ")
                f.write(f"专业: {result.major_match_score:.3f} | ")
                f.write(f"兴趣: {result.interest_match_score:.3f}\n")
                f.write(f"   匹配技能: {', '.join(result.matched_skills[:5])}\n")
                f.write(f"   缺失技能: {', '.join(result.missing_skills[:5])}\n")
                f.write(f"   学生专业: {', '.join(result.student_majors)}\n\n")
        
        print(f"   💾 结果已保存:")
        print(f"      • {json_file}")
        print(f"      • {csv_file}")
        print(f"      • {report_file}")
    
    def run_all_matching(self, output_dir: str = "outputs/matching"):
        """运行所有项目的匹配"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print(f"\n{'='*80}")
        print(f"🚀 开始项目-学生匹配")
        print(f"{'='*80}")
        print(f"📁 项目目录: {self.projects_dir}")
        print(f"📁 学生KG目录: {self.students_kg_dir}")
        print(f"📁 输出目录: {output_path}")
        
        # 获取所有项目文件
        project_files = list(self.projects_dir.glob("*.md"))
        print(f"\n📊 找到 {len(project_files)} 个项目\n")
        
        # 统计信息
        all_results = []
        project_stats = []
        
        for i, project_file in enumerate(project_files, 1):
            print(f"\n{'='*80}")
            print(f"[{i}/{len(project_files)}] 处理项目")
            print(f"{'='*80}")
            
            results = self.match_all_for_project(project_file)
            
            if results:
                self.save_matching_results(project_file.stem, results, output_path)
                all_results.extend(results)
                
                project_stats.append({
                    'project': project_file.stem,
                    'students': len(results),
                    'avg_score': sum(r.match_score for r in results) / len(results),
                    'max_score': max(r.match_score for r in results),
                    'top_student': results[0].student_name if results else 'N/A'
                })
        
        # 生成总结报告
        self._generate_summary_report(project_stats, all_results, output_path)
        
        print(f"\n{'='*80}")
        print(f"✅ 匹配完成！")
        print(f"{'='*80}")
        print(f"📊 总计:")
        print(f"   • 项目数: {len(project_stats)}")
        print(f"   • 匹配记录: {len(all_results)}")
        print(f"   • 输出目录: {output_path}")
        print(f"{'='*80}\n")
    
    def _generate_summary_report(self, project_stats: List[Dict], all_results: List[MatchResult], output_dir: Path):
        """生成总结报告"""
        summary_file = output_dir / "summary_report.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump({
                'generation_time': datetime.now().isoformat(),
                'total_projects': len(project_stats),
                'total_matches': len(all_results),
                'overall_avg_score': sum(r.match_score for r in all_results) / len(all_results) if all_results else 0,
                'project_statistics': project_stats
            }, f, indent=2, ensure_ascii=False)
        
        # CSV格式的项目统计
        stats_csv = output_dir / "project_statistics.csv"
        pd.DataFrame(project_stats).to_csv(stats_csv, index=False, encoding='utf-8-sig')
        
        print(f"\n   📄 总结报告已保存:")
        print(f"      • {summary_file}")
        print(f"      • {stats_csv}")


def main():
    """主函数"""
    matcher = ProjectStudentMatcher()
    matcher.run_all_matching()


if __name__ == "__main__":
    main()

