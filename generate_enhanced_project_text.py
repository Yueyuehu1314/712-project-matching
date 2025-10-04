#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成融合了Unit Outline的Project文本
用于 Method 1b (PD+UO Embedding) 实验
"""

import os
import glob

def generate_enhanced_project_texts():
    """生成 PD+UO 融合文本"""
    
    project_dir = 'data/processed/projects_md'
    unit_dir = 'data/processed/units_md'
    output_dir = 'data/processed/enhanced_projects_md'
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 读取Unit文件
    unit_files = glob.glob(f'{unit_dir}/*.md')
    unit_contents = {}
    
    for unit_file in unit_files:
        unit_name = os.path.basename(unit_file).replace('.md', '')
        with open(unit_file, 'r', encoding='utf-8') as f:
            unit_contents[unit_name] = f.read()
    
    print(f"📚 已加载 {len(unit_contents)} 个Unit文件:")
    for name in unit_contents.keys():
        print(f"   - {name}")
    print()
    
    # 处理每个项目
    projects = glob.glob(f'{project_dir}/*.md')
    
    for proj_path in projects:
        proj_name = os.path.basename(proj_path).replace('.md', '')
        
        # 读取project内容
        with open(proj_path, 'r', encoding='utf-8') as f:
            proj_content = f.read()
        
        # 融合内容
        enhanced_content = f"""# {proj_name}

## Project Description

{proj_content}

---

"""
        
        # 添加所有Unit内容
        for unit_name, unit_content in unit_contents.items():
            enhanced_content += f"""## Related Unit Outline: {unit_name}

{unit_content}

---

"""
        
        # 保存
        output_path = f'{output_dir}/{proj_name}.md'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(enhanced_content)
        
        print(f'✅ Generated: {proj_name}.md')
    
    print()
    print(f"🎉 完成！共生成 {len(projects)} 个 PD+UO 融合文本")
    print(f"📂 输出目录: {output_dir}")


if __name__ == '__main__':
    generate_enhanced_project_texts()

