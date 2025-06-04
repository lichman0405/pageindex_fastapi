# PageIndex - PDF Document Structure Analyzer
[![中文](https://img.shields.io/badge/语言-中文-red)](README.md) 
[![English](https://img.shields.io/badge/language-English-blue)](readme-en.md)

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
- 🌐 **Web API支持**: 提供RESTful API接口，支持异步任务处理
- 📁 **文件上传下载**: 支持在线PDF上传和结果文件下载

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

### 方式1: 命令行使用

#### 基本用法

```bash
python main.py --pdf_path path/to/your/document.pdf
```

#### 完整参数

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

### 方式2: Web API 使用

#### 启动API服务器

```bash
# 启动FastAPI服务器
python api_main.py

# 或者使用uvicorn直接启动
uvicorn api_main:app --host 0.0.0.0 --port 8000 --reload
```

服务启动后访问 `http://localhost:8000/docs` 查看API文档。

#### API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `POST /api/process-pdf/` | POST | 上传PDF并开始处理 |
| `GET /api/status/{task_id}` | GET | 查询任务状态 |
| `GET /api/download/{task_id}` | GET | 下载处理结果 |

#### 使用示例

1. **上传PDF并开始处理**:
```bash
curl -X POST "http://localhost:8000/api/process-pdf/" \
  -F "pdf_file=@your_document.pdf" \
  -F "model=deepseek-chat" \
  -F "toc_check_pages=20" \
  -F "max_pages_per_node=10" \
  -F "max_tokens_per_node=20000" \
  -F "if_add_node_id=yes" \
  -F "if_add_node_summary=no" \
  -F "if_add_doc_description=yes" \
  -F "if_add_node_text=no"
```

2. **查询任务状态**:
```bash
curl "http://localhost:8000/api/status/{task_id}"
```

3. **下载结果**:
```bash
curl -O "http://localhost:8000/api/download/{task_id}"
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `pdf_path` / `pdf_file` | str/file | - | PDF文件路径或上传文件 |
| `model` | str | deepseek-chat | 使用的LLM模型 |
| `toc_check_pages` | int | 20 | 检查目录的页面数量 |
| `max_pages_per_node` | int | 10 | 每个节点的最大页面数 |
| `max_tokens_per_node` | int | 20000 | 每个节点的最大token数 |
| `if_add_node_id` | str | yes | 是否添加节点ID |
| `if_add_node_summary` | str | no | 是否添加节点摘要 |
| `if_add_doc_description` | str | yes | 是否添加文档描述 |
| `if_add_node_text` | str | no | 是否添加节点原文 |

## 输出格式

处理完成后，会生成结构化的JSON文件：

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
├── api/                         # Web API模块
│   ├── __init__.py
│   ├── routers/                 # API路由
│   │   ├── __init__.py
│   │   └── pdf_processing.py    # PDF处理路由
│   └── services.py              # API服务层
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
├── results/                     # 命令行模式输出结果
├── api_results/                 # API模式输出结果
├── uploads_api/                 # API上传文件临时目录
├── main.py                      # 命令行程序入口
├── api_main.py                  # Web API程序入口
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

### Web API ([`api/`](api/))
- 提供RESTful API接口
- 支持异步任务处理和状态查询
- 文件上传下载功能
- 任务状态管理

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
- API请求和响应日志

## 部署建议

### 生产环境部署

1. **使用Gunicorn部署**:
```bash
pip install gunicorn
gunicorn api_main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

2. **使用Docker部署**:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "api_main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

3. **使用Docker Compose部署**:

创建 `docker-compose.yml` 文件：
```yaml
version: '3.8'

services:
  pageindex-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - DEEPSEEK_MODEL=${DEEPSEEK_MODEL}
      - DEEPSEEK_BASE_URL=${DEEPSEEK_BASE_URL}
      - CHATGPT_API_KEY=${CHATGPT_API_KEY}
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    volumes:
      - ./logs:/app/logs
      - ./api_results:/app/api_results
      - ./uploads_api:/app/uploads_api
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/docs"]
      interval: 30s
      timeout: 10s
      retries: 3

  # 可选：添加Redis用于生产环境任务状态存储
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

启动服务：
```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f pageindex-api

# 停止服务
docker-compose down
```

4. **任务状态存储**: 生产环境建议使用Redis或数据库替代内存存储任务状态。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 许可证

MIT License

## 作者

**Shibo Li** - 项目创建者和主要开发者

请去原Repo进行Fork和Star
[PageIndex](https://github.com/VectifyAI/PageIndex.git)

---

如需更多帮助，请查看代码注释或提交Issue。