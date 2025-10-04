"""
实验2a结果可视化
使用知识图谱相似度（Jaccard相似度和编辑距离）分析项目-学生匹配结果
"""

import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import pandas as pd

# 设置中文字体和样式
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
sns.set_style("whitegrid")
sns.set_palette("husl")

# 读取数据，兼容新旧路径及文件名
data_dir_candidates = [
    Path("outputs/kg_similarity/2a"),
    Path("outputs1/kg_similarity/2a")
]

data_dir = None
for candidate in data_dir_candidates:
    if candidate.exists():
        data_dir = candidate
        break

if data_dir is None:
    raise FileNotFoundError("无法找到Method 2a的数据目录，请确认已生成实验结果")

output_dir = data_dir

score_file_candidates = [
    "method_2a_scores_with_negatives.json",
    "method_2a_scores.json"
]

analysis_file_candidates = [
    "method_2a_analysis_with_negatives.json",
    "method_2a_analysis.json"
]

scores_file = next((data_dir / name for name in score_file_candidates if (data_dir / name).exists()), None)
analysis_file = next((data_dir / name for name in analysis_file_candidates if (data_dir / name).exists()), None)

if scores_file is None or analysis_file is None:
    raise FileNotFoundError("缺少Method 2a的分数或分析文件，请先运行rerun_method2_with_neg_samples.py")

with open(scores_file, "r", encoding="utf-8") as f:
    scores = json.load(f)

with open(analysis_file, "r", encoding="utf-8") as f:
    analysis = json.load(f)

# 转换为DataFrame
df = pd.DataFrame(scores)

# 标准化字段名称
project_column = 'project_name' if 'project_name' in df.columns else 'project_id'
df.rename(columns={project_column: 'project_name'}, inplace=True)

if 'label' not in df.columns:
    df['label'] = df['is_match'].map(lambda x: 'positive' if x else 'negative') if 'is_match' in df.columns else 'unknown'

# 确保节点统计字段存在
for col in ['common_nodes', 'project_only_nodes', 'student_only_nodes']:
    if col not in df.columns:
        df[col] = np.nan

# 将is_match转换为布尔值便于筛选
if 'is_match' in df.columns:
    df['is_match'] = df['is_match'].astype(bool)

print(f"📊 实验2a数据概览:")
print(f"  总配对数: {len(df)}")
print(f"  唯一项目数: {df['project_name'].nunique()}")
print(f"  唯一学生数: {df['student_id'].nunique()}")
print(f"\n📈 统计信息:")
print(f"  Jaccard相似度: mean={analysis['matched_jaccard']['mean']:.4f}, "
      f"median={analysis['matched_jaccard']['median']:.4f}, "
      f"max={analysis['matched_jaccard']['max']:.4f}")
print(f"  编辑距离: mean={analysis['matched_edit_distance']['mean']:.1f}, "
      f"median={analysis['matched_edit_distance']['median']:.1f}, "
      f"min={analysis['matched_edit_distance']['min']:.0f}")

# 创建大型综合可视化（6个子图）
fig = plt.figure(figsize=(20, 12))

# 1. Jaccard相似度分布（直方图）
ax1 = plt.subplot(2, 3, 1)
plt.hist(df['jaccard_similarity'], bins=50, color='steelblue', alpha=0.7, edgecolor='black')
plt.axvline(df['jaccard_similarity'].mean(), color='red', linestyle='--', 
            linewidth=2, label=f'Mean: {df["jaccard_similarity"].mean():.4f}')
plt.axvline(df['jaccard_similarity'].median(), color='orange', linestyle='--', 
            linewidth=2, label=f'Median: {df["jaccard_similarity"].median():.4f}')
plt.xlabel('Jaccard Similarity', fontsize=11, fontweight='bold')
plt.ylabel('Frequency', fontsize=11, fontweight='bold')
plt.title('Method 2a: Jaccard Similarity Distribution', fontsize=13, fontweight='bold', pad=10)
plt.legend(fontsize=10)
plt.grid(True, alpha=0.3)

# 2. 编辑距离分布（直方图）
ax2 = plt.subplot(2, 3, 2)
plt.hist(df['edit_distance'], bins=30, color='coral', alpha=0.7, edgecolor='black')
plt.axvline(df['edit_distance'].mean(), color='red', linestyle='--', 
            linewidth=2, label=f'Mean: {df["edit_distance"].mean():.1f}')
plt.axvline(df['edit_distance'].median(), color='orange', linestyle='--', 
            linewidth=2, label=f'Median: {df["edit_distance"].median():.1f}')
plt.xlabel('Edit Distance', fontsize=11, fontweight='bold')
plt.ylabel('Frequency', fontsize=11, fontweight='bold')
plt.title('Method 2a: Edit Distance Distribution', fontsize=13, fontweight='bold', pad=10)
plt.legend(fontsize=10)
plt.grid(True, alpha=0.3)

# 3. Jaccard vs 编辑距离散点图（带密度）
ax3 = plt.subplot(2, 3, 3)
scatter = plt.scatter(df['jaccard_similarity'], df['edit_distance'], 
                     c=df['common_nodes'], cmap='viridis', 
                     alpha=0.6, s=50, edgecolors='black', linewidth=0.5)
plt.xlabel('Jaccard Similarity', fontsize=11, fontweight='bold')
plt.ylabel('Edit Distance', fontsize=11, fontweight='bold')
plt.title('Method 2a: Jaccard vs Edit Distance', fontsize=13, fontweight='bold', pad=10)
cbar = plt.colorbar(scatter, ax=ax3)
cbar.set_label('Common Nodes', fontsize=10, fontweight='bold')
plt.grid(True, alpha=0.3)

# 4. 共同节点数分布
ax4 = plt.subplot(2, 3, 4)
common_nodes_counts = df['common_nodes'].dropna().value_counts().sort_index()
plt.bar(common_nodes_counts.index, common_nodes_counts.values, 
        color='mediumseagreen', alpha=0.7, edgecolor='black')
plt.xlabel('Number of Common Nodes', fontsize=11, fontweight='bold')
plt.ylabel('Frequency', fontsize=11, fontweight='bold')
plt.title('Method 2a: Common Nodes Distribution', fontsize=13, fontweight='bold', pad=10)
plt.grid(True, alpha=0.3, axis='y')

# 5. Top 10 项目的平均Jaccard相似度
ax5 = plt.subplot(2, 3, 5)
top_projects = df[df['is_match']].groupby('project_name')['jaccard_similarity'].mean().nlargest(10)
y_pos = np.arange(len(top_projects))
colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(top_projects)))
plt.barh(y_pos, top_projects.values, color=colors, alpha=0.8, edgecolor='black')
plt.yticks(y_pos, [name[:30] + '...' if len(name) > 30 else name 
                   for name in top_projects.index], fontsize=9)
plt.xlabel('Average Jaccard Similarity', fontsize=11, fontweight='bold')
plt.title('Method 2a: Top 10 Projects by Avg Jaccard', fontsize=13, fontweight='bold', pad=10)
plt.grid(True, alpha=0.3, axis='x')

# 6. 箱线图：节点统计比较
ax6 = plt.subplot(2, 3, 6)
box_data = [df['common_nodes'], df['project_only_nodes'], df['student_only_nodes']]
bp = plt.boxplot(box_data, labels=['Common\nNodes', 'Project Only\nNodes', 'Student Only\nNodes'],
                 patch_artist=True, showmeans=True, meanline=True)
colors_box = ['lightblue', 'lightcoral', 'lightgreen']
for patch, color in zip(bp['boxes'], colors_box):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
plt.ylabel('Number of Nodes', fontsize=11, fontweight='bold')
plt.title('Method 2a: Node Statistics Comparison', fontsize=13, fontweight='bold', pad=10)
plt.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(output_dir / "method_2a_comprehensive_visualization.png", dpi=300, bbox_inches='tight')
print(f"\n✅ 综合可视化已保存: {output_dir / 'method_2a_comprehensive_visualization.png'}")

# 创建额外的详细分析图（4个子图）
fig2 = plt.figure(figsize=(18, 10))

# 1. 相似度分组统计
ax1 = plt.subplot(2, 2, 1)
bins = [0, 0.01, 0.02, 0.03, 0.04, 0.05, 1.0]
labels = ['0-0.01', '0.01-0.02', '0.02-0.03', '0.03-0.04', '0.04-0.05', '>0.05']
df['jaccard_group'] = pd.cut(df['jaccard_similarity'], bins=bins, labels=labels)
jaccard_counts = df['jaccard_group'].value_counts().sort_index()
colors_pie = plt.cm.Set3(np.arange(len(jaccard_counts)))
plt.pie(jaccard_counts.values, labels=jaccard_counts.index, autopct='%1.1f%%',
        colors=colors_pie, startangle=90, explode=[0.05]*len(jaccard_counts))
plt.title('Method 2a: Jaccard Similarity Groups', fontsize=13, fontweight='bold', pad=10)

# 2. 编辑距离热力图（按项目）
ax2 = plt.subplot(2, 2, 2)
project_edit_distances = df[df['is_match']].groupby('project_name')['edit_distance'].agg(['mean', 'min', 'max']).nlargest(15, 'mean')
x = np.arange(len(project_edit_distances))
width = 0.25
plt.bar(x - width, project_edit_distances['min'], width, label='Min', alpha=0.8, color='lightgreen')
plt.bar(x, project_edit_distances['mean'], width, label='Mean', alpha=0.8, color='skyblue')
plt.bar(x + width, project_edit_distances['max'], width, label='Max', alpha=0.8, color='salmon')
plt.xlabel('Project', fontsize=11, fontweight='bold')
plt.ylabel('Edit Distance', fontsize=11, fontweight='bold')
plt.title('Method 2a: Top 15 Projects Edit Distance Stats', fontsize=13, fontweight='bold', pad=10)
plt.xticks(x, ['P' + str(i+1) for i in range(len(project_edit_distances))], fontsize=9)
plt.legend(fontsize=10)
plt.grid(True, alpha=0.3, axis='y')

# 3. Jaccard相似度累积分布
ax3 = plt.subplot(2, 2, 3)
sorted_jaccard = np.sort(df['jaccard_similarity'])
cumulative = np.arange(1, len(sorted_jaccard) + 1) / len(sorted_jaccard) * 100
plt.plot(sorted_jaccard, cumulative, linewidth=2.5, color='purple', label='CDF')
plt.fill_between(sorted_jaccard, cumulative, alpha=0.3, color='purple')
plt.xlabel('Jaccard Similarity', fontsize=11, fontweight='bold')
plt.ylabel('Cumulative Percentage (%)', fontsize=11, fontweight='bold')
plt.title('Method 2a: Jaccard Similarity CDF', fontsize=13, fontweight='bold', pad=10)
plt.grid(True, alpha=0.3)
plt.legend(fontsize=10)

# 添加关键百分位点
percentiles = [25, 50, 75, 90]
for p in percentiles:
    val = np.percentile(df['jaccard_similarity'], p)
    plt.axvline(val, color='red', linestyle='--', alpha=0.5, linewidth=1)
    plt.text(val, p, f'P{p}={val:.3f}', fontsize=8, rotation=90, va='bottom')

# 4. 节点比例分析
ax4 = plt.subplot(2, 2, 4)
df['total_nodes'] = df['common_nodes'] + df['project_only_nodes'] + df['student_only_nodes']
df['common_ratio'] = df['common_nodes'] / df['total_nodes']
df['project_ratio'] = df['project_only_nodes'] / df['total_nodes']
df['student_ratio'] = df['student_only_nodes'] / df['total_nodes']

# 堆叠面积图（抽样以提高性能）
sample_df = df.sample(min(100, len(df))).sort_values('jaccard_similarity')
x_vals = np.arange(len(sample_df))
plt.fill_between(x_vals, 0, sample_df['common_ratio'].values, 
                 label='Common Nodes', alpha=0.7, color='#2ecc71')
plt.fill_between(x_vals, sample_df['common_ratio'].values, 
                 sample_df['common_ratio'].values + sample_df['project_ratio'].values,
                 label='Project Only', alpha=0.7, color='#3498db')
plt.fill_between(x_vals, 
                 sample_df['common_ratio'].values + sample_df['project_ratio'].values,
                 1.0, label='Student Only', alpha=0.7, color='#e74c3c')
plt.xlabel('Sample Index (sorted by Jaccard)', fontsize=11, fontweight='bold')
plt.ylabel('Node Ratio', fontsize=11, fontweight='bold')
plt.title('Method 2a: Node Type Ratios (Stacked)', fontsize=13, fontweight='bold', pad=10)
plt.legend(fontsize=10, loc='upper left')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(output_dir / "method_2a_detailed_analysis.png", dpi=300, bbox_inches='tight')
print(f"✅ 详细分析图已保存: {output_dir / 'method_2a_detailed_analysis.png'}")

# 创建统计摘要
summary = {
    "method": "Method 2a - Knowledge Graph Similarity",
    "total_pairs": len(df),
    "unique_projects": df['project_name'].nunique(),
    "unique_students": df['student_id'].nunique(),
    "jaccard_statistics": {
        "mean": float(df['jaccard_similarity'].mean()),
        "median": float(df['jaccard_similarity'].median()),
        "std": float(df['jaccard_similarity'].std()),
        "min": float(df['jaccard_similarity'].min()),
        "max": float(df['jaccard_similarity'].max()),
        "percentile_25": float(df['jaccard_similarity'].quantile(0.25)),
        "percentile_75": float(df['jaccard_similarity'].quantile(0.75)),
        "percentile_90": float(df['jaccard_similarity'].quantile(0.90))
    },
    "edit_distance_statistics": {
        "mean": float(df['edit_distance'].mean()),
        "median": float(df['edit_distance'].median()),
        "std": float(df['edit_distance'].std()),
        "min": float(df['edit_distance'].min()),
        "max": float(df['edit_distance'].max())
    },
    "node_statistics": {
        "common_nodes": {
            "mean": float(df['common_nodes'].mean()),
            "median": float(df['common_nodes'].median()),
            "max": int(df['common_nodes'].max())
        },
        "project_only_nodes": {
            "mean": float(df['project_only_nodes'].mean()),
            "median": float(df['project_only_nodes'].median())
        },
        "student_only_nodes": {
            "mean": float(df['student_only_nodes'].mean()),
            "median": float(df['student_only_nodes'].median())
        }
    },
    "top_5_matches": df.nlargest(5, 'jaccard_similarity')[
        ['project_name', 'student_id', 'jaccard_similarity', 'edit_distance', 'common_nodes']
    ].to_dict('records')
}

with open(output_dir / "method_2a_visualization_summary.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)

print(f"✅ 统计摘要已保存: {output_dir / 'method_2a_visualization_summary.json'}")

# 打印关键发现
print("\n" + "="*60)
print("📊 Method 2a 关键发现:")
print("="*60)
print(f"\n1. 相似度分析:")
print(f"   - Jaccard相似度普遍较低 (mean={summary['jaccard_statistics']['mean']:.4f})")
print(f"   - 90%的配对Jaccard相似度 < {summary['jaccard_statistics']['percentile_90']:.4f}")
print(f"\n2. 编辑距离分析:")
print(f"   - 平均编辑距离: {summary['edit_distance_statistics']['mean']:.1f}")
print(f"   - 范围: {summary['edit_distance_statistics']['min']:.0f} - {summary['edit_distance_statistics']['max']:.0f}")
print(f"\n3. 节点重叠分析:")
print(f"   - 平均共同节点: {summary['node_statistics']['common_nodes']['mean']:.1f}")
print(f"   - 最大共同节点: {summary['node_statistics']['common_nodes']['max']}")
print(f"   - 学生KG平均节点数 > 项目KG节点数")
print(f"\n4. Top 5 最佳匹配:")
for i, match in enumerate(summary['top_5_matches'], 1):
    print(f"   {i}. {match['project_name'][:40]}... <-> {match['student_id']}")
    print(f"      Jaccard={match['jaccard_similarity']:.4f}, Distance={match['edit_distance']}, Common={match['common_nodes']}")

print("\n" + "="*60)
print("🎨 可视化完成！")
print("="*60)
plt.show()
