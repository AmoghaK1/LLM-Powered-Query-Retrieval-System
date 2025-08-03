# LLM Query Retrieval System

A complete system for processing natural language queries against policy documents using semantic search and LLM-based question answering.

## Quick Start

### 1. Activate Virtual Environment
```bash
# Activate your virtual environment first
venv\Scripts\activate
```

### 2. Install Dependencies (if not already installed)
```bash
pip install -r requirements.txt
```

### 3. Start the API Server
```bash
# Option 1: Use the batch file (Windows)
start_server.bat

# Option 2: Manual start
python api_server.py
```

The server will start on `http://localhost:8000`

### 2. API Documentation
- Interactive docs: `http://localhost:8000/docs`
- API base URL: `http://localhost:8000/api/v1`

### 3. Test the API
```bash
python test_api.py
```

## API Usage

### Authentication
Include the bearer token in all requests:
```
Authorization: Bearer fdf120852ce30af3c730346cd2905b97173db2e1b0ed00eb407c16166a3bb57a
```

### Main Endpoint
**POST** `/api/v1/hackrx/run`

**Request:**
```json
{
    "documents": ["https://example.com/policy.pdf"],
    "questions": [
        "What is the waiting period for pre-existing conditions?",
        "Does this policy cover maternity expenses?"
    ]
}
```

**Response:**
```json
{
    "answers": [
        {
            "question": "What is the waiting period for pre-existing conditions?",
            "answer": "The waiting period for pre-existing diseases is 2 years..."
        }
    ]
}
```

## System Components

1. **PDF Extraction** (`pdf-extract/`) - Extracts text, tables, and images from PDFs
2. **LLM Parser** (`llm-parser/`) - Converts natural language to structured queries
3. **Semantic Search** (`sematic-search/`) - FAISS-based vector search
4. **Clause Matcher** (`clause-matcher/`) - Main query processing engine
5. **API Server** (`api_server.py`) - REST API wrapper

## Architecture

```
Input Documents → LLM Parser → Embedding Search → Clause Matching → Logic Evaluation → JSON Output
```

## Files Structure

- `api_server.py` - Main FastAPI server
- `requirements.txt` - Python dependencies
- `test_api.py` - API testing script
- `start_server.bat` - Windows startup script
- `clause-matcher/main.py` - Core query processing logic

## Dependencies

- FastAPI - Web framework
- Sentence Transformers - Embeddings
- FAISS - Vector search
- Google Generative AI - LLM queries
- NLTK - Text processing

## Notes

- The system is pre-loaded with the Arogya Sanjeevani Policy document
- Supports natural language queries about insurance policies
- Returns structured answers based on semantic search and LLM processing
