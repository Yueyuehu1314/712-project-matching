#!/usr/bin/env python3
"""
为带前置课程的学生KG生成可视化图片
支持显示所有权重和PREREQUISITE_FOR关系
"""

import json
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import networkx as nx
from pathlib import Path
import argparse
from typing import Dict, List


def load_kg_from_json(json_path: str) -> nx.MultiDiGraph:
    """从JSON文件加载知识图谱"""
    with open(json_path, 'r', encoding='utf-8') as f:
        kg_data = json.load(f)
    
    G = nx.MultiDiGraph()
    
    # 添加节点
    for entity in kg_data['entities']:
        G.add_node(
            entity['id'],
            name=entity['name'],
            type=entity['entity_type'],
            **entity.get('properties', {})
        )
    
    # 添加边
    for rel in kg_data['relationships']:
        G.add_edge(
            rel['source_id'],
            rel['target_id'],
            relation=rel['relation_type'],
            weight=rel.get('weight', 1.0),
            **rel.get('properties', {})
        )
    
    return G


def create_visualization_with_prereq(
    graph: nx.MultiDiGraph,
    name: str,
    output_file: str,
    show_all_weights: bool = True,
    highlight_prereq: bool = True
):
    """
    创建包含前置课程关系的可视化
    
    Args:
        graph: NetworkX图对象
        name: 学生姓名
        output_file: 输出文件路径
        show_all_weights: 是否显示所有权重（包括1.0）
        highlight_prereq: 是否高亮前置课程关系
    """
    
    plt.figure(figsize=(20, 16))
    plt.clf()
    
    # 使用spring_layout但增加节点间距
    pos = nx.spring_layout(graph, k=3.5, iterations=150, seed=42)
    
    # 颜色映射（添加了PREREQUISITE关系相关的颜色）
    node_colors = {
        'STUDENT': '#4ECDC4',           # 青色 - 学生
        'MAJOR': '#96CEB4',             # 绿色 - 专业
        'COURSE': '#DDA0DD',            # 紫色 - 课程
        'SKILL': '#45B7D1',             # 蓝色 - 技能
        'PROJECT_EXPERIENCE': '#FF6B6B', # 红色 - 项目经历
        'INTEREST': '#F7DC6F'           # 黄色 - 兴趣
    }
    
    # 按类型绘制节点
    for node_type, color in node_colors.items():
        nodes = [n for n, d in graph.nodes(data=True) if d.get('type') == node_type]
        if nodes:
            if node_type == 'STUDENT':
                node_size = 2500
                alpha = 1.0
            elif node_type in ['COURSE', 'PROJECT_EXPERIENCE']:
                node_size = 900
                alpha = 0.85
            else:
                node_size = 650
                alpha = 0.75
            
            nx.draw_networkx_nodes(graph, pos, nodelist=nodes,
                                 node_color=color, node_size=node_size,
                                 alpha=alpha, edgecolors='black', linewidths=2)
    
    # 绘制不同类型的边（添加PREREQUISITE_FOR）
    edge_styles = {
        'PREREQUISITE_FOR': {'color': '#FF1493', 'width': 4, 'style': 'dashdot', 'alpha': 0.95},  # 深粉色，高亮
        'TEACHES_SKILL': {'color': 'purple', 'width': 3, 'style': 'dashed', 'alpha': 0.9},
        'REQUIRES_SKILL': {'color': 'red', 'width': 2.5, 'style': 'dotted', 'alpha': 0.8},
        'COMPLETED_COURSE': {'color': 'green', 'width': 2, 'style': 'solid', 'alpha': 0.7},
        'PARTICIPATED_IN_PROJECT': {'color': 'orange', 'width': 2, 'style': 'solid', 'alpha': 0.7},
        'HAS_SKILL': {'color': 'blue', 'width': 1.5, 'style': 'solid', 'alpha': 0.6},
        'STUDIED_MAJOR': {'color': 'darkgreen', 'width': 2.5, 'style': 'solid', 'alpha': 0.8},
        'INTERESTED_IN': {'color': 'gold', 'width': 1.5, 'style': 'solid', 'alpha': 0.6}
    }
    
    # 统计前置课程关系数量
    prereq_count = 0
    
    for relation_type, style in edge_styles.items():
        edges = [(u, v) for u, v, d in graph.edges(data=True) if d.get('relation') == relation_type]
        if edges:
            if relation_type == 'PREREQUISITE_FOR':
                prereq_count = len(edges)
                print(f"  📚 发现 {prereq_count} 条前置课程关系")
            
            # 如果是前置课程且需要高亮，使用特殊样式
            if relation_type == 'PREREQUISITE_FOR' and highlight_prereq:
                nx.draw_networkx_edges(graph, pos, edgelist=edges,
                                     edge_color=style['color'],
                                     width=style['width'],
                                     style=style['style'],
                                     alpha=style['alpha'],
                                     arrows=True,
                                     arrowsize=20,
                                     connectionstyle='arc3,rad=0.1')  # 添加弧度以区分多重边
            else:
                nx.draw_networkx_edges(graph, pos, edgelist=edges,
                                     edge_color=style['color'],
                                     width=style['width'],
                                     style=style['style'],
                                     alpha=style['alpha'],
                                     arrows=True,
                                     arrowsize=15)
    
    # 添加节点标签
    labels = {}
    for node in graph.nodes():
        node_name = graph.nodes[node].get('name', node)
        # 课程节点显示课程代码，其他节点截断
        if graph.nodes[node].get('type') == 'COURSE':
            # 提取课程代码（如 IFN666）
            if ' ' in node_name:
                node_name = node_name.split(' ')[0]
        elif len(node_name) > 20:
            node_name = node_name[:17] + "..."
        labels[node] = node_name
    
    nx.draw_networkx_labels(graph, pos, labels, font_size=9, font_weight='bold')
    
    # 添加边的权重和关系类型标签
    edge_labels = {}
    for u, v, data in graph.edges(data=True):
        weight = data.get('weight', 1.0)
        relation = data.get('relation', '')
        
        # 根据参数决定是否显示所有权重
        if show_all_weights or weight != 1.0:
            # 对于前置课程关系，显示关系类型
            if relation == 'PREREQUISITE_FOR':
                edge_labels[(u, v)] = f"PREREQ\nw={weight:.1f}"
            elif weight != 1.0:
                edge_labels[(u, v)] = f"{weight:.2f}"
    
    if edge_labels:
        nx.draw_networkx_edge_labels(graph, pos, edge_labels, 
                                    font_size=7, font_color='darkred',
                                    bbox=dict(boxstyle='round,pad=0.3', 
                                             facecolor='yellow', 
                                             edgecolor='red', 
                                             alpha=0.8))
    
    # 标题（添加前置课程数量信息）
    title = f"Student Knowledge Graph with Prerequisites\n{name}"
    if prereq_count > 0:
        title += f"\n(包含 {prereq_count} 条前置课程关系)"
    plt.title(title, fontsize=18, fontweight='bold', pad=20)
    plt.axis('off')
    
    # 创建图例 - 分为节点和边两部分
    # 节点类型图例
    node_legend_elements = []
    for node_type, color in node_colors.items():
        if any(d.get('type') == node_type for n, d in graph.nodes(data=True)):
            node_legend_elements.append(
                plt.Line2D([0], [0], marker='o', color='w',
                          markerfacecolor=color, markersize=12,
                          label=node_type.replace('_', ' '))
            )
    
    # 边类型图例
    edge_legend_elements = []
    for relation_type, style in edge_styles.items():
        if any(d.get('relation') == relation_type for u, v, d in graph.edges(data=True)):
            label = relation_type.replace('_', ' ')
            # 高亮前置课程关系
            if relation_type == 'PREREQUISITE_FOR':
                label = f"⭐ {label}"
            edge_legend_elements.append(
                plt.Line2D([0], [0], color=style['color'], linewidth=3,
                          linestyle=style['style'], label=label)
            )
    
    # 组合图例
    if node_legend_elements:
        legend1 = plt.legend(handles=node_legend_elements, 
                           title='Node Types',
                           loc='upper left', 
                           bbox_to_anchor=(0, 1),
                           fontsize=10,
                           title_fontsize=11)
        plt.gca().add_artist(legend1)
    
    if edge_legend_elements:
        plt.legend(handles=edge_legend_elements,
                  title='Edge Types',
                  loc='upper left',
                  bbox_to_anchor=(0, 0.75),
                  fontsize=10,
                  title_fontsize=11)
    
    plt.tight_layout()
    
    # 保存图片
    plt.savefig(output_file, dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    
    print(f"  ✅ 可视化已保存: {output_file}")


def process_single_kg(json_path: str, show_all_weights: bool = True):
    """处理单个KG文件"""
    json_path = Path(json_path)
    
    if not json_path.exists():
        print(f"❌ 文件不存在: {json_path}")
        return
    
    print(f"📊 处理: {json_path.name}")
    
    # 加载KG
    graph = load_kg_from_json(str(json_path))
    
    # 获取学生名称
    student_nodes = [n for n, d in graph.nodes(data=True) if d.get('type') == 'STUDENT']
    if student_nodes:
        name = graph.nodes[student_nodes[0]].get('name', 'Unknown')
    else:
        name = json_path.stem
    
    # 生成输出文件名
    output_file = json_path.parent / f"{json_path.stem}_visualization.png"
    
    # 创建可视化
    create_visualization_with_prereq(graph, name, str(output_file), show_all_weights)


def process_all_kgs(kg_dir: str, show_all_weights: bool = True):
    """批量处理所有带前置课程的KG文件"""
    kg_dir = Path(kg_dir)
    
    if not kg_dir.exists():
        print(f"❌ 目录不存在: {kg_dir}")
        return
    
    # 查找所有 *_with_prereq.json 文件
    prereq_files = list(kg_dir.rglob("*_with_prereq.json"))
    
    if not prereq_files:
        print(f"❌ 未找到任何 *_with_prereq.json 文件")
        return
    
    print(f"\n{'='*60}")
    print(f"批量生成学生KG可视化（带前置课程）")
    print(f"{'='*60}")
    print(f"  目录: {kg_dir}")
    print(f"  文件数: {len(prereq_files)}")
    print(f"  显示所有权重: {'是' if show_all_weights else '否（仅非1.0）'}")
    print(f"{'='*60}\n")
    
    success_count = 0
    for json_file in prereq_files:
        try:
            process_single_kg(str(json_file), show_all_weights)
            success_count += 1
        except Exception as e:
            print(f"  ❌ 错误: {e}")
    
    print(f"\n{'='*60}")
    print(f"✅ 完成！成功生成 {success_count}/{len(prereq_files)} 个可视化")
    print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(
        description='为带前置课程的学生KG生成可视化图片',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 批量处理所有学生KG（显示所有权重）
  python visualize_student_kg_with_prereq.py --kg-dir outputs/knowledge_graphs/individual/enhanced_student_kg
  
  # 仅显示非1.0的权重
  python visualize_student_kg_with_prereq.py --kg-dir outputs/knowledge_graphs/individual/enhanced_student_kg --hide-1.0
  
  # 处理单个文件
  python visualize_student_kg_with_prereq.py --file path/to/student_xxx_with_prereq.json
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--kg-dir', type=str,
                      help='包含学生KG的目录')
    group.add_argument('--file', type=str,
                      help='单个KG JSON文件路径')
    
    parser.add_argument('--hide-1.0', action='store_true', dest='hide_one',
                       help='不显示权重为1.0的边（减少图片拥挤度）')
    
    args = parser.parse_args()
    
    show_all_weights = not args.hide_one
    
    if args.kg_dir:
        process_all_kgs(args.kg_dir, show_all_weights)
    else:
        process_single_kg(args.file, show_all_weights)


if __name__ == "__main__":
    main()

