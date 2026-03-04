import os
import sys
import google.generativeai as genai
from tavily import TavilyClient

def run_health_check():
    print("🚀 --- 2026 AI Agent Health Check --- 🚀")
    print(f"Python Version: {sys.version.split()[0]}")
    
    # 1. Check Environment Variables
    tavily_key = os.getenv("TAVILY_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    errors = 0
    if not tavily_key:
        print("❌ ERROR: TAVILY_API_KEY is missing from environment.")
        errors += 1
    else:
        print("✅ TAVILY_API_KEY: Found")

    if not gemini_key:
        print("❌ ERROR: GEMINI_API_KEY is missing from environment.")
        errors += 1
    else:
        print("✅ GEMINI_API_KEY: Found")

    if errors > 0:
        print("\n💡 FIX: Run '$env:GEMINI_API_KEY=\"your_key\"' in PowerShell or set GitHub Secrets.")
        return

    # 2. Test Gemini Connection & Model Discovery
    print("\n🤖 Testing Gemini Connection...")
    try:
        genai.configure(api_key=gemini_key)
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Check for 2026 specific models
        top_model = "models/gemini-3.1-flash-lite"
        if top_model in models:
            print(f"✅ Connection Successful! Best 2026 model found: {top_model}")
        else:
            print(f"⚠️ {top_model} not found. Available: {models[0]}")
            
        # Quick Response Test
        model = genai.GenerativeModel(models[0].replace('models/', ''))
        test_resp = model.generate_content("Hi", generation_config={"max_output_tokens": 5})
        print("✅ Gemini Response Test: Passed")
    except Exception as e:
        print(f"❌ Gemini Connection Failed: {e}")

    # 3. Test Tavily Connection
    print("\n🔎 Testing Tavily Connection...")
    try:
        tavily = TavilyClient(api_key=tavily_key)
        # Simple search to verify API key validity
        tavily.search(query="test", max_results=1)
        print("✅ Tavily Connection: Passed")
    except Exception as e:
        print(f"❌ Tavily Connection Failed: {e}")

    print("\n✨ --- HEALTH CHECK COMPLETE --- ✨")
    if errors == 0:
        print("Everything is green! You are ready to automate.")

if __name__ == "__main__":
    run_health_check()