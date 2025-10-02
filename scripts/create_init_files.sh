#!/bin/bash
# 创建所有必要的 __init__.py 文件

PROJECT_ROOT="/Users/lynn/Documents/GitHub/ProjectMatching"
cd "$PROJECT_ROOT"

echo "📝 创建 __init__.py 文件..."

# 创建主模块 __init__.py
cat > src/__init__.py << 'EOF'
"""
ProjectMatching - Student-Project Intelligent Matching System
"""

__version__ = "1.0.0"
__author__ = "Lynn"
EOF

# 创建子模块 __init__.py
for dir in src/converters src/knowledge_graphs src/profile src/matching src/utils src/cli tests; do
    if [ -d "$dir" ]; then
        touch "$dir/__init__.py"
        echo "   ✅ 创建 $dir/__init__.py"
    fi
done

echo "✨ 完成！"

