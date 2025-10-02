#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实验CLI工具
Command Line Interface for Knowledge Graph Comparison Experiments
"""

print("🚀 Starting experiment CLI...")

import argparse
import sys
import os
from pathlib import Path

print("📦 Basic imports completed")

try:
    print("📦 Importing KGComparisonExperiment...")
    from kg_comparison_experiment import KGComparisonExperiment
    print("✅ KGComparisonExperiment imported")
except Exception as e:
    print(f"❌ Failed to import KGComparisonExperiment: {e}")
    sys.exit(1)

try:
    print("📦 Importing EnhancedProjectKnowledgeGraphBuilder...")
    from enhanced_project_kg import EnhancedProjectKnowledgeGraphBuilder
    print("✅ EnhancedProjectKnowledgeGraphBuilder imported")
except Exception as e:
    print(f"❌ Failed to import EnhancedProjectKnowledgeGraphBuilder: {e}")
    sys.exit(1)

print("✅ All imports completed successfully")


def run_enhanced_kg_only(args):
    """仅运行增强版知识图谱构建"""
    print("🚀 构建增强版知识图谱...")
    
    builder = EnhancedProjectKnowledgeGraphBuilder()
    builder.build_enhanced_from_files(
        project_dir=args.project_dir,
        student_dir=args.student_dir,
        unit_dir=args.unit_dir
    )
    
    # 保存结果
    output_dir = args.output_dir or "enhanced_kg_output"
    os.makedirs(output_dir, exist_ok=True)
    
    builder.save_graph(output_dir)
    if args.visualize:
        builder.create_enhanced_visualization(output_dir)
    
    print(f"✅ 增强版知识图谱已保存到: {output_dir}")


def run_full_experiment(args):
    """运行完整的对比实验"""
    print("🎯 运行完整对比实验...")
    
    experiment = KGComparisonExperiment()
    
    # 设置实验
    experiment.setup_experiment(
        project_dir=args.project_dir,
        student_dir=args.student_dir,
        unit_dir=args.unit_dir
    )
    
    # 运行实验
    results = experiment.run_comparison()
    
    # 生成报告
    output_dir = args.output_dir or "experiment_results"
    experiment.generate_report(output_dir)
    
    print(f"✅ 实验完成，结果保存到: {output_dir}")
    
    # 如果要求简要输出
    if args.brief:
        baseline = results['baseline']
        enhanced = results['enhanced']
        
        print(f"\n📊 简要结果:")
        print(f"基线 AUC: {baseline.auc_score:.3f}, Top-1: {baseline.top1_accuracy:.3f}")
        print(f"增强 AUC: {enhanced.auc_score:.3f}, Top-1: {enhanced.top1_accuracy:.3f}")
        print(f"改进: AUC {enhanced.auc_score - baseline.auc_score:+.3f}, Top-1 {enhanced.top1_accuracy - baseline.top1_accuracy:+.3f}")


def validate_directories(args):
    """验证目录是否存在"""
    dirs_to_check = [
        (args.project_dir, "项目目录"),
        (args.student_dir, "学生目录")
    ]
    
    if hasattr(args, 'unit_dir') and args.unit_dir:
        dirs_to_check.append((args.unit_dir, "Unit目录"))
    
    for dir_path, dir_name in dirs_to_check:
        if not os.path.exists(dir_path):
            print(f"❌ 错误: {dir_name} 不存在: {dir_path}")
            return False
    
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Knowledge Graph Comparison Experiment CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:

1. 构建增强版知识图谱:
   python experiment_cli.py enhanced --visualize

2. 运行完整对比实验:
   python experiment_cli.py experiment --brief

3. 自定义目录:
   python experiment_cli.py experiment --project-dir custom_projects --unit-dir custom_units

4. 指定输出目录:
   python experiment_cli.py enhanced --output-dir my_results
        """
    )
    
    # 添加子命令
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 增强版知识图谱构建命令
    enhanced_parser = subparsers.add_parser('enhanced', help='构建增强版知识图谱')
    enhanced_parser.add_argument('--project-dir', default='project_md', 
                               help='项目文件目录 (默认: project_md)')
    enhanced_parser.add_argument('--student-dir', default='profile_md', 
                               help='学生档案目录 (默认: profile_md)')
    enhanced_parser.add_argument('--unit-dir', default='unit_md', 
                               help='Unit outline目录 (默认: unit_md)')
    enhanced_parser.add_argument('--output-dir', 
                               help='输出目录 (默认: enhanced_kg_output)')
    enhanced_parser.add_argument('--visualize', action='store_true', 
                               help='生成可视化图表')
    
    # 完整实验命令
    experiment_parser = subparsers.add_parser('experiment', help='运行完整对比实验')
    experiment_parser.add_argument('--project-dir', default='project_md', 
                                 help='项目文件目录 (默认: project_md)')
    experiment_parser.add_argument('--student-dir', default='profile_md', 
                                 help='学生档案目录 (默认: profile_md)')
    experiment_parser.add_argument('--unit-dir', default='unit_md', 
                                 help='Unit outline目录 (默认: unit_md)')
    experiment_parser.add_argument('--output-dir', 
                                 help='输出目录 (默认: experiment_results)')
    experiment_parser.add_argument('--brief', action='store_true', 
                                 help='显示简要结果摘要')
    
    # 解析参数
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # 验证目录
    if not validate_directories(args):
        sys.exit(1)
    
    try:
        if args.command == 'enhanced':
            run_enhanced_kg_only(args)
        elif args.command == 'experiment':
            run_full_experiment(args)
        else:
            print(f"❌ 未知命令: {args.command}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
