#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命令行界面 - 学生档案生成系统
"""

import argparse
import os
import sys
from student_profile_generator import ProjectMatchingSystem
from research_experiment import ResearchExperiment
from knowledge_graph_generator import (
    ProjectKGGenerator, StudentKGGenerator, 
    KnowledgeGraphPersistence
)


def main():
    parser = argparse.ArgumentParser(description="基于Ollama的学生档案生成系统")
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 生成档案命令
    generate_parser = subparsers.add_parser('generate', help='生成学生档案')
    generate_parser.add_argument('--project', '-p', help='项目文件路径')
    generate_parser.add_argument('--all', '-a', action='store_true', help='为所有项目生成档案')
    generate_parser.add_argument('--model', '-m', default='llama3.2', help='使用的Ollama模型')
    generate_parser.add_argument('--num-students', '-n', type=int, default=10, help='每个项目生成的学生数量')
    
    # 对话命令
    chat_parser = subparsers.add_parser('chat', help='与学生对话')
    chat_parser.add_argument('--project', '-p', required=True, help='项目文件路径')
    chat_parser.add_argument('--model', '-m', default='llama3.2', help='使用的Ollama模型')
    
    # 列表命令
    list_parser = subparsers.add_parser('list', help='列出项目文件')
    
    # 研究实验命令
    research_parser = subparsers.add_parser('research', help='运行研究实验')
    research_parser.add_argument('--rq1', action='store_true', help='运行RQ1实验')
    research_parser.add_argument('--rq2', action='store_true', help='运行RQ2实验')
    research_parser.add_argument('--all', action='store_true', help='运行所有实验')
    research_parser.add_argument('--output', '-o', default='experiment_results', help='结果输出目录')
    
    # 知识图谱命令
    kg_parser = subparsers.add_parser('kg', help='生成知识图谱')
    kg_parser.add_argument('--type', choices=['project', 'project-unit', 'student'], 
                          required=True, help='知识图谱类型')
    kg_parser.add_argument('--input', '-i', required=True, help='输入文件路径')
    kg_parser.add_argument('--output', '-o', help='输出文件路径')
    kg_parser.add_argument('--visualize', action='store_true', help='生成可视化')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 初始化系统
    system = ProjectMatchingSystem()
    if not system.initialize():
        sys.exit(1)
    
    if args.command == 'list':
        projects = system.list_available_projects()
        print(f"找到 {len(projects)} 个项目文件:")
        for i, project in enumerate(projects, 1):
            print(f"{i:2d}. {os.path.basename(project)}")
    
    elif args.command == 'generate':
        if args.all:
            # 为所有项目生成档案
            generated_files = system.generate_all_profiles(args.num_students, args.model)
            print(f"✓ 已生成 {len(generated_files)} 个学生档案到 profile_md/ 目录")
        
        elif args.project:
            # 为指定项目生成档案
            if not os.path.exists(args.project):
                print(f"错误: 项目文件不存在: {args.project}")
                sys.exit(1)
            
            generated_files = system.generate_students_for_project(args.project, args.num_students, args.model)
            if generated_files:
                print(f"✓ 已为项目生成 {len(generated_files)} 个学生档案")
                for filepath in generated_files:
                    print(f"  - {filepath}")
        
        else:
            print("请指定项目文件 (--project) 或使用 --all 生成所有档案")
    
    elif args.command == 'chat':
        # 对话模式
        if not os.path.exists(args.project):
            print(f"错误: 项目文件不存在: {args.project}")
            sys.exit(1)
        
        # 生成或加载学生档案
        filepath = system.generate_student_for_project(args.project, args.model)
        if not filepath:
            sys.exit(1)
        
        # 开始对话
        conversation_id = system.start_conversation_with_student(args.project)
        if not conversation_id:
            sys.exit(1)
        
        # 获取学生姓名
        import re
        markdown_content = system.profiles[args.project]
        name_match = re.search(r'\*\*Name\*\*:\s*([^\n]+)', markdown_content)
        student_name = name_match.group(1).strip() if name_match else "Unknown Student"
        
        print(f"\n=== 与学生 {student_name} 的对话 ===")
        print(f"档案文件: {filepath}")
        print("输入 'quit' 或 'exit' 退出对话\n")
        
        while True:
            try:
                user_input = input("你: ").strip()
                if user_input.lower() in ['quit', 'exit', '退出']:
                    print("对话结束")
                    break
                
                if not user_input:
                    continue
                
                response = system.chat_with_student(conversation_id, user_input, args.model)
                print(f"{student_name}: {response}\n")
                
            except KeyboardInterrupt:
                print("\n对话结束")
                break
            except EOFError:
                break
    
    elif args.command == 'research':
        # 研究实验命令
        try:
            from research_experiment import ResearchExperiment
            experiment = ResearchExperiment()
            
            if args.all or args.rq1:
                print("运行RQ1实验...")
                experiment.run_rq1_experiment()
            
            if args.all or args.rq2:
                print("运行RQ2实验...")
                experiment.run_rq2_experiment()
            
            if args.all or args.rq1 or args.rq2:
                experiment.save_results(args.output)
                experiment.generate_summary_report(args.output)
                print(f"✓ 实验结果已保存到: {args.output}")
            else:
                print("请指定要运行的实验: --rq1, --rq2, 或 --all")
                
        except ImportError as e:
            print(f"错误: 缺少研究实验依赖: {e}")
            print("请安装: pip install -r requirements_research.txt")
        except Exception as e:
            print(f"研究实验失败: {e}")
    
    elif args.command == 'kg':
        # 知识图谱生成命令
        try:
            from knowledge_graph_generator import ProjectKGGenerator, StudentKGGenerator, KnowledgeGraphPersistence
            
            if not os.path.exists(args.input):
                print(f"错误: 输入文件不存在: {args.input}")
                sys.exit(1)
            
            if args.type == 'project':
                generator = ProjectKGGenerator()
                with open(args.input, 'r', encoding='utf-8') as f:
                    content = f.read()
                project_title = os.path.basename(args.input).replace('.md', '')
                kg = generator.generate_project_kg(content, project_title)
                
            elif args.type == 'project-unit':
                generator = ProjectKGGenerator()
                with open(args.input, 'r', encoding='utf-8') as f:
                    content = f.read()
                # 加载课程单元内容
                unit_file = "unit_md/qut_IN20_39851_int_cms_unit.md"
                if os.path.exists(unit_file):
                    with open(unit_file, 'r', encoding='utf-8') as f:
                        unit_content = f.read()
                else:
                    unit_content = ""
                project_title = os.path.basename(args.input).replace('.md', '')
                kg = generator.generate_project_unit_kg(content, project_title, unit_content)
                
            elif args.type == 'student':
                generator = StudentKGGenerator()
                # 这里需要解析学生档案文件
                print("学生KG生成功能正在开发中...")
                return
            
            # 保存知识图谱
            output_file = args.output or f"{args.type}_kg_{os.path.basename(args.input).replace('.md', '.json')}"
            KnowledgeGraphPersistence.save_kg(kg, output_file)
            print(f"✓ 知识图谱已保存: {output_file}")
            
            # 可视化
            if args.visualize:
                try:
                    import matplotlib.pyplot as plt
                    import networkx as nx
                    
                    G = KnowledgeGraphPersistence.export_to_networkx(kg)
                    plt.figure(figsize=(12, 8))
                    pos = nx.spring_layout(G)
                    nx.draw(G, pos, with_labels=True, node_color='lightblue', 
                           node_size=1000, font_size=8, font_weight='bold')
                    plt.title(f"Knowledge Graph: {kg.name}")
                    
                    viz_file = output_file.replace('.json', '_visualization.png')
                    plt.savefig(viz_file, dpi=300, bbox_inches='tight')
                    plt.close()
                    print(f"✓ 可视化已保存: {viz_file}")
                    
                except ImportError:
                    print("警告: 无法生成可视化，请安装 matplotlib 和 networkx")
                
        except ImportError as e:
            print(f"错误: 缺少知识图谱依赖: {e}")
            print("请安装: pip install -r requirements_research.txt")
        except Exception as e:
            print(f"知识图谱生成失败: {e}")


if __name__ == "__main__":
    main()
