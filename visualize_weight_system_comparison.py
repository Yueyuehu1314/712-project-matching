#!/usr/bin/env python3
"""
可视化两种不同的权重系统
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def create_weight_system_comparison():
    """创建两种权重系统的对比图"""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 10))
    
    # ============= 左侧：学生KG - 归一化权重 (0-1) =============
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    ax1.axis('off')
    
    ax1.text(5, 9.5, '学生KG - 归一化权重系统', fontsize=16, fontweight='bold', ha='center',
            bbox=dict(boxstyle='round,pad=0.6', facecolor='#E8F4F8', edgecolor='#2980B9', linewidth=3))
    
    ax1.text(5, 8.8, '权重范围: 0 - 1.0 (可信度)', fontsize=12, ha='center', style='italic')
    
    # 学生节点
    ax1.add_patch(FancyBboxPatch((3.5, 7), 3, 0.8, boxstyle="round,pad=0.1", 
                                facecolor='#3498DB', edgecolor='black', linewidth=2))
    ax1.text(5, 7.4, '学生\nSTUDENT', ha='center', va='center', fontsize=12, fontweight='bold', color='white')
    
    # 技能节点们
    skills_student = [
        ('Python\n(course)', 0.8, 3, '#2ECC71'),
        ('Java\n(project)', 0.75, 5, '#F39C12'),
        ('React\n(self-taught)', 0.6, 7, '#E74C3C'),
    ]
    
    y_pos = 4.5
    for skill_name, weight, x_pos, color in skills_student:
        # 技能节点
        ax1.add_patch(FancyBboxPatch((x_pos-0.7, y_pos-0.3), 1.4, 0.6, boxstyle="round,pad=0.05", 
                                    facecolor=color, edgecolor='black', linewidth=1.5, alpha=0.7))
        ax1.text(x_pos, y_pos, skill_name, ha='center', va='center', fontsize=9, fontweight='bold')
        
        # 箭头
        arrow = FancyArrowPatch((5, 7), (x_pos, y_pos+0.3),
                               arrowstyle='->', mutation_scale=20, linewidth=2.5, 
                               color=color, alpha=0.8)
        ax1.add_patch(arrow)
        
        # 权重标签
        ax1.text((5+x_pos)/2, (7+y_pos)/2+0.3, f'{weight}', fontsize=11, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=color, linewidth=2))
    
    # 权重说明
    ax1.text(5, 2.5, '权重含义', fontsize=13, ha='center', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#ECF0F1'))
    ax1.text(5, 2, '1.0 = 完全可信 (课程证明)', fontsize=10, ha='center')
    ax1.text(5, 1.5, '0.8 = 高度可信 (课程学习)', fontsize=10, ha='center')
    ax1.text(5, 1, '0.6 = 无法验证 (自述)', fontsize=10, ha='center')
    
    # ============= 右侧：项目KG - 原始匹配分数 (无上限) =============
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.axis('off')
    
    ax2.text(5, 9.5, '项目KG - 匹配分数系统', fontsize=16, fontweight='bold', ha='center',
            bbox=dict(boxstyle='round,pad=0.6', facecolor='#FFF5E6', edgecolor='#E67E22', linewidth=3))
    
    ax2.text(5, 8.8, '权重范围: 0 - 无上限 (匹配强度)', fontsize=12, ha='center', style='italic')
    
    # 项目节点
    ax2.add_patch(FancyBboxPatch((3.5, 7), 3, 0.8, boxstyle="round,pad=0.1", 
                                facecolor='#E74C3C', edgecolor='black', linewidth=2))
    ax2.text(5, 7.4, '项目\nPROJECT', ha='center', va='center', fontsize=12, fontweight='bold', color='white')
    
    # 技能节点们（不同匹配分数）
    skills_project = [
        ('Machine\nLearning', 15, 2, '#9B59B6'),
        ('Python', 7, 4.3, '#3498DB'),
        ('Database', 3, 6.6, '#1ABC9C'),
        ('React', 2, 8.5, '#95A5A6'),
    ]
    
    y_pos = 4.5
    for skill_name, weight, x_pos, color in skills_project:
        # 技能节点大小根据权重变化
        size_factor = min(weight / 10, 1.5)
        width = 1.2 * size_factor
        height = 0.6 * size_factor
        
        ax2.add_patch(FancyBboxPatch((x_pos-width/2, y_pos-height/2), width, height, 
                                    boxstyle="round,pad=0.05", 
                                    facecolor=color, edgecolor='black', linewidth=2, alpha=0.8))
        ax2.text(x_pos, y_pos, skill_name, ha='center', va='center', fontsize=9, fontweight='bold', color='white')
        
        # 箭头粗细根据权重变化
        lw = min(weight / 3, 5)
        arrow = FancyArrowPatch((5, 7), (x_pos, y_pos+height/2),
                               arrowstyle='->', mutation_scale=20, linewidth=lw, 
                               color=color, alpha=0.7)
        ax2.add_patch(arrow)
        
        # 权重标签
        ax2.text((5+x_pos)/2, (7+y_pos)/2+0.4, f'{weight}', fontsize=12, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', edgecolor=color, linewidth=2))
    
    # 权重说明
    ax2.text(5, 2.5, '权重含义', fontsize=13, ha='center', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#ECF0F1'))
    ax2.text(5, 2, '15 = 核心技能 (多次提及)', fontsize=10, ha='center')
    ax2.text(5, 1.5, '7 = 重要技能 (明确要求)', fontsize=10, ha='center')
    ax2.text(5, 1, '2-3 = 次要技能 (偶尔提及)', fontsize=10, ha='center')
    
    plt.suptitle('两种权重系统对比\nStudent KG (0-1 Confidence) vs Project KG (Unbounded Match Score)', 
                 fontsize=18, fontweight='bold', y=0.98)
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    output_file = 'WEIGHT_SYSTEM_COMPARISON.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ 权重系统对比图已保存: {output_file}")
    plt.close()


def create_weight_range_chart():
    """创建权重范围对比柱状图"""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # 左侧：学生KG
    relations_student = [
        'PREREQUISITE_FOR',
        'COMPLETED_COURSE',
        'TEACHES_SKILL',
        'HAS_SKILL\n(course)',
        'HAS_SKILL\n(project)',
        'HAS_SKILL\n(self-taught)',
    ]
    weights_student = [1.0, 1.0, 0.9, 0.8, 0.75, 0.6]
    colors_student = ['#2ECC71', '#2ECC71', '#3498DB', '#3498DB', '#F39C12', '#E74C3C']
    
    bars1 = ax1.barh(relations_student, weights_student, color=colors_student, 
                     alpha=0.8, edgecolor='black', linewidth=2)
    
    for bar, weight in zip(bars1, weights_student):
        ax1.text(weight + 0.02, bar.get_y() + bar.get_height()/2, 
                f'{weight:.2f}', va='center', fontsize=11, fontweight='bold')
    
    ax1.set_xlim(0, 1.2)
    ax1.set_xlabel('权重 (可信度)', fontsize=13, fontweight='bold')
    ax1.set_title('学生KG - 归一化权重 (0-1)', fontsize=15, fontweight='bold', pad=15)
    ax1.axvline(x=1.0, color='red', linestyle='--', linewidth=2.5, alpha=0.7, label='上限=1.0')
    ax1.grid(axis='x', alpha=0.3, linestyle='--')
    ax1.legend(fontsize=11)
    
    # 右侧：项目KG
    relations_project = [
        'Machine Learning\n(核心)',
        'Python\n(重要)',
        'Web Dev\n(一般)',
        'Database\n(次要)',
        'PREREQUISITE_FOR',
    ]
    weights_project = [15, 7, 5, 2, 1]
    colors_project = ['#9B59B6', '#3498DB', '#1ABC9C', '#95A5A6', '#2ECC71']
    
    bars2 = ax2.barh(relations_project, weights_project, color=colors_project, 
                     alpha=0.8, edgecolor='black', linewidth=2)
    
    for bar, weight in zip(bars2, weights_project):
        ax2.text(weight + 0.3, bar.get_y() + bar.get_height()/2, 
                f'{weight}', va='center', fontsize=11, fontweight='bold')
    
    ax2.set_xlim(0, 20)
    ax2.set_xlabel('权重 (匹配分数)', fontsize=13, fontweight='bold')
    ax2.set_title('项目KG - 原始匹配分数 (无上限)', fontsize=15, fontweight='bold', pad=15)
    ax2.axvline(x=1.0, color='red', linestyle='--', linewidth=2.5, alpha=0.3, label='学生KG上限')
    ax2.grid(axis='x', alpha=0.3, linestyle='--')
    ax2.legend(fontsize=11)
    
    plt.suptitle('权重范围对比：归一化 vs 原始分数\nNormalized (0-1) vs Unbounded Scores', 
                 fontsize=17, fontweight='bold', y=0.98)
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    
    output_file = 'WEIGHT_RANGE_COMPARISON.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ 权重范围对比图已保存: {output_file}")
    plt.close()


def main():
    print("=" * 60)
    print("生成权重系统对比可视化")
    print("=" * 60)
    
    create_weight_system_comparison()
    create_weight_range_chart()
    
    print("\n" + "=" * 60)
    print("✅ 完成！生成了以下文件:")
    print("  1. WEIGHT_SYSTEM_COMPARISON.png - 两种权重系统对比")
    print("  2. WEIGHT_RANGE_COMPARISON.png - 权重范围对比柱状图")
    print("=" * 60)


if __name__ == "__main__":
    main()

