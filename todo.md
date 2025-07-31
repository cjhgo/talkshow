/Users/junhangc/workspace/me/talkshow/history
这个目录中的数据由 specstory 插件产生.

[Quickstart - SpecStory](https://docs.specstory.com/specstory/quickstart)

这里描述了这个目录的作用,即自动记录 cursor 开发一个项目过程中

产生的 chat history.

在 llm generate code 的大背景下,

chat history 比代码更重要,它记录项目产生过程中的动态决策和思路.

就像 git 记录了 代码的 版本一样, chat history 记录了代码写成这样背后的 why.

本项目 TalkShow 则服务于这样一个目的: show talk.

即 分析然后可视化的展示 chat history.

chat hisotry 由一个个 md 文件组成,

每个 md 文件由连续的 User/Assistant 对话构成,

并且每次 Assistant 都会先输出时间信息.

基于这样的结构信息,我们对这些数据进行结构化分析,然后可视化展示.

所以,本项目 TalkShow 在代码的结构设计上分成两大块: 数据分析,数据展示.

以下分别展开讨论.

# 数据分析

* 以第一条 Assistant 产生的时间为当前 md 的产生时间, CTime
  因为文件名中的时间并不准
* 暂时以文件名中的描述字段作为当前 md 的主题, Theme
* 文件内容用 `[ (Q,A),(Q,A)...]` 这样的结构表示

以上描述了 md 文件怎样用 内存中的数据结构表示的问题.

即 `md-> (CTime, Theme): [ (Q,A),(Q,A)...]`

---

为了有效的对这些文件进行结构化存储,需要选择合适的数据库方案.

最朴素的是存为 json, 更紧凑一些可以用 sqlite

---

考虑到 md 中的 Q/A 内容长度差异角度,需要对这些信息进一步进行统一化精简表示.

这里可以考虑用 litellm + apikey 把 文本内容送到 llm 中然后得到 summary, summary 要限定长度

Q 一般不会太长,如果不超过 20,可以不摘要, 超过则 summary 为不超过 20

A 可能会比较长, 估计要 summary 为不超过 80.

# 数据展示

数据展示分为两种场景, cli 展示, web 前端展示.

cli 展示可以快速在终端中查看基本摘要, web 前端则可以更加丰富的交互查看.


### web 前端展示

基本的设限是一个滑动展示的 table

一个 md 是一列, 按照时间产生行.

history 中的多个 md 产生 多个 列,

拖动向左时, row header 的 时间轴也要跟着变化.


# plan

## 项目目录结构

```
talkshow/
├── talkshow/                    # 核心库
│   ├── __init__.py
│   ├── models/                  # 数据模型
│   │   ├── __init__.py
│   │   ├── chat.py             # ChatSession, QAPair 等数据类
│   │   └── storage.py          # 存储相关模型
│   ├── parser/                  # MD 文件解析
│   │   ├── __init__.py
│   │   ├── md_parser.py        # MD 文件解析器
│   │   └── time_extractor.py   # 时间提取器
│   ├── summarizer/              # 摘要生成
│   │   ├── __init__.py
│   │   ├── llm_summarizer.py   # LiteLLM 摘要器
│   │   └── rule_summarizer.py  # 基于规则的摘要器
│   ├── storage/                 # 数据存储
│   │   ├── __init__.py
│   │   ├── json_storage.py     # JSON 存储实现
│   │   └── sqlite_storage.py   # SQLite 存储实现
│   ├── cli/                     # CLI 展示
│   │   ├── __init__.py
│   │   ├── commands.py         # CLI 命令实现
│   │   └── formatter.py        # 输出格式化
│   └── web/                     # Web 前端
│       ├── __init__.py
│       ├── app.py              # FastAPI 应用
│       ├── routers/            # API 路由
│       │   ├── __init__.py
│       │   └── api.py
│       └── static/             # 静态文件 (HTML/CSS/JS)
│           ├── index.html
│           ├── style.css
│           └── script.js
├── scripts/                     # 入口脚本
│   ├── talkshow-cli.py         # CLI 入口
│   └── talkshow-web.py         # Web 服务入口
├── tests/                       # 测试代码
│   ├── __init__.py
│   ├── test_parser.py
│   ├── test_summarizer.py
│   └── test_storage.py
├── config/                      # 配置文件
│   ├── default.yaml
│   └── example.env
├── requirements.txt             # 依赖列表
├── setup.py                     # 包安装配置
└── README.md                    # 项目说明
```

## 实现步骤规划

### Phase 1: 数据分析核心 (MVP)

1. **数据模型定义** (`talkshow/models/`)
   - `ChatSession`: 表示一个 MD 文件的完整会话
   - `QAPair`: 表示一个问答对
   - `SessionMeta`: 会话元数据 (CTime, Theme)

2. **MD 文件解析器** (`talkshow/parser/`)
   - 解析 MD 文件结构
   - 提取 User/Assistant 对话
   - 提取时间戳信息
   - 从文件名提取主题

3. **基础存储层** (`talkshow/storage/`)
   - 先实现 JSON 存储
   - 定义统一的存储接口

4. **基础摘要器** (`talkshow/summarizer/`)
   - 先实现基于规则的摘要 (长度截断)
   - 为 LLM 摘要预留接口

### Phase 2: CLI 工具

5. **CLI 命令实现** (`talkshow/cli/`)
   - `parse`: 解析 history 目录
   - `list`: 列出所有会话
   - `show`: 显示特定会话详情
   - `summary`: 显示整体统计

### Phase 3: LLM 集成

6. **LLM 摘要器** (`talkshow/summarizer/`)
   - 集成 LiteLLM
   - 实现智能摘要生成
   - 支持配置不同的 LLM 提供商

### Phase 4: Web 前端

7. **API 服务** (`talkshow/web/`)
   - FastAPI 后端
   - 提供 RESTful API
   - 支持会话列表、详情、搜索等

8. **前端界面** (`talkshow/web/static/`)
   - 时间轴表格展示
   - 交互式滑动
   - 会话内容查看

### Phase 5: 高级功能

9. **SQLite 存储**
   - 更高效的数据存储
   - 支持复杂查询

10. **增强功能**
    - 全文搜索
    - 标签系统
    - 导出功能

## 技术栈选择

- **核心库**: Python 3.8+
- **CLI**: Click 或 Typer
- **Web 后端**: FastAPI
- **Web 前端**: 原生 HTML/CSS/JS (保持轻量)
- **LLM 集成**: LiteLLM
- **存储**: JSON (初期), SQLite (后期)
- **配置管理**: PyYAML
- **测试**: pytest

## 配置管理

支持通过配置文件或环境变量设置:
- LLM API 密钥和提供商
- 摘要长度限制
- 存储方式选择
- Web 服务端口等

## 开发优先级

1. **MVP**: 能够解析 MD 文件并生成基础摘要
2. **CLI**: 提供命令行工具进行基本操作
3. **LLM**: 集成智能摘要功能
4. **Web**: 提供可视化界面
5. **优化**: 性能优化和功能增强
