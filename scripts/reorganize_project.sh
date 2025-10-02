#!/bin/bash
# 项目重组脚本
# 使用方法: bash scripts/reorganize_project.sh

set -e  # 遇到错误立即停止

PROJECT_ROOT="/Users/lynn/Documents/GitHub/ProjectMatching"
cd "$PROJECT_ROOT"

echo "🚀 开始重组项目结构..."

# ============================================
# 1. 移动源代码文件到 src/
# ============================================
echo ""
echo "📦 步骤 1/6: 移动源代码文件..."

# 文档转换器
mv document_converter.py src/converters/ 2>/dev/null || true
mv document_converter_ocr.py src/converters/ 2>/dev/null || true

# 知识图谱生成器（保留最重要的版本）
mv balanced_kg_generator.py src/knowledge_graphs/ 2>/dev/null || true
mv batch_complete_clean_kg.py src/knowledge_graphs/ 2>/dev/null || true
mv enhanced_project_kg.py src/knowledge_graphs/ 2>/dev/null || true
mv individual_project_unit_kg.py src/knowledge_graphs/ 2>/dev/null || true
mv project_knowledge_graph.py src/knowledge_graphs/ 2>/dev/null || true
mv knowledge_graph_generator.py src/knowledge_graphs/ 2>/dev/null || true

# 学生档案生成器
mv student_profile_generator.py src/profile/ 2>/dev/null || true
mv enhanced_student_profile_generator.py src/profile/ 2>/dev/null || true

# 匹配算法
mv student_project_similarity_matrix.py src/matching/similarity_matrix.py 2>/dev/null || true
mv project_unit_skill_matcher.py src/matching/skill_matcher.py 2>/dev/null || true

# 工具函数
mv progress_quantifier.py src/utils/ 2>/dev/null || true
mv pd_uo_intersection_viewer.py src/utils/intersection_viewer.py 2>/dev/null || true

# CLI 接口
mv cli.py src/cli/main_cli.py 2>/dev/null || true
mv kg_cli.py src/cli/ 2>/dev/null || true
mv experiment_cli.py src/cli/ 2>/dev/null || true
mv individual_kg_cli.py src/cli/ 2>/dev/null || true
mv project_unit_cli.py src/cli/ 2>/dev/null || true

echo "   ✅ 源代码文件已移动"

# ============================================
# 2. 移动数据文件到 data/
# ============================================
echo ""
echo "📊 步骤 2/6: 重组数据文件..."

# 原始数据
mv project/ data/raw/projects/ 2>/dev/null || true
mv unit/ data/raw/units/ 2>/dev/null || true

# 处理后的数据
mv project_md/ data/processed/projects_md/ 2>/dev/null || true
mv unit_md/ data/processed/units_md/ 2>/dev/null || true
mv profile_md/ data/processed/profiles_md/ 2>/dev/null || true
mv enhanced_profile_md/ data/processed/enhanced_profiles_md/ 2>/dev/null || true

echo "   ✅ 数据文件已重组"

# ============================================
# 3. 移动输出文件到 outputs/
# ============================================
echo ""
echo "📤 步骤 3/6: 重组输出文件..."

# 知识图谱输出
mv individual_kg/ outputs/knowledge_graphs/individual/ 2>/dev/null || true
mv balanced_kg_output/ outputs/knowledge_graphs/balanced/ 2>/dev/null || true

# 旧版本归档
mkdir -p outputs/knowledge_graphs/archive
mv clean_kg_output/ outputs/knowledge_graphs/archive/ 2>/dev/null || true
mv refined_clean_kg_output/ outputs/knowledge_graphs/archive/ 2>/dev/null || true
mv complete_clean_kg_output/ outputs/knowledge_graphs/archive/ 2>/dev/null || true
mv balanced_kg_output_fixed/ outputs/knowledge_graphs/archive/ 2>/dev/null || true
mv test_output/ outputs/knowledge_graphs/archive/ 2>/dev/null || true

# 相似度结果
mv similarity_results/ outputs/ 2>/dev/null || true

# 报告
mv conversion_report.json outputs/reports/ 2>/dev/null || true

echo "   ✅ 输出文件已重组"

# ============================================
# 4. 归档旧版本生成器
# ============================================
echo ""
echo "🗄️  步骤 4/6: 归档旧版本脚本..."

mkdir -p experiments/archive/old_generators
mv clean_kg_extractor.py experiments/archive/old_generators/ 2>/dev/null || true
mv optimized_clean_kg_extractor.py experiments/archive/old_generators/ 2>/dev/null || true
mv refined_clean_kg_generator.py experiments/archive/old_generators/ 2>/dev/null || true
mv complete_clean_kg_extractor.py experiments/archive/old_generators/ 2>/dev/null || true
mv flexible_clean_kg_extractor.py experiments/archive/old_generators/ 2>/dev/null || true
mv fixed_balanced_kg_generator.py experiments/archive/old_generators/ 2>/dev/null || true
mv individual_knowledge_graphs.py experiments/archive/old_generators/ 2>/dev/null || true

echo "   ✅ 旧版本已归档"

# ============================================
# 5. 移动文档文件到 docs/
# ============================================
echo ""
echo "📚 步骤 5/6: 整理文档..."

mv 使用指南.md docs/USAGE_CN.md 2>/dev/null || true
mv 项目总结.md docs/PROJECT_SUMMARY_CN.md 2>/dev/null || true

echo "   ✅ 文档已整理"

# ============================================
# 6. 清理不需要的文件
# ============================================
echo ""
echo "🧹 步骤 6/6: 清理临时文件..."

# 删除虚拟环境
rm -rf project_matching/ 2>/dev/null || true

# 删除缓存
rm -rf __pycache__/ 2>/dev/null || true
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

# 删除系统文件
find . -name ".DS_Store" -delete 2>/dev/null || true

echo "   ✅ 临时文件已清理"

# ============================================
# 7. 创建 __init__.py 文件
# ============================================
echo ""
echo "📝 创建 __init__.py 文件..."

touch src/__init__.py
touch src/converters/__init__.py
touch src/knowledge_graphs/__init__.py
touch src/profile/__init__.py
touch src/matching/__init__.py
touch src/utils/__init__.py
touch src/cli/__init__.py
touch tests/__init__.py

echo "   ✅ __init__.py 已创建"

# ============================================
# 完成
# ============================================
echo ""
echo "✨ 项目重组完成！"
echo ""
echo "📋 新的目录结构："
echo "   src/          - 源代码"
echo "   data/         - 数据文件"
echo "   outputs/      - 输出结果"
echo "   docs/         - 文档"
echo "   experiments/  - 实验归档"
echo "   scripts/      - 辅助脚本"
echo "   tests/        - 测试文件"
echo ""
echo "💡 下一步建议："
echo "   1. 查看新的目录结构: tree -L 2 -I '__pycache__|*.pyc'"
echo "   2. 更新导入路径: 需要修改 import 语句"
echo "   3. 测试功能: 运行核心脚本确保正常工作"
echo "   4. 创建 .gitignore: bash scripts/create_gitignore.sh"
echo "   5. 提交到Git: git add . && git commit -m 'Reorganize project structure'"
echo ""

