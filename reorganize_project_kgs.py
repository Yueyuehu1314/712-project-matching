#!/usr/bin/env python3
"""
重新组织项目知识图谱文件结构，并补齐缺失的项目KG

功能:
1. 分析 data/processed/projects_md 目录下的所有项目文件
2. 检查 outputs/knowledge_graphs/three_layer_projects 中已有的KG
3. 为缺失的项目生成三层知识图谱
4. 将所有KG文件重新组织到独立的项目子目录中
"""

import os
import json
import glob
import shutil
from pathlib import Path
from typing import Dict, List, Set, Tuple
import re

# 导入现有的KG生成模块
import sys
sys.path.append(os.path.dirname(__file__))

from src.knowledge_graphs.three_layer_project_kg import ThreeLayerProjectKGGenerator


class ProjectKGReorganizer:
    """项目知识图谱重组器"""
    
    def __init__(self):
        self.project_md_dir = Path("data/processed/projects_md")
        self.kg_dir = Path("outputs/knowledge_graphs/three_layer_projects")
        self.new_kg_dir = Path("outputs/knowledge_graphs/projects")  # 新的组织结构
        
        self.kg_generator = ThreeLayerProjectKGGenerator(use_existing_weights=False)
        
    def extract_project_title_from_md(self, md_file: Path) -> str:
        """从markdown文件中提取项目标题"""
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 尝试多种方式提取标题
            lines = content.split('\n')
            
            # 方法1: 查找 "Project title" 字段
            for i, line in enumerate(lines):
                if 'project title' in line.lower():
                    # 检查后续几行
                    for j in range(i+1, min(i+5, len(lines))):
                        title = lines[j].strip('| ').strip()
                        if title and len(title) > 10:
                            return self._clean_title(title)
            
            # 方法2: 查找第一个 # 标题
            for line in lines:
                if line.startswith('# ') and len(line) > 3:
                    title = line[2:].strip()
                    if 'form' not in title.lower():  # 排除表单标题
                        return self._clean_title(title)
            
            # 方法3: 查找第一个 ## 标题
            for line in lines:
                if line.startswith('## ') and len(line) > 4:
                    title = line[3:].strip()
                    if len(title) > 10:
                        return self._clean_title(title)
            
            # 方法4: 从文件名推断
            filename = md_file.stem
            # 移除常见的前缀/后缀
            filename = re.sub(r'(IFN712|Project|Proposal|Template|_2025|_CS)', '', filename)
            filename = filename.strip('_- ')
            if filename:
                return self._clean_title(filename)
            
            # 方法5: 使用文件名作为备选
            return self._clean_title(md_file.stem)
            
        except Exception as e:
            print(f"  ⚠️  读取文件 {md_file.name} 时出错: {e}")
            return self._clean_title(md_file.stem)
    
    def _clean_title(self, title: str) -> str:
        """清理标题，生成合适的项目名称"""
        # 移除特殊字符
        title = re.sub(r'[^\w\s-]', '', title)
        # 替换空格为下划线
        title = re.sub(r'\s+', '_', title.strip())
        # 移除多余的下划线
        title = re.sub(r'_+', '_', title)
        # 限制长度
        if len(title) > 50:
            title = title[:50]
        return title.strip('_')
    
    def find_existing_kg_files(self, project_name: str) -> List[Path]:
        """查找现有的KG文件"""
        patterns = [
            f"{project_name}_entities.json",
            f"{project_name}_relationships.json",
            f"{project_name}_stats.json",
            f"{project_name}_kg.png"
        ]
        
        found_files = []
        for pattern in patterns:
            file_path = self.kg_dir / pattern
            if file_path.exists():
                found_files.append(file_path)
        
        return found_files
    
    def analyze_projects(self) -> Tuple[Dict, Dict]:
        """分析项目文件和现有KG的对应关系"""
        print("=" * 80)
        print("分析项目文件和知识图谱")
        print("=" * 80)
        print()
        
        # 1. 读取所有项目MD文件
        md_files = sorted(self.project_md_dir.glob("*.md"))
        print(f"📁 找到 {len(md_files)} 个项目 Markdown 文件")
        
        # 2. 读取所有现有的KG文件
        entity_files = sorted(self.kg_dir.glob("*_entities.json"))
        print(f"📊 找到 {len(entity_files)} 个知识图谱文件")
        print()
        
        # 3. 建立映射关系
        md_to_project = {}  # md_file -> project_name
        kg_projects = set()  # 已有KG的项目名称
        
        # 提取已有KG的项目名称
        for entity_file in entity_files:
            project_name = entity_file.stem.replace('_entities', '')
            if project_name:  # 排除空名称
                kg_projects.add(project_name)
        
        # 为每个MD文件确定项目名称
        print("项目映射关系:")
        print("-" * 80)
        for md_file in md_files:
            # 先尝试从文件名推断项目名称
            filename_based = self._clean_title(md_file.stem)
            
            # 检查是否已有对应的KG
            has_kg = filename_based in kg_projects
            
            md_to_project[md_file] = {
                'name': filename_based,
                'has_kg': has_kg,
                'title': self.extract_project_title_from_md(md_file)
            }
            
            status = "✅" if has_kg else "❌"
            print(f"{status} {md_file.name}")
            print(f"     → 项目名: {filename_based}")
            if not has_kg:
                print(f"     → 标题: {md_to_project[md_file]['title']}")
        
        print()
        print("-" * 80)
        
        # 统计
        missing = [k for k, v in md_to_project.items() if not v['has_kg']]
        print(f"\n📊 统计:")
        print(f"   • 总项目数: {len(md_files)}")
        print(f"   • 已有KG: {len(md_files) - len(missing)}")
        print(f"   • 缺失KG: {len(missing)}")
        
        if missing:
            print(f"\n❌ 缺失KG的项目:")
            for md_file in missing:
                print(f"   • {md_file.name}")
        
        print()
        
        return md_to_project, kg_projects
    
    def generate_missing_kgs(self, md_to_project: Dict) -> None:
        """为缺失的项目生成知识图谱"""
        missing = [(k, v) for k, v in md_to_project.items() if not v['has_kg']]
        
        if not missing:
            print("✅ 所有项目都已有知识图谱")
            return
        
        print("=" * 80)
        print(f"生成缺失的 {len(missing)} 个知识图谱")
        print("=" * 80)
        print()
        
        for md_file, info in missing:
            project_name = info['name']
            title = info['title']
            
            print(f"📝 处理项目: {md_file.name}")
            print(f"   项目名称: {project_name}")
            print(f"   项目标题: {title}")
            
            try:
                # 使用现有的生成器生成KG
                # generate_project_kg 会自动保存所有文件
                stats = self.kg_generator.generate_project_kg(
                    project_file=str(md_file),
                    output_dir=str(self.kg_dir)
                )
                
                if stats:
                    print(f"   ✅ 生成成功:")
                    print(f"      • Entities: {stats.get('entity_count', 0)}")
                    print(f"      • Relationships: {stats.get('relationship_count', 0)}")
                    print(f"      • Domains: {stats.get('domain_count', 0)}")
                    print(f"      • Skills: {stats.get('skill_count', 0)}")
                else:
                    print(f"   ⚠️  生成失败（无返回结果）")
                
            except Exception as e:
                print(f"   ❌ 生成失败: {e}")
                import traceback
                traceback.print_exc()
            
            print()
    
    def reorganize_directory_structure(self, md_to_project: Dict) -> None:
        """重新组织目录结构"""
        print("=" * 80)
        print("重新组织目录结构")
        print("=" * 80)
        print()
        
        # 创建新的根目录
        self.new_kg_dir.mkdir(parents=True, exist_ok=True)
        
        # 为每个项目创建子目录并移动文件
        for md_file, info in md_to_project.items():
            project_name = info['name']
            
            # 创建项目子目录
            project_dir = self.new_kg_dir / project_name
            project_dir.mkdir(exist_ok=True)
            
            print(f"📁 {project_name}/")
            
            # 查找并复制所有相关文件
            file_patterns = [
                f"{project_name}_entities.json",
                f"{project_name}_relationships.json",
                f"{project_name}_stats.json",
                f"{project_name}_kg.png"
            ]
            
            copied_count = 0
            for pattern in file_patterns:
                src_file = self.kg_dir / pattern
                if src_file.exists():
                    # 简化文件名（去掉项目名前缀）
                    simple_name = pattern.replace(f"{project_name}_", "")
                    dst_file = project_dir / simple_name
                    
                    shutil.copy2(src_file, dst_file)
                    print(f"   ✅ {simple_name}")
                    copied_count += 1
            
            if copied_count == 0:
                print(f"   ⚠️  未找到任何文件")
            
            # 复制原始MD文件作为参考
            src_md = md_file
            dst_md = project_dir / "project.md"
            shutil.copy2(src_md, dst_md)
            print(f"   ✅ project.md (原始提案)")
            
            print()
        
        print("-" * 80)
        print(f"✅ 重组完成！新目录: {self.new_kg_dir}")
        print()
    
    def run(self):
        """运行完整的重组流程"""
        print("\n")
        print("╔" + "=" * 78 + "╗")
        print("║" + " " * 20 + "项目知识图谱重组工具" + " " * 20 + "║")
        print("╚" + "=" * 78 + "╝")
        print()
        
        # Step 1: 分析现有项目
        md_to_project, kg_projects = self.analyze_projects()
        
        # Step 2: 生成缺失的KG
        self.generate_missing_kgs(md_to_project)
        
        # Step 3: 重新组织目录结构
        self.reorganize_directory_structure(md_to_project)
        
        print("=" * 80)
        print("🎉 全部完成！")
        print("=" * 80)
        print()
        print(f"新的项目知识图谱目录: {self.new_kg_dir}")
        print(f"每个项目都有独立的子目录，包含:")
        print(f"  • entities.json - 实体列表")
        print(f"  • relationships.json - 关系列表")
        print(f"  • stats.json - 统计信息")
        print(f"  • kg.png - 可视化图谱")
        print(f"  • project.md - 原始项目提案")
        print()


def main():
    reorganizer = ProjectKGReorganizer()
    reorganizer.run()


if __name__ == "__main__":
    main()

