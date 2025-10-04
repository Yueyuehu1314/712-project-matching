#!/usr/bin/env python3
"""
重新组织 outputs1/knowledge_graphs/three_layer_projects 的目录结构

功能：
1. 分析 outputs1/knowledge_graphs/three_layer_projects 中现有的 KG 文件
2. 为每个项目创建独立的子目录
3. 将相关的 JSON 和 PNG 文件移动到对应的项目目录
4. 复制原始的项目 MD 文件作为参考
"""

import os
import json
import glob
import shutil
from pathlib import Path
from typing import Dict, List
from collections import defaultdict


class KGReorganizer:
    """KG 文件重组器"""
    
    def __init__(self, source_dir: str, target_dir: str, projects_md_dir: str):
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        self.projects_md_dir = Path(projects_md_dir)
        
    def find_all_kg_projects(self) -> Dict[str, List[Path]]:
        """找到所有项目及其相关文件"""
        print("=" * 80)
        print("扫描现有的知识图谱文件")
        print("=" * 80)
        print()
        
        # 找到所有 entities 文件
        entity_files = sorted(self.source_dir.glob("*_entities.json"))
        print(f"📊 找到 {len(entity_files)} 个项目知识图谱")
        print()
        
        # 为每个项目收集所有相关文件
        project_files = defaultdict(list)
        
        for entity_file in entity_files:
            # 提取项目名称
            project_name = entity_file.stem.replace('_entities', '')
            
            if not project_name:  # 跳过空名称
                print(f"⚠️  跳过空名称项目: {entity_file}")
                continue
            
            # 查找所有相关文件
            file_patterns = [
                f"{project_name}_entities.json",
                f"{project_name}_relationships.json",
                f"{project_name}_stats.json",
                f"{project_name}_kg.png"
            ]
            
            for pattern in file_patterns:
                file_path = self.source_dir / pattern
                if file_path.exists():
                    project_files[project_name].append(file_path)
            
            # 显示找到的文件
            file_count = len(project_files[project_name])
            print(f"📁 {project_name}: {file_count} 个文件")
        
        print()
        print(f"✅ 总共找到 {len(project_files)} 个有效项目")
        print()
        
        return project_files
    
    def find_matching_md_file(self, project_name: str) -> Path:
        """根据项目名称找到匹配的 MD 文件"""
        # 尝试不同的匹配策略
        
        # 策略1: 直接读取 entities.json 查找原始文件路径
        entity_file = self.source_dir / f"{project_name}_entities.json"
        if entity_file.exists():
            with open(entity_file, 'r', encoding='utf-8') as f:
                entities = json.load(f)
            
            # 找到 PROJECT 类型的实体
            for entity in entities:
                if entity.get('entity_type') == 'PROJECT':
                    file_path = entity.get('properties', {}).get('file_path', '')
                    if file_path and os.path.exists(file_path):
                        return Path(file_path)
        
        # 策略2: 在 projects_md 目录中搜索匹配的文件
        # 这个策略作为备选，因为项目名可能与文件名不完全匹配
        all_md_files = list(self.projects_md_dir.glob("*.md"))
        
        # 尝试精确匹配
        for md_file in all_md_files:
            if md_file.stem.replace(' ', '_') == project_name:
                return md_file
        
        # 尝试模糊匹配（包含关系）
        project_name_lower = project_name.lower().replace('_', '')
        for md_file in all_md_files:
            file_name_lower = md_file.stem.lower().replace(' ', '').replace('_', '')
            if project_name_lower in file_name_lower or file_name_lower in project_name_lower:
                return md_file
        
        return None
    
    def reorganize_project_files(self, project_files: Dict[str, List[Path]]):
        """重新组织项目文件"""
        print("=" * 80)
        print("重新组织目录结构")
        print("=" * 80)
        print()
        
        # 创建目标目录
        self.target_dir.mkdir(parents=True, exist_ok=True)
        
        # 处理每个项目
        for project_name, files in sorted(project_files.items()):
            print(f"📁 {project_name}/")
            
            # 创建项目子目录
            project_dir = self.target_dir / project_name
            project_dir.mkdir(exist_ok=True)
            
            # 复制所有相关文件
            for src_file in files:
                # 简化文件名（移除项目名前缀）
                simple_name = src_file.name.replace(f"{project_name}_", "")
                dst_file = project_dir / simple_name
                
                shutil.copy2(src_file, dst_file)
                print(f"   ✅ {simple_name}")
            
            # 查找并复制原始 MD 文件
            md_file = self.find_matching_md_file(project_name)
            if md_file:
                dst_md = project_dir / "project.md"
                shutil.copy2(md_file, dst_md)
                print(f"   ✅ project.md (来源: {md_file.name})")
            else:
                print(f"   ⚠️  未找到匹配的 MD 文件")
            
            print()
        
        print("-" * 80)
        print(f"✅ 重组完成！新目录: {self.target_dir}")
        print()
    
    def generate_summary(self, project_files: Dict[str, List[Path]]):
        """生成重组总结"""
        print("=" * 80)
        print("重组总结")
        print("=" * 80)
        print()
        
        print(f"📊 统计信息:")
        print(f"   • 项目总数: {len(project_files)}")
        print(f"   • 源目录: {self.source_dir}")
        print(f"   • 目标目录: {self.target_dir}")
        print()
        
        print(f"📁 新目录结构:")
        print(f"   {self.target_dir}/")
        for project_name in sorted(project_files.keys())[:5]:
            print(f"   ├── {project_name}/")
            print(f"   │   ├── entities.json")
            print(f"   │   ├── relationships.json")
            print(f"   │   ├── stats.json")
            print(f"   │   ├── kg.png")
            print(f"   │   └── project.md")
        if len(project_files) > 5:
            print(f"   ├── ... ({len(project_files) - 5} 个更多项目)")
        print()
    
    def run(self):
        """运行完整的重组流程"""
        print("\n")
        print("╔" + "=" * 78 + "╗")
        print("║" + " " * 20 + "知识图谱目录重组工具" + " " * 18 + "║")
        print("╚" + "=" * 78 + "╝")
        print()
        
        # Step 1: 找到所有项目
        project_files = self.find_all_kg_projects()
        
        if not project_files:
            print("❌ 未找到任何项目文件")
            return
        
        # Step 2: 重新组织文件
        self.reorganize_project_files(project_files)
        
        # Step 3: 生成总结
        self.generate_summary(project_files)
        
        print("=" * 80)
        print("🎉 全部完成！")
        print("=" * 80)
        print()


def main():
    """主函数"""
    # 配置路径
    source_dir = "outputs1/knowledge_graphs/three_layer_projects"
    target_dir = "outputs1/knowledge_graphs/projects_organized"
    projects_md_dir = "data/processed/projects_md"
    
    # 检查源目录是否存在
    if not os.path.exists(source_dir):
        print(f"❌ 源目录不存在: {source_dir}")
        return
    
    # 运行重组
    reorganizer = KGReorganizer(source_dir, target_dir, projects_md_dir)
    reorganizer.run()


if __name__ == "__main__":
    main()

