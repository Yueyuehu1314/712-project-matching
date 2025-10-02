# 🚀 快速开始指南

本指南帮助你快速重组项目并开始使用。

## ⚠️ 重要提示

在执行任何操作前，建议先**备份整个项目目录**！

```bash
cd /Users/lynn/Documents/GitHub
cp -r ProjectMatching ProjectMatching_backup
```

---

## 📋 重组步骤

### 步骤 1: 赋予脚本执行权限

```bash
cd /Users/lynn/Documents/GitHub/ProjectMatching
chmod +x scripts/*.sh
```

### 步骤 2: 查看当前文件清单

```bash
# 查看项目根目录的文件
ls -la

# 查看主要的 Python 文件
ls *.py
```

### 步骤 3: 执行重组脚本

```bash
# 执行重组
bash scripts/reorganize_project.sh
```

这个脚本会：
- ✅ 移动源代码到 `src/` 目录
- ✅ 移动数据到 `data/` 目录
- ✅ 移动输出到 `outputs/` 目录
- ✅ 归档旧版本到 `experiments/archive/`
- ✅ 删除虚拟环境和缓存文件
- ✅ 创建 `__init__.py` 文件

### 步骤 4: 验证新结构

```bash
# 查看新的目录结构
tree -L 2 -I '__pycache__|*.pyc|.venv'

# 或者使用 ls
ls -la src/
ls -la data/
ls -la outputs/
```

### 步骤 5: 创建新的虚拟环境

```bash
# 创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# 安装依赖
pip install --upgrade pip
pip install -r requirements-all.txt
```

---

## 🧪 测试核心功能

### 测试 1: 文档转换

```bash
# 激活虚拟环境（如果还没激活）
source .venv/bin/activate

# 运行文档转换器
python src/converters/document_converter.py
```

### 测试 2: 知识图谱生成

```bash
# 生成平衡版知识图谱
python src/knowledge_graphs/balanced_kg_generator.py
```

### 测试 3: 查看 CLI 帮助

```bash
# 主CLI
python src/cli/main_cli.py --help

# 知识图谱CLI
python src/cli/kg_cli.py --help
```

---

## 🔧 如果遇到导入错误

重组后，某些脚本的导入路径可能需要更新。

### 方案 A: 设置 PYTHONPATH（临时）

```bash
export PYTHONPATH=/Users/lynn/Documents/GitHub/ProjectMatching:$PYTHONPATH
```

### 方案 B: 安装为可编辑包（推荐）

创建 `setup.py`:

```python
from setuptools import setup, find_packages

setup(
    name="project_matching",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        # 从 requirements-all.txt 读取
    ],
)
```

然后安装：

```bash
pip install -e .
```

### 方案 C: 修改导入语句

如果脚本中有：
```python
from student_profile_generator import ProjectMatchingSystem
```

改为：
```python
from src.profile.student_profile_generator import ProjectMatchingSystem
```

或使用相对导入：
```python
from ..profile.student_profile_generator import ProjectMatchingSystem
```

---

## 📁 重组后的目录映射

| 原位置 | 新位置 |
|--------|--------|
| `*.py` (转换器) | `src/converters/` |
| `*kg*.py` (知识图谱) | `src/knowledge_graphs/` |
| `student_profile*.py` | `src/profile/` |
| `*similarity*.py` | `src/matching/` |
| `*cli.py` | `src/cli/` |
| `project/` | `data/raw/projects/` |
| `project_md/` | `data/processed/projects_md/` |
| `profile_md/` | `data/processed/profiles_md/` |
| `individual_kg/` | `outputs/knowledge_graphs/individual/` |
| `balanced_kg_output/` | `outputs/knowledge_graphs/balanced/` |
| `clean_kg_output/` | `outputs/knowledge_graphs/archive/` |

---

## 🗑️ 清理不需要的文件（可选）

如果重组成功，可以删除归档的旧版本：

```bash
# 删除归档的旧生成器（谨慎操作）
rm -rf experiments/archive/old_generators/

# 删除归档的旧输出（谨慎操作）
rm -rf outputs/knowledge_graphs/archive/clean_kg_output/
rm -rf outputs/knowledge_graphs/archive/refined_clean_kg_output/
rm -rf outputs/knowledge_graphs/archive/complete_clean_kg_output/
```

---

## ✅ 提交到 Git

```bash
# 添加 .gitignore
git add .gitignore

# 添加所有新结构
git add .

# 查看变更
git status

# 提交
git commit -m "Reorganize project structure

- Move source code to src/
- Move data files to data/
- Move outputs to outputs/
- Create proper documentation
- Add .gitignore
- Remove virtual environment and cache files"

# 推送（如果有远程仓库）
git push origin main
```

---

## 📞 遇到问题？

### 常见问题

1. **脚本执行失败**
   - 检查是否有文件正在被使用
   - 尝试手动移动文件

2. **导入错误**
   - 设置 PYTHONPATH
   - 或使用 `pip install -e .` 安装为包

3. **文件找不到**
   - 检查路径配置
   - 更新脚本中的路径引用

4. **虚拟环境问题**
   - 删除 `.venv` 重新创建
   - 确保使用正确的 Python 版本

---

## 🎉 完成！

现在你的项目有了清晰的结构：

```
ProjectMatching/
├── src/           # 所有源代码
├── data/          # 数据文件（raw + processed）
├── outputs/       # 生成的输出
├── docs/          # 文档
├── scripts/       # 辅助脚本
└── tests/         # 测试文件
```

**下一步建议：**
1. 运行测试确保功能正常
2. 更新文档
3. 设置 CI/CD（如果需要）
4. 分享给团队成员

