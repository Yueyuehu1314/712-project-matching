#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清洁知识图谱信息提取代理
从项目描述(PD)和单元大纲(UO)构建清洁的知识图谱

规则:
1. 实体: PROJECT, UNIT, SKILL/TECHNOLOGY
2. 关系: requires, teaches, belongs_to
3. 约束: 避免星型爆炸，过滤泛化术语，合并同义词，Top-K相关技能
"""

import os
import json
import re
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
from typing import Dict, List, Set, Optional, Any, Tuple
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict

@dataclass 
class CleanEntity:
    """清洁实体"""
    id: str
    name: str
    entity_type: str  # PROJECT, UNIT, SKILL, TECHNOLOGY, PROGRAM
    relevance_score: float = 1.0
    properties: Dict[str, Any] = None

@dataclass
class CleanRelation:
    """清洁关系"""
    source_id: str
    target_id: str
    relation_type: str  # requires, teaches, belongs_to
    confidence: float = 1.0
    properties: Dict[str, Any] = None

class CleanKGExtractor:
    """清洁知识图谱提取器"""
    
    def __init__(self):
        # 同义词映射表
        self.skill_synonyms = {
            'machine learning': ['ml', 'machine learning', 'artificial intelligence', 'ai', 'deep learning'],
            'web development': ['web dev', 'web development', 'web programming', 'frontend', 'backend'],
            'data science': ['data science', 'data analytics', 'data analysis', 'big data'],
            'cybersecurity': ['cyber security', 'cybersecurity', 'information security', 'network security'],
            'database': ['database', 'db', 'database management', 'sql'],
            'programming': ['programming', 'coding', 'software development', 'development'],
            'networking': ['networking', 'network', 'tcp/ip', 'computer networks'],
            'cloud computing': ['cloud', 'cloud computing', 'aws', 'azure', 'gcp'],
            'mobile development': ['mobile', 'mobile dev', 'ios', 'android', 'app development'],
            'business analysis': ['business analysis', 'ba', 'business analytics', 'requirements analysis'],
            'project management': ['project management', 'pm', 'agile', 'scrum'],
            'user experience': ['ux', 'user experience', 'ui/ux', 'interface design']
        }
        
        # 过滤掉的泛化术语
        self.generic_terms = {
            'computer', 'software', 'technology', 'system', 'application', 
            'development', 'programming', 'coding', 'technical', 'digital',
            'information', 'data', 'analysis', 'management', 'design'
        }
        
        # 单元代码模式
        self.unit_code_pattern = r'\b[A-Z]{3}\d{3}\b'
        
        # Top-K 技能数量
        self.top_k_skills = 5
        
        # 置信度阈值
        self.confidence_threshold = 0.5
    
    def normalize_skill_name(self, skill_name: str) -> Optional[str]:
        """标准化技能名称"""
        skill_lower = skill_name.lower().strip()
        
        # 过滤泛化术语
        if skill_lower in self.generic_terms:
            return None
        
        # 检查同义词映射
        for canonical, variants in self.skill_synonyms.items():
            if any(variant in skill_lower for variant in variants):
                return canonical
        
        # 过滤过短的术语
        if len(skill_lower) < 3:
            return None
            
        return skill_lower
    
    def extract_units_from_text(self, text: str) -> List[Tuple[str, str]]:
        """从文本中提取单元代码和名称"""
        units = []
        
        # 查找单元代码
        unit_codes = re.findall(self.unit_code_pattern, text)
        
        for code in set(unit_codes):  # 去重
            # 尝试从文本中找到对应的单元名称
            pattern = rf'{code}[^\n]*'
            matches = re.findall(pattern, text)
            
            if matches:
                full_text = matches[0]
                # 提取单元名称（去掉代码部分）
                name_part = re.sub(rf'^{code}\s*', '', full_text).strip()
                name = name_part[:50] if name_part else f"Unit {code}"
            else:
                name = f"Unit {code}"
            
            units.append((code, name))
        
        return units
    
    def extract_skills_from_project(self, project_text: str) -> List[Tuple[str, float]]:
        """从项目描述中提取技能和相关性分数"""
        skills_with_scores = []
        text_lower = project_text.lower()
        
        # 基于关键词权重的技能提取
        skill_weights = {
            'machine learning': ['machine learning', 'ml', 'deep learning', 'neural network', 'ai'],
            'web development': ['web', 'html', 'css', 'javascript', 'react', 'angular', 'vue'],
            'data science': ['data science', 'data mining', 'analytics', 'visualization', 'pandas'],
            'cybersecurity': ['security', 'encryption', 'firewall', 'vulnerability', 'attack'],
            'database': ['database', 'sql', 'mysql', 'postgresql', 'mongodb', 'nosql'],
            'networking': ['network', 'tcp/ip', 'wifi', 'routing', 'protocol'],
            'cloud computing': ['cloud', 'aws', 'azure', 'docker', 'kubernetes'],
            'mobile development': ['mobile', 'android', 'ios', 'app', 'smartphone'],
            'business analysis': ['business', 'requirements', 'stakeholder', 'process'],
            'programming': ['python', 'java', 'c++', 'programming', 'coding'],
            'project management': ['project management', 'agile', 'scrum', 'pm'],
            'user experience': ['ux', 'ui', 'user experience', 'interface', 'usability']
        }
        
        for skill, keywords in skill_weights.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    # 计算权重：基于关键词出现次数和位置
                    occurrences = text_lower.count(keyword)
                    score += occurrences * (1.0 if keyword == skill else 0.5)
            
            if score > 0:
                skills_with_scores.append((skill, min(score, 5.0)))  # 限制最大分数
        
        # 按分数排序并返回Top-K
        skills_with_scores.sort(key=lambda x: x[1], reverse=True)
        return skills_with_scores[:self.top_k_skills]
    
    def extract_skills_from_unit(self, unit_text: str, unit_code: str) -> List[Tuple[str, float]]:
        """从单元大纲中提取技能"""
        skills_with_scores = []
        text_lower = unit_text.lower()
        
        # 基于单元代码的技能映射（QUT课程体系）
        unit_skill_mapping = {
            'IFN': {  # Information Technology Faculty
                'machine learning': ['machine learning', 'ml', 'data mining', 'predictive'],
                'web development': ['web', 'html', 'css', 'javascript', 'frontend'],
                'database': ['database', 'sql', 'data management', 'query'],
                'programming': ['programming', 'coding', 'algorithm', 'software'],
                'networking': ['network', 'communication', 'protocol', 'internet'],
                'cybersecurity': ['security', 'cryptography', 'protection', 'privacy'],
                'data science': ['analytics', 'statistics', 'visualization', 'insight'],
                'business analysis': ['business', 'requirements', 'process', 'analysis'],
                'project management': ['project', 'management', 'planning', 'coordination'],
                'user experience': ['user', 'interface', 'design', 'interaction']
            }
        }
        
        # 获取单元前缀（如IFN, CAB等）
        unit_prefix = unit_code[:3] if len(unit_code) >= 3 else unit_code
        
        if unit_prefix in unit_skill_mapping:
            skill_keywords = unit_skill_mapping[unit_prefix]
            
            for skill, keywords in skill_keywords.items():
                score = 0
                for keyword in keywords:
                    if keyword in text_lower:
                        occurrences = text_lower.count(keyword)
                        score += occurrences * 0.8  # 单元技能权重稍低
                
                if score > 0:
                    skills_with_scores.append((skill, min(score, 3.0)))
        
        # 按分数排序并返回Top-K  
        skills_with_scores.sort(key=lambda x: x[1], reverse=True)
        return skills_with_scores[:self.top_k_skills]
    
    def extract_clean_kg(self, project_file: str, unit_dir: str = "unit_md") -> Tuple[List[CleanEntity], List[CleanRelation]]:
        """提取清洁的知识图谱"""
        
        entities = []
        relations = []
        
        # 1. 读取项目描述
        with open(project_file, 'r', encoding='utf-8') as f:
            project_content = f.read()
        
        project_name = os.path.splitext(os.path.basename(project_file))[0]
        project_title = self._extract_project_title(project_content)
        
        # 创建项目实体
        project_entity = CleanEntity(
            id=f"project_{project_name}",
            name=project_title,
            entity_type="PROJECT",
            relevance_score=1.0,
            properties={"description": project_content[:200]}
        )
        entities.append(project_entity)
        
        # 2. 从项目中提取技能
        project_skills = self.extract_skills_from_project(project_content)
        
        for skill_name, score in project_skills:
            if score >= self.confidence_threshold:
                skill_entity = CleanEntity(
                    id=f"skill_{skill_name.replace(' ', '_')}",
                    name=skill_name,
                    entity_type="SKILL",
                    relevance_score=score,
                    properties={"source": "project"}
                )
                entities.append(skill_entity)
                
                # 创建 PROJECT —requires→ SKILL 关系
                relation = CleanRelation(
                    source_id=project_entity.id,
                    target_id=skill_entity.id,
                    relation_type="requires",
                    confidence=score / 5.0,  # 标准化到[0,1]
                    properties={"extracted_from": "project_description"}
                )
                relations.append(relation)
        
        # 3. 读取单元大纲
        unit_files = []
        if os.path.exists(unit_dir):
            unit_files = [f for f in os.listdir(unit_dir) if f.endswith('.md')]
        
        for unit_file in unit_files:
            unit_path = os.path.join(unit_dir, unit_file)
            with open(unit_path, 'r', encoding='utf-8') as f:
                unit_content = f.read()
            
            # 提取单元信息
            units_in_file = self.extract_units_from_text(unit_content)
            
            for unit_code, unit_name in units_in_file:
                # 创建单元实体
                unit_entity = CleanEntity(
                    id=f"unit_{unit_code}",
                    name=f"{unit_code} {unit_name}",
                    entity_type="UNIT",
                    relevance_score=1.0,
                    properties={"code": unit_code, "full_name": unit_name}
                )
                entities.append(unit_entity)
                
                # 提取单元教授的技能
                unit_skills = self.extract_skills_from_unit(unit_content, unit_code)
                
                for skill_name, score in unit_skills:
                    if score >= self.confidence_threshold:
                        skill_id = f"skill_{skill_name.replace(' ', '_')}"
                        
                        # 检查技能实体是否已存在
                        existing_skill = next((e for e in entities if e.id == skill_id), None)
                        if not existing_skill:
                            skill_entity = CleanEntity(
                                id=skill_id,
                                name=skill_name,
                                entity_type="SKILL",
                                relevance_score=score,
                                properties={"source": "unit"}
                            )
                            entities.append(skill_entity)
                        else:
                            # 更新现有技能的相关性分数
                            existing_skill.relevance_score = max(existing_skill.relevance_score, score)
                        
                        # 创建 UNIT —teaches→ SKILL 关系
                        relation = CleanRelation(
                            source_id=unit_entity.id,
                            target_id=skill_id,
                            relation_type="teaches",
                            confidence=score / 3.0,  # 标准化到[0,1]
                            properties={"unit_code": unit_code}
                        )
                        relations.append(relation)
        
        # 4. 去重和清理
        entities = self._deduplicate_entities(entities)
        relations = self._filter_relations(relations, entities)
        
        return entities, relations
    
    def _extract_project_title(self, content: str) -> str:
        """提取项目标题"""
        lines = content.split('\n')
        for line in lines:
            if 'title' in line.lower() and '|' in line:
                parts = line.split('|')
                if len(parts) >= 3:
                    title = parts[-2].strip()
                    if title and len(title) > 3:
                        return title
        
        # 备选方案：返回第一行非空内容
        for line in lines:
            if line.strip() and not line.startswith('#'):
                return line.strip()[:50]
        
        return "Unknown Project"
    
    def _deduplicate_entities(self, entities: List[CleanEntity]) -> List[CleanEntity]:
        """去重实体"""
        seen_ids = set()
        unique_entities = []
        
        for entity in entities:
            if entity.id not in seen_ids:
                seen_ids.add(entity.id)
                unique_entities.append(entity)
        
        return unique_entities
    
    def _filter_relations(self, relations: List[CleanRelation], entities: List[CleanEntity]) -> List[CleanRelation]:
        """过滤关系"""
        entity_ids = {e.id for e in entities}
        
        valid_relations = []
        for relation in relations:
            # 确保关系的两端实体都存在
            if relation.source_id in entity_ids and relation.target_id in entity_ids:
                # 过滤低置信度关系
                if relation.confidence >= 0.3:
                    valid_relations.append(relation)
        
        return valid_relations
    
    def create_clean_visualization(self, entities: List[CleanEntity], relations: List[CleanRelation], 
                                 project_name: str, output_file: str):
        """创建清洁的知识图谱可视化"""
        
        try:
            # 创建NetworkX图
            G = nx.DiGraph()
            
            # 添加节点
            for entity in entities:
                G.add_node(entity.id, 
                          name=entity.name,
                          type=entity.entity_type,
                          score=entity.relevance_score)
            
            # 添加边
            for relation in relations:
                G.add_edge(relation.source_id, relation.target_id,
                          relation=relation.relation_type,
                          confidence=relation.confidence)
            
            # 创建可视化
            plt.figure(figsize=(14, 10))
            
            # 计算布局
            pos = nx.spring_layout(G, k=3, iterations=50, seed=42)
            
            # 定义颜色
            colors = {
                'PROJECT': '#FF6B6B',
                'UNIT': '#4ECDC4', 
                'SKILL': '#45B7D1',
                'TECHNOLOGY': '#96CEB4'
            }
            
            # 按类型绘制节点
            for node_type, color in colors.items():
                nodes = [n for n, d in G.nodes(data=True) if d.get('type') == node_type]
                if nodes:
                    node_sizes = [1500 if node_type == 'PROJECT' 
                                else 800 if node_type == 'UNIT'
                                else 600 for _ in nodes]
                    
                    nx.draw_networkx_nodes(G, pos, nodelist=nodes,
                                         node_color=color, node_size=node_sizes,
                                         alpha=0.8, edgecolors='black', linewidths=1)
            
            # 按关系类型绘制边
            requires_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('relation') == 'requires']
            teaches_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('relation') == 'teaches']
            
            if requires_edges:
                nx.draw_networkx_edges(G, pos, edgelist=requires_edges,
                                     edge_color='red', width=2, alpha=0.7, arrows=True, arrowsize=15)
            
            if teaches_edges:
                nx.draw_networkx_edges(G, pos, edgelist=teaches_edges,
                                     edge_color='blue', width=2, alpha=0.7, arrows=True, arrowsize=15)
            
            # 添加标签
            labels = {}
            for node in G.nodes():
                name = G.nodes[node].get('name', node)
                if len(name) > 20:
                    name = name[:17] + "..."
                labels[node] = name
            
            nx.draw_networkx_labels(G, pos, labels, font_size=9, font_weight='bold')
            
            # 设置标题和图例
            plt.title(f'Clean Knowledge Graph\n{project_name}', fontsize=14, fontweight='bold')
            
            # 创建图例
            legend_elements = [
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=colors['PROJECT'], 
                          markersize=15, label='PROJECT'),
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=colors['UNIT'], 
                          markersize=12, label='UNIT'),
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=colors['SKILL'], 
                          markersize=10, label='SKILL'),
                plt.Line2D([0], [0], color='red', linewidth=2, label='requires'),
                plt.Line2D([0], [0], color='blue', linewidth=2, label='teaches')
            ]
            
            plt.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0, 1))
            
            plt.axis('off')
            plt.tight_layout()
            
            # 保存图片
            plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            print(f"✅ 清洁知识图谱可视化生成: {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ 可视化生成失败: {e}")
            plt.close()
            return False
    
    def process_single_project(self, project_file: str, output_dir: str = None) -> bool:
        """处理单个项目"""
        
        project_name = os.path.splitext(os.path.basename(project_file))[0]
        print(f"\n🧠 处理项目: {project_name}")
        
        try:
            # 提取清洁KG
            entities, relations = self.extract_clean_kg(project_file)
            
            print(f"  📊 提取结果: {len(entities)} 实体, {len(relations)} 关系")
            
            # 设置输出目录
            if not output_dir:
                output_dir = f"clean_kg_output/{project_name}"
            os.makedirs(output_dir, exist_ok=True)
            
            # 保存实体数据
            entities_data = [asdict(e) for e in entities]
            with open(os.path.join(output_dir, f"{project_name}_clean_entities.json"), 'w', encoding='utf-8') as f:
                json.dump(entities_data, f, ensure_ascii=False, indent=2)
            
            # 保存关系数据
            relations_data = [asdict(r) for r in relations]
            with open(os.path.join(output_dir, f"{project_name}_clean_relations.json"), 'w', encoding='utf-8') as f:
                json.dump(relations_data, f, ensure_ascii=False, indent=2)
            
            # 生成可视化
            vis_file = os.path.join(output_dir, f"{project_name}_clean_kg.png")
            self.create_clean_visualization(entities, relations, project_name, vis_file)
            
            # 生成统计报告
            stats = {
                'project_name': project_name,
                'total_entities': len(entities),
                'total_relations': len(relations),
                'entity_types': Counter(e.entity_type for e in entities),
                'relation_types': Counter(r.relation_type for r in relations),
                'avg_confidence': sum(r.confidence for r in relations) / len(relations) if relations else 0,
                'top_skills': [e.name for e in sorted(entities, key=lambda x: x.relevance_score, reverse=True) 
                              if e.entity_type == 'SKILL'][:5]
            }
            
            with open(os.path.join(output_dir, f"{project_name}_clean_stats.json"), 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
            
            print(f"  ✅ 清洁KG生成完成: {output_dir}")
            return True
            
        except Exception as e:
            print(f"  ❌ 处理失败: {e}")
            return False
    
    def process_all_projects(self, project_dir: str = "project_md"):
        """处理所有项目"""
        
        print("🚀 清洁知识图谱信息提取代理启动...")
        print("=" * 60)
        
        if not os.path.exists(project_dir):
            print(f"❌ 项目目录不存在: {project_dir}")
            return
        
        project_files = [f for f in os.listdir(project_dir) if f.endswith('.md')]
        print(f"📁 找到 {len(project_files)} 个项目文件")
        
        success_count = 0
        for i, project_file in enumerate(project_files, 1):
            project_path = os.path.join(project_dir, project_file)
            print(f"\n[{i}/{len(project_files)}] 处理: {project_file}")
            
            if self.process_single_project(project_path):
                success_count += 1
        
        print(f"\n📊 清洁知识图谱提取完成!")
        print(f"  成功处理: {success_count}/{len(project_files)} 个项目")
        print(f"  成功率: {success_count/len(project_files)*100:.1f}%")
        print(f"  输出目录: clean_kg_output/")

def main():
    """主函数"""
    print("🧠 清洁知识图谱信息提取代理")
    print("=" * 60)
    print("规则:")
    print("• 实体: PROJECT, UNIT, SKILL/TECHNOLOGY") 
    print("• 关系: requires, teaches, belongs_to")
    print("• 约束: Top-K技能, 合并同义词, 过滤泛化术语")
    print("=" * 60)
    
    extractor = CleanKGExtractor()
    extractor.process_all_projects()
    
    print("\n🎉 清洁知识图谱提取完成!")

if __name__ == "__main__":
    main()





