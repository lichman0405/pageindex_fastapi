# PageIndex - PDF Document Structure Analyzer

一个基于大语言模型(LLM)的PDF文档结构分析工具，能够自动提取文档的目录结构并生成层次化的JSON格式输出。

这个项目是对[Vectify AI](https://vectify.ai/)的[PageIndex](https://github.com/VectifyAI/PageIndex.git)的一个解耦项目，并且丰富化了Logs。

原Repo请看：[PageIndex](https://github.com/VectifyAI/PageIndex.git)

## 功能特点

- 🔍 **智能目录检测**: 自动检测PDF中的目录页面和页码信息
- 📊 **层次结构生成**: 构建完整的文档层次结构，包括章节、子章节等
- 🤖 **LLM驱动**: 使用大语言模型进行内容理解和结构分析
- 📝 **多种输出格式**: 支持添加节点ID、摘要、原文等信息
- ⚡ **异步处理**: 支持并发处理提高效率
- 📋 **详细日志**: 使用Rich库提供美观的日志输出

## 安装

1. 克隆项目
```bash
git clone <repository-url>
cd pageindex
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
```bash
# 建立.env文件，可以参考.env.example
cp .env.example .env
# 编辑 .env 文件，配置你的API密钥
```

## 环境配置

在 `.env` 文件中配置你的LLM API密钥：

```env
# DeepSeek (默认)
DEEPSEEK_API_KEY="your-deepseek-api-key"
DEEPSEEK_MODEL="deepseek-chat"
DEEPSEEK_BASE_URL="https://api.deepseek.com/v1"

# 其他支持的模型
CHATGPT_API_KEY="your-openai-api-key"
CLAUDE_API_KEY="your-claude-api-key"
GEMINI_API_KEY="your-gemini-api-key"
```

## 使用方法

### 基本用法

```bash
python main.py --pdf_path path/to/your/document.pdf
```

### 完整参数

```bash
python main.py \
  --pdf_path path/to/your/document.pdf \
  --model deepseek-chat \
  --toc-check-pages 20 \
  --max-pages-per-node 10 \
  --max-tokens-per-node 20000 \
  --if-add-node-id yes \
  --if-add-node-summary no \
  --if-add-doc-description yes \
  --if-add-node-text no
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--pdf_path` | str | - | PDF文件路径 |
| `--model` | str | deepseek-chat | 使用的LLM模型 |
| `--toc-check-pages` | int | 20 | 检查目录的页面数量 |
| `--max-pages-per-node` | int | 10 | 每个节点的最大页面数 |
| `--max-tokens-per-node` | int | 20000 | 每个节点的最大token数 |
| `--if-add-node-id` | str | yes | 是否添加节点ID |
| `--if-add-node-summary` | str | no | 是否添加节点摘要 |
| `--if-add-doc-description` | str | yes | 是否添加文档描述 |
| `--if-add-node-text` | str | no | 是否添加节点原文 |

## 输出格式

处理完成后，会在 `results/` 目录下生成结构化的JSON文件：

```json
{
  "doc_name": "four-lectures.pdf",
  "structure": [
    {
      "title": "Four Lectures on Standard ML",
      "start_index": 1,
      "end_index": 1,
      "nodes": [
        {
          "title": "ML at a Glance",
          "start_index": 2,
          "end_index": 2,
          "nodes": [
            {
              "title": "An ML session",
              "start_index": 2,
              "end_index": 4,
              "node_id": "0002"
            }
          ],
          "node_id": "0001"
        }
      ],
      "node_id": "0000"
    }
  ]
}
```

## 项目结构

```
pageindex/
├── app/
│   ├── core/                    # 核心功能模块
│   │   ├── document_parser.py   # 主要文档解析器
│   │   ├── toc_discovery.py     # 目录发现
│   │   ├── toc_structuring_llm.py # 结构化处理
│   │   ├── toc_indexing.py      # 页码索引
│   │   ├── toc_validation_llm.py # 验证模块
│   │   └── toc_utils.py         # 工具函数
│   └── utils/                   # 工具模块
│       ├── config_utils.py      # 配置管理
│       ├── pdf_utils.py         # PDF处理
│       ├── text_utils.py        # 文本处理
│       ├── openai_api.py        # LLM API接口
│       ├── logging_utils.py     # 日志工具
│       └── ...
├── docs/                        # 文档目录
├── logs/                        # 日志文件
├── results/                     # 输出结果
├── main.py                      # 主程序入口
└── requirements.txt             # 依赖列表
```

## 工作流程

1. **PDF解析**: 使用PyPDF2和PyMuPDF提取文本内容
2. **目录检测**: 智能识别文档中的目录页面
3. **结构分析**: 使用LLM分析文档的层次结构
4. **页码映射**: 将结构与实际页码进行映射
5. **验证修正**: 验证结果准确性并自动修正错误
6. **输出生成**: 生成标准化的JSON结构

## 核心功能模块

### 目录发现 ([`toc_discovery.py`](app/core/toc_discovery.py))
- 自动检测PDF中的目录页面
- 提取目录内容和页码信息

### 结构化处理 ([`toc_structuring_llm.py`](app/core/toc_structuring_llm.py))
- 将原始目录转换为结构化JSON格式
- 支持层次化的章节组织

### 页码索引 ([`toc_indexing.py`](app/core/toc_indexing.py))
- 计算页码偏移量
- 处理目录页码与实际页码的映射关系

### 验证模块 ([`toc_validation_llm.py`](app/core/toc_validation_llm.py))
- 验证提取结果的准确性
- 自动修正错误的页码映射

## API支持

支持多种LLM服务商：
- [DeepSeek](https://api.deepseek.com) (默认)
- [OpenAI GPT](https://api.openai.com)
- [Anthropic Claude](https://api.anthropic.com)
- [Google Gemini](https://generativelanguage.googleapis.com)

## 日志与监控

项目使用Rich库提供美观的控制台输出和详细的JSON日志记录：
- 实时处理进度显示
- 详细的错误信息和调试日志
- 处理结果的准确性统计

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 许可证

MIT License

## 作者

**Shibo Li** - 项目创建者和主要开发者

请去原Repo进行Fork和Star
[PageIndex](https://github.com/VectifyAI/PageIndex.git)

---

如需更多帮助，请查看代码注释或提交。
