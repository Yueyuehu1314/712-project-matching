#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PD与UO交集知识图谱可视化器
只显示项目描述(PD)与单元大纲(UO)的交集部分
"""

import os
import json
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from typing import Dict, List, Set, Any
from collections import defaultdict

class PDUOIntersectionViewer:
    """PD与UO交集可视化器"""
    
    def __init__(self, kg_base_dir="individual_kg/projects_uo"):
        self.kg_base_dir = kg_base_dir
        
        # 定义颜色
        self.colors = {
            'PROJECT': '#FF6B6B',      # 红色 - 项目
            'UNIT': '#4ECDC4',         # 青色 - 单元
            'SKILL': '#45B7D1',        # 蓝色 - 普通技能
            'OVERLAP_SKILL': '#F39C12', # 橙色 - 交集技能
            'TECHNOLOGY': '#96CEB4'     # 绿色 - 技术
        }
        
        # 关系颜色
        self.relation_colors = {
            'REQUIRES_SKILL': '#E74C3C',    # 红色 - 项目需要技能
            'TEACHES_SKILL': '#3498DB',     # 蓝色 - 单元教授技能
            'RELATES_TO_UNIT': '#9B59B6'    # 紫色 - 项目相关单元
        }
    
    def _load_kg_data(self, project_dir):
        """加载知识图谱数据"""
        entities_file = None
        relationships_file = None
        
        # 查找文件
        for file in os.listdir(project_dir):
            if file.endswith('_entities.json'):
                entities_file = os.path.join(project_dir, file)
            elif file.endswith('_relationships.json'):
                relationships_file = os.path.join(project_dir, file)
        
        if not entities_file or not relationships_file:
            return None, None, None
        
        # 加载数据
        with open(entities_file, 'r', encoding='utf-8') as f:
            entities = json.load(f)
        
        with open(relationships_file, 'r', encoding='utf-8') as f:
            relationships = json.load(f)
        
        # 提取项目名称
        project_name = "Unknown Project"
        for entity in entities:
            if entity.get('entity_type') == 'PROJECT':
                project_name = entity.get('name', 'Unknown Project')
                break
        
        return entities, relationships, project_name
    
    def _find_intersection_skills(self, entities, relationships):
        """找出PD与UO的交集技能"""
        
        # 分析技能来源
        project_skills = set()  # 项目需要的技能
        unit_skills = set()     # 单元教授的技能
        
        # 获取项目ID
        project_id = None
        for entity in entities:
            if entity.get('entity_type') == 'PROJECT':
                project_id = entity.get('id')
                break
        
        if not project_id:
            return set(), set(), set()
        
        # 分析关系找出技能来源
        for rel in relationships:
            if rel.get('relation') == 'REQUIRES_SKILL' and rel.get('source_id') == project_id:
                # 项目需要的技能
                skill_id = rel.get('target_id')
                for entity in entities:
                    if entity.get('id') == skill_id and entity.get('entity_type') == 'SKILL':
                        project_skills.add(entity.get('name'))
                        
            elif rel.get('relation') == 'TEACHES_SKILL':
                # 单元教授的技能
                skill_id = rel.get('target_id')
                for entity in entities:
                    if entity.get('id') == skill_id and entity.get('entity_type') == 'SKILL':
                        unit_skills.add(entity.get('name'))
        
        # 找出交集
        intersection_skills = project_skills & unit_skills
        
        return project_skills, unit_skills, intersection_skills
    
    def _create_intersection_graph(self, entities, relationships, intersection_skills):
        """创建只包含交集部分的图"""
        
        # 创建NetworkX图
        G = nx.DiGraph()
        
        # 获取项目实体
        project_entity = None
        for entity in entities:
            if entity.get('entity_type') == 'PROJECT':
                project_entity = entity
                break
        
        if not project_entity:
            return G
        
        # 添加项目节点
        G.add_node(project_entity['id'], 
                   name=project_entity['name'],
                   type='PROJECT')
        
        # 只添加交集技能和相关的单元
        intersection_skill_ids = set()
        related_unit_ids = set()
        
        # 找出交集技能的ID
        for entity in entities:
            if (entity.get('entity_type') == 'SKILL' and 
                entity.get('name') in intersection_skills):
                intersection_skill_ids.add(entity['id'])
                
                # 添加技能节点
                G.add_node(entity['id'],
                          name=entity['name'],
                          type='OVERLAP_SKILL')
        
        # 找出教授交集技能的单元
        for rel in relationships:
            if (rel.get('relation') == 'TEACHES_SKILL' and 
                rel.get('target_id') in intersection_skill_ids):
                related_unit_ids.add(rel.get('source_id'))
        
        # 添加相关单元节点
        for entity in entities:
            if (entity.get('entity_type') == 'UNIT' and 
                entity.get('id') in related_unit_ids):
                G.add_node(entity['id'],
                          name=entity['name'],
                          type='UNIT')
        
        # 添加相关关系
        for rel in relationships:
            source_id = rel.get('source_id')
            target_id = rel.get('target_id')
            relation = rel.get('relation')
            
            # 只保留图中存在的节点之间的关系
            if source_id in G.nodes() and target_id in G.nodes():
                # 项目需要交集技能
                if (relation == 'REQUIRES_SKILL' and 
                    target_id in intersection_skill_ids):
                    G.add_edge(source_id, target_id, 
                              relation='REQUIRES_SKILL',
                              weight=rel.get('weight', 1.0))
                
                # 单元教授交集技能
                elif (relation == 'TEACHES_SKILL' and 
                      target_id in intersection_skill_ids):
                    G.add_edge(source_id, target_id,
                              relation='TEACHES_SKILL', 
                              weight=rel.get('weight', 1.0))
                
                # 项目与单元的关系
                elif relation == 'RELATES_TO_UNIT':
                    G.add_edge(source_id, target_id,
                              relation='RELATES_TO_UNIT',
                              weight=rel.get('weight', 1.0))
        
        return G
    
    def _create_intersection_layout(self, G):
        """为交集图创建专门的布局"""
        
        # 按节点类型分层
        pos = {}
        
        # 获取不同类型的节点
        project_nodes = [n for n, d in G.nodes(data=True) if d.get('type') == 'PROJECT']
        unit_nodes = [n for n, d in G.nodes(data=True) if d.get('type') == 'UNIT']
        skill_nodes = [n for n, d in G.nodes(data=True) if d.get('type') == 'OVERLAP_SKILL']
        
        # 项目在顶部中央
        if project_nodes:
            pos[project_nodes[0]] = (0, 3)
        
        # 技能在中间，水平分布
        for i, node in enumerate(skill_nodes):
            x = (i - len(skill_nodes)/2) * 2
            pos[node] = (x, 1.5)
        
        # 单元在底部，水平分布
        for i, node in enumerate(unit_nodes):
            x = (i - len(unit_nodes)/2) * 1.5
            pos[node] = (x, 0)
        
        return pos
    
    def generate_intersection_view(self, project_dir):
        """生成PD与UO交集视图"""
        
        print(f"🔍 分析项目: {os.path.basename(project_dir)}")
        
        # 加载数据
        entities, relationships, project_name = self._load_kg_data(project_dir)
        if not entities or not relationships:
            print(f"❌ 无法加载数据: {project_dir}")
            return {"status": "error", "message": "数据加载失败"}
        
        # 找出交集技能
        project_skills, unit_skills, intersection_skills = self._find_intersection_skills(entities, relationships)
        
        print(f"  📊 项目技能: {len(project_skills)} 个")
        print(f"  📚 单元技能: {len(unit_skills)} 个")
        print(f"  ⭐ 交集技能: {len(intersection_skills)} 个")
        
        if not intersection_skills:
            print(f"  ⚠️  没有发现PD与UO的技能交集")
            return {"status": "no_intersection", "message": "无技能交集"}
        
        # 创建交集图
        G = self._create_intersection_graph(entities, relationships, intersection_skills)
        
        if G.number_of_nodes() == 0:
            print(f"  ❌ 生成的交集图为空")
            return {"status": "empty_graph", "message": "交集图为空"}
        
        # 生成可视化
        output_file = os.path.join(project_dir, f"{os.path.basename(project_dir)}_intersection_view.png")
        success = self._visualize_intersection(G, project_name, intersection_skills, output_file)
        
        if success:
            print(f"  ✅ 交集视图生成: {output_file}")
            return {
                "status": "success", 
                "output_file": output_file,
                "intersection_count": len(intersection_skills),
                "intersection_skills": list(intersection_skills)
            }
        else:
            return {"status": "visualization_failed", "message": "可视化失败"}
    
    def _visualize_intersection(self, G, project_name, intersection_skills, output_file):
        """可视化交集图"""
        
        try:
            plt.figure(figsize=(14, 10))
            
            # 创建布局
            pos = self._create_intersection_layout(G)
            
            # 按类型绘制节点
            node_types = ['PROJECT', 'OVERLAP_SKILL', 'UNIT']
            
            for node_type in node_types:
                nodes = [n for n, d in G.nodes(data=True) if d.get('type') == node_type]
                if nodes:
                    color = self.colors.get(node_type, '#CCCCCC')
                    
                    if node_type == 'PROJECT':
                        size = 2000
                        alpha = 0.9
                        edge_color = 'black'
                        linewidth = 3
                    elif node_type == 'OVERLAP_SKILL':
                        size = 1500  # 交集技能稍大
                        alpha = 0.9
                        edge_color = 'red'  # 红色边框突出交集
                        linewidth = 3
                    else:  # UNIT
                        size = 1200
                        alpha = 0.8
                        edge_color = 'black'
                        linewidth = 2
                    
                    nx.draw_networkx_nodes(G, pos, nodelist=nodes,
                                         node_color=color, node_size=size,
                                         alpha=alpha, edgecolors=edge_color,
                                         linewidths=linewidth)
            
            # 按关系类型绘制边
            relation_types = ['REQUIRES_SKILL', 'TEACHES_SKILL', 'RELATES_TO_UNIT']
            
            for rel_type in relation_types:
                edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('relation') == rel_type]
                if edges:
                    color = self.relation_colors.get(rel_type, '#666666')
                    
                    if rel_type == 'REQUIRES_SKILL':
                        width = 3.0
                        style = '-'
                        alpha = 0.9
                    elif rel_type == 'TEACHES_SKILL':
                        width = 3.0
                        style = '-'
                        alpha = 0.9
                    else:  # RELATES_TO_UNIT
                        width = 2.0
                        style = '--'
                        alpha = 0.7
                    
                    nx.draw_networkx_edges(G, pos, edgelist=edges,
                                         edge_color=color, width=width,
                                         style=style, alpha=alpha,
                                         arrows=True, arrowsize=20,
                                         arrowstyle='->')
            
            # 添加标签
            labels = {}
            for node in G.nodes():
                name = G.nodes[node].get('name', node)
                # 限制标签长度
                if len(name) > 20:
                    name = name[:17] + "..."
                labels[node] = name
            
            nx.draw_networkx_labels(G, pos, labels, font_size=10, font_weight='bold')
            
            # 设置标题
            plt.title(f'PD ∩ UO 技能交集视图\n{project_name}\n交集技能: {len(intersection_skills)} 个', 
                     fontsize=16, fontweight='bold', pad=20)
            
            # 创建图例
            legend_elements = [
                plt.Line2D([0], [0], marker='o', color='w', 
                          markerfacecolor=self.colors['PROJECT'], markersize=15,
                          markeredgecolor='black', markeredgewidth=2, label='PROJECT'),
                plt.Line2D([0], [0], marker='o', color='w', 
                          markerfacecolor=self.colors['OVERLAP_SKILL'], markersize=12,
                          markeredgecolor='red', markeredgewidth=2, label='交集技能'),
                plt.Line2D([0], [0], marker='o', color='w', 
                          markerfacecolor=self.colors['UNIT'], markersize=10,
                          markeredgecolor='black', markeredgewidth=1, label='UNIT'),
                plt.Line2D([0], [0], color=self.relation_colors['REQUIRES_SKILL'], 
                          linewidth=3, label='项目需要'),
                plt.Line2D([0], [0], color=self.relation_colors['TEACHES_SKILL'], 
                          linewidth=3, label='单元教授'),
                plt.Line2D([0], [0], color=self.relation_colors['RELATES_TO_UNIT'], 
                          linewidth=2, linestyle='--', label='项目相关')
            ]
            
            plt.legend(handles=legend_elements, loc='upper right', 
                      bbox_to_anchor=(1, 1), fontsize=12)
            
            # 添加交集技能列表
            if intersection_skills:
                skills_text = "交集技能:\n" + "\n".join([f"• {skill}" for skill in sorted(intersection_skills)])
                plt.text(0.02, 0.02, skills_text, transform=plt.gca().transAxes,
                        fontsize=10, verticalalignment='bottom',
                        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            
            plt.axis('off')
            plt.tight_layout()
            
            # 保存图片
            plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            return True
            
        except Exception as e:
            print(f"❌ 可视化失败: {e}")
            plt.close()
            return False
    
    def generate_all_intersection_views(self):
        """为所有项目生成交集视图"""
        
        print("🔍 PD与UO交集分析器启动...")
        print("=" * 60)
        
        if not os.path.exists(self.kg_base_dir):
            print(f"❌ 目录不存在: {self.kg_base_dir}")
            return
        
        project_dirs = [d for d in os.listdir(self.kg_base_dir) 
                       if os.path.isdir(os.path.join(self.kg_base_dir, d)) and d.startswith('project_')]
        
        print(f"📁 找到 {len(project_dirs)} 个项目")
        
        results = []
        total_intersections = 0
        
        for i, project_dir in enumerate(project_dirs, 1):
            project_path = os.path.join(self.kg_base_dir, project_dir)
            print(f"\n[{i}/{len(project_dirs)}] 处理: {project_dir}")
            
            result = self.generate_intersection_view(project_path)
            results.append(result)
            
            if result["status"] == "success":
                total_intersections += result["intersection_count"]
        
        # 生成总结报告
        success_count = sum(1 for r in results if r["status"] == "success")
        no_intersection_count = sum(1 for r in results if r["status"] == "no_intersection")
        
        print(f"\n📊 PD与UO交集分析完成!")
        print(f"  成功生成: {success_count}/{len(project_dirs)} 个交集视图")
        print(f"  无交集项目: {no_intersection_count} 个")
        print(f"  总交集技能: {total_intersections} 个")
        print(f"  平均每项目: {total_intersections/success_count:.1f} 个交集技能" if success_count > 0 else "")
        
        # 保存总结报告
        summary = {
            "total_projects": len(project_dirs),
            "successful_intersections": success_count,
            "no_intersection_projects": no_intersection_count,
            "total_intersection_skills": total_intersections,
            "avg_intersection_per_project": total_intersections/success_count if success_count > 0 else 0,
            "detailed_results": results
        }
        
        summary_file = os.path.join(self.kg_base_dir, "intersection_analysis_summary.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"  📄 总结报告: {summary_file}")

def main():
    """主函数"""
    print("🔍 PD与UO交集知识图谱可视化器")
    print("=" * 60)
    print("📋 功能: 只显示项目描述(PD)与单元大纲(UO)的技能交集")
    print("🎯 输出: 简化的交集视图，突出共同技能")
    print("=" * 60)
    
    viewer = PDUOIntersectionViewer()
    viewer.generate_all_intersection_views()
    
    print("\n🎉 PD与UO交集分析完成!")

if __name__ == "__main__":
    main()








