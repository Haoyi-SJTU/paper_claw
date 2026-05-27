# Paper-claw: 文献解析与论文写作辅助工具

![](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)

专为上海交通大学研究生打造的AI驱动学术写作解决方案。基于LLM自动化处理文献阅读、笔记整理、大纲生成和论文写作全流程，显著提升学术研究效率。
基于 LLM Agent 的学术论文阅读、总结与写作辅助工具。上传 PDF 论文，自动生成结构化摘要；基于已有文献素材，辅助撰写新论文并导出为 Word/Markdown 格式。

## 功能特性

### 论文库 (Paper Library)
- **PDF 解析**：上传 PDF 论文，自动提取全文文本、章节结构、参考文献
- **结构化摘要**：调用 LLM 生成研究问题、方法论、关键发现、结论、局限性、关键术语等结构化总结
- **摘要持久化**：摘要以 JSON 格式保存，可反复查阅和引用

### 写作助手 (Writing Assistant)
- **大纲生成**：根据主题、用户笔记和参考文献摘要，自动生成论文大纲
- **逐章节写作**：支持对每个章节添加个性化笔记，LLM 逐节生成草稿
- **参考文献引用**：自动在生成的文本中插入引用标记
- **文档导出**：一键导出为 Word (.docx) 和 Markdown (.md) 格式

### 设置 (Settings)
- **多模型支持**：OpenAI (GPT-4o)、Anthropic (Claude)、阿里云通义千问 (Qwen) 等
- **自定义 API 地址**：支持 DashScope 等第三方兼容接口
- **运行时切换**：在 UI 中随时切换 LLM 模型

## 项目结构

```
literature_claw/
├── app.py                              # Streamlit Web UI 主入口
├── pyproject.toml                      # 项目元数据与依赖声明
├── .env                                # API Key 与模型配置（不入库）
├── .env.example                        # 配置模板
├── src/literature_claw/
│   ├── config.py                       # 全局配置（读取 .env，定义模型映射）
│   ├── llm/
│   │   └── client.py                   # LLM 统一客户端（LiteLLM 封装）
│   ├── pdf/
│   │   └── reader.py                   # PDF 解析（PyMuPDF）
│   ├── summary/
│   │   └── summarizer.py               # 论文结构化摘要生成
│   ├── writing/
│   │   ├── assistant.py                # 论文写作辅助（大纲 + 章节生成）
│   │   └── templates/
│   │       └── paper_template.md       # Markdown 论文模板
│   ├── references/
│   │   └── manager.py                  # 参考文献管理（BibTeX 解析与格式化）
│   └── export/
│       └── exporter.py                 # 文档导出（Word / Markdown）
├── data/
│   ├── papers/                         # 上传的 PDF 原文
│   ├── summaries/                      # 生成的摘要 JSON
│   └── output/                         # 导出的论文文稿
└── tests/
    ├── test_reader.py                  # PDF 解析测试
    ├── test_summarizer.py              # 摘要解析测试
    └── test_exporter.py                # 文档导出测试
```

## 实现原理

### 架构总览

```
用户上传 PDF
    │
    ▼
┌──────────────┐      ┌──────────────┐     ┌──────────────┐
│  PDF Reader  │────▶│  Summarizer  │────▶│  JSON 摘要   │
│  (PyMuPDF)   │      │  (LLM)       │     │  持久化存储   │
└──────────────┘      └──────────────┘     └──────────────┘
                                                  │
                                                  ▼
┌──────────────┐      ┌──────────────┐       ┌──────────────┐
│  文档导出     │◀────│  写作助手     │◀────│  主题 + 笔记  │
│  (Word/MD)   │      │  (LLM)       │       │  + 参考文献   │
└──────────────┘      └──────────────┘       └──────────────┘
```

### PDF 解析 (`pdf/reader.py`)

使用 **PyMuPDF** 库提取 PDF 内容，输出为结构化的 `PaperData` 数据类：

- **文本提取**：逐页提取全文文本
- **章节识别**：通过正则表达式匹配学术论文常见章节标题（Abstract、Introduction、Methodology、Results、Conclusion 等）
- **参考文献提取**：定位 References/Bibliography 部分，按编号分割引用条目
- **元数据提取**：从 PDF 元数据中读取标题、作者、关键词等信息

### LLM 统一客户端 (`llm/client.py`)

基于 **LiteLLM** 封装统一的 LLM 调用接口：

- 通过 `provider/model` 格式标识模型（如 `openai/gpt-4o`、`anthropic/claude-sonnet`）
- 自动根据模型前缀选择对应的 API Key 和 Base URL
- 支持 OpenAI 兼容接口（DashScope）和 Anthropic 兼容接口的自定义 Base URL

### 论文摘要 (`summary/summarizer.py`)

采用 **Prompt Engineering** 策略，向 LLM 发送结构化提示词：

- 输入：论文全文（超过 30000 字符时截断）
- 输出：7 个结构化维度 —— 研究问题、方法论、关键发现、结论、局限性、关键术语、相关性
- 解析：通过正则表达式从 LLM 响应中提取各维度内容，封装为 `PaperSummary` 对象

### 写作辅助 (`writing/assistant.py`)

分两步完成论文生成：

1. **大纲生成**：将用户主题、笔记、参考文献摘要组合为 Prompt，LLM 生成包含多个章节的论文大纲（`PaperOutline`）
2. **逐章节草稿**：遍历大纲中的每个章节，将章节描述 + 其他章节上下文 + 相关参考文献 + 用户笔记组合为 Prompt，LLM 生成 500-1000 词的章节草稿

### 文档导出 (`export/exporter.py`)

- **Markdown**：使用 Jinja2 模板渲染，结构清晰易编辑
- **Word**：使用 python-docx 生成，设置 Times New Roman 12pt 字体、1.25 英寸页边距、段落首行缩进等学术排版格式

### 参考文献管理 (`references/manager.py`)

基于 **pybtex** 解析 BibTeX 文件：

- 支持 APA 和 IEEE 两种引用格式
- 自动格式化文内引用（如 `(Smith et al., 2020)` 或 `[1]`）和参考文献列表
- 支持按标题、作者、引用键搜索文献

## 使用方法

### 环境要求

- Python 3.11+
- LLM API 密钥（OpenAI / Anthropic / DashScope 任选其一）

### 安装

```bash
# 克隆项目
git clone <repo-url>
cd literature_claw

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 安装项目（含所有依赖）
pip install -e .

# 安装开发依赖（可选，用于运行测试）
pip install -e ".[dev]"
```

### 配置

复制 `.env.example` 为 `.env`，填入你的 API 配置：

**方式一：阿里云 DashScope（Anthropic 兼容接口）**
```env
ANTHROPIC_API_KEY=your-token-here
ANTHROPIC_API_BASE=https://your-dashscope-endpoint/apps/anthropic
DEFAULT_MODEL=qwen3.7-max
```

**方式二：阿里云 DashScope（OpenAI 兼容接口）**
```env
OPENAI_API_KEY=your-token-here
OPENAI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
DEFAULT_MODEL=qwen-plus
```

**方式三：OpenAI 官方**
```env
OPENAI_API_KEY=your-key-here
DEFAULT_MODEL=gpt-4o
```

**方式四：Anthropic 官方**
```env
ANTHROPIC_API_KEY=your-key-here
DEFAULT_MODEL=claude-sonnet-4-20250514
```

### 启动

```bash
streamlit run app.py
```

浏览器自动打开 `http://localhost:8501`。

### 使用流程

#### 1. 阅读与总结论文

1. 进入 **Paper Library** 页面
2. 上传 PDF 论文（支持批量上传）
3. 点击论文下方的 **Parse & Summarize** 按钮
4. 等待解析和摘要生成完成，查看结构化摘要

#### 2. 撰写论文

1. 进入 **Writing Assistant** 页面
2. 输入论文主题（如 "Deep Learning for Soft Robot Control"）
3. 在 Notes 中补充具体要求和素材
4. 在 Reference Papers 中选择要引用的已总结论文
5. 点击 **Generate Outline** 生成大纲
6. 展开每个章节，可添加个性化笔记后点击 **Draft Section** 生成草稿
7. 或点击 **Draft All Sections** 一次性生成所有章节
8. 点击 **Export to Word & Markdown** 导出文稿

#### 3. 切换模型

1. 进入 **Settings** 页面
2. 在下拉菜单中选择目标模型
3. 查看当前 API 配置状态

### 运行测试

```bash
pytest tests/ -v
```

## 技术栈

| 组件 | 技术 | 用途 |
|------|------|------|
| LLM 接口 | LiteLLM | 统一调用 OpenAI / Anthropic / DashScope 等多模型 |
| PDF 解析 | PyMuPDF (fitz) | 提取 PDF 文本、章节、元数据 |
| 文档生成 | python-docx | 生成 Word 格式学术论文 |
| 模板引擎 | Jinja2 | Markdown 模板渲染 |
| 文献管理 | pybtex | BibTeX 解析与引用格式化 |
| Web UI | Streamlit | 交互式 Web 界面 |
| 配置管理 | python-dotenv | 环境变量与 API Key 管理 |

## 支持的 LLM 模型

| 模型 | Provider | 说明 |
|------|----------|------|
| `gpt-4o` | OpenAI | 最强通用模型 |
| `gpt-4o-mini` | OpenAI | 轻量快速 |
| `claude-sonnet-4-20250514` | Anthropic | Claude Sonnet |
| `claude-haiku-3-5` | Anthropic | Claude Haiku，速度快 |
| `qwen-plus` | DashScope (OpenAI) | 通义千问 Plus |
| `qwen-turbo` | DashScope (OpenAI) | 通义千问 Turbo |
| `qwen-max` | DashScope (OpenAI) | 通义千问 Max |
| `qwen3.7-max` | DashScope (Anthropic) | 通义千问 3.7 Max |

可在 `config.py` 的 `AVAILABLE_MODELS` 中自行添加更多模型。

## 📄 许可证

本项目基于 MIT 许可证开源。

---

> 提示：学术诚信至关重要。本工具旨在辅助研究工作，生成内容需经学术判断和适当引用。请确保最终论文符合学术规范和学校要求。
