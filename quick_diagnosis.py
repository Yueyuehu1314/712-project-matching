#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速诊断脚本
一键检查所有实验结果并给出改进建议
"""

import json
from pathlib import Path
import numpy as np


def load_json(file_path):
    """加载JSON文件"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  无法加载 {file_path}: {e}")
        return None


def diagnose_method_1a():
    """诊断Method 1a"""
    file_path = Path("outputs/embeddings/1a/similarity_comparison_results.json")
    
    if not file_path.exists():
        return {"status": "missing", "message": "结果文件不存在"}
    
    data = load_json(file_path)
    if not data:
        return {"status": "error", "message": "无法读取结果"}
    
    # 提取关键指标
    try:
        matched_mean = data["analysis"]["matched_pairs"]["mean"]
        unmatched_mean = data["analysis"]["unmatched_pairs"]["mean"]
        cohens_d = data["analysis"]["comparison"]["effect_size_cohens_d"]
        
        diagnosis = {
            "status": "ok",
            "matched_mean": matched_mean,
            "unmatched_mean": unmatched_mean,
            "difference": matched_mean - unmatched_mean,
            "cohens_d": cohens_d,
        }
        
        # 评估
        if abs(cohens_d) < 0.05:
            diagnosis["evaluation"] = "❌ 极差"
            diagnosis["problem"] = "效果量接近0，完全无区分能力"
        elif abs(cohens_d) < 0.2:
            diagnosis["evaluation"] = "⚠️  很弱"
            diagnosis["problem"] = "效果量过小，区分能力很弱"
        elif abs(cohens_d) < 0.5:
            diagnosis["evaluation"] = "🔶 较弱"
            diagnosis["problem"] = "效果量小，区分能力有限"
        else:
            diagnosis["evaluation"] = "✅ 可用"
            diagnosis["problem"] = None
        
        return diagnosis
    
    except Exception as e:
        return {"status": "error", "message": str(e)}


def diagnose_method_1b():
    """诊断Method 1b"""
    file_path = Path("outputs/embeddings/1b/similarity_comparison_results.json")
    
    if not file_path.exists():
        return {"status": "missing", "message": "结果文件不存在"}
    
    data = load_json(file_path)
    if not data:
        return {"status": "error", "message": "无法读取结果"}
    
    try:
        matched_mean = data["statistics"]["matched_pairs"]["mean"]
        unmatched_mean = data["statistics"]["unmatched_pairs"]["mean"]
        cohens_d = data["effect_size"]["cohens_d"]
        
        diagnosis = {
            "status": "ok",
            "matched_mean": matched_mean,
            "unmatched_mean": unmatched_mean,
            "difference": matched_mean - unmatched_mean,
            "cohens_d": cohens_d,
        }
        
        if abs(cohens_d) < 0.01:
            diagnosis["evaluation"] = "❌ 完全失效"
            diagnosis["problem"] = "matched和unmatched得分几乎相同"
        elif cohens_d < 0:
            diagnosis["evaluation"] = "❌ 反向"
            diagnosis["problem"] = "matched得分反而低于unmatched"
        elif abs(cohens_d) < 0.2:
            diagnosis["evaluation"] = "⚠️  很弱"
            diagnosis["problem"] = "效果量过小"
        else:
            diagnosis["evaluation"] = "✅ 可用"
            diagnosis["problem"] = None
        
        return diagnosis
    
    except Exception as e:
        return {"status": "error", "message": str(e)}


def diagnose_method_2a():
    """诊断Method 2a"""
    # 加载基础分析
    analysis_file = Path("outputs/kg_similarity/2a/method_2a_analysis.json")
    scores_file = Path("outputs/kg_similarity/2a/method_2a_scores.json")
    
    if not analysis_file.exists():
        return {"status": "missing", "message": "结果文件不存在"}
    
    data = load_json(analysis_file)
    if not data:
        return {"status": "error", "message": "无法读取结果"}
    
    try:
        # 基础指标
        jaccard_mean = data["matched_jaccard"]["mean"]
        jaccard_median = data["matched_jaccard"]["median"]
        edit_dist_mean = data["matched_edit_distance"]["mean"]
        
        diagnosis = {
            "status": "ok",
            "jaccard_mean": jaccard_mean,
            "jaccard_median": jaccard_median,
            "edit_distance_mean": edit_dist_mean,
        }
        
        # 分析正负样本的modification steps
        if scores_file.exists():
            scores = load_json(scores_file)
            if scores:
                matched_edits = [s["edit_distance"] for s in scores if s.get("is_match", False)]
                unmatched_edits = [s["edit_distance"] for s in scores if not s.get("is_match", False)]
                
                if matched_edits and unmatched_edits:
                    diagnosis["matched_modifications"] = {
                        "mean": float(np.mean(matched_edits)),
                        "median": float(np.median(matched_edits)),
                        "std": float(np.std(matched_edits)),
                    }
                    diagnosis["unmatched_modifications"] = {
                        "mean": float(np.mean(unmatched_edits)),
                        "median": float(np.median(unmatched_edits)),
                        "std": float(np.std(unmatched_edits)),
                    }
                    diagnosis["modification_difference"] = diagnosis["matched_modifications"]["mean"] - diagnosis["unmatched_modifications"]["mean"]
        
        # 评估
        if jaccard_mean < 0.02:
            diagnosis["evaluation"] = "❌ 极低"
            diagnosis["problem"] = "Jaccard相似度<2%，知识重叠极少"
        elif jaccard_mean < 0.05:
            diagnosis["evaluation"] = "⚠️  很低"
            diagnosis["problem"] = "Jaccard相似度<5%，知识重叠很少"
        elif jaccard_mean < 0.15:
            diagnosis["evaluation"] = "🔶 较低"
            diagnosis["problem"] = "Jaccard相似度<15%，仍有改进空间"
        else:
            diagnosis["evaluation"] = "✅ 可用"
            diagnosis["problem"] = None
        
        return diagnosis
    
    except Exception as e:
        return {"status": "error", "message": str(e)}


def diagnose_method_2b():
    """诊断Method 2b"""
    analysis_file = Path("outputs/kg_similarity/2b/method_2b_analysis_enhanced.json")
    gaps_file = Path("outputs/kg_similarity/2b/method_2b_gaps.json")
    scores_file = Path("outputs/kg_similarity/2b/method_2b_scores_enhanced.json")
    
    if not analysis_file.exists():
        return {"status": "missing", "message": "结果文件不存在"}
    
    data = load_json(analysis_file)
    if not data:
        return {"status": "error", "message": "无法读取结果"}
    
    try:
        node_jaccard = data["similarity_metrics"]["jaccard_nodes"]["mean"]
        edge_jaccard = data["similarity_metrics"]["jaccard_edges"]["mean"]
        readiness = data.get("gap_analysis", {}).get("readiness_score", {}).get("mean", 0)
        modifications_mean = data.get("gap_analysis", {}).get("modification_steps", {}).get("mean", 0)
        
        diagnosis = {
            "status": "ok",
            "node_jaccard": node_jaccard,
            "edge_jaccard": edge_jaccard,
            "readiness": readiness,
            "modifications_mean": modifications_mean,
        }
        
        # 分析正负样本的modification steps对比
        if gaps_file.exists() and scores_file.exists():
            gaps = load_json(gaps_file)
            scores = load_json(scores_file)
            
            if gaps and scores:
                # 创建student_id->project_name映射来判断是否匹配
                matched_modifications = []
                unmatched_modifications = []
                
                for gap in gaps:
                    student_id = gap.get("student_id", "")
                    project_name = gap.get("project_name", "")
                    modifications = gap.get("total_modification_steps", 0)
                    
                    # 从scores中找到对应的is_match
                    is_match = False
                    for score in scores:
                        if score.get("student_id") == student_id and score.get("project_name") == project_name:
                            is_match = score.get("is_match", False)
                            break
                    
                    if is_match:
                        matched_modifications.append(modifications)
                    else:
                        unmatched_modifications.append(modifications)
                
                if matched_modifications and unmatched_modifications:
                    diagnosis["matched_modifications"] = {
                        "mean": float(np.mean(matched_modifications)),
                        "median": float(np.median(matched_modifications)),
                        "std": float(np.std(matched_modifications)),
                    }
                    diagnosis["unmatched_modifications"] = {
                        "mean": float(np.mean(unmatched_modifications)),
                        "median": float(np.median(unmatched_modifications)),
                        "std": float(np.std(unmatched_modifications)),
                    }
                    diagnosis["modification_difference"] = diagnosis["matched_modifications"]["mean"] - diagnosis["unmatched_modifications"]["mean"]
        
        # 评估
        if node_jaccard < 0.05:
            diagnosis["evaluation"] = "⚠️  节点重叠低"
            diagnosis["problem"] = "节点Jaccard<5%，知识重叠不足"
        elif node_jaccard < 0.15:
            diagnosis["evaluation"] = "🔶 节点重叠较低"
            diagnosis["problem"] = "节点Jaccard<15%，有改进空间"
        else:
            diagnosis["evaluation"] = "✅ 节点重叠可用"
            diagnosis["problem"] = None
        
        return diagnosis
    
    except Exception as e:
        return {"status": "error", "message": str(e)}


def generate_recommendations(diagnoses):
    """根据诊断生成改进建议"""
    print("\n" + "="*70)
    print("🎯 改进建议（按优先级排序）")
    print("="*70)
    
    recommendations = []
    
    # 分析所有方法的状态
    all_poor = all(
        d.get("status") == "ok" and "❌" in d.get("evaluation", "")
        for d in diagnoses.values()
        if isinstance(d, dict) and d.get("status") == "ok"
    )
    
    if all_poor:
        recommendations.append({
            "priority": "🔴 最高",
            "action": "先检查数据质量",
            "reason": "所有方法都表现不佳，可能是数据问题",
            "command": "python src/utils/data_quality_checker.py"
        })
    
    # Method 1相关建议
    method_1a = diagnoses.get("1a", {})
    method_1b = diagnoses.get("1b", {})
    
    if method_1a.get("status") == "ok" and abs(method_1a.get("cohens_d", 0)) < 0.1:
        recommendations.append({
            "priority": "🟠 高",
            "action": "优化Embedding方法",
            "reason": f"Method 1a的Cohen's d={method_1a.get('cohens_d', 0):.4f}，太小了",
            "suggestions": [
                "尝试只比较技能部分，不要整个文档",
                "尝试不同的embedding模型（nomic-embed-text, mxbai-embed-large）",
                "添加特征工程，提取结构化特征"
            ]
        })
    
    if method_1b.get("status") == "ok" and method_1b.get("cohens_d", 0) < 0:
        recommendations.append({
            "priority": "🟡 中",
            "action": "放弃Method 1b或重新设计",
            "reason": "添加更多信息后效果反而变差（信息稀释）",
            "suggestions": [
                "如果要用1b，需要精心选择添加哪些信息",
                "或者直接使用1a的简化版本"
            ]
        })
    
    # Method 2相关建议
    method_2a = diagnoses.get("2a", {})
    method_2b = diagnoses.get("2b", {})
    
    if method_2a.get("status") == "ok" and method_2a.get("jaccard_mean", 0) < 0.05:
        recommendations.append({
            "priority": "🟠 高",
            "action": "改进知识图谱匹配算法",
            "reason": f"Method 2a的Jaccard={method_2a.get('jaccard_mean', 0):.2%}，过低",
            "suggestions": [
                "实现语义相似度节点匹配（不要求完全相同）",
                "考虑间接关系（如果学生有先决条件技能）",
                "使用加权Jaccard（核心技能权重更高）"
            ]
        })
    
    if method_2b.get("status") == "ok":
        node_j = method_2b.get("node_jaccard", 0)
        if node_j < 0.10:
            recommendations.append({
                "priority": "🟠 高",
                "action": "增强知识图谱的节点匹配",
                "reason": f"Method 2b的节点Jaccard={node_j:.2%}，仍然很低",
                "suggestions": [
                    "使用Node2Vec生成节点embedding",
                    "计算节点间的语义相似度",
                    "扩展同义词（如Python Programming = Python）"
                ]
            })
    
    # 混合方法建议
    if len([d for d in diagnoses.values() if isinstance(d, dict) and d.get("status") == "ok"]) >= 2:
        recommendations.append({
            "priority": "🟢 中低",
            "action": "尝试混合方法",
            "reason": "单一方法效果有限，混合可能更好",
            "suggestions": [
                "结合Embedding的语义理解和KG的结构信息",
                "两阶段：先用Embedding筛选，再用KG精排",
                "特征融合：提取多维度特征后用机器学习模型"
            ]
        })
    
    # 评估指标建议
    recommendations.append({
        "priority": "🟡 中",
        "action": "使用更实际的评估指标",
        "reason": "Cohen's d可能过于严格",
        "suggestions": [
            "计算Top-K准确率（能否推荐正确项目在前K名）",
            "计算MRR（Mean Reciprocal Rank）",
            "评估实际可用性（推荐的项目是否真的合适）"
        ],
        "command": "python src/experiments/improved_evaluation_metrics.py --method all"
    })
    
    # 打印建议
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['priority']} - {rec['action']}")
        print(f"   原因: {rec['reason']}")
        
        if "suggestions" in rec:
            print("   建议:")
            for sug in rec["suggestions"]:
                print(f"     • {sug}")
        
        if "command" in rec:
            print(f"   命令: {rec['command']}")
    
    print("\n" + "="*70)


def main():
    """主函数"""
    print("\n" + "="*70)
    print("🔍 快速诊断：分析所有实验结果")
    print("="*70 + "\n")
    
    methods = {
        "1a": "Method 1a (PD only Embedding)",
        "1b": "Method 1b (PD+UO+Profile Embedding)",
        "2a": "Method 2a (基础KG相似度)",
        "2b": "Method 2b (增强KG相似度)",
    }
    
    diagnoses = {}
    
    for method_id, method_name in methods.items():
        print(f"\n{'='*70}")
        print(f"📊 {method_name}")
        print(f"{'='*70}")
        
        # 选择诊断函数
        if method_id == "1a":
            diagnosis = diagnose_method_1a()
        elif method_id == "1b":
            diagnosis = diagnose_method_1b()
        elif method_id == "2a":
            diagnosis = diagnose_method_2a()
        elif method_id == "2b":
            diagnosis = diagnose_method_2b()
        else:
            diagnosis = {"status": "unknown"}
        
        diagnoses[method_id] = diagnosis
        
        # 打印诊断结果
        if diagnosis.get("status") == "missing":
            print(f"⚠️  {diagnosis.get('message', 'Unknown error')}")
        elif diagnosis.get("status") == "error":
            print(f"❌ 错误: {diagnosis.get('message', 'Unknown error')}")
        elif diagnosis.get("status") == "ok":
            print(f"状态: {diagnosis.get('evaluation', 'Unknown')}")
            
            # 打印关键指标
            if "matched_mean" in diagnosis:
                print(f"\n关键指标:")
                print(f"  Matched均值:   {diagnosis['matched_mean']:.4f}")
                print(f"  Unmatched均值: {diagnosis['unmatched_mean']:.4f}")
                print(f"  差异:          {diagnosis['difference']:.4f}")
                print(f"  Cohen's d:     {diagnosis['cohens_d']:.4f}")
            
            if "jaccard_mean" in diagnosis:
                print(f"\n关键指标:")
                print(f"  Jaccard均值:   {diagnosis['jaccard_mean']:.4f} ({diagnosis['jaccard_mean']*100:.2f}%)")
                print(f"  Jaccard中位数: {diagnosis['jaccard_median']:.4f} ({diagnosis['jaccard_median']*100:.2f}%)")
                print(f"  Edit距离均值:  {diagnosis.get('edit_distance_mean', 0):.2f}")
                
                # 打印modifications对比
                if "matched_modifications" in diagnosis and "unmatched_modifications" in diagnosis:
                    print(f"\n📊 Modification Steps对比:")
                    print(f"  正样本(匹配):   {diagnosis['matched_modifications']['mean']:.2f} ± {diagnosis['matched_modifications']['std']:.2f}")
                    print(f"  负样本(不匹配): {diagnosis['unmatched_modifications']['mean']:.2f} ± {diagnosis['unmatched_modifications']['std']:.2f}")
                    print(f"  差异:          {diagnosis['modification_difference']:.2f}")
                    
                    # 判断是否有区分度
                    if diagnosis['modification_difference'] > 0:
                        print(f"  ⚠️  正样本需要更多modifications（差）")
                    else:
                        print(f"  ✅ 正样本需要更少modifications（好）")
            
            if "node_jaccard" in diagnosis:
                print(f"\n关键指标:")
                print(f"  节点Jaccard:   {diagnosis['node_jaccard']:.4f} ({diagnosis['node_jaccard']*100:.2f}%)")
                print(f"  边Jaccard:     {diagnosis['edge_jaccard']:.4f} ({diagnosis['edge_jaccard']*100:.2f}%)")
                if "readiness" in diagnosis:
                    print(f"  准备度:        {diagnosis['readiness']:.4f} ({diagnosis['readiness']*100:.2f}%)")
                if "modifications_mean" in diagnosis:
                    print(f"  Modifications: {diagnosis['modifications_mean']:.2f}")
                
                # 打印modifications对比
                if "matched_modifications" in diagnosis and "unmatched_modifications" in diagnosis:
                    print(f"\n📊 Modification Steps对比:")
                    print(f"  正样本(匹配):   {diagnosis['matched_modifications']['mean']:.2f} ± {diagnosis['matched_modifications']['std']:.2f}")
                    print(f"  负样本(不匹配): {diagnosis['unmatched_modifications']['mean']:.2f} ± {diagnosis['unmatched_modifications']['std']:.2f}")
                    print(f"  差异:          {diagnosis['modification_difference']:.2f}")
                    
                    # 判断是否有区分度
                    if diagnosis['modification_difference'] > 0:
                        print(f"  ⚠️  正样本需要更多modifications（差）")
                    elif abs(diagnosis['modification_difference']) < 2:
                        print(f"  ❌ 几乎没有区分度")
                    else:
                        print(f"  ✅ 正样本需要更少modifications（好）")
            
            # 打印问题
            if diagnosis.get("problem"):
                print(f"\n问题: {diagnosis['problem']}")
    
    # 生成改进建议
    generate_recommendations(diagnoses)
    
    print("\n💡 提示: 详细的改进策略请查看 IMPROVEMENT_STRATEGIES.md\n")


if __name__ == "__main__":
    main()

