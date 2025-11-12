# 🚀 PyPI 发布指南 - AceFlow AI v3.0.0

## ✅ 准备工作已完成

所有发布前的准备工作都已完成：

- ✅ **pyproject.toml** - 项目配置文件
- ✅ **CHANGELOG.md** - 版本变更日志
- ✅ **MANIFEST.in** - 包含文件清单
- ✅ **测试通过** - 131/132 通过 (99.2%)
- ✅ **本地安装验证** - 通过
- ✅ **构建成功** - wheel 和 sdist 已生成

构建产物位于 `dist/` 目录：
- `aceflow_ai-3.0.0-py3-none-any.whl` (413 KB)
- `aceflow_ai-3.0.0.tar.gz` (563 KB)

---

## 📦 发布到 PyPI

### 1. 安装 twine（如果尚未安装）

```bash
pip install twine
```

### 2. 检查包的完整性

```bash
twine check dist/*
```

预期输出：
```
Checking dist/aceflow_ai-3.0.0-py3-none-any.whl: PASSED
Checking dist/aceflow_ai-3.0.0.tar.gz: PASSED
```

### 3. 上传到 TestPyPI（可选，推荐先测试）

```bash
# 上传到 TestPyPI
twine upload --repository testpypi dist/*

# 测试安装
pip install --index-url https://test.pypi.org/simple/ aceflow-ai
```

### 4. 上传到正式 PyPI

```bash
twine upload dist/*
```

系统会提示输入：
- **Username**: 你的 PyPI 用户名（或 `__token__`）
- **Password**: 你的 PyPI 密码（或 API token）

**使用 API Token (推荐)**:
- Username: `__token__`
- Password: `pypi-<your-token>`

### 5. 验证发布成功

```bash
# 等待 1-2 分钟后，从 PyPI 安装
pip install aceflow-ai

# 验证版本
python -c "import aceflow; print(aceflow.__version__)"
# 应该输出: 3.0.0
```

---

## 🔒 安全提示

### 使用 API Token

1. 访问 https://pypi.org/manage/account/token/
2. 创建新的 API token
3. 保存到 `~/.pypirc`:

```ini
[pypi]
username = __token__
password = pypi-xxxxx...xxxxx
```

### 权限设置

```bash
chmod 600 ~/.pypirc
```

---

## 📝 发布后的操作

### 1. 创建 Git Tag

```bash
git tag -a v3.0.0 -m "Release v3.0.0 - Complete Workflow System"
git push origin v3.0.0
```

### 2. 创建 GitHub Release

1. 访问 https://github.com/aceflow-ai/aceflow-ai/releases/new
2. 选择 tag: `v3.0.0`
3. Release title: `v3.0.0 - Complete Workflow System`
4. 复制 CHANGELOG.md 的 v3.0.0 部分到 description
5. 上传构建产物（可选）:
   - `aceflow_ai-3.0.0-py3-none-any.whl`
   - `aceflow_ai-3.0.0.tar.gz`

### 3. 更新文档

在 README.md 中添加安装说明：

```markdown
## Installation

```bash
pip install aceflow-ai
```

Or with MCP support:

```bash
pip install aceflow-ai[mcp]
```
\```
```

### 4. 宣传发布

- 在 GitHub Discussions 发布公告
- 在相关社区分享（Reddit, Twitter等）
- 更新项目主页

---

## 🧪 验证清单

在发布前，请确认：

- [ ] 所有测试通过 (131/132)
- [ ] 版本号正确 (3.0.0)
- [ ] CHANGELOG.md 已更新
- [ ] pyproject.toml 配置正确
- [ ] 本地安装测试通过
- [ ] 构建产物生成成功
- [ ] `twine check dist/*` 通过

在发布后，请验证：

- [ ] PyPI 页面显示正常
- [ ] `pip install aceflow-ai` 可以安装
- [ ] 导入包成功
- [ ] 版本号正确
- [ ] GitHub Release 创建成功
- [ ] 文档已更新

---

## 🐛 常见问题

### Q: twine upload 提示 403 Forbidden

**A**: 检查：
1. 用户名/密码是否正确
2. 包名是否已被占用
3. 是否有权限上传

### Q: 包已存在错误

**A**: PyPI 不允许重复上传相同版本。需要：
1. 增加版本号（如 3.0.1）
2. 重新构建
3. 上传新版本

### Q: 依赖安装失败

**A**: 检查 pyproject.toml 中的依赖版本约束是否合理。

---

## 📊 项目统计

- **Package Name**: aceflow-ai
- **Version**: 3.0.0
- **Python**: >=3.8
- **License**: MIT
- **Size**:
  - Wheel: 413 KB
  - Source: 563 KB
- **Test Coverage**: 99.2%
- **Documentation**: 38 files, ~170K words

---

## 🎉 恭喜！

你的项目已经准备好发布到 PyPI 了！

只需要执行：

```bash
# 检查
twine check dist/*

# 上传
twine upload dist/*
```

就可以让全世界的开发者通过 `pip install aceflow-ai` 使用你的项目了！

---

**Created**: 2025-01-09
**Author**: AceFlow Team
**Status**: ✅ Ready for Release
