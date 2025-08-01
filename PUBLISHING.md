# TalkShow 发布指南

本指南介绍如何将 TalkShow 发布到 PyPI。

## 📋 发布前检查清单

### 1. 代码质量检查
- [ ] 所有测试通过
- [ ] 代码格式正确
- [ ] 文档更新完整
- [ ] 版本号已更新

### 2. 文件完整性检查
- [ ] `setup.py` 配置正确
- [ ] `pyproject.toml` 配置正确
- [ ] `README.md` 内容完整
- [ ] `LICENSE` 文件存在
- [ ] `MANIFEST.in` 包含必要文件
- [ ] `requirements.txt` 依赖正确

### 3. 功能测试
- [ ] 本地安装测试通过
- [ ] CLI 命令正常工作
- [ ] Web 服务正常启动
- [ ] LLM 功能正常（如果启用）

## 🚀 发布步骤

### 方法一：使用发布脚本（推荐）

1. **安装发布工具**
   ```bash
   pip install build twine
   ```

2. **运行发布脚本**
   ```bash
   python scripts/publish.py
   ```

3. **选择发布目标**
   - 选择 1：发布到 TestPyPI（测试）
   - 选择 2：发布到 PyPI（生产）

### 方法二：手动发布

1. **清理构建文件**
   ```bash
   rm -rf build/ dist/ *.egg-info/
   ```

2. **构建包**
   ```bash
   python -m build
   ```

3. **检查包**
   ```bash
   twine check dist/*
   ```

4. **上传到 TestPyPI（测试）**
   ```bash
   twine upload --repository testpypi dist/*
   ```

5. **上传到 PyPI（生产）**
   ```bash
   twine upload dist/*
   ```

## 🔧 配置 PyPI 账户

### 1. 注册 PyPI 账户
- 访问 https://pypi.org/account/register/
- 创建账户并验证邮箱

### 2. 注册 TestPyPI 账户
- 访问 https://test.pypi.org/account/register/
- 创建账户并验证邮箱

### 3. 配置认证
创建 `~/.pypirc` 文件：
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = your_username
password = your_password

[testpypi]
repository = https://test.pypi.org/legacy/
username = your_username
password = your_password
```

## 📦 版本管理

### 更新版本号
1. 修改 `setup.py` 中的 `version`
2. 修改 `pyproject.toml` 中的 `version`
3. 更新 `talkshow/__init__.py` 中的 `__version__`

### 版本号规范
- `0.1.0` - 初始版本
- `0.1.1` - 补丁版本（bug 修复）
- `0.2.0` - 次要版本（新功能）
- `1.0.0` - 主要版本（重大变更）

## 🧪 测试发布

### 1. 测试 TestPyPI
```bash
# 安装测试版本
pip install --index-url https://test.pypi.org/simple/ talkshow

# 测试功能
talkshow --help
```

### 2. 测试 PyPI
```bash
# 安装正式版本
pip install talkshow

# 测试功能
talkshow --help
```

## 📝 发布后检查

### 1. 检查 PyPI 页面
- 访问 https://pypi.org/project/talkshow/
- 确认包信息正确
- 检查文档链接

### 2. 测试安装
```bash
# 创建新的虚拟环境
python -m venv test_env
source test_env/bin/activate  # Linux/Mac
# test_env\Scripts\activate  # Windows

# 安装包
pip install talkshow

# 测试功能
talkshow init
talkshow --help
```

## 🐛 常见问题

### 1. 认证失败
- 检查 `~/.pypirc` 配置
- 确认用户名和密码正确
- 验证账户邮箱

### 2. 包名冲突
- 检查 PyPI 上是否已存在同名包
- 考虑修改包名或联系包所有者

### 3. 依赖问题
- 检查 `requirements.txt` 中的依赖版本
- 确保所有依赖都可在 PyPI 上找到

### 4. 构建失败
- 检查 `setup.py` 和 `pyproject.toml` 配置
- 确认所有必要文件都存在
- 检查 Python 版本兼容性

## 📚 相关资源

- [PyPI 发布指南](https://packaging.python.org/tutorials/packaging-projects/)
- [setuptools 文档](https://setuptools.pypa.io/)
- [twine 文档](https://twine.readthedocs.io/)
- [Python 打包用户指南](https://packaging.python.org/)

## 🤝 贡献

如果你发现发布过程中的问题或有改进建议，请：

1. 创建 Issue
2. 提交 Pull Request
3. 联系维护团队

---

**注意**：发布到 PyPI 是永久性的，请确保代码质量和功能完整性。 