#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目 ⇄ 单元 ⇄ 关键技能 匹配视图生成器
专门用于展示项目、单元和技能之间的匹配关系
"""

import os
import json
import glob
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
from typing import Dict, List, Set, Optional, Any, Tuple
from collections import defaultdict, Counter

class ProjectUnitSkillMatcher:
    """项目-单元-技能匹配视图生成器"""
    
    def __init__(self):
        # 定义颜色方案
        self.colors = {
            'project': '#FF6B6B',      # 红色 - 项目
            'unit': '#FF9FF3',         # 粉紫色 - 单元
            'skill': '#45B7D1',        # 蓝色 - 技能
            'connection': '#98FB98',    # 浅绿色 - 连接线
            'highlight': '#FFD700'      # 金色 - 高亮
        }
        
        self.layout_config = {
            'project_y': 0.8,          # 项目节点Y位置
            'unit_y': 0.5,             # 单元节点Y位置  
            'skill_y': 0.2,            # 技能节点Y位置
            'spacing': 0.15            # 节点间距
        }
    
    def load_project_data(self, project_dir: str) -> Tuple[List[Dict], List[Dict]]:
        """加载项目的实体和关系数据"""
        
        entities_file = None
        relationships_file = None
        
        # 查找文件
        for file in os.listdir(project_dir):
            if file.endswith('_entities.json'):
                entities_file = os.path.join(project_dir, file)
            elif file.endswith('_relationships.json'):
                relationships_file = os.path.join(project_dir, file)
        
        if not entities_file or not relationships_file:
            raise FileNotFoundError(f"在 {project_dir} 中找不到必要的JSON文件")
        
        # 加载数据
        with open(entities_file, 'r', encoding='utf-8') as f:
            entities = json.load(f)
        
        with open(relationships_file, 'r', encoding='utf-8') as f:
            relationships = json.load(f)
        
        return entities, relationships
    
    def extract_matching_chains(self, entities: List[Dict], relationships: List[Dict]) -> Dict:
        """提取项目-单元-技能的匹配链"""
        
        # 构建实体映射
        entity_map = {e['id']: e for e in entities}
        
        # 构建关系映射
        relations_by_source = defaultdict(list)
        for rel in relationships:
            relations_by_source[rel['source_id']].append(rel)
        
        # 查找项目实体
        project_entities = [e for e in entities if e['entity_type'] == 'PROJECT']
        if not project_entities:
            return {}
        
        project = project_entities[0]  # 取第一个项目
        
        # 查找项目直接相关的单元
        project_to_units = []
        for rel in relations_by_source.get(project['id'], []):
            if rel['relation_type'] == 'RELATES_TO_UNIT':
                target_entity = entity_map.get(rel['target_id'])
                if target_entity and target_entity['entity_type'] == 'UNIT':
                    project_to_units.append(target_entity)
        
        # 查找单元支持的技能
        unit_to_skills = defaultdict(list)
        for unit in project_to_units:
            for rel in relations_by_source.get(unit['id'], []):
                if rel['relation_type'] == 'SUPPORTS_SKILL':
                    target_entity = entity_map.get(rel['target_id'])
                    if target_entity and target_entity['entity_type'] == 'SKILL':
                        unit_to_skills[unit['id']].append(target_entity)
        
        # 查找项目直接需要的技能
        project_required_skills = []
        for rel in relations_by_source.get(project['id'], []):
            if rel['relation_type'] == 'REQUIRES_SKILL':
                target_entity = entity_map.get(rel['target_id'])
                if target_entity and target_entity['entity_type'] == 'SKILL':
                    project_required_skills.append(target_entity)
        
        # 分析技能匹配情况
        unit_supported_skills = set()
        for skills in unit_to_skills.values():
            unit_supported_skills.update(s['id'] for s in skills)
        
        project_required_skill_ids = set(s['id'] for s in project_required_skills)
        
        matched_skills = unit_supported_skills.intersection(project_required_skill_ids)
        unmatched_skills = project_required_skill_ids - unit_supported_skills
        extra_skills = unit_supported_skills - project_required_skill_ids
        
        return {
            'project': project,
            'units': project_to_units,
            'unit_to_skills': dict(unit_to_skills),
            'project_required_skills': project_required_skills,
            'matched_skills': matched_skills,
            'unmatched_skills': unmatched_skills,
            'extra_skills': extra_skills,
            'entity_map': entity_map
        }
    
    def create_matching_layout(self, matching_data: Dict) -> Dict:
        """创建匹配视图的布局"""
        
        project = matching_data['project']
        units = matching_data['units']
        unit_to_skills = matching_data['unit_to_skills']
        entity_map = matching_data['entity_map']
        
        pos = {}
        
        # 项目节点（顶部中央）
        pos[project['id']] = (0.5, self.layout_config['project_y'])
        
        # 单元节点（中间层，水平分布）
        if units:
            unit_width = min(0.8, len(units) * self.layout_config['spacing'])
            unit_start_x = 0.5 - unit_width / 2
            for i, unit in enumerate(units):
                x = unit_start_x + i * (unit_width / max(1, len(units) - 1)) if len(units) > 1 else 0.5
                pos[unit['id']] = (x, self.layout_config['unit_y'])
        
        # 技能节点（底部层，按单元分组）
        skill_positions = {}
        used_x_positions = set()
        
        for unit_id, skills in unit_to_skills.items():
            if not skills:
                continue
            
            unit_x = pos.get(unit_id, [0.5, 0.5])[0]
            
            # 为每个单元的技能分配位置
            skill_width = min(0.3, len(skills) * 0.05)
            skill_start_x = unit_x - skill_width / 2
            
            for i, skill in enumerate(skills):
                if len(skills) == 1:
                    x = unit_x
                else:
                    x = skill_start_x + i * (skill_width / (len(skills) - 1))
                
                # 避免重叠
                while x in used_x_positions:
                    x += 0.02
                
                pos[skill['id']] = (x, self.layout_config['skill_y'])
                used_x_positions.add(x)
        
        return pos
    
    def create_matching_visualization(self, matching_data: Dict, project_name: str, output_file: str):
        """创建匹配视图可视化"""
        
        if not matching_data or not matching_data.get('project'):
            print("❌ 没有足够的匹配数据")
            return False
        
        try:
            # 创建图形
            fig, ax = plt.subplots(figsize=(16, 12))
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            # 获取数据
            project = matching_data['project']
            units = matching_data['units']
            unit_to_skills = matching_data['unit_to_skills']
            entity_map = matching_data['entity_map']
            matched_skills = matching_data['matched_skills']
            unmatched_skills = matching_data['unmatched_skills']
            
            # 计算布局
            pos = self.create_matching_layout(matching_data)
            
            # 绘制连接线
            print("🎨 绘制连接线...")
            
            # 项目到单元的连接
            project_pos = pos[project['id']]
            for unit in units:
                unit_pos = pos[unit['id']]
                ax.plot([project_pos[0], unit_pos[0]], [project_pos[1], unit_pos[1]], 
                       color=self.colors['connection'], linewidth=3, alpha=0.7, zorder=1)
            
            # 单元到技能的连接
            for unit_id, skills in unit_to_skills.items():
                unit_pos = pos.get(unit_id)
                if not unit_pos:
                    continue
                
                for skill in skills:
                    skill_pos = pos.get(skill['id'])
                    if skill_pos:
                        # 根据技能匹配状态选择颜色
                        if skill['id'] in matched_skills:
                            line_color = self.colors['highlight']
                            line_width = 4
                            alpha = 0.9
                        else:
                            line_color = self.colors['connection']
                            line_width = 2
                            alpha = 0.6
                        
                        ax.plot([unit_pos[0], skill_pos[0]], [unit_pos[1], skill_pos[1]], 
                               color=line_color, linewidth=line_width, alpha=alpha, zorder=1)
            
            # 绘制节点
            print("🎨 绘制节点...")
            
            # 项目节点
            project_pos = pos[project['id']]
            ax.scatter(project_pos[0], project_pos[1], s=2000, c=self.colors['project'], 
                      alpha=0.9, edgecolors='black', linewidth=2, zorder=3)
            
            # 单元节点
            for unit in units:
                unit_pos = pos[unit['id']]
                ax.scatter(unit_pos[0], unit_pos[1], s=1200, c=self.colors['unit'], 
                          alpha=0.8, edgecolors='black', linewidth=1.5, zorder=3)
            
            # 技能节点
            for unit_id, skills in unit_to_skills.items():
                for skill in skills:
                    skill_pos = pos.get(skill['id'])
                    if skill_pos:
                        # 根据匹配状态选择颜色和大小
                        if skill['id'] in matched_skills:
                            color = self.colors['highlight']
                            size = 800
                            edge_width = 2
                        elif skill['id'] in unmatched_skills:
                            color = '#FF6B6B'  # 红色表示未匹配
                            size = 600
                            edge_width = 1
                        else:
                            color = self.colors['skill']
                            size = 600
                            edge_width = 1
                        
                        ax.scatter(skill_pos[0], skill_pos[1], s=size, c=color, 
                                  alpha=0.8, edgecolors='black', linewidth=edge_width, zorder=3)
            
            # 添加标签
            print("🎨 添加标签...")
            
            # 项目标签
            project_name_short = project['name'][:30] + "..." if len(project['name']) > 30 else project['name']
            ax.text(project_pos[0], project_pos[1], project_name_short, 
                   ha='center', va='center', fontsize=12, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
            
            # 单元标签
            for unit in units:
                unit_pos = pos[unit['id']]
                unit_name = unit['name'][:20] + "..." if len(unit['name']) > 20 else unit['name']
                ax.text(unit_pos[0], unit_pos[1] + 0.05, unit_name, 
                       ha='center', va='bottom', fontsize=10, fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))
            
            # 技能标签
            for unit_id, skills in unit_to_skills.items():
                for skill in skills:
                    skill_pos = pos.get(skill['id'])
                    if skill_pos:
                        skill_name = skill['name'][:15] + "..." if len(skill['name']) > 15 else skill['name']
                        
                        # 根据匹配状态选择字体样式
                        if skill['id'] in matched_skills:
                            fontweight = 'bold'
                            fontsize = 9
                        else:
                            fontweight = 'normal'
                            fontsize = 8
                        
                        ax.text(skill_pos[0], skill_pos[1] - 0.03, skill_name, 
                               ha='center', va='top', fontsize=fontsize, fontweight=fontweight,
                               bbox=dict(boxstyle='round,pad=0.1', facecolor='white', alpha=0.6))
            
            # 添加层级标签
            ax.text(0.02, self.layout_config['project_y'], 'PROJECT', 
                   fontsize=14, fontweight='bold', va='center',
                   bbox=dict(boxstyle='round', facecolor=self.colors['project'], alpha=0.3))
            
            ax.text(0.02, self.layout_config['unit_y'], 'UNITS', 
                   fontsize=14, fontweight='bold', va='center',
                   bbox=dict(boxstyle='round', facecolor=self.colors['unit'], alpha=0.3))
            
            ax.text(0.02, self.layout_config['skill_y'], 'SKILLS', 
                   fontsize=14, fontweight='bold', va='center',
                   bbox=dict(boxstyle='round', facecolor=self.colors['skill'], alpha=0.3))
            
            # 添加统计信息
            total_skills = sum(len(skills) for skills in unit_to_skills.values())
            matched_count = len(matched_skills)
            coverage = matched_count / len(matching_data['project_required_skills']) * 100 if matching_data['project_required_skills'] else 0
            
            stats_text = f"""匹配统计:
• 连接单元数: {len(units)}
• 支持技能数: {total_skills}
• 匹配技能数: {matched_count}
• 匹配覆盖率: {coverage:.1f}%"""
            
            ax.text(0.98, 0.98, stats_text, ha='right', va='top', fontsize=10,
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.8),
                   transform=ax.transAxes)
            
            # 添加图例
            legend_elements = [
                mpatches.Circle((0, 0), 0.1, facecolor=self.colors['project'], label='项目'),
                mpatches.Circle((0, 0), 0.1, facecolor=self.colors['unit'], label='单元'),
                mpatches.Circle((0, 0), 0.1, facecolor=self.colors['skill'], label='技能'),
                mpatches.Circle((0, 0), 0.1, facecolor=self.colors['highlight'], label='匹配技能'),
                plt.Line2D([0], [0], color=self.colors['connection'], linewidth=3, label='连接关系'),
                plt.Line2D([0], [0], color=self.colors['highlight'], linewidth=4, label='匹配关系')
            ]
            
            ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0, 0.9),
                     fontsize=10, framealpha=0.9)
            
            # 设置标题
            plt.title(f'项目 ⇄ 单元 ⇄ 技能 匹配视图\n{project_name}', 
                     fontsize=16, fontweight='bold', pad=20)
            
            plt.tight_layout()
            
            # 保存图片
            print(f"💾 保存匹配视图到: {output_file}")
            plt.savefig(output_file, dpi=300, bbox_inches='tight',
                        facecolor='white', edgecolor='none', format='png')
            plt.close()
            
            print(f"✅ 匹配视图生成成功: {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ 匹配视图生成失败: {e}")
            import traceback
            traceback.print_exc()
            plt.close()
            return False
    
    def generate_single_project_view(self, project_dir: str) -> bool:
        """为单个项目生成匹配视图"""
        
        project_name = os.path.basename(project_dir)
        print(f"\n🎯 生成匹配视图: {project_name}")
        
        try:
            # 加载数据
            entities, relationships = self.load_project_data(project_dir)
            
            # 提取匹配链
            matching_data = self.extract_matching_chains(entities, relationships)
            
            if not matching_data:
                print("❌ 没有找到匹配数据")
                return False
            
            # 生成可视化
            output_file = os.path.join(project_dir, f"{project_name}_matching_view.png")
            return self.create_matching_visualization(matching_data, project_name, output_file)
            
        except Exception as e:
            print(f"❌ 生成失败: {e}")
            return False
    
    def generate_all_matching_views(self, base_dir: str = "individual_kg/projects_uo"):
        """为所有项目生成匹配视图"""
        
        print("🚀 开始生成所有项目的匹配视图...")
        
        if not os.path.exists(base_dir):
            print(f"❌ 目录不存在: {base_dir}")
            return
        
        # 获取所有项目目录
        project_dirs = [d for d in os.listdir(base_dir) 
                       if os.path.isdir(os.path.join(base_dir, d)) and d.startswith('project_')]
        
        print(f"📁 找到 {len(project_dirs)} 个项目目录")
        
        success_count = 0
        for i, project_dir_name in enumerate(project_dirs, 1):
            project_full_path = os.path.join(base_dir, project_dir_name)
            print(f"\n[{i}/{len(project_dirs)}] 处理: {project_dir_name}")
            
            if self.generate_single_project_view(project_full_path):
                success_count += 1
                print(f"  ✅ 成功")
            else:
                print(f"  ❌ 失败")
        
        print(f"\n📊 匹配视图生成完成!")
        print(f"  成功生成: {success_count}/{len(project_dirs)} 个")
        print(f"  成功率: {success_count/len(project_dirs)*100:.1f}%")

def main():
    """主函数"""
    print("🎯 项目 ⇄ 单元 ⇄ 技能 匹配视图生成器")
    print("=" * 60)
    
    matcher = ProjectUnitSkillMatcher()
    matcher.generate_all_matching_views()
    
    print("\n🎉 匹配视图生成完成!")
    print("现在你可以在 individual_kg/projects_uo/ 中查看 *_matching_view.png 文件")

if __name__ == "__main__":
    main()
