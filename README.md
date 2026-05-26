# 文献解析与论文写作智能辅助工具

![](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)

专为上海交通大学研究生打造的AI驱动学术写作解决方案。基于LLM自动化处理文献阅读、笔记整理、大纲生成和论文写作全流程，显著提升学术研究效率。

## 核心特性

### 智能文献管理
- **PDF智能解析**：自动提取学术PDF中的标题、摘要、方法、结论等关键信息
- **结构化摘要生成**：将复杂文献转化为标准化的JSON摘要，便于快速回顾与引用
- **参考文献管理**：自动整理引用格式，支持多种引文样式（IEEE、APA、GB/T 7714等）

### AI写作助手
- **智能大纲生成**：基于研究主题自动生成逻辑严谨的论文框架
- **章节内容辅助**：根据选定参考文献，协助撰写引言、方法论、分析等关键章节
- **多模型支持**：无缝切换GPT-4、Claude、DeepSeek等主流大语言模型

### 高效工作流
- **模板化写作**：内置上海交通大学学位论文LaTeX/Word模板
- **多格式导出**：一键导出为Word、Markdown或LaTeX格式
- **本地化管理**：所有文献、摘要和个人笔记安全存储于本地

## 系统架构

```
literature_claw/
├── app.py                          # Streamlit Web应用主界面
├── pyproject.toml                  # 项目配置与依赖管理
├── .env.example                    # API密钥配置文件模板
├── src/literature_claw/
│   ├── config.py                   # 全局配置管理
│   ├── llm/client.py               # 统一LLM客户端（支持OpenAI/Anthropic/DeepSeek）
│   ├── pdf/reader.py               # PDF解析引擎（基于PyMuPDF）
│   ├── summary/summarizer.py       # 论文结构化摘要生成器
│   ├── references/manager.py       # 参考文献管理器
│   ├── writing/assistant.py        # 论文写作智能辅助
│   ├── export/exporter.py          # 多格式文档导出（Word/Markdown）
│   └── writing/templates/          # SJTU学位论文模板库
├── data/                           # 运行时数据目录
│   ├── papers/                     # 原始PDF文献存储
│   ├── summaries/                  # 结构化摘要（JSON格式）
│   └── output/                     # 导出文稿目录
└── tests/                          # 单元测试套件
```

## 快速开始

### 环境准备

1. **克隆仓库**
```bash
git clone https://github.com/Haoyi-SJTU/paper_claw.git
cd paper_claw
```

2. **创建虚拟环境**
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

3. **安装依赖**
```bash
pip install -e .
```

### 配置API密钥

1. 复制环境变量模板文件：
```bash
cp .env.example .env
```

2. 编辑`.env`文件，填入您的API密钥：
```ini
# 支持多平台API密钥配置
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=your-claude-key-here
DEEPSEEK_API_KEY=your-deepseek-key-here

# 可选配置
MODEL_PREFERENCE=gpt-4o  # 默认使用模型
MAX_TOKENS=4096
```

### 启动应用

```bash
streamlit run app.py
```

启动后，在浏览器中访问控制台显示的地址（通常为 http://localhost:8501）

## 使用指南

### 1. 文献库管理
- **上传文献**：将PDF论文拖拽至上传区域
- **批量处理**：支持同时上传多篇文献，系统将自动排队处理
- **智能分类**：自动识别文献的研究领域和关键词

### 2. 文献阅读辅助
- **一键摘要**：点击任意文献，30秒内生成结构化摘要
- **要点提取**：自动标记研究问题、方法、创新点和局限
- **关联分析**：发现不同文献间的引用关系和主题关联

### 3. 论文写作流程
1. **主题设定**：输入研究课题和关键词
2. **文献选择**：从文献库中挑选相关参考文献
3. **大纲生成**：AI生成三级论文大纲，可手动调整
4. **章节撰写**：逐章节辅助写作，支持实时编辑
5. **参考文献自动生成**：系统自动整理引用格式

### 4. 导出与定制
- **格式选择**：Word（.docx）、Markdown（.md）或LaTeX
- **模板应用**：使用SJTU官方论文模板样式
- **参考文献样式**：支持多种学术期刊引文格式

## 🔧 配置选项

### 模型选择
支持多种大语言模型，可根据需求切换：
- **GPT-4o**：综合性能最佳，推理能力强
- **Claude 3.5 Sonnet**：长文本处理优秀
- **DeepSeek**：性价比高，中文优化

### 解析设置
- 支持中英文文献混合处理
- 可调整摘要详细程度（简洁/标准/详细）
- 自定义关键词提取数量

## 测试

运行测试套件确保功能正常：

```bash
pytest tests/ -v
```

## 📄 许可证

本项目基于 MIT 许可证开源。详见 LICENSE 文件。

---

> 提示：学术诚信至关重要。本工具旨在辅助研究工作，生成内容需经学术判断和适当引用。请确保最终论文符合学术规范和学校要求。
