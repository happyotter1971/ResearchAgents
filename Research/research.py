import os
import requests
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env
load_dotenv()

# Initialize OpenAI client (uses OPENAI_API_KEY from environment automatically)
client = OpenAI()

# Load SerpAPI key from environment
serpapi_key = os.getenv("SERPAPI_KEY")

# Key check
assert os.getenv("OPENAI_API_KEY"), "Missing OpenAI API key. Set OPENAI_API_KEY in your .env file."
assert serpapi_key, "Missing SerpAPI key. Set SERPAPI_KEY in your .env file."

# Simple web search using SerpAPI
def search_web(query):
    params = {"q": query, "num": 3, "api_key": serpapi_key}
    resp = requests.get("https://serpapi.com/search", params=params)
    results = resp.json().get("organic_results", [])
    snippets = " ".join([r.get("snippet", "") for r in results])
    return snippets or "No relevant context found."

# Augmented LLM function using OpenAI Chat API
def augmented_llm(prompt):
    context = search_web(prompt)
    full_prompt = f"Use this context to answer the question.\nContext:\n{context}\nQuestion: {prompt}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": full_prompt}
        ],
        temperature=0.2
    )
    return response.choices[0].message.content

# Example usage
if __name__ == "__main__":
    question = "What recent policies exist for cloud computing in the U.S. federal government?"
    answer = augmented_llm(question)
    print("\n🧠 Answer:\n", answer)
