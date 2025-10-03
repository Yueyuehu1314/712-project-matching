#!/usr/bin/env python3
"""
测试增强的知识图谱生成器 (PD + IN20 + IN27)
"""

from src.knowledge_graphs.balanced_kg_generator_in20_in27 import BalancedKGGeneratorIN20IN27

def test_single_project():
    """测试单个项目生成"""
    print("=" * 80)
    print("🧪 测试单个项目: IFN712 Project 13-1")
    print("=" * 80)
    
    generator = BalancedKGGeneratorIN20IN27()
    generator.generate_for_project('IFN712 Project 13-1')
    
    print("\n✅ 测试完成！")
    print("📁 输出目录: outputs/knowledge_graphs/enhanced_in20_in27/IFN712 Project 13-1/")
    print("   包含:")
    print("   • IFN712 Project 13-1_enhanced_kg.json         - JSON数据")
    print("   • IFN712 Project 13-1_enhanced_kg_full.png     - 完整可视化")
    print("   • IFN712 Project 13-1_enhanced_kg_simple.png   - 简化可视化（推荐查看）")

if __name__ == "__main__":
    test_single_project()



