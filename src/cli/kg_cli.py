#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识图谱命令行工具
"""

import argparse
import os
import sys
from project_knowledge_graph import ProjectKnowledgeGraphBuilder


def main():
    parser = argparse.ArgumentParser(description="项目匹配知识图谱系统")
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 构建知识图谱命令
    build_parser = subparsers.add_parser('build', help='构建知识图谱')
    build_parser.add_argument('--project-dir', '-p', default='project_md', help='项目文件目录')
    build_parser.add_argument('--student-dir', '-s', default='profile_md', help='学生档案目录')
    build_parser.add_argument('--output-dir', '-o', default='knowledge_graph_output', help='输出目录')
    build_parser.add_argument('--visualize', '-v', action='store_true', help='生成可视化')
    
    # 推荐命令
    recommend_parser = subparsers.add_parser('recommend', help='获取推荐')
    recommend_parser.add_argument('--entity-id', '-e', required=True, help='实体ID')
    recommend_parser.add_argument('--top-k', '-k', type=int, default=5, help='返回的推荐数量')
    recommend_parser.add_argument('--data-dir', '-d', default='knowledge_graph_output', help='数据目录')
    
    # 统计命令
    stats_parser = subparsers.add_parser('stats', help='显示统计信息')
    stats_parser.add_argument('--data-dir', '-d', default='knowledge_graph_output', help='数据目录')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'build':
        # 构建知识图谱
        print(f"🛠️  开始构建知识图谱...")
        print(f"📁 项目目录: {args.project_dir}")
        print(f"👥 学生目录: {args.student_dir}")
        print(f"📂 输出目录: {args.output_dir}")
        
        # 检查目录是否存在
        if not os.path.exists(args.project_dir):
            print(f"❌ 错误: 项目目录不存在: {args.project_dir}")
            sys.exit(1)
        
        if not os.path.exists(args.student_dir):
            print(f"❌ 错误: 学生目录不存在: {args.student_dir}")
            sys.exit(1)
        
        # 创建构建器
        builder = ProjectKnowledgeGraphBuilder()
        
        # 构建知识图谱
        builder.build_from_files(args.project_dir, args.student_dir)
        
        # 保存结果
        builder.save_graph(args.output_dir)
        
        # 生成可视化
        if args.visualize:
            print(f"🎨 生成可视化...")
            builder.create_simple_visualization(args.output_dir)
        
        print(f"✅ 知识图谱构建完成！")
        
    elif args.command == 'recommend':
        # 获取推荐
        print(f"🔍 为 {args.entity_id} 获取推荐...")
        
        # 加载已构建的知识图谱
        try:
            builder = ProjectKnowledgeGraphBuilder()
            # 这里需要从保存的数据加载知识图谱
            # 简化实现：重新构建
            builder.build_from_files()
            
            recommendations = builder.get_recommendations(args.entity_id, 'MATCHES', args.top_k)
            
            if recommendations:
                print(f"🎆 找到 {len(recommendations)} 条推荐:")
                for i, (name, score) in enumerate(recommendations, 1):
                    print(f"  {i}. {name} (匹配度: {score:.3f})")
            else:
                print(f"😔 没有找到相关推荐")
                
        except Exception as e:
            print(f"❌ 错误: {e}")
            print(f"提示: 请先使用 'build' 命令构建知识图谱")
    
    elif args.command == 'stats':
        # 显示统计信息
        import json
        
        stats_file = os.path.join(args.data_dir, 'statistics.json')
        if os.path.exists(stats_file):
            with open(stats_file, 'r', encoding='utf-8') as f:
                stats = json.load(f)
            
            print(f"📊 知识图谱统计信息:")
            print(f"  实体总数: {stats.get('total_entities', 0)}")
            print(f"  关系总数: {stats.get('total_relationships', 0)}")
            print(f"  创建时间: {stats.get('created_at', 'Unknown')}")
            
            print(f"\n📊 实体类型分布:")
            for entity_type, count in stats.get('entity_types', {}).items():
                print(f"  {entity_type}: {count}")
            
            print(f"\n🔗 关系类型分布:")
            for relation_type, count in stats.get('relation_types', {}).items():
                print(f"  {relation_type}: {count}")
        else:
            print(f"❌ 统计文件不存在: {stats_file}")
            print(f"提示: 请先使用 'build' 命令构建知识图谱")


if __name__ == "__main__":
    main()

