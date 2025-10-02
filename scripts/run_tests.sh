#!/bin/bash
# 运行所有测试

echo "🧪 运行ProjectMatching测试套件..."
echo "=================================="
echo ""

cd "$(dirname "$0")/.."

# 检查Python环境
echo "📍 Python版本:"
python --version
echo ""

# 运行测试
echo "🚀 执行测试..."
python -m pytest tests/ -v --tb=short

# 显示测试覆盖率（如果安装了pytest-cov）
if python -c "import pytest_cov" 2>/dev/null; then
    echo ""
    echo "📊 测试覆盖率:"
    python -m pytest tests/ --cov=src --cov-report=term-missing
fi

echo ""
echo "✅ 测试完成！"

