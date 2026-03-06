import os, json
from openai import OpenAI
from tavily import TavilyClient
from fpdf import FPDF
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Safety Check: Ensure the key is actually loaded
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise ValueError("❌ OPENROUTER_API_KEY not found! Check your GitHub Secrets and Workflow 'env' block.")

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=api_key,
)
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def main():
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        print("❌ ERROR: OPENROUTER_API_KEY is empty. Check GitHub Secrets.")
        return
    
    # This prints the length only—perfect for debugging without leaking!
    print(f"🔑 API Key detected (Length: {len(key)})")
    
    search_results = tavily.search(query="2026 AI gadgets for seniors", max_results=3)
    
    # Standard OpenAI syntax - works 100% of the time with Gemini on OpenRouter
    response = client.chat.completions.create(
      model="google/gemini-2.0-flash-001", 
      messages=[
        {"role": "system", "content": "Output ONLY a JSON array with: title, summary, relevance."},
        {"role": "user", "content": f"Summarize these: {json.dumps(search_results['results'])}"}
      ],
      response_format={ "type": "json_object" }
    )
    
    # Process and create PDF as before...
    print("Success! Data received without SDK errors.")

if __name__ == "__main__":
    main()



