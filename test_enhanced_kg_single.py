#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试单个学生的增强知识图谱生成
"""

from src.knowledge_graphs.enhanced_student_kg import EnhancedStudentKGBuilder
import os

def main():
    # 初始化
    in20_path = "outputs/knowledge_graphs/enhanced_in20_in27/AI-Based Human Activity Recognition Using WiFi Channel State Information/AI-Based Human Activity Recognition Using WiFi Channel State Information_enhanced_kg.json"
    
    builder = EnhancedStudentKGBuilder(
        in20_data_path=in20_path if os.path.exists(in20_path) else None
    )
    
    # 测试单个学生
    student_file = "data/processed/profiles_md/IFN712_proposal_conversational_agent_prosody/n00114716_Finley_Thompson.md"
    
    print("=" * 60)
    print("测试增强版学生知识图谱生成器")
    print("=" * 60)
    
    stats = builder.create_enhanced_student_kg(
        student_file=student_file,
        output_dir="outputs/knowledge_graphs/individual/enhanced_student_kg"
    )
    
    print("\n" + "=" * 60)
    print("✅ 完成！")
    print("=" * 60)
    print(f"统计信息: {stats}")
    
    # 打开生成的图片
    import subprocess
    png_file = "outputs/knowledge_graphs/individual/enhanced_student_kg/student_n00114716_Finley_Thompson_kg.png"
    if os.path.exists(png_file):
        subprocess.run(["open", png_file])

if __name__ == "__main__":
    main()






