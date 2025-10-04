#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进的评估指标
使用Top-K准确率、排名相关性等更实际的指标重新评估匹配效果
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Any
from collections import defaultdict
import argparse


class ImprovedEvaluator:
    """改进的评估器"""
    
    def __init__(self):
        self.results = {}
    
    def load_similarity_matrix(self, method: str) -> Dict[str, List[Tuple[str, float]]]:
        """
        加载相似度矩阵并转换为排序列表
        返回: {student_id: [(project_id, similarity_score), ...]}
        """
        # 根据方法确定文件路径
        if method == "1a":
            result_file = Path("outputs/embeddings/1a/similarity_comparison_results.json")
        elif method == "1b":
            result_file = Path("outputs/embeddings/1b/similarity_comparison_results.json")
        elif method == "2a":
            result_file = Path("outputs/kg_similarity/2a/method_2a_scores.json")
        elif method == "2b":
            result_file = Path("outputs/kg_similarity/2b/method_2b_scores_enhanced.json")
        else:
            raise ValueError(f"Unknown method: {method}")
        
        if not result_file.exists():
            print(f"⚠️  文件不存在: {result_file}")
            return {}
        
        with open(result_file, 'r') as f:
            data = json.load(f)
        
        # 解析数据结构（需要根据实际格式调整）
        rankings = defaultdict(list)
        
        if method in ["1a", "1b"]:
            # Embedding方法的结果格式
            # 需要从raw_similarities或其他字段构建
            # 这里提供一个框架
            pass
        elif method in ["2a", "2b"]:
            # KG方法的结果格式
            if isinstance(data, list):
                for item in data:
                    student_id = item.get("student_id", "")
                    project_id = item.get("project_id", "")
                    
                    # 使用node_jaccard作为相似度
                    similarity = item.get("node_jaccard", item.get("jaccard_similarity", 0))
                    
                    rankings[student_id].append((project_id, similarity))
        
        # 对每个学生的项目按相似度排序
        for student_id in rankings:
            rankings[student_id].sort(key=lambda x: x[1], reverse=True)
        
        return dict(rankings)
    
    def create_ground_truth(self, rankings: Dict[str, List[Tuple[str, float]]]) -> Dict[str, str]:
        """
        创建ground truth：每个学生的真实匹配项目
        假设：为每个学生生成档案时就指定了目标项目
        """
        ground_truth = {}
        
        # 从学生ID中提取项目信息
        # 例如: "student_project0_0" -> project0
        for student_id in rankings.keys():
            # 尝试从ID中提取项目编号
            if "_" in student_id:
                parts = student_id.split("_")
                if len(parts) >= 2:
                    project_part = parts[1]  # project0, project1, etc.
                    ground_truth[student_id] = project_part
        
        return ground_truth
    
    def evaluate_topk_accuracy(
        self, 
        rankings: Dict[str, List[Tuple[str, float]]], 
        ground_truth: Dict[str, str],
        k_values: List[int] = [1, 3, 5, 10, 20]
    ) -> Dict[str, float]:
        """
        计算Top-K准确率
        """
        results = {}
        
        for k in k_values:
            correct = 0
            total = 0
            
            for student_id, true_project in ground_truth.items():
                if student_id not in rankings:
                    continue
                
                # 获取Top-K推荐
                top_k = rankings[student_id][:k]
                top_k_projects = [proj_id for proj_id, score in top_k]
                
                # 检查真实项目是否在Top-K中
                if true_project in top_k_projects:
                    correct += 1
                
                total += 1
            
            accuracy = correct / total if total > 0 else 0
            results[f"top_{k}_accuracy"] = accuracy
        
        return results
    
    def evaluate_ranking_quality(
        self, 
        rankings: Dict[str, List[Tuple[str, float]]], 
        ground_truth: Dict[str, str]
    ) -> Dict[str, float]:
        """
        评估排名质量
        """
        ranks = []
        reciprocal_ranks = []
        
        for student_id, true_project in ground_truth.items():
            if student_id not in rankings:
                continue
            
            ranking = rankings[student_id]
            project_ids = [proj_id for proj_id, score in ranking]
            
            try:
                # 找到真实项目的排名（1-based）
                rank = project_ids.index(true_project) + 1
                ranks.append(rank)
                reciprocal_ranks.append(1.0 / rank)
            except ValueError:
                # 如果真实项目不在排名中，给最差排名
                ranks.append(len(project_ids) + 1)
                reciprocal_ranks.append(0)
        
        results = {
            "mean_rank": float(np.mean(ranks)),
            "median_rank": float(np.median(ranks)),
            "std_rank": float(np.std(ranks)),
            "mrr": float(np.mean(reciprocal_ranks)),  # Mean Reciprocal Rank
            "best_rank": int(np.min(ranks)),
            "worst_rank": int(np.max(ranks)),
        }
        
        return results
    
    def evaluate_score_distribution(
        self, 
        rankings: Dict[str, List[Tuple[str, float]]], 
        ground_truth: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        分析相似度得分的分布
        """
        matched_scores = []
        unmatched_scores = []
        
        for student_id, true_project in ground_truth.items():
            if student_id not in rankings:
                continue
            
            for project_id, score in rankings[student_id]:
                if project_id == true_project:
                    matched_scores.append(score)
                else:
                    unmatched_scores.append(score)
        
        results = {
            "matched": {
                "mean": float(np.mean(matched_scores)) if matched_scores else 0,
                "std": float(np.std(matched_scores)) if matched_scores else 0,
                "median": float(np.median(matched_scores)) if matched_scores else 0,
                "min": float(np.min(matched_scores)) if matched_scores else 0,
                "max": float(np.max(matched_scores)) if matched_scores else 0,
            },
            "unmatched": {
                "mean": float(np.mean(unmatched_scores)) if unmatched_scores else 0,
                "std": float(np.std(unmatched_scores)) if unmatched_scores else 0,
                "median": float(np.median(unmatched_scores)) if unmatched_scores else 0,
                "min": float(np.min(unmatched_scores)) if unmatched_scores else 0,
                "max": float(np.max(unmatched_scores)) if unmatched_scores else 0,
            },
        }
        
        # 计算Cohen's d
        if matched_scores and unmatched_scores:
            pooled_std = np.sqrt((np.var(matched_scores) + np.var(unmatched_scores)) / 2)
            cohens_d = (np.mean(matched_scores) - np.mean(unmatched_scores)) / pooled_std if pooled_std > 0 else 0
            results["cohens_d"] = float(cohens_d)
        else:
            results["cohens_d"] = 0
        
        return results
    
    def evaluate_method(self, method: str) -> Dict[str, Any]:
        """
        完整评估一个方法
        """
        print(f"\n{'='*60}")
        print(f"📊 评估 Method {method}")
        print(f"{'='*60}\n")
        
        # 加载数据
        rankings = self.load_similarity_matrix(method)
        if not rankings:
            print(f"⚠️  无法加载 Method {method} 的数据")
            return {}
        
        # 创建ground truth
        ground_truth = self.create_ground_truth(rankings)
        if not ground_truth:
            print("⚠️  无法创建ground truth")
            return {}
        
        print(f"✅ 加载了 {len(rankings)} 个学生的排名")
        print(f"✅ Ground truth包含 {len(ground_truth)} 个匹配\n")
        
        # 各种评估
        topk_results = self.evaluate_topk_accuracy(rankings, ground_truth)
        ranking_results = self.evaluate_ranking_quality(rankings, ground_truth)
        score_dist = self.evaluate_score_distribution(rankings, ground_truth)
        
        # 打印结果
        print("📈 Top-K准确率:")
        for k_name, accuracy in sorted(topk_results.items()):
            print(f"  {k_name}: {accuracy:.2%}")
        
        print("\n📊 排名质量:")
        print(f"  平均排名: {ranking_results['mean_rank']:.2f}")
        print(f"  中位数排名: {ranking_results['median_rank']:.2f}")
        print(f"  MRR: {ranking_results['mrr']:.4f}")
        print(f"  排名范围: [{ranking_results['best_rank']}, {ranking_results['worst_rank']}]")
        
        print("\n📉 得分分布:")
        print(f"  Matched得分: {score_dist['matched']['mean']:.4f} ± {score_dist['matched']['std']:.4f}")
        print(f"  Unmatched得分: {score_dist['unmatched']['mean']:.4f} ± {score_dist['unmatched']['std']:.4f}")
        print(f"  Cohen's d: {score_dist['cohens_d']:.4f}")
        
        # 综合报告
        full_results = {
            "method": method,
            "topk_accuracy": topk_results,
            "ranking_quality": ranking_results,
            "score_distribution": score_dist,
        }
        
        # 评估
        print("\n🎯 评估:")
        top3_acc = topk_results.get("top_3_accuracy", 0)
        mrr = ranking_results.get("mrr", 0)
        
        if top3_acc >= 0.5:
            print("  ✅ 优秀！Top-3准确率 >= 50%")
        elif top3_acc >= 0.3:
            print("  ⚠️  中等。Top-3准确率在30-50%之间")
        else:
            print("  ❌ 较差。Top-3准确率 < 30%")
        
        if mrr >= 0.5:
            print("  ✅ 优秀！MRR >= 0.5")
        elif mrr >= 0.3:
            print("  ⚠️  中等。MRR在0.3-0.5之间")
        else:
            print("  ❌ 较差。MRR < 0.3")
        
        return full_results
    
    def compare_methods(self, methods: List[str]) -> Dict[str, Any]:
        """
        比较多个方法
        """
        all_results = {}
        
        for method in methods:
            try:
                results = self.evaluate_method(method)
                if results:
                    all_results[method] = results
            except Exception as e:
                print(f"⚠️  评估 Method {method} 时出错: {e}")
        
        # 生成对比表
        if len(all_results) > 1:
            print(f"\n{'='*60}")
            print("📊 方法对比")
            print(f"{'='*60}\n")
            
            # Top-K准确率对比
            print("Top-K准确率对比:")
            print(f"{'Method':<10} {'Top-1':<10} {'Top-3':<10} {'Top-5':<10} {'MRR':<10}")
            print("-" * 50)
            
            for method, results in sorted(all_results.items()):
                top1 = results["topk_accuracy"].get("top_1_accuracy", 0)
                top3 = results["topk_accuracy"].get("top_3_accuracy", 0)
                top5 = results["topk_accuracy"].get("top_5_accuracy", 0)
                mrr = results["ranking_quality"].get("mrr", 0)
                
                print(f"{method:<10} {top1:<10.2%} {top3:<10.2%} {top5:<10.2%} {mrr:<10.4f}")
            
            # 得分分布对比
            print("\nCohen's d对比:")
            print(f"{'Method':<10} {'Cohen\\'s d':<15} {'解释'}")
            print("-" * 50)
            
            for method, results in sorted(all_results.items()):
                d = results["score_distribution"].get("cohens_d", 0)
                
                if abs(d) < 0.2:
                    interp = "可忽略"
                elif abs(d) < 0.5:
                    interp = "小"
                elif abs(d) < 0.8:
                    interp = "中等"
                else:
                    interp = "大"
                
                print(f"{method:<10} {d:<15.4f} {interp}")
        
        return all_results
    
    def save_results(self, results: Dict[str, Any], output_file: str):
        """保存结果"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✅ 结果已保存至: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="使用改进的指标评估匹配方法")
    parser.add_argument(
        "--method",
        type=str,
        choices=["1a", "1b", "2a", "2b", "all"],
        default="all",
        help="要评估的方法"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="outputs/improved_evaluation_results.json",
        help="输出文件路径"
    )
    
    args = parser.parse_args()
    
    evaluator = ImprovedEvaluator()
    
    if args.method == "all":
        methods = ["1a", "1b", "2a", "2b"]
        results = evaluator.compare_methods(methods)
    else:
        results = {args.method: evaluator.evaluate_method(args.method)}
    
    if results:
        evaluator.save_results(results, args.output)
    else:
        print("\n⚠️  没有生成有效的评估结果")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())


