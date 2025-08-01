# 🎭 TalkShow 安装和使用指南

## 📦 安装

### 从源码安装（开发模式）

```bash
# 克隆项目
git clone <repository-url>
cd talkshow

# 安装依赖
pip install -r requirements.txt

# 安装包（开发模式）
pip install -e .
```

### 从 PyPI 安装（发布后）

```bash
pip install talkshow
```

## 🚀 快速开始

### 1. 初始化配置

在包含 `.specstory` 目录的项目中运行：

```bash
talkshow init
```

这会：
- 检查 `.specstory` 目录是否存在
- 在 `.specstory` 中创建 `talkshow.yaml` 配置文件
- 创建 `.specstory/data` 目录用于存储数据

### 2. 解析聊天历史

```bash
talkshow parse
```

这会：
- 读取 `.specstory/history` 中的聊天记录
- 生成摘要（基于规则或 LLM）
- 保存到 `.specstory/data/sessions.json`

### 3. 启动 Web 服务器

```bash
talkshow server
```

这会：
- 启动 Web 服务器（默认端口 8000）
- 提供可视化界面：http://localhost:8000
- 提供 API 文档：http://localhost:8000/docs

### 4. 停止 Web 服务器

```bash
talkshow stop
```

这会：
- 查找并停止正在运行的 TalkShow 服务器
- 支持确认提示（使用 `--force` 跳过确认）
- 优雅地关闭服务器进程

## ⚙️ 配置选项

### 命令行选项

```bash
# 初始化（强制覆盖现有配置）
talkshow init --force

# 解析（使用 LLM 摘要）
talkshow parse --use-llm

# 解析（指定输出文件）
talkshow parse --output custom/path/sessions.json

# 服务器（指定端口）
talkshow server --port 8080

# 服务器（指定主机）
talkshow server --host 0.0.0.0

# 服务器（指定数据文件）
talkshow server --data-file custom/path/sessions.json

# 停止服务器
talkshow stop

# 强制停止服务器
talkshow stop --force

# 停止指定端口的服务器
talkshow stop --port 8080
```

### 配置文件

配置文件位于 `.specstory/talkshow.yaml`，包含：

```yaml
project:
  name: "TalkShow Project"
  description: "Chat history analysis and visualization"

paths:
  history_dir: ".specstory/history"
  output_dir: ".specstory/data"
  config_file: ".specstory/talkshow.yaml"

server:
  host: "127.0.0.1"
  port: 8000
  reload: true

summarizer:
  enabled: true
  use_llm: false
  max_question_length: 20
  max_answer_length: 80

llm:
  provider: "moonshot"
  model: "moonshot/kimi-k2-0711-preview"
  max_tokens: 150
  temperature: 0.3
```

## 🔧 环境变量

支持通过环境变量配置 LLM：

```bash
export MOONSHOT_API_KEY="your_api_key"
export LLM_MODEL="moonshot/kimi-k2-0711-preview"
```

## 📁 目录结构

安装后的项目结构：

```
your-project/
├── .specstory/
│   ├── history/           # SpecStory 生成的聊天记录
│   ├── data/              # TalkShow 生成的数据文件
│   └── talkshow.yaml      # TalkShow 配置文件
└── ... (其他项目文件)
```

## 🎯 使用场景

### 开发环境

1. **初始化项目**：
   ```bash
   cd your-project
   talkshow init
   ```

2. **定期解析聊天记录**：
   ```bash
   talkshow parse
   ```

3. **查看可视化界面**：
   ```bash
   talkshow server
   ```

### 生产环境

1. **配置 LLM API**：
   ```bash
   export MOONSHOT_API_KEY="your_api_key"
   ```

2. **使用 LLM 摘要**：
   ```bash
   talkshow parse --use-llm
   ```

3. **启动生产服务器**：
   ```bash
   talkshow server --host 0.0.0.0 --port 8080
   ```

## 🔍 故障排除

### 常见问题

1. **`.specstory` 目录不存在**
   - 确保在正确的项目目录中运行
   - 确保 SpecStory 插件已启用

2. **配置文件未找到**
   - 运行 `talkshow init` 初始化配置

3. **数据文件未找到**
   - 运行 `talkshow parse` 生成数据文件

4. **LLM 连接失败**
   - 检查 API 密钥配置
   - 使用 `--use-llm` 选项时会自动降级到规则摘要

### 调试模式

```bash
# 查看详细日志
talkshow parse --verbose

# 测试 LLM 连接
python -c "from talkshow.summarizer.llm_summarizer import LLMSummarizer; print(LLMSummarizer().test_connection())"
```

## 📚 更多信息

- 项目文档：查看 `README.md`
- API 文档：启动服务器后访问 `http://localhost:8000/docs`
- 问题反馈：提交 GitHub Issue 