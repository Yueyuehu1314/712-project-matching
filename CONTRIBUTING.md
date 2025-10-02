# 贡献指南 | Contributing Guide

感谢你对 ProjectMatching 项目的兴趣！🎉

## 🚀 快速开始

### 1. Fork 和克隆仓库

```bash
# Fork 项目到你的GitHub账户
# 然后克隆你的fork
git clone https://github.com/YOUR_USERNAME/712-project-matching.git
cd 712-project-matching
```

### 2. 设置开发环境

```bash
# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements-all.txt
pip install -r requirements-dev.txt  # 开发依赖（pytest等）
```

### 3. 创建分支

```bash
# 从main创建功能分支
git checkout -b feature/your-feature-name
```

## 📝 开发流程

### 代码风格

- 遵循 PEP 8 Python代码风格
- 使用有意义的变量和函数名
- 添加适当的注释和文档字符串
- 保持代码简洁清晰

### 提交规范

使用语义化提交信息（带emoji）：

```
✨ feat: 添加新功能
🐛 fix: 修复bug
📚 docs: 更新文档
🎨 style: 代码格式调整
♻️ refactor: 重构代码
🧪 test: 添加测试
🔧 chore: 构建/工具链更新
⚡ perf: 性能优化
```

示例：
```bash
git commit -m "✨ feat: 添加项目相似度计算功能"
git commit -m "🐛 fix: 修复知识图谱可视化bug"
```

### 测试

在提交前运行测试：

```bash
# 运行所有测试
./scripts/run_tests.sh

# 或使用pytest
python -m pytest tests/ -v

# 运行特定测试文件
python -m pytest tests/test_document_converter.py -v
```

## 🔍 Pull Request流程

1. **确保所有测试通过**
   ```bash
   python -m pytest tests/
   ```

2. **更新文档**（如果需要）
   - 更新 README.md
   - 更新相关文档

3. **推送到你的Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

4. **创建Pull Request**
   - 访问原仓库
   - 点击 "New Pull Request"
   - 选择你的分支
   - 填写详细的PR描述

### PR描述模板

```markdown
## 变更类型
- [ ] 新功能
- [ ] Bug修复
- [ ] 文档更新
- [ ] 性能优化
- [ ] 其他

## 变更描述
简要描述你的更改...

## 相关Issue
关闭 #123

## 测试
- [ ] 添加了单元测试
- [ ] 所有测试通过
- [ ] 手动测试通过

## 截图（如果适用）
```

## 🐛 报告Bug

使用GitHub Issues报告bug时，请提供：

1. **环境信息**
   - Python版本
   - 操作系统
   - 依赖版本

2. **复现步骤**
   - 详细的步骤
   - 最小化可复现示例

3. **预期行为 vs 实际行为**

4. **错误信息和日志**

## 💡 功能建议

欢迎提出新功能建议！请在Issue中包含：

1. **功能描述**
2. **使用场景**
3. **可能的实现方案**
4. **潜在影响**

## 📋 项目结构

```
src/
├── converters/       # 文档转换
├── knowledge_graphs/ # 知识图谱生成
├── profile/         # 学生档案
├── matching/        # 匹配算法
├── utils/           # 工具函数
└── cli/             # 命令行接口

tests/               # 单元测试
docs/                # 文档
scripts/             # 辅助脚本
```

## ❓ 需要帮助？

- 📧 提Issue
- 💬 参与Discussions
- 📖 查看文档

## 📜 许可证

通过贡献代码，你同意你的贡献将采用与项目相同的许可证。

---

**再次感谢你的贡献！** 🙏

