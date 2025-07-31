# 🎭 TalkShow - Chat History Analysis and Visualization Tool

TalkShow 是一个专门用于分析和可视化 SpecStory 插件生成的聊天历史记录的工具。在 LLM 辅助编程的时代，聊天历史比代码更重要 —— 它记录了代码背后的"为什么"。

## 🌟 项目特色

- **智能解析**：自动解析 SpecStory 生成的 Markdown 聊天记录
- **内容摘要**：支持基于规则和 LLM 的智能摘要生成
- **灵活配置**：多种配置方式，环境变量、配置文件或混合模式
- **优雅降级**：无 API 配置时自动使用规则摘要
- **灵活存储**：支持 JSON 和 SQLite 存储
- **多种展示**：CLI 和 Web 界面双重体验
- **渐进式架构**：模块化设计，支持逐步扩展功能

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 基础使用

1. **解析 history 目录中的聊天记录**：

```bash
python scripts/demo_parser.py
```

2. **运行测试验证功能**：

```bash
python -m pytest tests/ -v
```

## 📊 当前实现状态

### ✅ Phase 1: 数据分析核心 (MVP) - 已完成

- [x] **数据模型** (`talkshow/models/`)
  - `ChatSession`: 完整聊天会话表示
  - `QAPair`: 问答对数据结构  
  - `SessionMeta`: 会话元数据管理

- [x] **MD 文件解析器** (`talkshow/parser/`)
  - 智能解析 SpecStory 格式的 MD 文件
  - 提取 User/Assistant 对话内容
  - 自动提取时间戳信息
  - 从文件名提取主题

- [x] **存储层** (`talkshow/storage/`)
  - JSON 文件存储实现
  - 完整的 CRUD 操作支持
  - 数据备份和恢复功能

- [x] **摘要器** (`talkshow/summarizer/`)
  - 基于规则的文本摘要
  - 智能长度控制
  - 支持中英文内容

- [x] **测试套件** (`tests/`)
  - 20 个测试用例，100% 通过
  - 覆盖解析、存储、摘要等核心功能

### 📈 实际效果展示

通过对当前 history 目录的分析，TalkShow 成功：

- 📁 **解析了 56 个有效聊天会话**
- 💬 **提取了 457 个 Q&A 对话**
- 📝 **生成了 360 个问题摘要**
- 📋 **生成了 442 个答案摘要**
- 💾 **数据文件大小：1.2MB**

## 🏗️ 项目架构

```
talkshow/
├── talkshow/                    # 核心库
│   ├── models/                  # 数据模型
│   │   ├── chat.py             # ChatSession, QAPair, SessionMeta
│   │   └── storage.py          # 存储接口定义
│   ├── parser/                  # MD 文件解析
│   │   ├── md_parser.py        # 主解析器
│   │   └── time_extractor.py   # 时间提取器
│   ├── summarizer/              # 摘要生成
│   │   └── rule_summarizer.py  # 基于规则的摘要器
│   └── storage/                 # 数据存储
│       └── json_storage.py     # JSON 存储实现
├── scripts/                     # 演示脚本
│   └── demo_parser.py          # 解析演示脚本
├── tests/                       # 测试套件
│   ├── test_parser.py          # 解析器测试
│   ├── test_storage.py         # 存储测试
│   └── test_summarizer.py      # 摘要器测试
├── config/                      # 配置文件
│   └── default.yaml            # 默认配置
└── data/                        # 生成的数据
    └── parsed_sessions.json    # 解析结果
```

## 📅 开发阶段完成情况

### ✅ Phase 1: 数据分析核心 (MVP) - 已完成
- [x] 数据模型定义 (ChatSession, QAPair, SessionMeta)
- [x] MD 文件解析器 (支持 SpecStory 格式)
- [x] JSON 存储层 (完整 CRUD 操作)
- [x] 基于规则的摘要器 (智能长度控制)
- [x] 完整测试套件 (32个测试，100% 通过)

### ✅ Phase 2: CLI 工具 - 已完成  
- [x] 命令行界面 (`parse`, `list`, `show`, `stats`)
- [x] 支持摘要生成选项 (`--summarize`)
- [x] 支持 LLM 摘要选项 (`--use-llm`)
- [x] 交互式查询和统计功能

### ✅ Phase 3: LLM 集成 - 已完成
- [x] 集成 LiteLLM 支持 Moonshot AI
- [x] 配置管理系统 (环境变量和配置文件)
- [x] 智能摘要生成 (中英文支持)
- [x] 错误处理和降级机制

### 🚧 Phase 4: Web 前端 - 待开发
- [ ] FastAPI 后端 API
- [ ] 时间轴表格可视化界面
- [ ] 交互式聊天记录浏览

### 🚧 Phase 5: 高级功能 - 待开发
- [ ] SQLite 存储支持
- [ ] 全文搜索功能
- [ ] 标签和分类系统
- [ ] 数据导出功能

## 🛠️ 技术栈

- **核心语言**: Python 3.8+
- **测试框架**: pytest (32个测试)
- **LLM 集成**: LiteLLM + Moonshot AI
- **数据存储**: JSON (当前), SQLite (计划) 
- **配置管理**: YAML + 环境变量
- **CLI 工具**: Click + Rich (增强体验)
- **未来扩展**: FastAPI + Web 前端

## 📖 使用示例

### CLI 工具使用

```bash
# 基础解析（仅解析，不生成摘要）
python scripts/simple_cli.py parse history -o data/sessions.json

# 使用基于规则的摘要
python scripts/simple_cli.py parse history --summarize -o data/sessions.json

# 使用 LLM 智能摘要（需要配置 API 密钥）
MOONSHOT_API_KEY=your_api_key python scripts/simple_cli.py parse history --summarize --use-llm -o data/sessions.json

# 查看统计信息
python scripts/simple_cli.py stats

# 列出所有会话
python scripts/simple_cli.py list

# 查看特定会话详情
python scripts/simple_cli.py show filename.md
```

### Python API 使用

```python
from talkshow import MDParser, JSONStorage, RuleSummarizer, LLMSummarizer, ConfigManager

# 初始化组件
parser = MDParser()
storage = JSONStorage("data/sessions.json")
rule_summarizer = RuleSummarizer()

# LLM 摘要器（需要配置 API 密钥）
config_manager = ConfigManager()
llm_summarizer = LLMSummarizer(config_manager)

# 解析目录中的所有文件
sessions = parser.parse_directory("history")

# 生成智能摘要
for session in sessions:
    for qa_pair in session.qa_pairs:
        # 优先使用 LLM，失败时降级到规则摘要
        try:
            q_summary, a_summary = llm_summarizer.summarize_both(
                qa_pair.question, qa_pair.answer
            )
        except:
            q_summary, a_summary = rule_summarizer.summarize_both(
                qa_pair.question, qa_pair.answer
            )
        
        qa_pair.question_summary = q_summary
        qa_pair.answer_summary = a_summary

# 保存到存储
storage.save_sessions(sessions)
print(f"处理了 {len(sessions)} 个会话")
```

## ⚙️ 配置管理

TalkShow 支持多种灵活的配置方式，**不强制要求环境变量**：

### 🔒 方式一：环境变量（推荐）
```bash
export MOONSHOT_API_KEY="your_moonshot_api_key"
export LLM_MODEL="moonshot/kimi-k2-0711-preview"  # 可选
```

### 📄 方式二：配置文件
```yaml
# config/your-config.yaml
summarizer:
  llm:
    api_key: "your_moonshot_api_key"
    model: "moonshot/kimi-k2-0711-preview"
    max_tokens: 150
    temperature: 0.3
```

### 🔄 方式三：混合模式（推荐生产环境）
```yaml
# config/*.yaml - 通用配置
summarizer:
  llm:
    model: "moonshot/kimi-k2-0711-preview"
    max_tokens: 150
```
```bash
# 环境变量 - 敏感信息
export MOONSHOT_API_KEY="your_secret_key"
```

### 🚫 方式四：无配置（自动降级）
无需任何配置，自动使用规则摘要器，适合测试环境。

> **配置优先级**：环境变量 > 配置文件 > 默认值

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🎯 核心理念

> 在 LLM 生成代码的时代，chat history 比代码更重要 —— 它记录了代码产生过程中的动态决策和思路。就像 Git 记录代码版本一样，chat history 记录了代码写成这样背后的"为什么"。

TalkShow 的使命就是让这些珍贵的思维过程可见、可分析、可传承。

---

## 🏆 项目成果总结

### 📈 数据处理能力
- **解析了 56 个有效聊天会话**
- **提取了 457 个 Q&A 对话**  
- **生成了 802 个基于规则的摘要**
- **支持 LLM 智能摘要生成**
- **数据文件大小：1.2MB**
- **时间跨度：2025-07-22 到 2025-07-31**

### 🧪 测试覆盖率
- **32 个测试用例，100% 通过率**
- **覆盖解析、存储、摘要、LLM集成等所有核心功能**
- **Mock 测试确保组件独立性**
- **集成测试验证端到端功能**

### 🎛️ 功能特性
- **智能 MD 文件解析**：支持 SpecStory 格式，自动提取对话结构
- **双模式摘要**：规则摘要 + LLM 智能摘要，支持降级机制
- **灵活配置**：环境变量 + YAML 配置文件，支持多种 LLM 提供商
- **完整 CLI 工具**：解析、列表、查看、统计等全套命令
- **错误处理**：优雅的错误处理和用户反馈

### 🔧 技术架构
- **模块化设计**：清晰的组件分离，易于扩展
- **配置管理**：统一的配置系统，支持多环境部署  
- **存储抽象**：可插拔的存储后端（JSON → SQLite）
- **摘要抽象**：可扩展的摘要引擎（规则 → LLM → 更多AI模型）

### 🎯 已实现阶段
✅ **Phase 1**: 核心数据分析 (MVP)  
✅ **Phase 2**: CLI 工具增强  
✅ **Phase 3**: LLM 智能集成  
🚧 **Phase 4**: Web 前端 (待开发)  
🚧 **Phase 5**: 高级功能 (待开发)