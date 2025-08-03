import json
import os
import sys
from google.generativeai import GenerativeModel
import google.generativeai as genai
from dotenv import load_dotenv
import nltk
from nltk.tokenize import sent_tokenize
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=api_key)

# Download required NLTK data
nltk.download('punkt_tab')

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

def parse_query_with_gemini(user_query):
    """Simple query parsing function"""
    model = GenerativeModel("gemini-1.5-flash")
    system_prompt = """
You are an intelligent parser. Convert the user's natural language query about a policy document into a structured JSON.

Return the following:
- intent: e.g., "coverage_check", "definition_request"
- entity: the main subject (e.g., "knee surgery", "hospital")
- attributes: a list of things the user is asking about (e.g., "coverage", "conditions")
- context_type: always "policy"
- output_format: always "text"

Only return a valid JSON object.
"""

    full_prompt = f"{system_prompt}\n\nUser Query: {user_query}"

    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f'{{"error": "API Error", "message": "{str(e)}"}}'

class PolicyQueryBot:
    def __init__(self, text_file_path, verbose=True):
        self.search_engine = SemanticSearch(text_file_path)
        self.model = GenerativeModel("gemini-1.5-flash")
        self.verbose = verbose
    
    def get_final_answer(self, user_query):
        """Get complete answer for user query"""
        if self.verbose:
            print(f"Processing query: {user_query}")
            print("=" * 60)
        
        # Step 1: Parse query with Gemini
        parsed_query_raw = parse_query_with_gemini(user_query)
        if self.verbose:
            print(f"Parsed Query: {parsed_query_raw}")
            print("-" * 40)
        
        # Step 2: Get relevant chunks from semantic search
        relevant_results = self.search_engine.search_relevant_chunks(user_query, top_k=5)
        
        # Extract just the text chunks
        top_matches = [result['chunk'] for result in relevant_results]
        relevant_chunks = "\n\n".join(top_matches)
        
        if self.verbose:
            print("Found relevant policy sections:")
            for i, result in enumerate(relevant_results, 1):
                print(f"{i}. Score: {result['score']:.4f}")
                print(f"   {result['chunk'][:100]}...")
            print("-" * 40)
        
        # Step 3: Generate final response using Gemini
        final_prompt = f"""
You are a health insurance policy assistant. Use the following query and relevant policy text to generate a clear, concise answer.

Query:
{user_query}

Parsed Query Analysis:
{parsed_query_raw}

Relevant Policy Clauses:
{relevant_chunks}

Instructions:
- Answer only based on the provided text.
- If coverage is conditional (e.g., waiting period), explain it clearly.
- If not found, say "This information is not present in the policy."
- Be specific about any exclusions, waiting periods, or conditions.
- Keep the answer concise but complete.

Answer:
"""
        
        try:
            response = self.model.generate_content(final_prompt)
            if self.verbose:
                print("FINAL ANSWER:")
                print("=" * 60)
                print(response.text)
            return response.text
        except Exception as e:
            if self.verbose:
                print(f"Error generating response: {e}")
            return "Sorry, I couldn't generate a response due to an API error."

# Only run tests if this file is executed directly
if __name__ == "__main__":
    # Initialize the bot
    text_file = r"g:\PROGRAMMING\Hackathon\Bajaj - LLM Query Retrieval\extracted_Arogya Sanjeevani Policy\text\pdf_text.txt"
    bot = PolicyQueryBot(text_file)

    # Test queries
    test_queries = [
        "Does this policy cover maternity and knee surgery?",
        "What is the waiting period for pre-existing conditions?",
        "What are the coverage limits for hospitalization?"
    ]

    for query in test_queries:
        bot.get_final_answer(query)
        print("\n" + "="*80 + "\n")
