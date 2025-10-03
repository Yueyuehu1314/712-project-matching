#!/usr/bin/env python3
"""
可视化权重规则对比
生成学生KG和项目KG的权重对比图表
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def create_weight_comparison_chart():
    """创建权重对比图表"""
    
    fig = plt.figure(figsize=(18, 12))
    
    # ============= 左侧：学生KG权重 =============
    ax1 = plt.subplot(1, 2, 1)
    
    student_kg_weights = {
        'STUDIED_MAJOR': 1.0,
        'COMPLETED_COURSE': 1.0,
        'INTERESTED_IN': 1.0,
        'PARTICIPATED_IN_PROJECT': 1.0,
        'PREREQUISITE_FOR': 1.0,
        'TEACHES_SKILL': 0.9,
        'HAS_SKILL (course)': 0.8,
        'HAS_SKILL (project)': 0.75,
        'REQUIRES_SKILL': 0.7,
        'HAS_SKILL (self-taught)': 0.6,
    }
    
    relations = list(student_kg_weights.keys())
    weights = list(student_kg_weights.values())
    
    # 颜色映射（根据权重）
    colors = []
    for w in weights:
        if w == 1.0:
            colors.append('#2ECC71')  # 绿色 - 最高
        elif w >= 0.8:
            colors.append('#3498DB')  # 蓝色 - 高
        elif w >= 0.7:
            colors.append('#F39C12')  # 橙色 - 中
        else:
            colors.append('#E74C3C')  # 红色 - 低
    
    bars1 = ax1.barh(relations, weights, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    
    # 添加权重数值标签
    for i, (bar, weight) in enumerate(zip(bars1, weights)):
        ax1.text(weight + 0.02, bar.get_y() + bar.get_height()/2, 
                f'{weight:.2f}', va='center', fontsize=10, fontweight='bold')
    
    ax1.set_xlabel('权重 (Weight)', fontsize=12, fontweight='bold')
    ax1.set_title('学生知识图谱 (Student KG)\n关系权重', fontsize=14, fontweight='bold', pad=15)
    ax1.set_xlim(0, 1.15)
    ax1.grid(axis='x', alpha=0.3, linestyle='--')
    ax1.axvline(x=1.0, color='red', linestyle='--', linewidth=2, alpha=0.5, label='最大权重')
    
    # 添加可信度注释
    ax1.text(0.5, -1.5, '⭐ 可信度: 绿色(最高) > 蓝色(高) > 橙色(中) > 红色(低)', 
             fontsize=10, ha='center', style='italic')
    
    # ============= 右侧：项目KG权重 =============
    ax2 = plt.subplot(1, 2, 2)
    
    # 项目KG的技能分数计算
    project_kg_data = [
        ('PREREQUISITE_FOR', 1.0, '#2ECC71'),
        ('REQUIRES_MAJOR', 1.0, '#2ECC71'),
        ('INCLUDES_UNIT', 1.0, '#2ECC71'),
        ('TAUGHT_IN', 1.0, '#2ECC71'),
        ('Skill (dual_supported)\nIN20+IN27, ×1.3', 1.0, '#9B59B6'),  # 紫色表示加成
        ('Skill (IN20 supported)\n×1.0', 0.75, '#3498DB'),
        ('Skill (IN27 supported)\n×1.0', 0.75, '#3498DB'),
        ('Skill (PD extended)\n×0.8', 0.48, '#E74C3C'),
    ]
    
    relations2 = [item[0] for item in project_kg_data]
    weights2 = [item[1] for item in project_kg_data]
    colors2 = [item[2] for item in project_kg_data]
    
    bars2 = ax2.barh(relations2, weights2, color=colors2, alpha=0.8, edgecolor='black', linewidth=1.5)
    
    # 添加权重数值标签
    for i, (bar, weight) in enumerate(zip(bars2, weights2)):
        ax2.text(weight + 0.02, bar.get_y() + bar.get_height()/2, 
                f'{weight:.2f}', va='center', fontsize=10, fontweight='bold')
    
    ax2.set_xlabel('权重 (Weight)', fontsize=12, fontweight='bold')
    ax2.set_title('项目知识图谱 (Project KG)\n关系/节点权重', fontsize=14, fontweight='bold', pad=15)
    ax2.set_xlim(0, 1.15)
    ax2.grid(axis='x', alpha=0.3, linestyle='--')
    ax2.axvline(x=1.0, color='red', linestyle='--', linewidth=2, alpha=0.5, label='最大权重')
    
    # 添加说明
    ax2.text(0.5, -1.8, '💡 技能权重示例（假设base_score=0.6）\ndual_supported: 0.6×1.3=0.78 | IN20/IN27: 0.6×1.0=0.6 | PD: 0.6×0.8=0.48', 
             fontsize=9, ha='center', style='italic', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.suptitle('知识图谱权重规则对比\nWeight Rules Comparison', 
                 fontsize=18, fontweight='bold', y=0.98)
    
    plt.tight_layout(rect=[0, 0.02, 1, 0.96])
    
    # 保存
    output_file = 'WEIGHT_RULES_COMPARISON.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ 权重对比图已保存: {output_file}")
    plt.close()


def create_weight_flow_diagram():
    """创建权重流程图"""
    
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # 隐藏坐标轴
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # ============= 学生KG流程 =============
    # 标题
    ax.text(2.5, 9.5, '学生KG权重流程', fontsize=16, fontweight='bold', ha='center',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', edgecolor='black', linewidth=2))
    
    # 学生节点
    ax.add_patch(FancyBboxPatch((1, 7.5), 3, 1, boxstyle="round,pad=0.1", 
                                facecolor='#4ECDC4', edgecolor='black', linewidth=2))
    ax.text(2.5, 8, '学生\nSTUDENT', ha='center', va='center', fontsize=12, fontweight='bold')
    
    # 分支1: 课程路径
    ax.arrow(2.5, 7.5, 0, -0.8, head_width=0.2, head_length=0.1, fc='green', ec='green', linewidth=2)
    ax.text(2.8, 7, '1.0', fontsize=10, color='green', fontweight='bold')
    
    ax.add_patch(FancyBboxPatch((1, 5.8), 3, 0.8, boxstyle="round,pad=0.05", 
                                facecolor='#DDA0DD', edgecolor='black', linewidth=1.5))
    ax.text(2.5, 6.2, '课程 COURSE', ha='center', va='center', fontsize=11)
    
    ax.arrow(2.5, 5.8, 0, -0.6, head_width=0.2, head_length=0.1, fc='blue', ec='blue', linewidth=2)
    ax.text(2.8, 5.4, '0.9', fontsize=10, color='blue', fontweight='bold')
    
    ax.add_patch(FancyBboxPatch((1, 4.5), 3, 0.7, boxstyle="round,pad=0.05", 
                                facecolor='#45B7D1', edgecolor='black', linewidth=1.5))
    ax.text(2.5, 4.85, '技能 SKILL', ha='center', va='center', fontsize=11)
    
    # 反向箭头：学生→技能 (0.8)
    ax.annotate('', xy=(1.8, 4.7), xytext=(1.8, 7.4),
                arrowprops=dict(arrowstyle='->', lw=2.5, color='orange', linestyle='dashed'))
    ax.text(1.3, 6, '0.8\n(course)', fontsize=9, color='orange', fontweight='bold')
    
    # 分支2: 项目路径
    ax.arrow(3.5, 7.8, 1, -1.2, head_width=0.2, head_length=0.1, fc='green', ec='green', linewidth=2)
    ax.text(4.6, 6.8, '1.0', fontsize=10, color='green', fontweight='bold')
    
    ax.add_patch(FancyBboxPatch((4.5, 5.8), 3, 0.8, boxstyle="round,pad=0.05", 
                                facecolor='#FF6B6B', edgecolor='black', linewidth=1.5))
    ax.text(6, 6.2, '项目经历\nPROJECT_EXP', ha='center', va='center', fontsize=10)
    
    ax.arrow(6, 5.8, 0, -0.6, head_width=0.2, head_length=0.1, fc='brown', ec='brown', linewidth=2)
    ax.text(6.3, 5.4, '0.7', fontsize=10, color='brown', fontweight='bold')
    
    ax.add_patch(FancyBboxPatch((4.5, 4.5), 3, 0.7, boxstyle="round,pad=0.05", 
                                facecolor='#45B7D1', edgecolor='black', linewidth=1.5))
    ax.text(6, 4.85, '技能 SKILL', ha='center', va='center', fontsize=11)
    
    # 反向箭头：学生→技能 (0.75)
    ax.annotate('', xy=(5.2, 4.7), xytext=(3.3, 7.5),
                arrowprops=dict(arrowstyle='->', lw=2.5, color='red', linestyle='dashed'))
    ax.text(4, 6, '0.75\n(project)', fontsize=9, color='red', fontweight='bold')
    
    # 分支3: 自学路径
    ax.annotate('', xy=(3.5, 4.85), xytext=(3.5, 7.5),
                arrowprops=dict(arrowstyle='->', lw=2.5, color='purple', linestyle='dotted'))
    ax.text(3.8, 6, '0.6\n(self)', fontsize=9, color='purple', fontweight='bold')
    
    # ============= 项目KG流程 =============
    ax.text(7.5, 9.5, '项目KG权重流程', fontsize=16, fontweight='bold', ha='center',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', edgecolor='black', linewidth=2))
    
    # 项目节点
    ax.add_patch(FancyBboxPatch((6, 7.5), 3, 1, boxstyle="round,pad=0.1", 
                                facecolor='#FF6B6B', edgecolor='black', linewidth=2))
    ax.text(7.5, 8, '项目\nPROJECT', ha='center', va='center', fontsize=12, fontweight='bold')
    
    # 技能分类
    ax.arrow(7.5, 7.5, 0, -0.5, head_width=0.2, head_length=0.1, fc='black', ec='black', linewidth=2)
    
    # Dual supported
    ax.add_patch(FancyBboxPatch((6, 6.2), 1.3, 0.6, boxstyle="round,pad=0.05", 
                                facecolor='#9B59B6', edgecolor='black', linewidth=1.5))
    ax.text(6.65, 6.5, 'Dual\n×1.3', ha='center', va='center', fontsize=9, fontweight='bold', color='white')
    
    # IN20
    ax.add_patch(FancyBboxPatch((6, 5.4), 1.3, 0.6, boxstyle="round,pad=0.05", 
                                facecolor='#3498DB', edgecolor='black', linewidth=1.5))
    ax.text(6.65, 5.7, 'IN20\n×1.0', ha='center', va='center', fontsize=9, fontweight='bold', color='white')
    
    # IN27
    ax.add_patch(FancyBboxPatch((7.5, 5.4), 1.3, 0.6, boxstyle="round,pad=0.05", 
                                facecolor='#3498DB', edgecolor='black', linewidth=1.5))
    ax.text(8.15, 5.7, 'IN27\n×1.0', ha='center', va='center', fontsize=9, fontweight='bold', color='white')
    
    # PD
    ax.add_patch(FancyBboxPatch((7.5, 6.2), 1.3, 0.6, boxstyle="round,pad=0.05", 
                                facecolor='#E74C3C', edgecolor='black', linewidth=1.5))
    ax.text(8.15, 6.5, 'PD\n×0.8', ha='center', va='center', fontsize=9, fontweight='bold', color='white')
    
    # UNIT节点
    ax.add_patch(FancyBboxPatch((6, 3.8), 3, 0.7, boxstyle="round,pad=0.05", 
                                facecolor='#96CEB4', edgecolor='black', linewidth=1.5))
    ax.text(7.5, 4.15, '课程 UNIT', ha='center', va='center', fontsize=11)
    
    # 连接技能到UNIT
    ax.arrow(6.65, 5.4, 0, -0.5, head_width=0.15, head_length=0.08, fc='green', ec='green', linewidth=1.5)
    ax.text(6.3, 4.9, '1.0', fontsize=9, color='green', fontweight='bold')
    
    # 图例
    legend_y = 2.5
    ax.text(5, legend_y + 0.5, '📊 权重说明', fontsize=14, fontweight='bold')
    ax.text(5, legend_y, '• 实线箭头: 直接关系', fontsize=10)
    ax.text(5, legend_y - 0.3, '• 虚线箭头: 间接推导', fontsize=10)
    ax.text(5, legend_y - 0.6, '• 数字: 权重值', fontsize=10)
    ax.text(5, legend_y - 0.9, '• 颜色: 绿(1.0) > 蓝(0.9) > 橙(0.8) > 红(≤0.75)', fontsize=10)
    
    plt.title('知识图谱权重计算流程图\nWeight Calculation Flow', fontsize=18, fontweight='bold', pad=20)
    
    output_file = 'WEIGHT_FLOW_DIAGRAM.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ 权重流程图已保存: {output_file}")
    plt.close()


def main():
    print("=" * 60)
    print("生成权重规则可视化图表")
    print("=" * 60)
    
    create_weight_comparison_chart()
    create_weight_flow_diagram()
    
    print("\n" + "=" * 60)
    print("✅ 完成！生成了以下文件:")
    print("  1. WEIGHT_RULES_COMPARISON.png - 权重对比柱状图")
    print("  2. WEIGHT_FLOW_DIAGRAM.png - 权重流程图")
    print("=" * 60)


if __name__ == "__main__":
    main()

