#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按Project分类学生知识图谱文件

将 outputs/knowledge_graphs/individual/enhanced_student_kg/ 中的学生KG文件
按照学生所属的project分类到对应的project目录下
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List
import glob

class StudentKGOrganizer:
    """学生知识图谱文件组织器"""
    
    def __init__(
        self,
        kg_source_dir: str = "outputs/knowledge_graphs/individual/enhanced_student_kg",
        profile_dir: str = "data/processed/profiles_md",
        output_base_dir: str = "outputs/knowledge_graphs/individual/by_project"
    ):
        self.kg_source_dir = kg_source_dir
        self.profile_dir = profile_dir
        self.output_base_dir = output_base_dir
        
        # 创建输出基础目录
        os.makedirs(self.output_base_dir, exist_ok=True)
    
    def _build_student_project_mapping(self) -> Dict[str, str]:
        """
        构建学生ID到项目的映射
        
        Returns:
            Dict[student_id, project_name]
        """
        student_to_project = {}
        
        # 遍历所有项目目录
        profile_path = Path(self.profile_dir)
        if not profile_path.exists():
            print(f"❌ Profile目录不存在: {self.profile_dir}")
            return student_to_project
        
        for project_dir in profile_path.iterdir():
            if not project_dir.is_dir():
                continue
            
            project_name = project_dir.name
            
            # 遍历该项目下的所有学生档案
            for student_file in project_dir.glob("*.md"):
                # 提取学生ID（文件名格式：nXXXXXXXX_Name.md）
                filename = student_file.stem  # 去掉.md
                if filename.startswith('n'):
                    student_id = filename.split('_')[0]  # 提取nXXXXXXXX
                    student_to_project[student_id] = project_name
        
        print(f"📚 构建学生-项目映射: {len(student_to_project)} 个学生")
        return student_to_project
    
    def organize_kg_files(self, copy_mode: bool = True) -> Dict[str, int]:
        """
        组织KG文件到对应的项目目录
        
        Args:
            copy_mode: True=复制文件, False=移动文件
        
        Returns:
            统计信息: {project_name: count}
        """
        # 构建映射
        student_to_project = self._build_student_project_mapping()
        
        if not student_to_project:
            print("❌ 没有找到学生-项目映射")
            return {}
        
        # 统计
        stats = {}
        organized_count = 0
        not_found_count = 0
        
        # 遍历所有KG文件
        kg_source_path = Path(self.kg_source_dir)
        if not kg_source_path.exists():
            print(f"❌ KG源目录不存在: {self.kg_source_dir}")
            return {}
        
        # 获取所有JSON文件（每个学生一个JSON和一个PNG）
        json_files = list(kg_source_path.glob("student_n*_enhanced_kg.json"))
        
        print(f"\n🔄 开始组织 {len(json_files)} 个学生的KG文件...")
        print(f"   模式: {'复制' if copy_mode else '移动'}")
        
        for json_file in json_files:
            # 提取学生ID
            filename = json_file.stem  # student_nXXXXXXXX_Name_enhanced_kg
            parts = filename.split('_')
            if len(parts) < 2:
                continue
            
            student_id = parts[1]  # nXXXXXXXX
            
            # 查找对应的项目
            project_name = student_to_project.get(student_id)
            
            if not project_name:
                not_found_count += 1
                print(f"  ⚠️  未找到项目: {student_id}")
                continue
            
            # 创建项目目录
            project_output_dir = Path(self.output_base_dir) / project_name
            project_output_dir.mkdir(parents=True, exist_ok=True)
            
            # 复制/移动JSON文件
            dest_json = project_output_dir / json_file.name
            if copy_mode:
                shutil.copy2(json_file, dest_json)
            else:
                shutil.move(str(json_file), str(dest_json))
            
            # 复制/移动对应的PNG文件
            png_file = json_file.with_name(json_file.name.replace('_enhanced_kg.json', '_kg.png'))
            if png_file.exists():
                dest_png = project_output_dir / png_file.name
                if copy_mode:
                    shutil.copy2(png_file, dest_png)
                else:
                    shutil.move(str(png_file), str(dest_png))
            
            # 统计
            stats[project_name] = stats.get(project_name, 0) + 1
            organized_count += 1
        
        # 打印统计
        print(f"\n{'='*60}")
        print(f"✅ 组织完成！")
        print(f"{'='*60}")
        print(f"  总学生数: {len(json_files)}")
        print(f"  成功组织: {organized_count}")
        print(f"  未找到项目: {not_found_count}")
        print(f"  项目数量: {len(stats)}")
        print(f"\n📊 各项目学生数量:")
        
        for project, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {project}: {count} 个学生")
        
        print(f"\n📁 输出目录: {self.output_base_dir}")
        
        return stats
    
    def verify_organization(self) -> None:
        """验证组织结果"""
        output_path = Path(self.output_base_dir)
        
        if not output_path.exists():
            print("❌ 输出目录不存在")
            return
        
        print(f"\n{'='*60}")
        print(f"🔍 验证组织结果")
        print(f"{'='*60}")
        
        total_json = 0
        total_png = 0
        
        for project_dir in sorted(output_path.iterdir()):
            if not project_dir.is_dir():
                continue
            
            json_count = len(list(project_dir.glob("*_enhanced_kg.json")))
            png_count = len(list(project_dir.glob("*_kg.png")))
            
            total_json += json_count
            total_png += png_count
            
            status = "✅" if json_count == png_count else "⚠️"
            print(f"{status} {project_dir.name}")
            print(f"     JSON: {json_count}, PNG: {png_count}")
        
        print(f"\n总计: {total_json} JSON, {total_png} PNG")


def main():
    """主函数"""
    print("="*60)
    print("学生知识图谱按Project组织工具")
    print("="*60)
    
    organizer = StudentKGOrganizer()
    
    # 组织文件（默认复制模式，保留原文件）
    stats = organizer.organize_kg_files(copy_mode=True)
    
    # 验证结果
    organizer.verify_organization()
    
    print("\n" + "="*60)
    print("✅ 完成！")
    print("="*60)


if __name__ == "__main__":
    main()




