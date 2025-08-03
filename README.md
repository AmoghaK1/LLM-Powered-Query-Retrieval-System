# LLM Query Retrieval System

A complete system for processing natural language queries against policy documents using semantic search and LLM-based question answering.

## 🚀 Quick Setup for New Users

### 1. Clone the Repository
```bash
git clone https://github.com/AmoghaK1/LLM-Powered-Query-Retrieval-System.git
cd LLM-Powered-Query-Retrieval-System
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv sandbox

# Activate virtual environment
# Windows:
sandbox\Scripts\activate
# Linux/Mac:
source sandbox/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Get Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key (free with rate limits)
3. Copy the API key

### 5. Setup Environment Variables
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_actual_api_key_here
```
**⚠️ Never commit your .env file to GitHub!**

### 6. Add Your PDF Documents
- **Option A**: Place PDF files in the `documents/` folder and use just the filename
- **Option B**: Use full file paths
- **Option C**: Use direct URLs to publicly accessible PDFs

**Examples:**
```json
{
    "documents": ["policy.pdf"],              // 📁 Auto-searches in documents/ folder
    "documents": ["./documents/policy.pdf"],  // 📁 Relative path
    "documents": ["C:/path/to/policy.pdf"],   // 📁 Full path
    "documents": ["https://example.com/policy.pdf"]  // 🌐 URL
}
```

### 7. Start the API Server
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
    "documents": ["policy.pdf"],  // File in documents/ folder
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
