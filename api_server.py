from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
import os
import sys
import requests
import tempfile
import importlib.util
from pathlib import Path

# Add the directories to the path
sys.path.append(str(Path(__file__).parent / "clause-matcher"))
sys.path.append(str(Path(__file__).parent / "pdf-extract"))

# Import with specific module names to avoid conflicts
import importlib.util
pdf_spec = importlib.util.spec_from_file_location("pdf_main", str(Path(__file__).parent / "pdf-extract" / "main.py"))
pdf_main = importlib.util.module_from_spec(pdf_spec)
pdf_spec.loader.exec_module(pdf_main)

clause_spec = importlib.util.spec_from_file_location("clause_main", str(Path(__file__).parent / "clause-matcher" / "main.py"))
clause_main = importlib.util.module_from_spec(clause_spec)
clause_spec.loader.exec_module(clause_main)

# Now we can use the functions
PolicyQueryBot = clause_main.PolicyQueryBot
create_output_structure = pdf_main.create_output_structure
extract_from_pdf = pdf_main.extract_from_pdf

def download_pdf(url: str, temp_dir: str) -> str:
    """Download PDF from URL and return local file path"""
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Generate filename from URL or use default
        filename = url.split('/')[-1].split('?')[0]
        if not filename.endswith('.pdf'):
            filename = 'document.pdf'
        
        pdf_path = os.path.join(temp_dir, filename)
        
        with open(pdf_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return pdf_path
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to download PDF: {str(e)}")

def process_pdf_url(pdf_url: str) -> str:
    """Download PDF and extract text, return path to extracted text file"""
    try:
        # Create temporary directory for processing
        temp_dir = tempfile.mkdtemp()
        
        # Check if it's a local file path or URL
        if os.path.exists(pdf_url):
            # It's a local file
            pdf_path = pdf_url
        else:
            # It's a URL - download it
            pdf_path = download_pdf(pdf_url, temp_dir)
        
        # Extract content using existing PDF extractor
        folders = create_output_structure(pdf_path)
        extract_from_pdf(pdf_path, folders)
        
        # Return path to extracted text
        text_file = os.path.join(folders['text'], "pdf_text.txt")
        return text_file
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")

app = FastAPI(
    title="Retrieval System API",
    description="API for LLM Query Retrieval System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Expected bearer token (as shown in the documentation)
EXPECTED_TOKEN = "fdf120852ce30af3c730346cd2905b97173db2e1b0ed00eb407c16166a3bb57a"

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != EXPECTED_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

# Request/Response models
class QueryRequest(BaseModel):
    documents: List[str]
    questions: List[str]

class Answer(BaseModel):
    question: str
    answer: str

class QueryResponse(BaseModel):
    answers: List[Answer]

# Don't initialize bot here - we'll create it dynamically for each request

@app.post("/api/v1/hackrx/run", response_model=QueryResponse)
async def run_submission(
    request: QueryRequest,
    token: str = Depends(verify_token)
):
    """
    Run submissions - process questions against the provided documents
    """
    try:
        answers = []
        
        # Process the first document URL (for now, handle one document)
        if not request.documents:
            raise HTTPException(status_code=400, detail="No documents provided")
        
        document_url = request.documents[0]
        
        # Check if it's a URL, local PDF, or local text file
        if document_url.startswith(('http://', 'https://')):
            # Download and process PDF from URL
            text_file = process_pdf_url(document_url)
        elif document_url.endswith('.pdf'):
            # Local PDF file - extract text
            text_file = process_pdf_url(document_url)
        else:
            # Assume it's already a text file
            text_file = document_url
        
        # Initialize bot with the processed document
        bot = PolicyQueryBot(text_file, verbose=False)
        
        # Process each question
        for question in request.questions:
            # Use our existing bot to get the answer
            answer_text = bot.get_final_answer(question)
            
            answers.append(Answer(
                question=question,
                answer=answer_text
            ))
        
        return QueryResponse(answers=answers)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing request: {str(e)}"
        )

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Retrieval System API", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
