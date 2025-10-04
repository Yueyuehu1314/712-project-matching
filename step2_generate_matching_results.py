#!/usr/bin/env python3
"""
Step 2: 生成Matching Results并导出可视化数据
"""

import json
import numpy as np
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity

def main():
    print("=" * 80)
    print("🎯 Step 2: 生成Matching Results并导出可视化数据")
    print("=" * 80)
    print()

    # 1. 加载embeddings
    print("📊 Step 2.1: 加载embeddings...")
    with open('outputs/embeddings/method_1b_embeddings.json') as f:
        method_1b_data = json.load(f)

    embeddings = method_1b_data['embeddings']
    print(f"   ✅ 已加载 {len(embeddings)} 个embeddings")
    print()

    # 2. 分离项目和学生embeddings
    print("🔍 Step 2.2: 分离项目和学生embeddings...")

    projects_emb = {}
    students_emb = {}

    for emb in embeddings:
        if emb['doc_type'] == 'project':
            # 从文件名提取项目名
            project_name = emb['file_name'].replace('.md', '')
            projects_emb[project_name] = np.array(emb['embedding'])
        
        elif emb['doc_type'] == 'profile':
            # 从文件名提取学生ID
            file_name = emb['file_name'].replace('.md', '')
            # 提取项目文件夹作为关联信息
            project_folder = emb.get('project_folder')
            matched_project = emb.get('matched_project')
            
            students_emb[file_name] = {
                'embedding': np.array(emb['embedding']),
                'project_folder': project_folder,
                'matched_project': matched_project
            }

    print(f"   ✅ 项目数量: {len(projects_emb)}")
    print(f"   ✅ 学生数量: {len(students_emb)}")
    print()

    # 3. 识别baseline和enhanced项目
    print("🔍 Step 2.3: 识别Baseline和Enhanced项目...")

    import os
    baseline_kg_dir = Path('outputs1/knowledge_graphs/three_layer_projects')
    baseline_files = [f for f in os.listdir(baseline_kg_dir) if f.endswith('_entities.json')]

    baseline_projects = set()
    for f in baseline_files:
        with open(baseline_kg_dir / f) as file:
            entities = json.load(file)
            if entities:
                file_path = entities[0].get('properties', {}).get('file_path', '')
                if file_path:
                    project_name = file_path.split('/')[-1].replace('.md', '')
                    baseline_projects.add(project_name)

    # Enhanced项目就是所有项目
    enhanced_projects = set(projects_emb.keys())

    baseline_projects = sorted(list(baseline_projects))
    enhanced_projects = sorted(list(enhanced_projects))

    print(f"   ✅ Baseline项目: {len(baseline_projects)}")
    print(f"   ✅ Enhanced项目: {len(enhanced_projects)}")
    
    # 找出共同项目
    common_projects = sorted(list(set(baseline_projects) & set(enhanced_projects)))
    print(f"   ℹ️  共同项目（可配对比较）: {len(common_projects)}")
    print()

    # 4. 计算相似度 - Method 1b
    print("📊 Step 2.4: 计算Method 1b相似度...")

    # 为baseline和enhanced分别计算相似度
    baseline_scores_1b = {}
    enhanced_scores_1b = {}

    for student_id, student_data in students_emb.items():
        student_vec = student_data['embedding'].reshape(1, -1)
        
        # Baseline
        for project_name in baseline_projects:
            if project_name in projects_emb:
                project_vec = projects_emb[project_name].reshape(1, -1)
                score = cosine_similarity(student_vec, project_vec)[0][0]
                
                if student_id not in baseline_scores_1b:
                    baseline_scores_1b[student_id] = {}
                baseline_scores_1b[student_id][project_name] = float(score)
        
        # Enhanced
        for project_name in enhanced_projects:
            if project_name in projects_emb:
                project_vec = projects_emb[project_name].reshape(1, -1)
                score = cosine_similarity(student_vec, project_vec)[0][0]
                
                if student_id not in enhanced_scores_1b:
                    enhanced_scores_1b[student_id] = {}
                enhanced_scores_1b[student_id][project_name] = float(score)

    print(f"   ✅ Baseline配对数: {sum(len(scores) for scores in baseline_scores_1b.values())}")
    print(f"   ✅ Enhanced配对数: {sum(len(scores) for scores in enhanced_scores_1b.values())}")
    print()

    # 5. 加载Method 2b的相似度分数
    print("📊 Step 2.5: 加载Method 2b的相似度分数...")
    with open('outputs/kg_similarity/method_2b_scores.json') as f:
        method_2b_results = json.load(f)

    baseline_scores_2b = {}
    enhanced_scores_2b = {}

    for result in method_2b_results:
        student_id = result['student_id']
        project = result['project_name']
        score = result['jaccard_similarity']
        
        # 检查是baseline还是enhanced
        if project in baseline_projects:
            if student_id not in baseline_scores_2b:
                baseline_scores_2b[student_id] = {}
            baseline_scores_2b[student_id][project] = score
        
        if project in enhanced_projects:
            if student_id not in enhanced_scores_2b:
                enhanced_scores_2b[student_id] = {}
            enhanced_scores_2b[student_id][project] = score

    print(f"   ✅ Baseline配对数: {sum(len(scores) for scores in baseline_scores_2b.values())}")
    print(f"   ✅ Enhanced配对数: {sum(len(scores) for scores in enhanced_scores_2b.values())}")
    print()

    # 6. 生成Top-K匹配结果
    print("🎯 Step 2.6: 生成Top-K匹配结果...")

    def get_top_k_matches(student_scores, k=5):
        """获取学生的Top-K匹配项目"""
        sorted_projects = sorted(student_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_projects[:k]

    matching_results = {
        'method_1b': {
            'baseline': {},
            'enhanced': {}
        },
        'method_2b': {
            'baseline': {},
            'enhanced': {}
        }
    }

    # Method 1b - Baseline
    for student_id, scores in baseline_scores_1b.items():
        top_k = get_top_k_matches(scores, k=5)
        matching_results['method_1b']['baseline'][student_id] = [
            {'project': proj, 'score': score, 'rank': i+1}
            for i, (proj, score) in enumerate(top_k)
        ]

    # Method 1b - Enhanced
    for student_id, scores in enhanced_scores_1b.items():
        top_k = get_top_k_matches(scores, k=5)
        matching_results['method_1b']['enhanced'][student_id] = [
            {'project': proj, 'score': score, 'rank': i+1}
            for i, (proj, score) in enumerate(top_k)
        ]

    # Method 2b - Baseline
    for student_id, scores in baseline_scores_2b.items():
        top_k = get_top_k_matches(scores, k=5)
        matching_results['method_2b']['baseline'][student_id] = [
            {'project': proj, 'score': score, 'rank': i+1}
            for i, (proj, score) in enumerate(top_k)
        ]

    # Method 2b - Enhanced
    for student_id, scores in enhanced_scores_2b.items():
        top_k = get_top_k_matches(scores, k=5)
        matching_results['method_2b']['enhanced'][student_id] = [
            {'project': proj, 'score': score, 'rank': i+1}
            for i, (proj, score) in enumerate(top_k)
        ]

    print(f"   ✅ 已生成Top-5匹配结果")
    print()

    # 7. 计算统计数据
    print("📈 Step 2.7: 计算统计数据...")

    stats = {
        'method_1b': {
            'baseline': {
                'n_students': len(matching_results['method_1b']['baseline']),
                'avg_top1_score': np.mean([matches[0]['score'] for matches in matching_results['method_1b']['baseline'].values()]),
                'avg_top5_score': np.mean([np.mean([m['score'] for m in matches]) for matches in matching_results['method_1b']['baseline'].values()])
            },
            'enhanced': {
                'n_students': len(matching_results['method_1b']['enhanced']),
                'avg_top1_score': np.mean([matches[0]['score'] for matches in matching_results['method_1b']['enhanced'].values()]),
                'avg_top5_score': np.mean([np.mean([m['score'] for m in matches]) for matches in matching_results['method_1b']['enhanced'].values()])
            }
        },
        'method_2b': {
            'baseline': {
                'n_students': len(matching_results['method_2b']['baseline']),
                'avg_top1_score': np.mean([matches[0]['score'] for matches in matching_results['method_2b']['baseline'].values()]),
                'avg_top5_score': np.mean([np.mean([m['score'] for m in matches]) for matches in matching_results['method_2b']['baseline'].values()])
            },
            'enhanced': {
                'n_students': len(matching_results['method_2b']['enhanced']),
                'avg_top1_score': np.mean([matches[0]['score'] for matches in matching_results['method_2b']['enhanced'].values()]),
                'avg_top5_score': np.mean([np.mean([m['score'] for m in matches]) for matches in matching_results['method_2b']['enhanced'].values()])
            }
        }
    }

    print(f"   Method 1b (Profile Embeddings):")
    print(f"      Baseline:")
    print(f"         • 学生数: {stats['method_1b']['baseline']['n_students']}")
    print(f"         • Top-1平均分: {stats['method_1b']['baseline']['avg_top1_score']:.4f}")
    print(f"         • Top-5平均分: {stats['method_1b']['baseline']['avg_top5_score']:.4f}")
    print(f"      Enhanced:")
    print(f"         • 学生数: {stats['method_1b']['enhanced']['n_students']}")
    print(f"         • Top-1平均分: {stats['method_1b']['enhanced']['avg_top1_score']:.4f}")
    print(f"         • Top-5平均分: {stats['method_1b']['enhanced']['avg_top5_score']:.4f}")
    print()
    print(f"   Method 2b (Graph Similarity):")
    print(f"      Baseline:")
    print(f"         • 学生数: {stats['method_2b']['baseline']['n_students']}")
    print(f"         • Top-1平均分: {stats['method_2b']['baseline']['avg_top1_score']:.4f}")
    print(f"         • Top-5平均分: {stats['method_2b']['baseline']['avg_top5_score']:.4f}")
    print(f"      Enhanced:")
    print(f"         • 学生数: {stats['method_2b']['enhanced']['n_students']}")
    print(f"         • Top-1平均分: {stats['method_2b']['enhanced']['avg_top1_score']:.4f}")
    print(f"         • Top-5平均分: {stats['method_2b']['enhanced']['avg_top5_score']:.4f}")
    print()

    # 8. 保存结果
    output_dir = Path('outputs/kg_comparison')
    output_dir.mkdir(parents=True, exist_ok=True)

    output_data = {
        'matching_results': matching_results,
        'statistics': stats,
        'metadata': {
            'n_baseline_projects': len(baseline_projects),
            'n_enhanced_projects': len(enhanced_projects),
            'n_common_projects': len(common_projects),
            'baseline_projects': baseline_projects,
            'enhanced_projects': enhanced_projects,
            'common_projects': common_projects,
            'methods': ['method_1b', 'method_2b'],
            'top_k': 5
        }
    }

    output_path = output_dir / 'step2_matching_results.json'
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"💾 Step 2.8: 保存结果到 {output_path}")
    print()
    print("=" * 80)
    print("✅ Step 2 完成!")
    print("=" * 80)

if __name__ == '__main__':
    main()

