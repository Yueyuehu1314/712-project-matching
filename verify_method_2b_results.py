#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证Method 2b Enhanced的结果数据
"""

import json
from pathlib import Path
from collections import defaultdict

def verify_results():
    """验证Method 2b结果的完整性和正确性"""
    
    print("=" * 80)
    print("Method 2b Enhanced 结果验证")
    print("=" * 80)
    print()
    
    # 1. 加载分数数据
    scores_file = "outputs/kg_similarity/method_2b_scores_enhanced.json"
    with open(scores_file, 'r', encoding='utf-8') as f:
        scores = json.load(f)
    
    print(f"✓ 加载分数数据: {len(scores)} 条记录")
    
    # 2. 加载Gap数据
    gaps_file = "outputs/kg_similarity/method_2b_gaps.json"
    with open(gaps_file, 'r', encoding='utf-8') as f:
        gaps = json.load(f)
    
    print(f"✓ 加载Gap数据: {len(gaps)} 条记录")
    print()
    
    # 3. 验证数据一致性
    print("📊 数据验证:")
    print("-" * 80)
    
    # 检查数量
    if len(scores) == len(gaps):
        print(f"✅ 数据数量一致: {len(scores)} 条")
    else:
        print(f"❌ 数据数量不一致: scores={len(scores)}, gaps={len(gaps)}")
    
    # 按项目统计
    project_counts = defaultdict(int)
    student_ids = set()
    
    for score in scores:
        project_counts[score['project_name']] += 1
        student_ids.add(score['student_id'])
    
    print(f"✅ 项目数量: {len(project_counts)}")
    print(f"✅ 唯一学生数: {len(student_ids)}")
    print()
    
    # 4. 每个项目的学生数
    print("📋 每个项目的学生数:")
    print("-" * 80)
    
    for project, count in sorted(project_counts.items()):
        status = "✅" if count == 10 else "⚠️ "
        print(f"{status} {project[:60]:<60} {count:>3} 个学生")
    
    print()
    
    # 5. 相似度分数范围检查
    print("📈 相似度指标检查:")
    print("-" * 80)
    
    jaccard_nodes = [s['jaccard_similarity'] for s in scores]
    jaccard_edges = [s['jaccard_edge_similarity'] for s in scores]
    edit_distances = [s['edit_distance'] for s in scores]
    
    print(f"Jaccard节点相似度:")
    print(f"  - 范围: [{min(jaccard_nodes):.4f}, {max(jaccard_nodes):.4f}]")
    print(f"  - 异常值: {sum(1 for x in jaccard_nodes if x > 0.2)} 个 (>20%)")
    
    print(f"\nJaccard边相似度:")
    print(f"  - 范围: [{min(jaccard_edges):.4f}, {max(jaccard_edges):.4f}]")
    print(f"  - 零值: {sum(1 for x in jaccard_edges if x == 0)} 个")
    
    print(f"\n编辑距离:")
    print(f"  - 范围: [{min(edit_distances):.0f}, {max(edit_distances):.0f}]")
    print(f"  - 大距离: {sum(1 for x in edit_distances if x > 80)} 个 (>80)")
    
    print()
    
    # 6. Gap分析检查
    print("🔍 Gap分析检查:")
    print("-" * 80)
    
    modification_steps = [g['total_modification_steps'] for g in gaps]
    readiness_scores = [g['readiness_score'] for g in gaps]
    missing_nodes = [g['missing_nodes_count'] for g in gaps]
    
    print(f"修改步骤数:")
    print(f"  - 范围: [{min(modification_steps)}, {max(modification_steps)}]")
    print(f"  - 零值: {sum(1 for x in modification_steps if x == 0)} 个")
    
    print(f"\n准备度分数:")
    print(f"  - 范围: [{min(readiness_scores):.4f}, {max(readiness_scores):.4f}]")
    print(f"  - 高准备度: {sum(1 for x in readiness_scores if x > 0.15)} 个 (>15%)")
    print(f"  - 零准备度: {sum(1 for x in readiness_scores if x == 0)} 个")
    
    print(f"\n缺失节点数:")
    print(f"  - 范围: [{min(missing_nodes)}, {max(missing_nodes)}]")
    print(f"  - 零值: {sum(1 for x in missing_nodes if x == 0)} 个")
    
    print()
    
    # 7. Top 5最匹配和最不匹配
    print("🏆 Top 5 最匹配的学生-项目对:")
    print("-" * 80)
    
    sorted_by_readiness = sorted(gaps, key=lambda x: x['readiness_score'], reverse=True)
    for i, gap in enumerate(sorted_by_readiness[:5], 1):
        print(f"{i}. {gap['project_name'][:40]:<40} | {gap['student_id'][:30]:<30}")
        print(f"   准备度: {gap['readiness_score']:.2%} | 缺失技能: {gap['missing_nodes_count']}")
    
    print()
    print("⚠️  Top 5 最不匹配的学生-项目对:")
    print("-" * 80)
    
    for i, gap in enumerate(sorted_by_readiness[-5:], 1):
        print(f"{i}. {gap['project_name'][:40]:<40} | {gap['student_id'][:30]:<30}")
        print(f"   准备度: {gap['readiness_score']:.2%} | 缺失技能: {gap['missing_nodes_count']}")
    
    print()
    print("=" * 80)
    print("✅ 验证完成！")
    print("=" * 80)


if __name__ == '__main__':
    verify_results()

