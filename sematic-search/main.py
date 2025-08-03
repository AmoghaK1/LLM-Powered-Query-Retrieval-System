import os
import sys
import nltk
from nltk.tokenize import sent_tokenize
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Download required NLTK data
nltk.download('punkt_tab')

# Add the llm-parser directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'llm-parser'))
from main import parse_query_with_gemini

class SemanticSearch:
    def __init__(self, text_file_path):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.chunks = []
        self.index = None
        self.chunk_map = {}
        self.load_and_process_text(text_file_path)
    
    def load_and_process_text(self, text_file_path):
        """Load text from file and create chunks"""
        with open(text_file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Split into chunks of 3 sentences
        self.chunks = self.split_into_chunks(text, max_sentences=3)
        
        # Create embeddings
        chunk_embeddings = self.model.encode(self.chunks)
        
        # Build FAISS index
        self.index = faiss.IndexFlatL2(chunk_embeddings.shape[1])
        self.index.add(np.array(chunk_embeddings))
        
        # Create chunk mapping
        self.chunk_map = {i: chunk for i, chunk in enumerate(self.chunks)}
    
    def split_into_chunks(self, text, max_sentences=3):
        """Split text into chunks of sentences"""
        sentences = sent_tokenize(text)
        return [' '.join(sentences[i:i+max_sentences]) for i in range(0, len(sentences), max_sentences)]
    
    def search_relevant_chunks(self, query, top_k=5):
        """Search for relevant chunks based on query"""
        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(np.array(query_embedding), top_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            results.append({
                'chunk': self.chunk_map[idx],
                'score': float(distances[0][i])
            })
        return results
    
    def answer_query(self, user_query):
        """Process user query and return relevant information"""
        print(f"Query: {user_query}")
        print("-" * 50)
        
        # Parse query with Gemini
        parsed_query = parse_query_with_gemini(user_query)
        print(f"Parsed Query: {parsed_query}")
        print("-" * 50)
        
        # Search for relevant chunks
        relevant_chunks = self.search_relevant_chunks(user_query)
        
        print("Relevant Information:")
        for i, result in enumerate(relevant_chunks, 1):
            print(f"\n{i}. Score: {result['score']:.4f}")
            print(f"Content: {result['chunk']}")
        
        return relevant_chunks

# Initialize semantic search
text_file = r"g:\PROGRAMMING\Hackathon\Bajaj - LLM Query Retrieval\extracted_Arogya Sanjeevani Policy\text\pdf_text.txt"
search_engine = SemanticSearch(text_file)

# Test query
query = "Does this policy cover knee surgery, and what are the conditions?"
results = search_engine.answer_query(query)
