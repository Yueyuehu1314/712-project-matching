#!/usr/bin/env python3
"""
单元测试: 文档转换器
"""

import unittest
import os
import tempfile
from pathlib import Path
from src.converters.document_converter import DocumentConverter


class TestDocumentConverter(unittest.TestCase):
    """测试DocumentConverter类"""
    
    def setUp(self):
        """测试前准备"""
        self.converter = DocumentConverter()
        self.test_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.converter)
        self.assertTrue(hasattr(self.converter, 'supported_extensions'))
        self.assertGreater(len(self.converter.supported_extensions), 0)
    
    def test_supported_formats(self):
        """测试支持的文件格式"""
        expected_formats = ['.pdf', '.docx', '.pptx', '.xlsx', '.txt']
        for fmt in expected_formats:
            self.assertIn(fmt, self.converter.supported_extensions)
    
    def test_base_directory(self):
        """测试基础目录设置"""
        custom_dir = Path('/tmp/test')
        converter = DocumentConverter(base_dir=str(custom_dir))
        self.assertEqual(converter.base_dir, custom_dir)


if __name__ == '__main__':
    unittest.main()

