#!/bin/bash
# 预览重组后的结果（不实际移动文件）

PROJECT_ROOT="/Users/lynn/Documents/GitHub/ProjectMatching"
cd "$PROJECT_ROOT"

echo "📋 重组预览 - 不会实际移动文件"
echo "======================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 统计函数
count_files() {
    local pattern=$1
    find . -maxdepth 1 -name "$pattern" -type f 2>/dev/null | wc -l | tr -d ' '
}

count_dirs() {
    local pattern=$1
    find . -maxdepth 1 -name "$pattern" -type d 2>/dev/null | wc -l | tr -d ' '
}

echo "📊 当前项目统计"
echo "----------------"
echo "Python 文件 (根目录): $(count_files '*.py')"
echo "数据目录: $(count_dirs '*md')"
echo "输出目录: $(count_dirs '*output*')"
echo ""

echo "🔄 将要执行的操作："
echo "===================="
echo ""

# 源代码移动
echo -e "${BLUE}📦 源代码文件 → src/${NC}"
echo "  文档转换器:"
for file in document_converter.py document_converter_ocr.py; do
    [ -f "$file" ] && echo "    ✓ $file → src/converters/"
done

echo "  知识图谱生成器:"
for file in balanced_kg_generator.py batch_complete_clean_kg.py enhanced_project_kg.py \
            individual_project_unit_kg.py project_knowledge_graph.py knowledge_graph_generator.py; do
    [ -f "$file" ] && echo "    ✓ $file → src/knowledge_graphs/"
done

echo "  学生档案生成器:"
for file in student_profile_generator.py enhanced_student_profile_generator.py; do
    [ -f "$file" ] && echo "    ✓ $file → src/profile/"
done

echo "  匹配算法:"
[ -f "student_project_similarity_matrix.py" ] && echo "    ✓ student_project_similarity_matrix.py → src/matching/"
[ -f "project_unit_skill_matcher.py" ] && echo "    ✓ project_unit_skill_matcher.py → src/matching/"

echo "  工具函数:"
[ -f "progress_quantifier.py" ] && echo "    ✓ progress_quantifier.py → src/utils/"
[ -f "pd_uo_intersection_viewer.py" ] && echo "    ✓ pd_uo_intersection_viewer.py → src/utils/"

echo "  CLI 接口:"
for file in cli.py kg_cli.py experiment_cli.py individual_kg_cli.py project_unit_cli.py; do
    [ -f "$file" ] && echo "    ✓ $file → src/cli/"
done

echo ""

# 数据文件移动
echo -e "${GREEN}📊 数据文件 → data/${NC}"
[ -d "project" ] && echo "  ✓ project/ → data/raw/projects/"
[ -d "unit" ] && echo "  ✓ unit/ → data/raw/units/"
[ -d "project_md" ] && echo "  ✓ project_md/ → data/processed/projects_md/"
[ -d "unit_md" ] && echo "  ✓ unit_md/ → data/processed/units_md/"
[ -d "profile_md" ] && echo "  ✓ profile_md/ → data/processed/profiles_md/"
[ -d "enhanced_profile_md" ] && echo "  ✓ enhanced_profile_md/ → data/processed/enhanced_profiles_md/"
echo ""

# 输出文件移动
echo -e "${YELLOW}📤 输出文件 → outputs/${NC}"
[ -d "individual_kg" ] && echo "  ✓ individual_kg/ → outputs/knowledge_graphs/individual/"
[ -d "balanced_kg_output" ] && echo "  ✓ balanced_kg_output/ → outputs/knowledge_graphs/balanced/"
[ -d "similarity_results" ] && echo "  ✓ similarity_results/ → outputs/similarity_results/"
[ -f "conversion_report.json" ] && echo "  ✓ conversion_report.json → outputs/reports/"
echo ""

# 归档文件
echo -e "${BLUE}🗄️  归档旧版本 → experiments/archive/${NC}"
for file in clean_kg_extractor.py optimized_clean_kg_extractor.py refined_clean_kg_generator.py \
            complete_clean_kg_extractor.py flexible_clean_kg_extractor.py fixed_balanced_kg_generator.py; do
    [ -f "$file" ] && echo "  ✓ $file"
done

for dir in clean_kg_output refined_clean_kg_output complete_clean_kg_output balanced_kg_output_fixed test_output; do
    [ -d "$dir" ] && echo "  ✓ $dir/"
done
echo ""

# 删除文件
echo -e "${RED}🗑️  将被删除的文件/目录${NC}"
[ -d "project_matching" ] && echo "  ✗ project_matching/ (虚拟环境, ~500MB-2GB)"
[ -d "__pycache__" ] && echo "  ✗ __pycache__/ (Python缓存)"
[ -f ".DS_Store" ] && echo "  ✗ .DS_Store (macOS系统文件)"
echo ""

# 空间统计
echo "💾 预估空间变化"
echo "----------------"
if [ -d "project_matching" ]; then
    venv_size=$(du -sh project_matching 2>/dev/null | cut -f1)
    echo "  虚拟环境: $venv_size (将被删除)"
fi

if [ -d "__pycache__" ]; then
    cache_size=$(du -sh __pycache__ 2>/dev/null | cut -f1)
    echo "  缓存文件: $cache_size (将被删除)"
fi

if [ -d "clean_kg_output" ]; then
    old_kg_size=$(du -sh clean_kg_output refined_clean_kg_output complete_clean_kg_output 2>/dev/null | awk '{sum+=$1} END {print sum}')
    echo "  旧版KG输出: 将被归档到 archive/"
fi

echo ""
echo "📁 重组后的目录结构预览"
echo "========================"
cat << 'EOF'
ProjectMatching/
├── src/
│   ├── converters/          # 文档转换器 (2个文件)
│   ├── knowledge_graphs/    # 知识图谱生成器 (6个文件)
│   ├── profile/            # 学生档案生成器 (2个文件)
│   ├── matching/           # 匹配算法 (2个文件)
│   ├── utils/              # 工具函数 (2个文件)
│   └── cli/                # CLI接口 (5个文件)
├── data/
│   ├── raw/
│   │   ├── projects/       # 20个原始项目文件
│   │   └── units/          # 2个课程PDF
│   └── processed/
│       ├── projects_md/    # 20个项目Markdown
│       ├── units_md/       # 3个课程Markdown
│       ├── profiles_md/    # 200个学生档案
│       └── enhanced_profiles_md/  # 12个增强档案
├── outputs/
│   ├── knowledge_graphs/
│   │   ├── individual/     # 个体知识图谱
│   │   ├── balanced/       # 平衡版知识图谱 (推荐)
│   │   └── archive/        # 旧版本归档
│   ├── similarity_results/ # 相似度结果
│   └── reports/           # 生成的报告
├── experiments/
│   └── archive/           # 实验脚本归档
├── docs/                  # 项目文档
├── scripts/               # 辅助脚本
├── tests/                 # 测试文件
├── .gitignore            # Git忽略文件
├── requirements.txt       # Python依赖
└── QUICKSTART.md         # 快速开始指南
EOF

echo ""
echo "======================================"
echo -e "${GREEN}✨ 预览完成！${NC}"
echo ""
echo "💡 下一步："
echo "  1. 如果满意这个结构，运行: bash scripts/reorganize_project.sh"
echo "  2. 如果需要修改，编辑: scripts/reorganize_project.sh"
echo "  3. 查看快速开始指南: cat QUICKSTART.md"
echo ""
echo "⚠️  建议先备份: cp -r . ../ProjectMatching_backup"
echo ""

