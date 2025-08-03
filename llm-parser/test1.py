import requests
import json
import sys

def check_ollama_status():
    """Check if Ollama server is running and accessible"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✓ Ollama is running with {len(models)} models available")
            return True, models
        else:
            print("✗ Ollama server is not responding properly")
            return False, []
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to Ollama. Make sure it's running on localhost:11434")
        print("  Run: ollama serve")
        return False, []
    except Exception as e:
        print(f"✗ Error checking Ollama status: {e}")
        return False, []

def ensure_model_available(model_name="llama3"):
    """Check if the specified model is available, if not suggest pulling it"""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            available_models = [model["name"] for model in models]
            
            # Check for exact match or partial match
            model_available = any(model_name in model for model in available_models)
            
            if not model_available:
                print(f"✗ Model '{model_name}' not found")
                print("Available models:", available_models)
                print(f"To install the model, run: ollama pull {model_name}")
                return False, available_models
            else:
                # Find the exact model name
                exact_model = next((model for model in available_models if model_name in model), model_name)
                print(f"✓ Model '{exact_model}' is available")
                return True, exact_model
        return False, []
    except Exception as e:
        print(f"Error checking models: {e}")
        return False, []

def parse_query_with_ollama(user_query, model="llama3"):
    system_prompt = """
You are a query parser AI. Convert the natural language user query into a structured JSON.

Extract the following:
- intent: (e.g. "coverage_check", "definition_request")
- entity: the subject (e.g. "knee surgery", "hospital")
- attributes: list of things being asked about (e.g. "conditions", "coverage", "waiting period")
- context_type: type of document (usually "policy")
- output_format: always "text"

Only return a valid JSON. No explanation.
"""

    # Request to Ollama's local server
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_query}
        ],
        "stream": False
    }

    try:
        print(f"Sending request to Ollama with model: {model}")
        response = requests.post("http://localhost:11434/api/chat", json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result["message"]["content"]
        else:
            print(f"Error: HTTP {response.status_code}")
            print("Response:", response.text)
            return None
            
    except requests.exceptions.Timeout:
        print("Request timed out. The model might be taking too long to respond.")
        return None
    except requests.exceptions.ConnectionError:
        print("Connection error. Make sure Ollama is running.")
        return None
    except Exception as e:
        print(f"Error calling Ollama: {e}")
        return None

if __name__ == "__main__":
    print("🤖 Ollama Query Parser")
    print("=" * 30)
    
    # Check if Ollama is running
    is_running, models = check_ollama_status()
    if not is_running:
        sys.exit(1)
    
    # Check if model is available
    model_available, model_name = ensure_model_available("llama3")
    if not model_available:
        print("\nTrying alternative models...")
        # Try other common models
        for alt_model in ["llama3.1", "llama2", "mistral", "qwen2"]:
            model_available, model_name = ensure_model_available(alt_model)
            if model_available:
                break
        
        if not model_available:
            print("No suitable model found. Please install a model first:")
            print("  ollama pull llama3")
            sys.exit(1)
    
    print(f"\nUsing model: {model_name}")
    print("\nEnter your query (or 'quit' to exit):")
    
    while True:
        query = input("\n> ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not query:
            print("Please enter a query.")
            continue
        
        print("Processing...")
        result = parse_query_with_ollama(query, model_name)
        
        if result:
            print("\n📋 Parsed Structured Query:")
            print("-" * 30)
            try:
                # Try to parse as JSON and pretty print
                parsed = json.loads(result)
                print(json.dumps(parsed, indent=2))
            except json.JSONDecodeError:
                # If not valid JSON, just print the result
                print(result)
        else:
            print("❌ Failed to get response from Ollama")
