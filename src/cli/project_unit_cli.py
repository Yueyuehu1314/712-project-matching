#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project + Unit Outline Knowledge Graph CLI
为每个项目生成包含 Unit Outline 信息的个体知识图谱的命令行工具
"""

import argparse
import sys
import os
from pathlib import Path

from individual_project_unit_kg import IndividualProjectUnitKGBuilder


def build_all_project_unit_kgs(args):
    """构建所有项目+Unit知识图谱"""
    print("🚀 构建所有项目+Unit知识图谱...")
    
    builder = IndividualProjectUnitKGBuilder()
    results = builder.build_all_project_unit_kgs(
        project_dir=args.project_dir,
        output_dir=args.output_dir
    )
    
    if results['projects']:
        print(f"\n✅ 构建完成！")
        print(f"📁 输出目录: {args.output_dir}")
        print(f"📊 生成了 {len(results['projects'])} 个项目知识图谱")
        
        if args.show_stats:
            print(f"\n📈 详细统计:")
            print(f"  总实体数: {results['summary']['total_entities']}")
            print(f"  总关系数: {results['summary']['total_relationships']}")
            print(f"  平均每项目实体数: {results['summary']['avg_entities_per_project']:.1f}")
            print(f"  平均每项目关系数: {results['summary']['avg_relationships_per_project']:.1f}")
    else:
        print("❌ 没有成功生成任何知识图谱")


def build_single_project_kg(args):
    """构建单个项目的知识图谱"""
    print(f"🔨 构建单个项目知识图谱: {args.project_file}")
    
    builder = IndividualProjectUnitKGBuilder()
    stats = builder.create_project_unit_knowledge_graph(
        project_file=args.project_file,
        output_dir=args.output_dir
    )
    
    if stats:
        print(f"✅ 成功生成知识图谱!")
        print(f"📁 输出目录: {stats['output_dir']}")
        print(f"📊 实体数: {stats['total_entities']}, 关系数: {stats['total_relationships']}")
        
        if args.show_details:
            print(f"\n📋 实体类型分布:")
            for entity_type, count in stats['entity_types'].items():
                print(f"  {entity_type}: {count}")
            
            print(f"\n🔗 关系类型分布:")
            for relation_type, count in stats['relation_types'].items():
                print(f"  {relation_type}: {count}")
    else:
        print("❌ 知识图谱生成失败")


def list_projects(args):
    """列出可用的项目文件"""
    import glob
    
    project_files = glob.glob(os.path.join(args.project_dir, "*.md"))
    
    print(f"📂 可用项目文件 ({len(project_files)} 个):")
    print(f"目录: {args.project_dir}")
    print("-" * 50)
    
    for i, project_file in enumerate(sorted(project_files), 1):
        filename = os.path.basename(project_file)
        print(f"{i:2d}. {filename}")


def show_summary(args):
    """显示已生成的知识图谱摘要"""
    import json
    
    summary_file = os.path.join(args.output_dir, "summary_report.json")
    
    if not os.path.exists(summary_file):
        print(f"❌ 摘要文件不存在: {summary_file}")
        print("请先运行构建命令生成知识图谱")
        return
    
    try:
        with open(summary_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        summary = data.get('summary', {})
        projects = data.get('projects', [])
        
        print(f"📊 项目+Unit知识图谱摘要")
        print("=" * 40)
        print(f"总项目数: {summary.get('total_projects', 0)}")
        print(f"总实体数: {summary.get('total_entities', 0)}")
        print(f"总关系数: {summary.get('total_relationships', 0)}")
        print(f"平均每项目实体数: {summary.get('avg_entities_per_project', 0):.1f}")
        print(f"平均每项目关系数: {summary.get('avg_relationships_per_project', 0):.1f}")
        print(f"生成时间: {summary.get('created_at', 'Unknown')}")
        
        if args.show_projects and projects:
            print(f"\n📋 项目列表:")
            print("-" * 60)
            for i, project in enumerate(projects, 1):
                print(f"{i:2d}. {project['name']}")
                print(f"     实体: {project['total_entities']}, 关系: {project['total_relationships']}")
                print(f"     输出: {project['output_dir']}")
                
    except Exception as e:
        print(f"❌ 读取摘要文件失败: {e}")


def validate_directories(args):
    """验证目录是否存在"""
    if hasattr(args, 'project_dir') and not os.path.exists(args.project_dir):
        print(f"❌ 错误: 项目目录不存在: {args.project_dir}")
        return False
    
    if hasattr(args, 'project_file') and not os.path.exists(args.project_file):
        print(f"❌ 错误: 项目文件不存在: {args.project_file}")
        return False
    
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Project + Unit Outline Knowledge Graph CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:

1. 构建所有项目的知识图谱:
   python project_unit_cli.py build-all

2. 构建单个项目的知识图谱:
   python project_unit_cli.py build-single --project-file project_md/example.md

3. 列出可用项目:
   python project_unit_cli.py list

4. 查看生成摘要:
   python project_unit_cli.py summary --show-projects

5. 自定义目录:
   python project_unit_cli.py build-all --project-dir custom_projects --output-dir custom_output
        """
    )
    
    # 添加子命令
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 构建所有项目命令
    build_all_parser = subparsers.add_parser('build-all', help='构建所有项目+Unit知识图谱')
    build_all_parser.add_argument('--project-dir', default='project_md',
                                 help='项目文件目录 (默认: project_md)')
    build_all_parser.add_argument('--output-dir', default='individual_kg/projects_uo',
                                 help='输出目录 (默认: individual_kg/projects_uo)')
    build_all_parser.add_argument('--show-stats', action='store_true',
                                 help='显示详细统计信息')
    
    # 构建单个项目命令
    build_single_parser = subparsers.add_parser('build-single', help='构建单个项目知识图谱')
    build_single_parser.add_argument('--project-file', required=True,
                                   help='项目文件路径')
    build_single_parser.add_argument('--output-dir', default='individual_kg/projects_uo',
                                   help='输出目录 (默认: individual_kg/projects_uo)')
    build_single_parser.add_argument('--show-details', action='store_true',
                                   help='显示详细信息')
    
    # 列出项目命令
    list_parser = subparsers.add_parser('list', help='列出可用项目文件')
    list_parser.add_argument('--project-dir', default='project_md',
                           help='项目文件目录 (默认: project_md)')
    
    # 显示摘要命令
    summary_parser = subparsers.add_parser('summary', help='显示生成摘要')
    summary_parser.add_argument('--output-dir', default='individual_kg/projects_uo',
                               help='输出目录 (默认: individual_kg/projects_uo)')
    summary_parser.add_argument('--show-projects', action='store_true',
                               help='显示项目列表')
    
    # 解析参数
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # 验证目录
    if not validate_directories(args):
        sys.exit(1)
    
    try:
        if args.command == 'build-all':
            build_all_project_unit_kgs(args)
        elif args.command == 'build-single':
            build_single_project_kg(args)
        elif args.command == 'list':
            list_projects(args)
        elif args.command == 'summary':
            show_summary(args)
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
