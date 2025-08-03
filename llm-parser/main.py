import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ✅ Step 1: Get your Gemini API key from environment variables
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it in your .env file.")

genai.configure(api_key=api_key)

# ✅ Step 2: Create the model object (using flash model for higher rate limits)
model = genai.GenerativeModel("gemini-1.5-flash")

# ✅ Step 3: Define the function to parse a query
def parse_query_with_gemini(user_query):
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
        if "ResourceExhausted" in str(e) or "429" in str(e):
            return """
{
    "error": "API quota exceeded",
    "message": "You've hit the Gemini API rate limit. Solutions:",
    "solutions": [
        "Wait a few minutes and try again",
        "Switch to gemini-1.5-flash (lighter model)",
        "Upgrade to a paid plan",
        "Use a different API key if available"
    ]
}
"""
        else:
            return f'{{"error": "API Error", "message": "{str(e)}"}}'

# ✅ Step 4: Test it
if __name__ == "__main__":
    user_query = input("Enter your query: ")
    print("\nParsed JSON:\n")
    print(parse_query_with_gemini(user_query))
