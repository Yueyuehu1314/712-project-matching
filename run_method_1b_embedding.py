#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Method 1b: PD+UO Text Embedding Similarity Comparison

生成融合了Unit Outline的Project文本的embeddings，
与Student Profile embeddings进行相似度对比
"""

import sys
import os
from pathlib import Path

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 直接复用现有的embedding_similarity_comparison.py
# 只是改变输入目录

def main():
    print("=" * 80)
    print("Method 1b: PD+UO Text Embedding Similarity Experiment")
    print("=" * 80)
    print()
    print("📋 实验设置:")
    print("   Project Input: data/processed/enhanced_projects_md/ (PD+UO融合文本)")
    print("   Student Input: data/processed/profiles_md/ (学生档案)")
    print("   Embedding Model: bge-m3 (via Ollama)")
    print("   Output: outputs/embeddings/method_1b_*")
    print()
    
    # 检查输入目录
    enhanced_dir = Path("data/processed/enhanced_projects_md")
    if not enhanced_dir.exists() or not list(enhanced_dir.glob("*.md")):
        print("❌ Error: enhanced_projects_md 目录为空或不存在")
        print("   请先运行: python generate_enhanced_project_text.py")
        return 1
    
    print(f"✓ Found {len(list(enhanced_dir.glob('*.md')))} enhanced project files")
    print()
    
    # 使用现有的脚本，但修改输入参数
    print("🚀 Running embedding generation and similarity analysis...")
    print()
    
    # 调用原有脚本的逻辑，但用不同的目录
    from experiments.embedding_similarity_comparison import EmbeddingGenerator, SimilarityComparator
    
    try:
        # Step 1: Generate embeddings
        print("=" * 80)
        print("Step 1: Generate Embeddings")  
        print("=" * 80)
        
        generator = EmbeddingGenerator(
            projects_dir="data/processed/enhanced_projects_md",  # 使用 PD+UO 文本
            profiles_dir="data/processed/profiles_md",
            output_file="outputs/embeddings/method_1b_embeddings.json"
        )
        
        embeddings_file = generator.generate_all_embeddings()
        
        # Step 2: Analyze similarity
        print("\n" + "=" * 80)
        print("Step 2: Compute Similarity")
        print("=" * 80)
        
        comparator = SimilarityComparator(embeddings_file)
        comparator.load_embeddings()
        
        matched_scores, unmatched_scores = comparator.compute_all_similarities()
        
        # Step 3: Statistical analysis
        print("\n" + "=" * 80)
        print("Step 3: Statistical Analysis")
        print("=" * 80)
        
        results = comparator.analyze_results(matched_scores, unmatched_scores)
        
        # Save results with method_1b prefix
        results_file = "outputs/embeddings/method_1b_similarity_results.json"
        comparator.save_results(matched_scores, unmatched_scores, results, results_file)
        
        print("\n" + "=" * 80)
        print("✅ Method 1b Experiment Complete!")
        print("=" * 80)
        print()
        print("📊 Results:")
        print(f"   - Embeddings: {embeddings_file}")
        print(f"   - Analysis: {results_file}")
        print()
        print("📈 Summary:")
        print(f"   Matched pairs mean: {results['matched_pairs']['mean']:.4f}")
        print(f"   Unmatched pairs mean: {results['unmatched_pairs']['mean']:.4f}")
        print(f"   Mean difference: {results['comparison']['mean_difference']:.4f}")
        print(f"   Effect size (Cohen's d): {results['comparison']['effect_size_cohens_d']:.4f}")
        print()
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())

