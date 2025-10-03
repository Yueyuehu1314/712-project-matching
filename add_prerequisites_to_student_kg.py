#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为学生知识图谱补充前置课程(Prerequisite)信息

基于IN20/IN27课程信息手册，分析学生修过的课程，
如果有前置课程，将前置课程信息添加到知识图谱中。
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

class PrerequisiteAnalyzer:
    """前置课程分析器"""
    
    def __init__(
        self,
        in20_path: str = "data/processed/units_md/qut_IN20_39851_int_cms_unit.md",
        in27_path: str = "data/processed/units_md/qut_IN27_44569.md"
    ):
        self.in20_path = in20_path
        self.in27_path = in27_path
        
        # 加载前置课程映射
        self.prerequisites = self._load_all_prerequisites()
        
        print(f"✅ 加载前置课程信息: {len(self.prerequisites)} 个课程有前置要求")
    
    def _extract_unit_prerequisites(self, content: str) -> Dict[str, List[str]]:
        """从课程手册中提取前置课程信息"""
        prerequisites = {}
        
        # 查找所有 "Unit Code + Title + Pre-requisites" 部分
        # 格式：CAB401 Title\nPre-requisites\n(prereq text)\nCredit Points
        pattern = r'([A-Z]{3}\d{3})\s+[^\n]+\nPre-requisites\s*\n(.*?)(?=\nCredit Points|\nEquivalents|\nAnti-requisites|\n[A-Z]{3}\d{3}|$)'
        
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        
        for unit_code, prereq_text in matches:
            # 从前置课程文本中提取课程代码
            prereq_codes = re.findall(r'\b([A-Z]{3}\d{3})\b', prereq_text)
            if prereq_codes:
                prerequisites[unit_code] = list(set(prereq_codes))
        
        return prerequisites
    
    def _load_all_prerequisites(self) -> Dict[str, List[str]]:
        """加载所有课程的前置课程信息"""
        all_prerequisites = {}
        
        # 加载IN20
        if os.path.exists(self.in20_path):
            try:
                with open(self.in20_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                in20_prereq = self._extract_unit_prerequisites(content)
                all_prerequisites.update(in20_prereq)
                print(f"  📚 IN20: {len(in20_prereq)} 个课程有前置要求")
            except Exception as e:
                print(f"  ⚠️  加载IN20失败: {e}")
        
        # 加载IN27
        if os.path.exists(self.in27_path):
            try:
                with open(self.in27_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                in27_prereq = self._extract_unit_prerequisites(content)
                all_prerequisites.update(in27_prereq)
                print(f"  📚 IN27: {len(in27_prereq)} 个课程有前置要求")
            except Exception as e:
                print(f"  ⚠️  加载IN27失败: {e}")
        
        return all_prerequisites
    
    def analyze_student_prerequisites(self, student_kg_json: Dict) -> Dict:
        """
        分析学生知识图谱中的课程，找出缺失的前置课程
        
        Returns:
            {
                'courses_with_prereq': [...],  # 学生修的有前置要求的课程
                'missing_prerequisites': [...], # 学生没修但需要的前置课程
                'completed_prerequisites': [...] # 学生已修的前置课程
            }
        """
        # 提取学生修过的课程
        student_courses = set()
        for entity in student_kg_json.get('entities', []):
            if entity.get('entity_type') == 'COURSE':
                # 提取课程代码（如 IFN564）
                course_code = self._extract_course_code(entity.get('name', ''))
                if course_code:
                    student_courses.add(course_code)
        
        # 分析前置课程
        courses_with_prereq = []
        missing_prerequisites = set()
        completed_prerequisites = set()
        
        for course in student_courses:
            if course in self.prerequisites:
                prereqs = self.prerequisites[course]
                courses_with_prereq.append({
                    'course': course,
                    'prerequisites': prereqs
                })
                
                for prereq in prereqs:
                    if prereq in student_courses:
                        completed_prerequisites.add(prereq)
                    else:
                        missing_prerequisites.add(prereq)
        
        return {
            'courses_with_prereq': courses_with_prereq,
            'missing_prerequisites': sorted(list(missing_prerequisites)),
            'completed_prerequisites': sorted(list(completed_prerequisites)),
            'student_courses': sorted(list(student_courses))
        }
    
    def _extract_course_code(self, course_name: str) -> str:
        """从课程名称中提取课程代码"""
        # 匹配格式如 "IFN564" 或 "CAB401"
        match = re.search(r'\b([A-Z]{3}\d{3})\b', course_name)
        return match.group(1) if match else None
    
    def add_prerequisites_to_kg(
        self,
        student_kg_json: Dict,
        add_missing: bool = False
    ) -> Tuple[Dict, Dict]:
        """
        为学生知识图谱添加前置课程关系
        
        Args:
            student_kg_json: 学生KG的JSON数据
            add_missing: 是否添加学生没修但需要的前置课程节点
        
        Returns:
            (updated_kg_json, stats)
        """
        analysis = self.analyze_student_prerequisites(student_kg_json)
        
        # 统计
        stats = {
            'courses_analyzed': len(analysis['student_courses']),
            'courses_with_prereq': len(analysis['courses_with_prereq']),
            'prerequisite_relations_added': 0,
            'missing_prerequisite_nodes_added': 0
        }
        
        # 构建课程ID映射
        course_id_map = {}
        for entity in student_kg_json.get('entities', []):
            if entity.get('entity_type') == 'COURSE':
                course_code = self._extract_course_code(entity.get('name', ''))
                if course_code:
                    course_id_map[course_code] = entity.get('id')
        
        # 添加前置课程关系
        existing_relationships = student_kg_json.get('relationships', [])
        new_relationships = []
        
        for course_info in analysis['courses_with_prereq']:
            course = course_info['course']
            prereqs = course_info['prerequisites']
            
            course_id = course_id_map.get(course)
            if not course_id:
                continue
            
            for prereq in prereqs:
                prereq_id = course_id_map.get(prereq)
                
                # 如果前置课程学生已修，添加关系
                if prereq_id:
                    new_relationships.append({
                        'source_id': prereq_id,
                        'target_id': course_id,
                        'relation_type': 'PREREQUISITE_FOR',
                        'weight': 1.0,
                        'properties': {
                            'description': f'{prereq} is a prerequisite for {course}'
                        }
                    })
                    stats['prerequisite_relations_added'] += 1
                
                # 如果要添加缺失的前置课程节点
                elif add_missing:
                    # 创建前置课程节点
                    prereq_id = f"course_{prereq.lower()}"
                    student_kg_json['entities'].append({
                        'id': prereq_id,
                        'name': prereq,
                        'entity_type': 'COURSE',
                        'properties': {
                            'status': 'prerequisite_not_completed',
                            'is_missing': True
                        }
                    })
                    
                    # 添加前置关系
                    new_relationships.append({
                        'source_id': prereq_id,
                        'target_id': course_id,
                        'relation_type': 'PREREQUISITE_FOR',
                        'weight': 1.0,
                        'properties': {
                            'description': f'{prereq} is a prerequisite for {course}',
                            'missing': True
                        }
                    })
                    
                    course_id_map[prereq] = prereq_id
                    stats['missing_prerequisite_nodes_added'] += 1
                    stats['prerequisite_relations_added'] += 1
        
        # 更新关系列表
        student_kg_json['relationships'].extend(new_relationships)
        
        # 添加分析信息到metadata
        if 'metadata' not in student_kg_json:
            student_kg_json['metadata'] = {}
        
        student_kg_json['metadata']['prerequisite_analysis'] = analysis
        
        return student_kg_json, stats


class StudentKGPrerequisiteEnhancer:
    """批量为学生KG添加前置课程信息"""
    
    def __init__(self, kg_directory: str):
        self.kg_directory = kg_directory
        self.analyzer = PrerequisiteAnalyzer()
    
    def enhance_all_student_kgs(
        self,
        add_missing: bool = False,
        output_suffix: str = "_with_prereq"
    ) -> Dict:
        """
        批量处理所有学生KG
        
        Args:
            add_missing: 是否添加缺失的前置课程节点
            output_suffix: 输出文件名后缀
        """
        kg_path = Path(self.kg_directory)
        json_files = list(kg_path.glob("**/*_enhanced_kg.json"))
        
        print(f"\n{'='*60}")
        print(f"开始批量添加前置课程信息")
        print(f"{'='*60}")
        print(f"  模式: {'添加缺失节点' if add_missing else '仅添加关系'}")
        print(f"  学生数量: {len(json_files)}")
        
        total_stats = {
            'processed': 0,
            'total_courses': 0,
            'total_prereq_relations': 0,
            'total_missing_nodes': 0
        }
        
        for json_file in json_files:
            try:
                # 读取KG
                with open(json_file, 'r', encoding='utf-8') as f:
                    kg_json = json.load(f)
                
                # 添加前置课程
                updated_kg, stats = self.analyzer.add_prerequisites_to_kg(
                    kg_json,
                    add_missing=add_missing
                )
                
                # 保存更新后的KG
                output_file = json_file.with_name(
                    json_file.name.replace('_enhanced_kg.json', f'{output_suffix}.json')
                )
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(updated_kg, f, indent=2, ensure_ascii=False)
                
                # 统计
                total_stats['processed'] += 1
                total_stats['total_courses'] += stats['courses_analyzed']
                total_stats['total_prereq_relations'] += stats['prerequisite_relations_added']
                total_stats['total_missing_nodes'] += stats['missing_prerequisite_nodes_added']
                
                if stats['prerequisite_relations_added'] > 0:
                    student_name = kg_json['metadata'].get('student_name', 'Unknown')
                    print(f"  ✅ {student_name}: +{stats['prerequisite_relations_added']} 关系, "
                          f"+{stats['missing_prerequisite_nodes_added']} 节点")
                
            except Exception as e:
                print(f"  ❌ 处理失败 {json_file.name}: {e}")
                continue
        
        print(f"\n{'='*60}")
        print(f"✅ 批量处理完成")
        print(f"{'='*60}")
        print(f"  处理学生数: {total_stats['processed']}")
        print(f"  总课程数: {total_stats['total_courses']}")
        print(f"  添加前置关系: {total_stats['total_prereq_relations']}")
        print(f"  添加缺失节点: {total_stats['total_missing_nodes']}")
        
        return total_stats
    
    def analyze_prerequisite_coverage(self) -> Dict:
        """分析所有学生的前置课程完成情况"""
        kg_path = Path(self.kg_directory)
        json_files = list(kg_path.glob("**/*_enhanced_kg.json"))
        
        print(f"\n{'='*60}")
        print(f"分析前置课程完成情况")
        print(f"{'='*60}")
        
        summary = {
            'students_analyzed': 0,
            'students_with_prereq_courses': 0,
            'total_missing_prerequisites': defaultdict(int),
            'common_missing': []
        }
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    kg_json = json.load(f)
                
                analysis = self.analyzer.analyze_student_prerequisites(kg_json)
                
                summary['students_analyzed'] += 1
                
                if analysis['courses_with_prereq']:
                    summary['students_with_prereq_courses'] += 1
                
                # 统计缺失的前置课程
                for missing in analysis['missing_prerequisites']:
                    summary['total_missing_prerequisites'][missing] += 1
                
            except Exception as e:
                continue
        
        # 找出最常见的缺失前置课程
        summary['common_missing'] = sorted(
            summary['total_missing_prerequisites'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # 打印结果
        print(f"\n  学生总数: {summary['students_analyzed']}")
        print(f"  有前置课程要求的学生: {summary['students_with_prereq_courses']}")
        print(f"\n  最常见的缺失前置课程 (Top 10):")
        for course, count in summary['common_missing']:
            print(f"    - {course}: {count} 个学生缺失")
        
        return summary


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='为学生知识图谱添加前置课程信息')
    parser.add_argument(
        '--kg-dir',
        default='outputs/knowledge_graphs/individual/enhanced_student_kg',
        help='学生KG目录'
    )
    parser.add_argument(
        '--add-missing',
        action='store_true',
        help='添加学生未修的前置课程节点'
    )
    parser.add_argument(
        '--analyze-only',
        action='store_true',
        help='仅分析，不修改文件'
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("学生知识图谱前置课程补充工具")
    print("="*60)
    
    enhancer = StudentKGPrerequisiteEnhancer(args.kg_dir)
    
    if args.analyze_only:
        # 仅分析
        enhancer.analyze_prerequisite_coverage()
    else:
        # 添加前置课程信息
        enhancer.enhance_all_student_kgs(add_missing=args.add_missing)
        
        # 分析结果
        enhancer.analyze_prerequisite_coverage()
    
    print("\n" + "="*60)
    print("✅ 完成！")
    print("="*60)


if __name__ == "__main__":
    main()


