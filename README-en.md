# PageIndex - PDF Document Structure Analyzer
[![中文](https://img.shields.io/badge/语言-中文-red)](README.md) 
[![English](https://img.shields.io/badge/language-English-blue)](readme-en.md)
A PDF document structure analysis tool based on Large Language Models (LLM) that can automatically extract document table of contents structure and generate hierarchical JSON format output.

This project is a decoupled version of [Vectify AI](https://vectify.ai/)'s [PageIndex](https://github.com/VectifyAI/PageIndex.git) with enhanced logging capabilities.

Original Repository: [PageIndex](https://github.com/VectifyAI/PageIndex.git)

## Features

- 🔍 **Smart TOC Detection**: Automatically detect table of contents pages and page numbers in PDFs
- 📊 **Hierarchical Structure Generation**: Build complete document hierarchical structure including chapters, sub-chapters, etc.
- 🤖 **LLM-Driven**: Use large language models for content understanding and structure analysis
- 📝 **Multiple Output Formats**: Support adding node IDs, summaries, original text, and other information
- ⚡ **Asynchronous Processing**: Support concurrent processing to improve efficiency
- 📋 **Detailed Logging**: Use Rich library for beautiful console output and detailed logs
- 🌐 **Web API Support**: Provide RESTful API interfaces with asynchronous task processing
- 📁 **File Upload/Download**: Support online PDF upload and result file download

## Installation

1. Clone the project
```bash
git clone <repository-url>
cd pageindex
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Configure environment variables
```bash
# Create .env file, you can refer to .env.example
cp .env.example .env
# Edit the .env file to configure your API keys
```

## Environment Configuration

Configure your LLM API keys in the `.env` file:

```env
# DeepSeek (default)
DEEPSEEK_API_KEY="your-deepseek-api-key"
DEEPSEEK_MODEL="deepseek-chat"
DEEPSEEK_BASE_URL="https://api.deepseek.com/v1"

# Other supported models
CHATGPT_API_KEY="your-openai-api-key"
CLAUDE_API_KEY="your-claude-api-key"
GEMINI_API_KEY="your-gemini-api-key"
```

## Usage

### Method 1: Command Line Usage

#### Basic Usage

```bash
python main.py --pdf_path path/to/your/document.pdf
```

#### Complete Parameters

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

### Method 2: Web API Usage

#### Start API Server

```bash
# Start FastAPI server
python api_main.py

# Or use uvicorn directly
uvicorn api_main:app --host 0.0.0.0 --port 8000 --reload
```

After the service starts, visit `http://localhost:8000/docs` to view the API documentation.

#### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `POST /api/process-pdf/` | POST | Upload PDF and start processing |
| `GET /api/status/{task_id}` | GET | Query task status |
| `GET /api/download/{task_id}` | GET | Download processing results |

#### Usage Examples

1. **Upload PDF and start processing**:
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

2. **Query task status**:
```bash
curl "http://localhost:8000/api/status/{task_id}"
```

3. **Download results**:
```bash
curl -O "http://localhost:8000/api/download/{task_id}"
```

### Parameter Description

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pdf_path` / `pdf_file` | str/file | - | PDF file path or uploaded file |
| `model` | str | deepseek-chat | LLM model to use |
| `toc_check_pages` | int | 20 | Number of pages to check for table of contents |
| `max_pages_per_node` | int | 10 | Maximum number of pages per node |
| `max_tokens_per_node` | int | 20000 | Maximum number of tokens per node |
| `if_add_node_id` | str | yes | Whether to add node ID |
| `if_add_node_summary` | str | no | Whether to add node summary |
| `if_add_doc_description` | str | yes | Whether to add document description |
| `if_add_node_text` | str | no | Whether to add node original text |

## Output Format

After processing, a structured JSON file will be generated:

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

## Project Structure

```
pageindex/
├── api/                         # Web API modules
│   ├── __init__.py
│   ├── routers/                 # API routes
│   │   ├── __init__.py
│   │   └── pdf_processing.py    # PDF processing routes
│   └── services.py              # API service layer
├── app/
│   ├── core/                    # Core functionality modules
│   │   ├── document_parser.py   # Main document parser
│   │   ├── toc_discovery.py     # TOC discovery
│   │   ├── toc_structuring_llm.py # Structure processing
│   │   ├── toc_indexing.py      # Page indexing
│   │   ├── toc_validation_llm.py # Validation module
│   │   └── toc_utils.py         # Utility functions
│   └── utils/                   # Utility modules
│       ├── config_utils.py      # Configuration management
│       ├── pdf_utils.py         # PDF processing
│       ├── text_utils.py        # Text processing
│       ├── openai_api.py        # LLM API interface
│       ├── logging_utils.py     # Logging utilities
│       └── ...
├── docs/                        # Documentation directory
├── logs/                        # Log files
├── results/                     # Command line mode output results
├── api_results/                 # API mode output results
├── uploads_api/                 # API upload file temporary directory
├── main.py                      # Command line program entry
├── api_main.py                  # Web API program entry
└── requirements.txt             # Dependencies list
```

## Workflow

1. **PDF Parsing**: Use PyPDF2 and PyMuPDF to extract text content
2. **TOC Detection**: Intelligently identify table of contents pages in documents
3. **Structure Analysis**: Use LLM to analyze document hierarchical structure
4. **Page Mapping**: Map structure to actual page numbers
5. **Validation and Correction**: Validate result accuracy and automatically correct errors
6. **Output Generation**: Generate standardized JSON structure

## Core Functionality Modules

### TOC Discovery ([`toc_discovery.py`](app/core/toc_discovery.py))
- Automatically detect table of contents pages in PDFs
- Extract TOC content and page number information

### Structure Processing ([`toc_structuring_llm.py`](app/core/toc_structuring_llm.py))
- Convert raw TOC to structured JSON format
- Support hierarchical chapter organization

### Page Indexing ([`toc_indexing.py`](app/core/toc_indexing.py))
- Calculate page offset
- Handle mapping between TOC page numbers and actual page numbers

### Validation Module ([`toc_validation_llm.py`](app/core/toc_validation_llm.py))
- Validate accuracy of extraction results
- Automatically correct incorrect page mappings

### Web API ([`api/`](api/))
- Provide RESTful API interfaces
- Support asynchronous task processing and status queries
- File upload and download functionality
- Task status management

## API Support

Support multiple LLM service providers:
- [DeepSeek](https://api.deepseek.com) (default)
- [OpenAI GPT](https://api.openai.com)
- [Anthropic Claude](https://api.anthropic.com)
- [Google Gemini](https://generativelanguage.googleapis.com)

## Logging and Monitoring

The project uses Rich library for beautiful console output and detailed JSON logging:
- Real-time processing progress display
- Detailed error information and debug logs
- Processing result accuracy statistics
- API request and response logs

## Deployment Recommendations

### Production Environment Deployment

1. **Deploy with Gunicorn**:
```bash
pip install gunicorn
gunicorn api_main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

2. **Deploy with Docker**:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "api_main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

3. **Deploy with Docker Compose**:

Create `docker-compose.yml` file:
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

  # Optional: Add Redis for production environment task status storage
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

Start services:
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f pageindex-api

# Stop services
docker-compose down
```

4. **Task Status Storage**: For production environments, it's recommended to use Redis or a database instead of in-memory storage for task status.

## Contributing

Welcome to submit Issues and Pull Requests to improve this project.

## License

MIT License

## Author

**Shibo Li** - Project creator and main developer

Please go to the original repository to Fork and Star
[PageIndex](https://github.com/VectifyAI/PageIndex.git)

---

For more help, please check the code comments or submit an Issue.