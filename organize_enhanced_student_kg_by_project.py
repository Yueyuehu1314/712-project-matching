#!/usr/bin/env python3
"""
将 enhanced_student_kg 目录下的学生知识图谱按项目分组
"""

import os
import json
import shutil
from pathlib import Path
from collections import defaultdict

def extract_project_from_json(json_path: str) -> str:
    """从JSON文件中提取项目名称"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 从 STUDENT 实体的 file_path 中提取项目名称
        for entity in data.get('entities', []):
            if entity.get('entity_type') == 'STUDENT':
                file_path = entity.get('properties', {}).get('file_path', '')
                # file_path 格式: data/processed/profiles_md/PROJECT_NAME/student_file.md
                if file_path:
                    parts = file_path.split('/')
                    if len(parts) >= 4 and parts[2] == 'profiles_md':
                        return parts[3]
        
        return "Unknown_Project"
    except Exception as e:
        print(f"  ⚠️ 无法从 {json_path} 提取项目: {e}")
        return "Unknown_Project"

def organize_by_project(source_dir: str, target_dir: str):
    """按项目组织学生知识图谱文件"""
    
    source_path = Path(source_dir)
    target_path = Path(target_dir)
    
    if not source_path.exists():
        print(f"❌ 源目录不存在: {source_dir}")
        return
    
    # 创建目标目录
    target_path.mkdir(parents=True, exist_ok=True)
    
    # 收集所有JSON文件
    json_files = list(source_path.glob("*.json"))
    print(f"📊 找到 {len(json_files)} 个JSON文件")
    
    # 按项目分组
    project_files = defaultdict(list)
    
    for json_file in json_files:
        # 跳过空文件名的情况（student___enhanced_kg.json）
        if '___' in json_file.name:
            print(f"  ⏭️  跳过: {json_file.name}")
            continue
        
        # 提取项目名称
        project_name = extract_project_from_json(str(json_file))
        
        # 找到对应的PNG文件
        png_file = json_file.with_suffix('.png').with_name(
            json_file.name.replace('_enhanced_kg.json', '_kg.png')
        )
        
        project_files[project_name].append({
            'json': json_file,
            'png': png_file if png_file.exists() else None
        })
    
    # 统计信息
    print(f"\n📁 按项目分组统计:")
    for project_name, files in sorted(project_files.items()):
        print(f"  {project_name}: {len(files)} 个学生")
    
    # 复制文件到项目目录
    print(f"\n🚀 开始组织文件...")
    total_copied = 0
    
    for project_name, files in project_files.items():
        # 创建项目目录
        project_dir = target_path / project_name
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # 复制文件
        for file_info in files:
            # 复制JSON文件
            if file_info['json'].exists():
                target_json = project_dir / file_info['json'].name
                shutil.copy2(file_info['json'], target_json)
                total_copied += 1
            
            # 复制PNG文件
            if file_info['png'] and file_info['png'].exists():
                target_png = project_dir / file_info['png'].name
                shutil.copy2(file_info['png'], target_png)
                total_copied += 1
    
    print(f"\n✅ 完成! 共复制 {total_copied} 个文件")
    print(f"📂 目标目录: {target_path}")
    
    # 显示目录结构预览
    print(f"\n📋 目录结构预览:")
    for project_name in sorted(project_files.keys())[:5]:
        project_dir = target_path / project_name
        file_count = len(list(project_dir.glob("*")))
        print(f"  {project_name}/ ({file_count} 文件)")
    
    if len(project_files) > 5:
        print(f"  ... 还有 {len(project_files) - 5} 个项目目录")

def main():
    """主函数"""
    print("=" * 60)
    print("  按项目组织增强版学生知识图谱")
    print("=" * 60)
    
    # 设置路径
    source_dir = "outputs/knowledge_graphs/individual/enhanced_student_kg"
    target_dir = "outputs/knowledge_graphs/individual/enhanced_student_kg_by_project"
    
    # 执行组织
    organize_by_project(source_dir, target_dir)
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()






