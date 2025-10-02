#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学生-项目相似度矩阵计算系统
计算所有学生与所有项目的交叉相似度分数
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import networkx as nx
from collections import defaultdict, Counter

@dataclass
class SimilarityResult:
    """相似度结果"""
    student_id: str
    project_id: str
    similarity_score: float
    skill_match: float
    course_match: float
    technology_match: float
    major_match: float
    total_entities: int
    matched_entities: int

class StudentProjectSimilarityMatrix:
    """学生-项目相似度矩阵计算器"""
    
    def __init__(self, output_dir: str = "similarity_results"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # 数据存储
        self.projects = {}
        self.students = {}
        self.similarity_matrix = {}
        self.detailed_results = []
        
        # 实体类型权重
        self.entity_weights = {
            'SKILL': 0.4,
            'TECHNOLOGY': 0.3,
            'COURSE': 0.2,
            'MAJOR': 0.1
        }
        
    def load_kg_data(self):
        """加载知识图谱数据"""
        print("📊 加载知识图谱数据...")
        
        # 加载项目数据
        self._load_projects()
        
        # 加载学生数据
        self._load_students()
        
        print(f"✅ 数据加载完成: {len(self.projects)} 个项目, {len(self.students)} 个学生")
        
    def _load_projects(self):
        """加载项目知识图谱数据"""
        project_kg_dir = "individual_kg/projects"
        if not os.path.exists(project_kg_dir):
            print(f"❌ 项目KG目录不存在: {project_kg_dir}")
            return
            
        for file in os.listdir(project_kg_dir):
            if file.endswith("_entities.json"):
                project_id = file.replace("_entities.json", "")
                try:
                    with open(os.path.join(project_kg_dir, file), 'r', encoding='utf-8') as f:
                        entities = json.load(f)
                    
                    # 统计实体类型
                    entity_counts = defaultdict(int)
                    for entity in entities:
                        entity_type = entity.get('entity_type', 'UNKNOWN')
                        entity_counts[entity_type] += 1
                    
                    self.projects[project_id] = {
                        'entities': entities,
                        'entity_counts': dict(entity_counts),
                        'total_entities': len(entities)
                    }
                    
                except Exception as e:
                    print(f"  ⚠️ 加载项目失败 {file}: {e}")
    
    def _load_students(self):
        """加载学生知识图谱数据"""
        student_kg_dir = "individual_kg/students"
        if not os.path.exists(student_kg_dir):
            print(f"❌ 学生KG目录不存在: {student_kg_dir}")
            return
            
        for file in os.listdir(student_kg_dir):
            if file.endswith("_entities.json"):
                student_id = file.replace("_entities.json", "")
                try:
                    with open(os.path.join(student_kg_dir, file), 'r', encoding='utf-8') as f:
                        entities = json.load(f)
                    
                    # 统计实体类型
                    entity_counts = defaultdict(int)
                    for entity in entities:
                        entity_type = entity.get('entity_type', 'UNKNOWN')
                        entity_counts[entity_type] += 1
                    
                    self.students[student_id] = {
                        'entities': entities,
                        'entity_counts': dict(entity_counts),
                        'total_entities': len(entities)
                    }
                    
                except Exception as e:
                    print(f"  ⚠️ 加载学生失败 {file}: {e}")
    
    def calculate_similarity_matrix(self):
        """计算相似度矩阵"""
        print("🔄 计算学生-项目相似度矩阵...")
        
        if not self.projects or not self.students:
            print("❌ 数据未加载，请先调用 load_kg_data()")
            return
        
        # 初始化矩阵
        student_ids = list(self.students.keys())
        project_ids = list(self.projects.keys())
        
        # 创建相似度矩阵
        similarity_matrix = np.zeros((len(student_ids), len(project_ids)))
        
        print(f"📊 计算 {len(student_ids)} 个学生 × {len(project_ids)} 个项目的相似度...")
        
        for i, student_id in enumerate(student_ids):
            for j, project_id in enumerate(project_ids):
                # 计算相似度
                similarity = self._calculate_similarity(student_id, project_id)
                similarity_matrix[i, j] = similarity
                
                # 保存详细结果
                detailed_result = self._get_detailed_similarity(student_id, project_id)
                self.detailed_results.append(detailed_result)
        
        # 保存矩阵
        self.similarity_matrix = {
            'matrix': similarity_matrix.tolist(),
            'student_ids': student_ids,
            'project_ids': project_ids,
            'shape': similarity_matrix.shape
        }
        
        print(f"✅ 相似度矩阵计算完成: {similarity_matrix.shape}")
        
    def _calculate_similarity(self, student_id: str, project_id: str) -> float:
        """计算单个学生-项目对的相似度"""
        if student_id not in self.students or project_id not in self.projects:
            return 0.0
        
        student_data = self.students[student_id]
        project_data = self.projects[project_id]
        
        student_entities = student_data['entity_counts']
        project_entities = project_data['entity_counts']
        
        total_similarity = 0.0
        total_weight = 0.0
        
        for entity_type, weight in self.entity_weights.items():
            student_count = student_entities.get(entity_type, 0)
            project_count = project_entities.get(entity_type, 0)
            
            if student_count > 0 or project_count > 0:
                # Jaccard相似度
                intersection = min(student_count, project_count)
                union = max(student_count, project_count)
                similarity = intersection / union if union > 0 else 0.0
                
                total_similarity += similarity * weight
                total_weight += weight
        
        return total_similarity / total_weight if total_weight > 0 else 0.0
    
    def _get_detailed_similarity(self, student_id: str, project_id: str) -> SimilarityResult:
        """获取详细的相似度分析"""
        if student_id not in self.students or project_id not in self.projects:
            return SimilarityResult(
                student_id=student_id, project_id=project_id, similarity_score=0.0,
                skill_match=0.0, course_match=0.0, technology_match=0.0, major_match=0.0,
                total_entities=0, matched_entities=0
            )
        
        student_data = self.students[student_id]
        project_data = self.projects[project_id]
        
        student_entities = student_data['entity_counts']
        project_entities = project_data['entity_counts']
        
        # 计算各类型匹配度
        skill_match = self._calculate_entity_match(student_entities.get('SKILL', 0), 
                                                  project_entities.get('SKILL', 0))
        course_match = self._calculate_entity_match(student_entities.get('COURSE', 0), 
                                                   project_entities.get('COURSE', 0))
        technology_match = self._calculate_entity_match(student_entities.get('TECHNOLOGY', 0), 
                                                       project_entities.get('TECHNOLOGY', 0))
        major_match = self._calculate_entity_match(student_entities.get('MAJOR', 0), 
                                                 project_entities.get('MAJOR', 0))
        
        # 计算总体相似度
        total_similarity = (skill_match * 0.4 + course_match * 0.2 + 
                          technology_match * 0.3 + major_match * 0.1)
        
        # 计算匹配实体数
        matched_entities = sum(min(student_entities.get(et, 0), project_entities.get(et, 0)) 
                              for et in self.entity_weights.keys())
        total_entities = sum(student_entities.get(et, 0) + project_entities.get(et, 0) 
                           for et in self.entity_weights.keys())
        
        return SimilarityResult(
            student_id=student_id,
            project_id=project_id,
            similarity_score=total_similarity,
            skill_match=skill_match,
            course_match=course_match,
            technology_match=technology_match,
            major_match=major_match,
            total_entities=total_entities,
            matched_entities=matched_entities
        )
    
    def _calculate_entity_match(self, student_count: int, project_count: int) -> float:
        """计算实体类型匹配度"""
        if student_count == 0 and project_count == 0:
            return 1.0  # 都为空，完全匹配
        if student_count == 0 or project_count == 0:
            return 0.0  # 一个为空，完全不匹配
        
        intersection = min(student_count, project_count)
        union = max(student_count, project_count)
        return intersection / union
    
    def generate_similarity_report(self):
        """生成相似度报告"""
        print("📊 生成相似度报告...")
        
        if not self.similarity_matrix:
            print("❌ 相似度矩阵未计算，请先调用 calculate_similarity_matrix()")
            return
        
        # 创建DataFrame
        matrix = np.array(self.similarity_matrix['matrix'])
        student_ids = self.similarity_matrix['student_ids']
        project_ids = self.similarity_matrix['project_ids']
        
        # 创建相似度DataFrame
        similarity_df = pd.DataFrame(
            matrix, 
            index=student_ids, 
            columns=project_ids
        )
        
        # 保存CSV
        csv_path = os.path.join(self.output_dir, "similarity_matrix.csv")
        similarity_df.to_csv(csv_path)
        print(f"📄 相似度矩阵已保存: {csv_path}")
        
        # 生成统计报告
        self._generate_statistics_report(similarity_df)
        
        # 生成可视化
        self._generate_visualizations(similarity_df)
        
        # 生成详细结果
        self._save_detailed_results()
        
    def _generate_statistics_report(self, similarity_df: pd.DataFrame):
        """生成统计报告"""
        print("📈 生成统计报告...")
        
        # 基本统计
        stats = {
            'total_students': len(similarity_df.index),
            'total_projects': len(similarity_df.columns),
            'total_comparisons': similarity_df.size,
            'mean_similarity': similarity_df.values.mean(),
            'std_similarity': similarity_df.values.std(),
            'min_similarity': similarity_df.values.min(),
            'max_similarity': similarity_df.values.max(),
            'median_similarity': np.median(similarity_df.values)
        }
        
        # 高相似度匹配统计
        high_similarity_threshold = 0.7
        high_similarity_count = (similarity_df >= high_similarity_threshold).sum().sum()
        stats['high_similarity_matches'] = high_similarity_count
        stats['high_similarity_percentage'] = (high_similarity_count / similarity_df.size) * 100
        
        # 每个学生的最佳匹配
        best_matches = []
        for student_id in similarity_df.index:
            best_project = similarity_df.loc[student_id].idxmax()
            best_score = similarity_df.loc[student_id, best_project]
            best_matches.append({
                'student_id': student_id,
                'best_project': best_project,
                'best_score': best_score
            })
        
        # 每个项目的最佳匹配
        best_students = []
        for project_id in similarity_df.columns:
            best_student = similarity_df[project_id].idxmax()
            best_score = similarity_df.loc[best_student, project_id]
            best_students.append({
                'project_id': project_id,
                'best_student': best_student,
                'best_score': best_score
            })
        
        # 保存统计报告
        report = {
            'statistics': {k: float(v) if isinstance(v, (np.integer, np.floating)) else v for k, v in stats.items()},
            'best_student_matches': best_matches,
            'best_project_matches': best_students,
            'generated_at': datetime.now().isoformat()
        }
        
        report_path = os.path.join(self.output_dir, "similarity_statistics.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📊 统计报告已保存: {report_path}")
        
        # 打印关键统计信息
        print("\n" + "="*60)
        print("📊 相似度矩阵统计报告")
        print("="*60)
        print(f"👥 学生总数: {stats['total_students']}")
        print(f"🎯 项目总数: {stats['total_projects']}")
        print(f"🔄 总比较次数: {stats['total_comparisons']}")
        print(f"📈 平均相似度: {stats['mean_similarity']:.3f}")
        print(f"📊 相似度标准差: {stats['std_similarity']:.3f}")
        print(f"📉 最低相似度: {stats['min_similarity']:.3f}")
        print(f"📈 最高相似度: {stats['max_similarity']:.3f}")
        print(f"🎯 高相似度匹配(≥0.7): {stats['high_similarity_matches']} ({stats['high_similarity_percentage']:.1f}%)")
        print("="*60)
    
    def _generate_visualizations(self, similarity_df: pd.DataFrame):
        """生成可视化图表"""
        print("📊 生成可视化图表...")
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 1. 相似度矩阵热力图
        plt.figure(figsize=(15, 10))
        sns.heatmap(similarity_df, annot=False, cmap='YlOrRd', cbar=True)
        plt.title('学生-项目相似度矩阵', fontsize=16, fontweight='bold')
        plt.xlabel('项目ID', fontsize=12)
        plt.ylabel('学生ID', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        
        heatmap_path = os.path.join(self.output_dir, "similarity_heatmap.png")
        plt.savefig(heatmap_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"🔥 热力图已保存: {heatmap_path}")
        
        # 2. 相似度分布直方图
        plt.figure(figsize=(10, 6))
        plt.hist(similarity_df.values.flatten(), bins=50, alpha=0.7, color='skyblue', edgecolor='black')
        plt.title('相似度分数分布', fontsize=14, fontweight='bold')
        plt.xlabel('相似度分数', fontsize=12)
        plt.ylabel('频次', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        hist_path = os.path.join(self.output_dir, "similarity_distribution.png")
        plt.savefig(hist_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"📊 分布图已保存: {hist_path}")
        
        # 3. 每个学生的最佳匹配分数
        best_scores = similarity_df.max(axis=1)
        plt.figure(figsize=(12, 6))
        best_scores.plot(kind='bar', color='lightcoral', alpha=0.7)
        plt.title('每个学生的最佳匹配分数', fontsize=14, fontweight='bold')
        plt.xlabel('学生ID', fontsize=12)
        plt.ylabel('最高相似度分数', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        best_scores_path = os.path.join(self.output_dir, "best_matches_per_student.png")
        plt.savefig(best_scores_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"🏆 最佳匹配图已保存: {best_scores_path}")
    
    def _save_detailed_results(self):
        """保存详细结果"""
        print("💾 保存详细结果...")
        
        # 转换为字典格式
        detailed_data = []
        for result in self.detailed_results:
            detailed_data.append(asdict(result))
        
        # 保存详细结果
        detailed_path = os.path.join(self.output_dir, "detailed_similarity_results.json")
        with open(detailed_path, 'w', encoding='utf-8') as f:
            json.dump(detailed_data, f, indent=2, ensure_ascii=False)
        
        print(f"📄 详细结果已保存: {detailed_path}")
        
        # 创建Top匹配报告
        self._create_top_matches_report()
    
    def _create_top_matches_report(self):
        """创建Top匹配报告"""
        print("🏆 创建Top匹配报告...")
        
        # 按相似度排序
        sorted_results = sorted(self.detailed_results, 
                               key=lambda x: x.similarity_score, reverse=True)
        
        # Top 20 匹配
        top_20 = sorted_results[:20]
        
        # 创建报告
        report = {
            'top_20_matches': [
                {
                    'rank': i+1,
                    'student_id': result.student_id,
                    'project_id': result.project_id,
                    'similarity_score': result.similarity_score,
                    'skill_match': result.skill_match,
                    'course_match': result.course_match,
                    'technology_match': result.technology_match,
                    'major_match': result.major_match,
                    'matched_entities': result.matched_entities,
                    'total_entities': result.total_entities
                }
                for i, result in enumerate(top_20)
            ],
            'generated_at': datetime.now().isoformat()
        }
        
        # 保存Top匹配报告
        top_matches_path = os.path.join(self.output_dir, "top_matches_report.json")
        with open(top_matches_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"🏆 Top匹配报告已保存: {top_matches_path}")
        
        # 打印Top 10
        print("\n" + "="*80)
        print("🏆 TOP 10 最佳匹配")
        print("="*80)
        for i, result in enumerate(top_20[:10], 1):
            print(f"{i:2d}. 学生: {result.student_id} | 项目: {result.project_id}")
            print(f"    相似度: {result.similarity_score:.3f} | 技能匹配: {result.skill_match:.3f} | 课程匹配: {result.course_match:.3f}")
            print(f"    技术匹配: {result.technology_match:.3f} | 专业匹配: {result.major_match:.3f}")
            print("-" * 80)

def main():
    """主函数"""
    print("🚀 启动学生-项目相似度矩阵计算系统")
    print("="*60)
    
    # 创建相似度计算器
    calculator = StudentProjectSimilarityMatrix()
    
    # 加载数据
    calculator.load_kg_data()
    
    if not calculator.projects or not calculator.students:
        print("❌ 数据加载失败，请检查知识图谱文件是否存在")
        return
    
    # 计算相似度矩阵
    calculator.calculate_similarity_matrix()
    
    # 生成报告
    calculator.generate_similarity_report()
    
    print("\n✅ 相似度矩阵计算完成！")
    print(f"📁 结果保存在: {calculator.output_dir}")

if __name__ == "__main__":
    main()
