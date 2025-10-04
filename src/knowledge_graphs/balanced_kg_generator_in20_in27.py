#!/usr/bin/env python3
"""
增强的平衡知识图谱生成器 - 融合 PD + IN20 + IN27
- 保留 Project Description 中的技能需求
- 整合 IN20 (Course) 和 IN27 (Master Program) 的支持
- 显示权重分数和多层次支持关系
"""

import os
import json
import re
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
from collections import Counter, defaultdict, OrderedDict
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, asdict
import math
from datetime import datetime

matplotlib.use('Agg')
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

@dataclass
class EnhancedKGNode:
    """增强的知识图谱节点"""
    id: str
    name: str
    type: str  # PROJECT, SKILL, UNIT, PROGRAM, MAJOR
    score: float = 0.0
    category: str = "core"  # supported, extended, core, dual_supported
    source: Optional[str] = None  # PD, IN20, IN27, or "IN20+IN27"
    prerequisites: Optional[List[str]] = None  # 前置课程列表
    full_name: Optional[str] = None  # 保留课程全名等信息

@dataclass
class EnhancedKGEdge:
    """增强的知识图谱边"""
    source: str
    target: str
    relation: str
    weight: float = 1.0
    category: str = "core"
    source_type: Optional[str] = None  # IN20, IN27, PD

class BalancedKGGeneratorIN20IN27:
    """融合 PD + IN20 + IN27 的平衡知识图谱生成器"""
    
    def __init__(self):
        # 技能同义词映射
        self.synonyms = {
            'ai': 'artificial intelligence',
            'ml': 'machine learning',
            'dl': 'deep learning',
            'data science': 'data analytics',
            'big data': 'data analytics',
            'visualization': 'data visualization',
            'mobile dev': 'mobile development',
            'app dev': 'mobile development',
            'web dev': 'web development',
            'cybersecurity': 'cyber security',
            'network': 'networking',
            'databases': 'database',
            'db': 'database',
            'iot': 'internet of things'
        }
        
        # IN27 数据
        self.in27_data = self._load_in27_data()

        # 优先级衰减系数（可根据需求调整）
        self.project_skill_priority_decay = 0.8   # 项目技能优先级递减系数
        self.skill_unit_priority_decay = 0.85      # 技能对应课程优先级递减系数
        
    def normalize_skill(self, skill: str) -> str:
        """标准化技能名称"""
        skill = skill.lower().strip()
        skill = re.sub(r'[^\w\s]', '', skill)
        skill = re.sub(r'\s+', ' ', skill)
        
        for short, full in self.synonyms.items():
            skill = re.sub(r'\b' + short + r'\b', full, skill)
        
        return skill
    
    def _load_in27_data(self) -> Dict:
        """加载 IN27 (Master of Data Analytics) 数据"""
        in27_path = "/Users/lynn/Documents/GitHub/ProjectMatching/data/processed/units_md/qut_IN27_44569.md"
        
        if not os.path.exists(in27_path):
            print("⚠️  IN27 文件不存在")
            return {}
        
        try:
            with open(in27_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取课程代码
            unit_codes = re.findall(r'\b([A-Z]{3}\d{3})\b', content)
            unit_codes_unique = sorted(set(unit_codes))
            
            # 提取 Major 信息
            majors = self._extract_majors_from_in27(content)
            
            # 提取每个 Unit 的前置课程
            unit_prerequisites = self._extract_unit_prerequisites(content)
            
            # 提取技能关键词
            skill_patterns = [
                r'data analytics?', r'data science', r'machine learning', r'deep learning',
                r'artificial intelligence', r'data visualization', r'big data',
                r'python', r'r programming', r'sql', r'database', r'statistics',
                r'programming', r'algorithms?', r'data mining', r'predictive analytics',
                r'cloud computing', r'distributed systems', r'data engineering'
            ]
            
            in27_skills = set()
            for pattern in skill_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    normalized = self.normalize_skill(matches[0])
                    in27_skills.add(normalized)
            
            print(f"✅ IN27 数据加载成功: {len(unit_codes_unique)} 课程, {len(in27_skills)} 技能")
            
            return {
                'units': unit_codes_unique,
                'skills': in27_skills,
                'content': content,
                'majors': majors,
                'unit_prerequisites': unit_prerequisites
            }
            
        except Exception as e:
            print(f"❌ 加载 IN27 失败: {e}")
            return {}
    
    def _extract_majors_from_in27(self, content: str) -> Dict[str, List[str]]:
        """从 IN27 文档中提取 Major 和其对应的 Units"""
        majors = {
            'Biomedical Data Science': [],
            'Computational Data Science': [],
            'Statistical Data Science': [],
            'No Major': []
        }
        
        # 提取每个 Major 的课程列表
        # 注意：文档中有两次出现，第二次才是实际的 Unit Options 内容
        # 所以我们使用 Unit Set 作为标记来匹配正确的部分
        major_patterns = {
            'Biomedical Data Science': r'Biomedical Data Science Major Unit Options\s+Unit Set.*?(?=Computational Data Science Major Unit Options)',
            'Computational Data Science': r'Computational Data Science Major Unit Options\s+Unit Set.*?(?=Statistical Data Science Major Unit Options)',
            'Statistical Data Science': r'Statistical Data Science Major Unit Options\s+Unit Set.*?(?=Master of Data Analytics Electives Lists)',
        }
        
        for major_name, pattern in major_patterns.items():
            matches = re.findall(pattern, content, re.DOTALL)
            if matches:
                # 从匹配的文本中提取课程代码
                unit_codes = re.findall(r'\b([A-Z]{3}\d{3})\b', matches[0])
                majors[major_name] = list(set(unit_codes))
        
        return majors
    
    def _extract_unit_prerequisites(self, content: str) -> Dict[str, List[str]]:
        """从 IN27 文档中提取每个 Unit 的前置课程"""
        prerequisites = {}
        
        # 查找所有 "Unit Code + Title + Pre-requisites" 部分
        # 格式：CAB401 Title\nPre-requisites\n(prereq text)\nCredit Points
        pattern = r'([A-Z]{3}\d{3})\s+[^\n]+\nPre-requisites\s*\n(.*?)(?=\nCredit Points|\nEquivalents|\nAnti-requisites|$)'
        
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        
        for unit_code, prereq_text in matches:
            # 从前置课程文本中提取课程代码
            prereq_codes = re.findall(r'\b([A-Z]{3}\d{3})\b', prereq_text)
            if prereq_codes:
                prerequisites[unit_code] = list(set(prereq_codes))
        
        return prerequisites
    
    def _extract_project_majors(self, project_name: str) -> List[str]:
        """从项目文档中提取适合的 Major"""
        project_path = f"/Users/lynn/Documents/GitHub/ProjectMatching/data/processed/projects_md/{project_name}.md"
        
        if not os.path.exists(project_path):
            return []
        
        try:
            with open(project_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 查找 "Information Technology major(s)" 行并获取后续行
            majors_text = ""
            in_major_section = False
            
            for i, line in enumerate(lines):
                if 'Information Technology major' in line:
                    in_major_section = True
                    # 提取当前行的内容
                    parts = line.split('|')
                    if len(parts) >= 3:
                        majors_text += parts[-2].strip() + " "
                    continue
                
                # 如果在 major 区域，继续收集直到遇到下一个分隔线
                if in_major_section:
                    if line.startswith('+') or line.startswith('|') and 'Project title' in line:
                        break
                    if '|' in line:
                        parts = line.split('|')
                        if len(parts) >= 3:
                            majors_text += parts[-2].strip() + " "
            
            if majors_text:
                # 按逗号分割
                majors = [m.strip() for m in majors_text.split(',') if m.strip()]
                
                # 标准化 major 名称
                standardized_majors = []
                for major in majors:
                    # 移除多余的空格
                    major = ' '.join(major.split())
                    if major and len(major) > 2:  # 排除单个字母
                        standardized_majors.append(major)
                
                return standardized_majors
            
            return []
            
        except Exception as e:
            print(f"⚠️  提取 Major 失败: {e}")
            return []
    
    def load_pd_data(self, project_name: str) -> List[Dict]:
        """加载 Project Description 技能数据"""
        pd_path = f"/Users/lynn/Documents/GitHub/ProjectMatching/outputs/knowledge_graphs/archive/clean_kg_output/{project_name}/{project_name}_clean_entities.json"
        
        if not os.path.exists(pd_path):
            return []
        
        try:
            with open(pd_path, 'r', encoding='utf-8') as f:
                entities = json.load(f)
            return [e for e in entities if e.get('entity_type') == 'SKILL']
        except:
            return []
    
    def load_pd_in20_data(self, project_name: str) -> Tuple[List[Dict], List[Dict]]:
        """加载 PD + IN20 数据"""
        in20_path = f"/Users/lynn/Documents/GitHub/ProjectMatching/outputs/knowledge_graphs/archive/complete_clean_kg_output/{project_name}/{project_name}_kg.json"
        
        if not os.path.exists(in20_path):
            return [], []
        
        try:
            with open(in20_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('nodes', []), data.get('edges', [])
        except:
            return [], []
    
    def get_project_title_from_md(self, project_name: str) -> str:
        """从项目md文件中提取真实标题"""
        md_path = f"/Users/lynn/Documents/GitHub/ProjectMatching/data/processed/projects_md/{project_name}.md"
        
        if not os.path.exists(md_path):
            return project_name  # 如果文件不存在，返回原名称
        
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 提取 "Project title" 行的内容（可能跨多行）
            title_parts = []
            in_title_section = False
            
            for i, line in enumerate(lines):
                if 'Project title' in line and '|' in line:
                    # 找到了 Project title 行
                    parts = line.split('|')
                    if len(parts) >= 3:
                        title_text = parts[-2].strip()
                        if title_text and title_text != 'Project title':
                            title_parts.append(title_text)
                    in_title_section = True
                elif in_title_section and '|' in line:
                    # 继续读取跨行的标题
                    parts = line.split('|')
                    if len(parts) >= 3:
                        title_text = parts[-2].strip()
                        # 如果遇到分隔线或下一个字段，停止
                        if title_text and not title_text.startswith('---') and not title_text.startswith('==='):
                            if title_text:  # 不为空
                                title_parts.append(title_text)
                        else:
                            break
                    else:
                        break
                elif in_title_section:
                    # 遇到非表格行，停止
                    break
            
            if title_parts:
                # 合并标题部分
                full_title = ' '.join(title_parts)
                # 清理标题，移除不适合文件名的字符
                clean_title = full_title.replace('/', '_').replace('\\', '_').replace(':', '_').replace('?', '').replace('*', '')
                return clean_title
            
            return project_name  # 如果没找到标题，返回原名称
        except Exception as e:
            print(f"⚠️ 读取项目标题失败: {e}")
            return project_name
    
    def create_enhanced_balanced_kg(self, project_name: str) -> Tuple[List[EnhancedKGNode], List[EnhancedKGEdge]]:
        """创建增强的平衡知识图谱 - 融合 PD + IN20 + IN27"""
        
        print(f"\n{'='*80}")
        print(f"🔄 创建增强知识图谱: {project_name}")
        print(f"{'='*80}")
        
        # 1. 加载三种数据源
        pd_skills = self.load_pd_data(project_name)
        in20_nodes, in20_edges = self.load_pd_in20_data(project_name)
        
        print(f"📊 数据统计:")
        print(f"   • PD 技能: {len(pd_skills)}")
        print(f"   • IN20 节点: {len(in20_nodes)}")
        print(f"   • IN20 边: {len(in20_edges)}")
        print(f"   • IN27 技能: {len(self.in27_data.get('skills', []))}")
        
        # 如果没有IN20数据，只使用PD
        if not in20_nodes:
            print("⚠️  没有IN20数据，仅使用PD创建KG")
            return self._create_pd_only_kg(project_name, pd_skills)
        
        # 2. 构建技能支持映射
        skill_support = self._build_skill_support_map(in20_nodes, in20_edges, pd_skills)
        skill_support = self._apply_project_skill_priority(skill_support)
        
        # 3. 创建节点
        enhanced_nodes = []
        
        # 3.1 项目节点
        project_node = EnhancedKGNode(
            id=f"project_{project_name}", 
            name=project_name, 
            type='PROJECT', 
            category="core",
            source="PD"
        )
        enhanced_nodes.append(project_node)
        
        # 3.2 技能节点 - 按支持度分类
        for skill_name, support_info in skill_support.items():
            in20_support = support_info['in20_support']
            in27_support = support_info['in27_support']
            
            # 确定类别和来源
            if in20_support and in27_support:
                category = "dual_supported"  # 双重支持
                source = "IN20+IN27"
                score = support_info['score'] * 1.3  # 双重支持加权
            elif in20_support:
                category = "supported"
                source = "IN20"
                score = support_info['score'] * 1.0
            elif in27_support:
                category = "supported"
                source = "IN27"
                score = support_info['score'] * 1.0
            else:
                category = "extended"
                source = "PD"
                score = support_info['score'] * 0.8
            
            skill_node = EnhancedKGNode(
                id=support_info['id'],
                name=skill_name,
                type='SKILL',
                score=min(score, 1.0),  # 限制最大值为1.0
                category=category,
                source=source
            )
            enhanced_nodes.append(skill_node)
        
        # 3.3 添加 MAJOR 节点（从 Project Description）
        project_majors = self._extract_project_majors(project_name)
        major_nodes_map = {}
        
        for major_name in project_majors:
            major_id = f"major_{major_name.lower().replace(' ', '_')}"
            major_node = EnhancedKGNode(
                id=major_id,
                name=major_name,
                type='MAJOR',
                score=1.0,
                category="core",
                source="PD"
            )
            enhanced_nodes.append(major_node)
            major_nodes_map[major_name] = major_id
        
        # 3.4 添加IN20中的Unit节点（移除PROGRAM节点）
        # 第一步：创建所有UNIT的映射（但先不添加到nodes）
        all_unit_nodes_map = {}  # 所有课程映射
        all_unit_prereqs_map = {}  # 所有课程的前置关系
        
        for node in in20_nodes:
            if node['type'] == 'UNIT':
                unit_id = node['id']
                unit_code = unit_id.replace('unit_', '') if unit_id.startswith('unit_') else unit_id
                unit_name_raw = node.get('name', unit_code)
                match = re.search(r'[A-Z]{3}\d{3}', unit_name_raw.upper())
                display_code = match.group(0) if match else unit_code
                prereqs = self.in27_data.get('unit_prerequisites', {}).get(unit_code, [])
                
                all_unit_nodes_map[unit_code] = {
                    'id': unit_id,
                    'name': display_code,
                    'full_name': unit_name_raw,
                    'prereqs': prereqs
                }
                all_unit_prereqs_map[unit_code] = prereqs
        
        # 第二步：稍后会在添加边之后，识别哪些UNIT是有价值的
        # 现在先保留空的unit_nodes_map，稍后填充
        unit_nodes_map = {}
        unit_prereqs_map = {}
        
        # 4. 创建边（分多个阶段）
        enhanced_edges = []
        
        # 4.1 项目->技能边
        for skill_name, support_info in skill_support.items():
            enhanced_edges.append(EnhancedKGEdge(
                source=project_node.id,
                target=support_info['id'],
                relation="REQUIRES_SKILL",
                weight=support_info['score'],
                category=support_info.get('category', 'extended'),
                source_type="PD"
            ))
        
        # 4.2 识别有价值的UNIT（连接到SKILL或MAJOR的UNIT）
        valuable_units = set()  # 存储有价值的UNIT代码
        
        # 4.2.1 从IN20边中找到连接到SKILL的UNIT
        for edge in in20_edges:
            source_id = edge['source']
            target_id = edge['target']
            
            source_code = source_id.replace('unit_', '') if source_id.startswith('unit_') else source_id
            
            # Unit -> SKILL 边
            if source_code in all_unit_nodes_map and target_id.startswith('skill_'):
                valuable_units.add(source_code)
        
        # 4.2.2 从IN27的Major数据中找到连接到MAJOR的UNIT
        in27_majors = self.in27_data.get('majors', {})
        major_mapping = {
            'Software Development': ['Computational Data Science'],
            'Computer Science': ['Computational Data Science', 'Statistical Data Science'],
            'Computer Science and Data Science': ['Computational Data Science', 'Statistical Data Science'],
            'Data Science': ['Statistical Data Science', 'Biomedical Data Science'],
            'Networks and cybersecurity': ['Computational Data Science'],
            'Networks and Cybersecurity': ['Computational Data Science'],
            'Business Analysis': ['Statistical Data Science'],
        }
        
        for major_name in major_nodes_map.keys():
            in27_major_names = major_mapping.get(major_name, [])
            for in27_major_name in in27_major_names:
                units = in27_majors.get(in27_major_name, [])
                for unit_code in units:
                    if unit_code in all_unit_nodes_map:
                        valuable_units.add(unit_code)
        
        # 4.2.3 从模糊匹配中找到的UNIT
        for skill_name, support_info in skill_support.items():
            matched_units = self._find_matching_units_for_skill(skill_name, in20_nodes, all_unit_nodes_map)
            for unit_code, _ in matched_units:
                valuable_units.add(unit_code)
        
        # 4.3 添加有价值UNIT的先修课程（递归添加）
        def add_unit_with_prerequisites(unit_code: str, depth: int = 0, max_depth: int = 3):
            """递归添加课程及其先修课程"""
            if depth > max_depth:  # 限制递归深度
                return
            
            if unit_code not in all_unit_nodes_map:
                return
            
            # 添加当前课程
            if unit_code not in unit_nodes_map:
                unit_info = all_unit_nodes_map[unit_code]
                unit_node = EnhancedKGNode(
                    id=unit_info['id'],
                    name=unit_info['name'],
                    type='UNIT',
                    score=1.0,
                    prerequisites=unit_info['prereqs'] if unit_info['prereqs'] else None,
                    full_name=unit_info.get('full_name')
                )
                enhanced_nodes.append(unit_node)
                unit_nodes_map[unit_code] = unit_info['id']
                unit_prereqs_map[unit_code] = unit_info['prereqs']
            
            # 递归添加先修课程
            prereqs = all_unit_prereqs_map.get(unit_code, [])
            for prereq_code in prereqs:
                add_unit_with_prerequisites(prereq_code, depth + 1, max_depth)
        
        # 添加所有有价值的UNIT及其先修课程
        print(f"\n🔍 识别到 {len(valuable_units)} 个有价值的UNIT（连接到技能或专业）")
        for unit_code in valuable_units:
            add_unit_with_prerequisites(unit_code)
        
        print(f"📦 最终保留 {len(unit_nodes_map)} 个UNIT（包含先修课程）")
        
        # 4.4 添加SKILL -> UNIT边
        skill_unit_mapping = {}
        
        for edge in in20_edges:
            source_id = edge['source']
            target_id = edge['target']
            source_code = source_id.replace('unit_', '') if source_id.startswith('unit_') else source_id
            
            # 只添加保留的UNIT的边
            if source_code in unit_nodes_map and target_id.startswith('skill_'):
                enhanced_edges.append(EnhancedKGEdge(
                    source=target_id,
                    target=unit_nodes_map[source_code],
                    relation="TAUGHT_IN",
                    weight=edge.get('weight', 1.0),
                    source_type="IN20"
                ))
                if target_id not in skill_unit_mapping:
                    skill_unit_mapping[target_id] = []
                skill_unit_mapping[target_id].append((unit_nodes_map[source_code], edge.get('weight', 1.0)))
        
        # 4.5 为还没有连到UNIT的技能，找到相关课程
        for skill_name, support_info in skill_support.items():
            skill_id = support_info['id']
            
            if skill_id not in skill_unit_mapping:
                matched_units = self._find_matching_units_for_skill(skill_name, in20_nodes, unit_nodes_map)
                source_type = "IN27" if support_info.get('in27_support') else "MATCHED"
                for unit_id, weight in matched_units:
                    enhanced_edges.append(EnhancedKGEdge(
                        source=skill_id,
                        target=unit_id,
                        relation="TAUGHT_IN",
                        weight=weight,
                        source_type=source_type
                    ))
        
        # 4.6 添加 PROJECT → MAJOR 边
        for major_name, major_id in major_nodes_map.items():
            enhanced_edges.append(EnhancedKGEdge(
                source=project_node.id,
                target=major_id,
                relation="SUITABLE_FOR_MAJOR",
                weight=1.0,
                category="core",
                source_type="PD"
            ))
        
        # 4.7 添加 MAJOR → UNIT 边（只添加保留的UNIT）
        for major_name, major_id in major_nodes_map.items():
            in27_major_names = major_mapping.get(major_name, [])
            
            major_units = set()
            for in27_major_name in in27_major_names:
                units = in27_majors.get(in27_major_name, [])
                major_units.update(units)
            
            # 只添加已保留的UNIT的边
            for unit_code in major_units:
                if unit_code in unit_nodes_map:
                    enhanced_edges.append(EnhancedKGEdge(
                        source=major_id,
                        target=unit_nodes_map[unit_code],
                        relation="REQUIRES_UNIT",
                        weight=1.0,
                        source_type="IN27"
                    ))
        
        # 4.8 添加UNIT之间的前置课程关系（只添加保留的UNIT）
        for unit_id, prereqs in unit_prereqs_map.items():
            if unit_id in unit_nodes_map:
                for prereq_id in prereqs:
                    if prereq_id in unit_nodes_map:
                        enhanced_edges.append(EnhancedKGEdge(
                            source=unit_nodes_map[prereq_id],
                            target=unit_nodes_map[unit_id],
                            relation="PREREQUISITE_FOR",
                            weight=1.0,
                            source_type="IN27"
                        ))

        # 根据技能优先级调整课程边权重
        self._apply_skill_unit_priority(enhanced_edges)

        print(f"\n✅ KG 构建完成:")
        print(f"   • 节点: {len(enhanced_nodes)}")
        print(f"   • 边: {len(enhanced_edges)}")
        print(f"   • Majors: {len(major_nodes_map)}")
        print(f"   • 双重支持技能: {sum(1 for n in enhanced_nodes if n.category == 'dual_supported')}")
        print(f"   • IN20支持技能: {sum(1 for n in enhanced_nodes if n.source == 'IN20')}")
        print(f"   • IN27支持技能: {sum(1 for n in enhanced_nodes if n.source == 'IN27')}")
        print(f"   • Units with Prerequisites: {sum(1 for n in enhanced_nodes if n.type == 'UNIT' and n.prerequisites)}")
        
        return enhanced_nodes, enhanced_edges
    
    def _find_matching_units_for_skill(self, skill_name: str, in20_nodes: List[Dict], 
                                       unit_nodes_map: Dict) -> List[Tuple[str, float]]:
        """为技能找到匹配的课程（基于关键词匹配）
        
        Args:
            skill_name: 技能名称
            in20_nodes: IN20节点列表
            unit_nodes_map: 可以是 all_unit_nodes_map (返回unit_code) 或 unit_nodes_map (返回unit_id)
        
        Returns:
            如果unit_nodes_map是all_unit_nodes_map: List[(unit_code, weight)]
            如果unit_nodes_map是unit_nodes_map: List[(unit_id, weight)]
        """
        matches = []
        skill_keywords = {
            'database': ['database', 'data'],
            'programming': ['programming', 'software', 'development', 'python', 'java', 'algorithm'],
            'mobile development': ['mobile', 'app', 'android', 'ios', 'web', 'rapid'],
            'web development': ['web', 'internet', 'html', 'css', 'rapid', 'development'],
            'networking': ['network', 'internet', 'communication', 'security', 'cloud'],
            'user experience': ['user', 'ux', 'ui', 'design', 'interaction', 'centred'],
        }
        
        # 获取技能的关键词
        keywords = skill_keywords.get(skill_name.lower(), [skill_name.lower()])
        
        # 在Unit名称中搜索关键词
        for node in in20_nodes:
            if node['type'] == 'UNIT':
                unit_id = node['id']
                unit_code = unit_id.replace('unit_', '') if unit_id.startswith('unit_') else unit_id
                
                if unit_code in unit_nodes_map:
                    unit_name = node['name'].lower()
                    # 检查是否包含关键词
                    for keyword in keywords:
                        if keyword in unit_name:
                            # 检查是否是dict（all_unit_nodes_map）或str（unit_nodes_map）
                            if isinstance(unit_nodes_map[unit_code], dict):
                                # all_unit_nodes_map: 返回 unit_code
                                matches.append((unit_code, 5.0))
                            else:
                                # unit_nodes_map: 返回 unit_id
                                matches.append((unit_nodes_map[unit_code], 5.0))
                            break
        
        # 限制匹配数量（最多5个课程）
        return matches[:5]
    
    def _build_skill_support_map(self, in20_nodes: List[Dict], in20_edges: List[Dict], 
                                  pd_skills: List[Dict]) -> Dict[str, Dict]:
        """构建技能支持映射 - 整合 IN20 和 IN27"""

        skill_map = {}
        
        # 1. 从 IN20 数据提取技能
        in20_skills = {}
        for node in in20_nodes:
            if node['type'] == 'SKILL':
                normalized_name = self.normalize_skill(node['name'])
                in20_skills[normalized_name] = node
        
        # 2. 从 PD 数据提取技能
        pd_skill_names = set()
        for skill in pd_skills:
            normalized_name = self.normalize_skill(skill['name'])
            pd_skill_names.add(normalized_name)
            
            if normalized_name not in skill_map:
                skill_map[normalized_name] = {
                    'id': skill['id'],
                    'original_name': skill['name'],
                    'score': skill.get('relevance_score', 0.5),
                    'in20_support': False,
                    'in27_support': False,
                    'category': 'extended'
                }
        
        # 3. 标记 IN20 支持
        for skill_name in list(skill_map.keys()):
            if skill_name in in20_skills:
                skill_map[skill_name]['in20_support'] = True
                skill_map[skill_name]['category'] = 'supported'
        
        # 4. 标记 IN27 支持
        in27_skills = self.in27_data.get('skills', set())
        for skill_name in list(skill_map.keys()):
            # 模糊匹配
            for in27_skill in in27_skills:
                if skill_name in in27_skill or in27_skill in skill_name:
                    skill_map[skill_name]['in27_support'] = True
                    if skill_map[skill_name]['in20_support']:
                        skill_map[skill_name]['category'] = 'dual_supported'
                    else:
                        skill_map[skill_name]['category'] = 'supported'
                    break

        return skill_map

    def _apply_project_skill_priority(self, skill_support: Dict[str, Dict]) -> Dict[str, Dict]:
        """根据优先级重新排序并缩放项目技能权重"""

        if not skill_support:
            return skill_support

        sorted_items = sorted(
            skill_support.items(),
            key=lambda item: item[1].get('score', 0),
            reverse=True
        )

        prioritized = OrderedDict()
        for rank, (skill_name, info) in enumerate(sorted_items):
            base_score = info.get('score', 0)
            # 记录原始分数，便于调试或后续使用
            info['original_score'] = base_score
            factor = self.project_skill_priority_decay ** rank
            info['priority_rank'] = rank + 1
            info['priority_factor'] = factor
            info['score'] = base_score * factor
            prioritized[skill_name] = info

        return prioritized

    def _apply_skill_unit_priority(self, edges: List[EnhancedKGEdge]) -> None:
        """按技能对课程进行优先级缩放，保持权重递减"""

        skill_edge_map: Dict[str, List[Tuple[int, EnhancedKGEdge, float]]] = {}

        for idx, edge in enumerate(edges):
            if edge.relation == 'TAUGHT_IN' and edge.source.startswith('skill_'):
                skill_edge_map.setdefault(edge.source, []).append((idx, edge, edge.weight))

        for edge_list in skill_edge_map.values():
            edge_list.sort(key=lambda item: item[2], reverse=True)
            for rank, (idx, edge, original_weight) in enumerate(edge_list):
                factor = self.skill_unit_priority_decay ** rank
                new_weight = round(original_weight * factor, 2)
                edge.original_weight = original_weight  # 记录原始权重便于调试
                edge.priority_rank = rank + 1
                edge.priority_factor = factor
                edge.weight = new_weight
    
    def _create_pd_only_kg(self, project_name: str, pd_skills: List[Dict]) -> Tuple[List[EnhancedKGNode], List[EnhancedKGEdge]]:
        """为只有PD数据的项目创建KG"""
        if not pd_skills:
            return [], []
        
        nodes = []
        edges = []
        
        # 项目节点
        project_node = EnhancedKGNode(
            id=f"project_{project_name}", 
            name=project_name, 
            type='PROJECT', 
            category="core",
            source="PD"
        )
        nodes.append(project_node)
        
        # 技能节点（取前8个）
        top_skills = sorted(pd_skills, key=lambda x: x.get('relevance_score', 0), reverse=True)[:8]
        
        for skill in top_skills:
            normalized_name = self.normalize_skill(skill['name'])
            
            # 检查 IN27 支持
            in27_support = any(
                normalized_name in in27_skill or in27_skill in normalized_name
                for in27_skill in self.in27_data.get('skills', set())
            )
            
            skill_node = EnhancedKGNode(
                id=skill['id'],
                name=skill['name'],
                type='SKILL',
                score=skill.get('relevance_score', 0.5),
                category="supported" if in27_support else "extended",
                source="IN27" if in27_support else "PD"
            )
            nodes.append(skill_node)
            
            # 项目->技能边
            edges.append(EnhancedKGEdge(
                source=project_node.id,
                target=skill_node.id,
                relation="REQUIRES_SKILL",
                weight=skill.get('relevance_score', 0.5),
                category="supported" if in27_support else "extended",
                source_type="IN27" if in27_support else "PD"
            ))
        
        return nodes, edges
    
    def create_enhanced_visualization(self, nodes: List[EnhancedKGNode], edges: List[EnhancedKGEdge],
                                     project_name: str, output_path: str, show_edge_weights: bool = True):
        """创建增强的可视化 - 放射状三层布局：PROJECT -> SKILL -> UNIT（移除PROGRAM）"""
        
        # 过滤掉PROGRAM节点
        filtered_nodes = [n for n in nodes if n.type != 'PROGRAM']
        filtered_edges = [e for e in edges if e.relation != 'BELONGS_TO']
        
        G = nx.DiGraph()
        
        # 添加过滤后的节点
        for node in filtered_nodes:
            G.add_node(node.id, **asdict(node))
        
        # 添加过滤后的边
        for edge in filtered_edges:
            if edge.source in G.nodes and edge.target in G.nodes:
                G.add_edge(edge.source, edge.target, **asdict(edge))
        
        # 创建放射状圆环布局（三层）
        pos = self._create_radial_3layer_layout(G, filtered_nodes)
        
        # 创建画布（缩小尺寸以更紧凑）
        plt.figure(figsize=(20, 20))
        plt.clf()
        
        # === 节点样式 ===
        node_colors = []
        node_sizes = []
        
        for node_id in G.nodes():
            node = G.nodes[node_id]
            node_type = node['type']
            category = node.get('category', 'core')
            source = node.get('source', None)
            
            if node_type == 'PROJECT':
                node_colors.append('#FF6B6B')  # 粉红色 - 项目中心
                node_sizes.append(6000)
            elif node_type == 'MAJOR':
                node_colors.append('#FFA07A')  # 浅橙色 - Major
                node_sizes.append(4000)
            elif node_type == 'SKILL':
                if category == 'dual_supported':
                    node_colors.append('#26de81')  # 鲜绿色 - 双重支持
                elif source == 'IN20':
                    node_colors.append('#4ECDC4')  # 青色 - IN20支持
                elif source == 'IN27':
                    node_colors.append('#9b59b6')  # 紫色 - IN27支持
                else:
                    node_colors.append('#FFB347')  # 橙色 - PD扩展
                node_sizes.append(3000)
            elif node_type == 'UNIT':
                node_colors.append('#FFD93D')  # 黄色 - 课程单元
                node_sizes.append(2000)
        
        # === 绘制边 - 按关系类型分层绘制 ===
        
        # 1. 先绘制前置课程关系（UNIT之间）
        prereq_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('relation') == 'PREREQUISITE_FOR']
        if prereq_edges:
            nx.draw_networkx_edges(
                G, pos, edgelist=prereq_edges,
                edge_color='#B8B8B8',  # 灰色
                width=1.5,
                alpha=0.4,
                style='--',
                arrows=True,
                arrowsize=12,
                arrowstyle='->',
                connectionstyle="arc3,rad=0.15"
            )
        
        # 2. 绘制 PROJECT → MAJOR 关系
        project_major_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('relation') == 'SUITABLE_FOR_MAJOR']
        if project_major_edges:
            nx.draw_networkx_edges(
                G, pos, edgelist=project_major_edges,
                edge_color='#FF6B6B',  # 红色
                width=3.5,
                alpha=0.8,
                style='-',
                arrows=True,
                arrowsize=20,
                arrowstyle='->',
                connectionstyle="arc3,rad=0.1"
            )
        
        # 3. 绘制 MAJOR → UNIT 关系
        major_unit_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('relation') == 'REQUIRES_UNIT']
        if major_unit_edges:
            nx.draw_networkx_edges(
                G, pos, edgelist=major_unit_edges,
                edge_color='#FFA07A',  # 浅橙色
                width=2,
                alpha=0.5,
                style='-',
                arrows=True,
                arrowsize=15,
                arrowstyle='->',
                connectionstyle="arc3,rad=0.05"
            )
        
        # 4. 绘制SKILL -> UNIT关系
        taught_in_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('relation') == 'TAUGHT_IN']
        if taught_in_edges:
            nx.draw_networkx_edges(
                G, pos, edgelist=taught_in_edges,
                edge_color='#45B7D1',  # 青色
                width=2,
                alpha=0.6,
                style='-',
                arrows=True,
                arrowsize=15,
                arrowstyle='->',
                connectionstyle="arc3,rad=0.05"
            )
        
        # 5. 绘制PROJECT -> SKILL关系（按类别）
        edge_styles = {
            'dual_supported': {'color': '#26de81', 'width': 4, 'alpha': 0.9, 'style': '-'},
            'supported': {'color': '#45B7D1', 'width': 3, 'alpha': 0.8, 'style': '-'},
            'extended': {'color': '#FFA502', 'width': 2.5, 'alpha': 0.7, 'style': '--'},
            'core': {'color': '#95a5a6', 'width': 2, 'alpha': 0.6, 'style': '-'}
        }
        
        for category in ['core', 'extended', 'supported', 'dual_supported']:
            edges_of_category = [(u, v) for u, v, d in G.edges(data=True) 
                                if d.get('relation') == 'REQUIRES_SKILL' and d.get('category', 'core') == category]
            
            if edges_of_category:
                style = edge_styles.get(category, edge_styles['core'])
                nx.draw_networkx_edges(
                    G, pos, edgelist=edges_of_category,
                    edge_color=style['color'],
                    width=style['width'],
                    alpha=style['alpha'],
                    style=style['style'],
                    arrows=True,
                    arrowsize=20,
                    arrowstyle='->',
                    connectionstyle="arc3,rad=0.08"
                )
        
        # === 绘制节点 ===
        nx.draw_networkx_nodes(
            G, pos, node_color=node_colors, node_size=node_sizes,
            alpha=0.9, linewidths=3, edgecolors='white'
        )
        
        # === 绘制节点标签 ===
        labels = self._create_smart_labels(G, nodes)
        
        font_configs = {
            'PROJECT': {'size': 16, 'weight': 'bold', 'color': 'darkred'},
            'MAJOR': {'size': 13, 'weight': 'bold', 'color': 'darkorange'},
            'SKILL': {'size': 14, 'weight': 'bold', 'color': 'black'},
            'UNIT': {'size': 7, 'weight': 'normal', 'color': 'darkblue'}
        }
        
        for node_type, config in font_configs.items():
            type_labels = {nid: label for nid, label in labels.items() 
                          if G.nodes[nid]['type'] == node_type}
            if type_labels:
                nx.draw_networkx_labels(
                    G, pos, type_labels,
                    font_size=config['size'],
                    font_weight=config['weight'],
                    font_color=config['color']
                )
        
        # === 绘制边权重标签 ===
        if show_edge_weights:
            edge_labels = {}
            for u, v, d in G.edges(data=True):
                weight = d.get('weight', 1.0)
                relation = d.get('relation', '')
                
                # 显示项目->技能的权重
                if relation == 'REQUIRES_SKILL':
                    edge_labels[(u, v)] = f"{weight:.1f}"
                # 显示技能->课程的权重（标记为IN20或IN27）
                elif relation == 'TAUGHT_IN':
                    source_type = d.get('source_type', '')
                    if weight >= 5.0:  # 高权重
                        edge_labels[(u, v)] = f"{weight:.0f}"
            
            if edge_labels:
                nx.draw_networkx_edge_labels(
                    G, pos, edge_labels,
                    font_size=7,
                    font_color='#c0392b',
                    font_weight='bold',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='white', 
                             edgecolor='lightgray', alpha=0.8)
                )
        
        # === 图例 ===
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#FF6B6B',
                      markersize=18, label='PROJECT', markeredgecolor='white', markeredgewidth=2.5),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#FFA07A',
                      markersize=17, label='MAJOR', markeredgecolor='white', markeredgewidth=2.5),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#26de81',
                      markersize=16, label='SKILL (IN20+IN27 Supported)', markeredgecolor='white', markeredgewidth=2.5),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#4ECDC4',
                      markersize=16, label='SKILL (IN20 Supported)', markeredgecolor='white', markeredgewidth=2.5),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#9b59b6',
                      markersize=16, label='SKILL (IN27 Supported)', markeredgecolor='white', markeredgewidth=2.5),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#FFB347',
                      markersize=16, label='SKILL (PD Extended)', markeredgecolor='white', markeredgewidth=2.5),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#FFD93D',
                      markersize=14, label='UNIT (Course)', markeredgecolor='white', markeredgewidth=2),
            plt.Line2D([0], [0], color='#FF6B6B', linewidth=3.5, label='PROJECT → MAJOR'),
            plt.Line2D([0], [0], color='#FFA07A', linewidth=2, label='MAJOR → UNIT'),
            plt.Line2D([0], [0], color='#26de81', linewidth=4, label='PROJECT → SKILL (Dual Support)'),
            plt.Line2D([0], [0], color='#45B7D1', linewidth=2, label='SKILL → UNIT (Taught In)'),
            plt.Line2D([0], [0], color='#B8B8B8', linewidth=1.5, linestyle='--', label='UNIT → UNIT (Prerequisite)')
        ]
        
        plt.legend(handles=legend_elements, loc='upper right', fontsize=10,
                  framealpha=0.95, edgecolor='gray', fancybox=True, shadow=True)
        
        # 标题和样式
        plt.title(f'Project Knowledge Graph (3-Layer Radial)\n{project_name}',
                 fontsize=16, fontweight='bold', pad=20)
        plt.axis('off')
        plt.tight_layout()
        
        # 保存
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"📊 可视化已保存: {output_path}")
    
    
    def _create_smart_labels(self, G: nx.DiGraph, nodes: List[EnhancedKGNode]) -> Dict[str, str]:
        """创建智能标签"""
        labels = {}
        
        for node in nodes:
            name = node.name
            
            if node.type == 'SKILL':
                # 技能节点添加支持标记
                if node.category == 'dual_supported':
                    labels[node.id] = f"✓✓ {name}"
                elif node.category == 'supported':
                    labels[node.id] = f"✓ {name}"
                else:
                    labels[node.id] = f"+ {name}"
            elif node.type == 'UNIT':
                # UNIT节点只显示课程代码（前6-7个字符）
                # 例如 "IFN701 Credit Points24" -> "IFN701"
                import re
                match = re.match(r'([A-Z]{2,4}\d{3})', name)
                if match:
                    labels[node.id] = match.group(1)
                else:
                    labels[node.id] = name[:7]  # 如果没有匹配到代码，取前7个字符
            else:
                labels[node.id] = name
        
        return labels
    
    def create_simplified_visualization(self, nodes: List[EnhancedKGNode], edges: List[EnhancedKGEdge],
                                       project_name: str, output_path: str):
        """创建简化的可视化 - 只显示项目和技能，类似Python课程图"""
        
        # 过滤节点：只保留PROJECT和SKILL
        filtered_nodes = [n for n in nodes if n.type in ['PROJECT', 'SKILL']]
        
        # 过滤边：只保留项目->技能的边
        filtered_edges = [e for e in edges if e.source.startswith('project_') and e.target.startswith('skill_')]
        
        G = nx.DiGraph()
        
        # 添加节点
        for node in filtered_nodes:
            G.add_node(node.id, **asdict(node))
        
        # 添加边
        for edge in filtered_edges:
            if edge.source in G.nodes and edge.target in G.nodes:
                G.add_edge(edge.source, edge.target, **asdict(edge))
        
        # 创建布局 - 径向布局
        pos = self._create_radial_layout(G, filtered_nodes)
        
        # 创建画布
        plt.figure(figsize=(16, 12))
        plt.clf()
        
        # === 节点样式 ===
        node_colors = []
        node_sizes = []
        
        for node_id in G.nodes():
            node = G.nodes[node_id]
            node_type = node['type']
            category = node.get('category', 'core')
            source = node.get('source', None)
            
            if node_type == 'PROJECT':
                node_colors.append('#FF6B6B')  # 红色
                node_sizes.append(6000)
            elif node_type == 'SKILL':
                if category == 'dual_supported':
                    node_colors.append('#26de81')  # 鲜绿色 - 双重支持
                elif source == 'IN27':
                    node_colors.append('#9b59b6')  # 紫色 - IN27支持
                elif category == 'supported':
                    node_colors.append('#4ECDC4')  # 青色 - IN20支持
                else:
                    node_colors.append('#FFB347')  # 橙色 - PD扩展
                node_sizes.append(4000)
        
        # === 绘制边 ===
        edge_styles = {
            'dual_supported': {'color': '#26de81', 'width': 4, 'alpha': 0.9},
            'supported': {'color': '#4ECDC4', 'width': 3, 'alpha': 0.8},
            'extended': {'color': '#FFB347', 'width': 2.5, 'alpha': 0.7}
        }
        
        for category in ['extended', 'supported', 'dual_supported']:
            edges_of_category = []
            for u, v, d in G.edges(data=True):
                if d.get('category', 'core') == category:
                    edges_of_category.append((u, v))
            
            if edges_of_category:
                style = edge_styles.get(category, edge_styles['extended'])
                nx.draw_networkx_edges(
                    G, pos, edgelist=edges_of_category,
                    edge_color=style['color'],
                    width=style['width'],
                    alpha=style['alpha'],
                    arrows=False,  # 不显示箭头，更简洁
                    connectionstyle="arc3,rad=0"
                )
        
        # === 绘制节点 ===
        nx.draw_networkx_nodes(
            G, pos, node_color=node_colors, node_size=node_sizes,
            alpha=0.9, linewidths=3, edgecolors='white'
        )
        
        # === 绘制标签 ===
        labels = {}
        for node in filtered_nodes:
            if node.type == 'SKILL':
                if node.category == 'dual_supported':
                    labels[node.id] = f"✓✓ {node.name}"
                elif node.category == 'supported':
                    labels[node.id] = f"✓ {node.name}"
                else:
                    labels[node.id] = f"+ {node.name}"
            else:
                labels[node.id] = node.name
        
        nx.draw_networkx_labels(
            G, pos, labels,
            font_size=12,
            font_weight='bold',
            font_color='black'
        )
        
        # === 绘制边权重 ===
        edge_labels = {}
        for u, v, d in G.edges(data=True):
            weight = d.get('weight', 1.0)
            if 0.5 <= weight < 1.0:
                edge_labels[(u, v)] = f"{weight:.2f}"
        
        if edge_labels:
            nx.draw_networkx_edge_labels(
                G, pos, edge_labels,
                font_size=9,
                font_color='#c0392b',
                font_weight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                         edgecolor='lightgray', alpha=0.8)
            )
        
        # === 图例 ===
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#FF6B6B',
                      markersize=18, label='PROJECT', markeredgecolor='white', markeredgewidth=2.5),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#26de81',
                      markersize=16, label='SKILL (IN20+IN27 Supported)', markeredgecolor='white', markeredgewidth=2.5),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#4ECDC4',
                      markersize=16, label='SKILL (IN20 Supported)', markeredgecolor='white', markeredgewidth=2.5),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#9b59b6',
                      markersize=16, label='SKILL (IN27 Supported)', markeredgecolor='white', markeredgewidth=2.5),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#FFB347',
                      markersize=16, label='SKILL (PD Extended)', markeredgecolor='white', markeredgewidth=2.5),
            plt.Line2D([0], [0], color='#26de81', linewidth=4, label='Dual Support (IN20+IN27)'),
            plt.Line2D([0], [0], color='#4ECDC4', linewidth=3, label='IN20 Support'),
            plt.Line2D([0], [0], color='#FFB347', linewidth=2.5, label='PD Extended Need')
        ]
        
        plt.legend(handles=legend_elements, loc='upper right', fontsize=11,
                  framealpha=0.95, edgecolor='gray', fancybox=True, shadow=True)
        
        # 标题
        plt.title(f'Simplified Knowledge Graph: PD + IN20 + IN27\n{project_name}',
                 fontsize=18, fontweight='bold', pad=25)
        plt.axis('off')
        plt.tight_layout()
        
        # 保存
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"📊 简化可视化已保存: {output_path}")
    
    def _create_radial_layout(self, G: nx.DiGraph, nodes: List[EnhancedKGNode]) -> Dict:
        """创建径向圆环布局 - 项目在中心，技能均匀围绕"""
        pos = {}
        
        # 找到项目节点和技能节点
        project_node = None
        skill_nodes = []
        for node in nodes:
            if node.type == 'PROJECT':
                project_node = node
            elif node.type == 'SKILL':
                skill_nodes.append(node)
        
        if not project_node:
            return nx.spring_layout(G)
        
        # 项目在中心 (0, 0)
        pos[project_node.id] = (0, 0)
        
        # 技能按圆形均匀分布
        n = len(skill_nodes)
        if n > 0:
            # 根据技能数量调整半径，确保不重叠
            radius = max(6, n * 0.5)  # 技能越多，半径越大
            
            for i, skill in enumerate(skill_nodes):
                # 从正上方开始，顺时针分布
                angle = 2 * math.pi * i / n - math.pi / 2
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)
                pos[skill.id] = (x, y)
        
        return pos
    
    def _create_radial_3layer_layout(self, G: nx.DiGraph, nodes: List[EnhancedKGNode]) -> Dict[str, Tuple[float, float]]:
        """创建自然的力导向放射状布局：使用 spring_layout 但固定中心节点"""
        
        # 1. 按类型分组节点
        project_nodes = [n for n in nodes if n.type == 'PROJECT']
        major_nodes = [n for n in nodes if n.type == 'MAJOR']
        skill_nodes = [n for n in nodes if n.type == 'SKILL']
        unit_nodes = [n for n in nodes if n.type == 'UNIT']
        
        if not project_nodes:
            return nx.spring_layout(G, k=2, iterations=50)
        
        project_node = project_nodes[0]
        
        # 2. 使用分层固定位置的spring layout
        # 固定PROJECT在中心
        fixed_positions = {project_node.id: (0, 0)}
        
        # 固定MAJOR在第二层（可选）
        n_majors = len(major_nodes)
        if n_majors > 0:
            radius_major = 2.5
            for i, major in enumerate(major_nodes):
                angle = 2 * math.pi * i / n_majors
                x = radius_major * math.cos(angle)
                y = radius_major * math.sin(angle)
                fixed_positions[major.id] = (x, y)
        
        # 3. 使用 spring_layout，但固定中心和MAJOR节点
        # 这会让SKILL和UNIT自然分散，形成放射状
        pos = nx.spring_layout(
            G,
            pos=fixed_positions,  # 初始位置
            fixed=list(fixed_positions.keys()),  # 固定这些节点
            k=1.5,  # 节点间理想距离
            iterations=100,  # 迭代次数
            seed=42  # 随机种子，保证可重复性
        )
        
        # 4. 后处理：调整SKILL和UNIT的位置，使它们更符合层次结构
        # 按距离中心的远近分层
        for skill in skill_nodes:
            if skill.id in pos:
                x, y = pos[skill.id]
                distance = math.sqrt(x**2 + y**2)
                
                # 确保SKILL至少在radius_skill的距离上
                min_radius_skill = 4.5
                if distance < min_radius_skill:
                    # 拉远一点
                    angle = math.atan2(y, x)
                    pos[skill.id] = (min_radius_skill * math.cos(angle), 
                                    min_radius_skill * math.sin(angle))
        
        for unit in unit_nodes:
            if unit.id in pos:
                x, y = pos[unit.id]
                distance = math.sqrt(x**2 + y**2)
                
                # 确保UNIT在最外层
                min_radius_unit = 7.0
                if distance < min_radius_unit:
                    # 拉到最外层
                    angle = math.atan2(y, x)
                    pos[unit.id] = (min_radius_unit * math.cos(angle),
                                   min_radius_unit * math.sin(angle))
        
        return pos
    
    def _create_hierarchical_layout(self, G: nx.DiGraph, nodes: List[EnhancedKGNode]) -> Dict[str, Tuple[float, float]]:
        """创建层级布局：PROJECT -> SKILL -> UNIT -> PROGRAM (从左到右)"""
        pos = {}
        
        # 1. 按类型分组节点
        project_nodes = [n for n in nodes if n.type == 'PROJECT']
        skill_nodes = [n for n in nodes if n.type == 'SKILL']
        unit_nodes = [n for n in nodes if n.type == 'UNIT']
        program_nodes = [n for n in nodes if n.type == 'PROGRAM']
        
        # 2. 层级X坐标
        layer_x = {
            'PROJECT': 0,
            'SKILL': 4,
            'UNIT': 8,
            'PROGRAM': 12
        }
        
        # 3. 布置PROJECT节点（左侧）
        if project_nodes:
            project_node = project_nodes[0]
            pos[project_node.id] = (layer_x['PROJECT'], 0)
        
        # 4. 布置SKILL节点（第二列）
        n_skills = len(skill_nodes)
        if n_skills > 0:
            y_start = -(n_skills - 1) / 2 * 2
            for i, skill in enumerate(skill_nodes):
                pos[skill.id] = (layer_x['SKILL'], y_start + i * 2)
        
        # 5. 布置UNIT节点（第三列）
        n_units = len(unit_nodes)
        if n_units > 0:
            y_start = -(n_units - 1) / 2 * 1.5
            for i, unit in enumerate(unit_nodes):
                pos[unit.id] = (layer_x['UNIT'], y_start + i * 1.5)
        
        # 6. 布置PROGRAM节点（最右侧）
        n_programs = len(program_nodes)
        if n_programs > 0:
            y_start = -(n_programs - 1) / 2 * 3
            for i, program in enumerate(program_nodes):
                pos[program.id] = (layer_x['PROGRAM'], y_start + i * 3)
        
        return pos
    
    def generate_for_project(self, project_name: str, output_dir: str = None):
        """为单个项目生成增强知识图谱"""
        
        # 获取项目真实标题
        project_title = self.get_project_title_from_md(project_name)
        print(f"📋 项目标题: {project_title}")
        
        if output_dir is None:
            output_dir = "/Users/lynn/Documents/GitHub/ProjectMatching/outputs/knowledge_graphs/enhanced_in20_in27"
        
        # 使用真实标题作为文件夹名
        project_output_dir = os.path.join(output_dir, project_title)
        os.makedirs(project_output_dir, exist_ok=True)
        
        # 创建知识图谱
        nodes, edges = self.create_enhanced_balanced_kg(project_name)
        
        if not nodes:
            print(f"❌ 无法为 {project_name} 创建知识图谱")
            return
        
        # 保存JSON
        kg_data = {
            'project': project_name,
            'project_title': project_title,
            'nodes': [asdict(n) for n in nodes],
            'edges': [asdict(e) for e in edges],
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'generator': 'BalancedKGGeneratorIN20IN27',
                'sources': ['PD', 'IN20', 'IN27']
            }
        }
        
        # 使用真实标题命名文件
        json_path = os.path.join(project_output_dir, f"{project_title}_enhanced_kg.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(kg_data, f, indent=2, ensure_ascii=False)
        print(f"💾 JSON 已保存: {json_path}")
        
        # 创建完整可视化
        img_path_full = os.path.join(project_output_dir, f"{project_title}_enhanced_kg_full.png")
        self.create_enhanced_visualization(nodes, edges, project_title, img_path_full, show_edge_weights=True)
        
        # 创建简化可视化（只显示技能和关键关系）
        img_path_simple = os.path.join(project_output_dir, f"{project_title}_enhanced_kg_simple.png")
        self.create_simplified_visualization(nodes, edges, project_title, img_path_simple)
        
        print(f"✅ 完成: {project_title}\n")


def main():
    """批量生成所有项目的增强知识图谱"""
    
    generator = BalancedKGGeneratorIN20IN27()
    
    # 自动扫描 projects_md 目录下的所有项目
    import glob
    project_md_dir = "/Users/lynn/Documents/GitHub/ProjectMatching/data/processed/projects_md"
    project_files = glob.glob(os.path.join(project_md_dir, "*.md"))
    
    # 提取项目名称（去掉 .md 扩展名）
    projects = [os.path.splitext(os.path.basename(f))[0] for f in project_files]
    projects.sort()  # 排序
    
    print("=" * 80)
    print("🚀 开始批量生成增强知识图谱 (PD + IN20 + IN27)")
    print(f"📁 找到 {len(projects)} 个项目")
    print("=" * 80)
    
    success_count = 0
    failed_projects = []
    
    for i, project in enumerate(projects, 1):
        print(f"\n[{i}/{len(projects)}] 处理: {project}")
        try:
            generator.generate_for_project(project)
            success_count += 1
        except Exception as e:
            print(f"❌ 失败: {project} - {e}")
            import traceback
            traceback.print_exc()
            failed_projects.append(project)
    
    print("\n" + "=" * 80)
    print("📊 生成完成统计")
    print("=" * 80)
    print(f"✅ 成功: {success_count}/{len(projects)}")
    print(f"❌ 失败: {len(failed_projects)}")
    if failed_projects:
        print(f"失败项目:")
        for fp in failed_projects:
            print(f"  • {fp}")
    print("=" * 80)


if __name__ == "__main__":
    main()
