#!/usr/bin/env python3
"""
单元测试: 知识图谱生成
"""

import unittest
import networkx as nx
from pathlib import Path


class TestKnowledgeGraphs(unittest.TestCase):
    """测试知识图谱生成功能"""
    
    def test_networkx_available(self):
        """测试networkx库是否可用"""
        G = nx.Graph()
        G.add_node("test")
        self.assertEqual(len(G.nodes()), 1)
    
    def test_graph_creation(self):
        """测试基本图创建"""
        G = nx.DiGraph()
        G.add_edge("Project", "Skill", relationship="requires")
        self.assertTrue(G.has_edge("Project", "Skill"))
        self.assertEqual(len(G.edges()), 1)
    
    def test_graph_visualization_libraries(self):
        """测试可视化库是否可用"""
        try:
            import matplotlib.pyplot as plt
            self.assertTrue(True, "matplotlib可用")
        except ImportError:
            self.fail("matplotlib未安装")


class TestBalancedKG(unittest.TestCase):
    """测试Balanced KG生成器"""
    
    def test_import_balanced_kg_generator(self):
        """测试是否能导入balanced_kg_generator"""
        try:
            from src.knowledge_graphs import balanced_kg_generator
            self.assertTrue(True, "balanced_kg_generator导入成功")
        except ImportError as e:
            self.fail(f"导入失败: {e}")


if __name__ == '__main__':
    unittest.main()

