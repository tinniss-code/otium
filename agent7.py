import os, json
from openai import OpenAI
from tavily import TavilyClient
from fpdf import FPDF
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def create_error_pdf(msg):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 12)
    pdf.multi_cell(0, 10, f"Error during generation: {msg}")
    pdf.output("daily_research.pdf")

def main():
    # --- STEP 1: KEY VALIDATION ---
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        create_error_pdf("OPENROUTER_API_KEY is missing from environment.")
        print("❌ Missing API Key")
        return

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    try:
        # --- STEP 2: RESEARCH ---
        search_results = tavily.search(query="2026 AI gadgets for seniors", max_results=3)
        
        # --- STEP 3: AI CALL ---
        response = client.chat.completions.create(
          model="google/gemini-2.0-flash-001",
          messages=[
            {"role": "system", "content": "Return ONLY a JSON array of 3 objects. Each with 'title', 'summary' (4 sentences), and 'relevance'."},
            {"role": "user", "content": f"Data: {json.dumps(search_results['results'])}"}
          ],
          response_format={ "type": "json_object" }
        )
        
        # --- STEP 4: PDF GENERATION ---
        raw_content = response.choices[0].message.content
        data = json.loads(raw_content)
        # Handle if AI wraps the array in a "items" or "articles" key
        articles = data.get('articles', data.get('items', data))
        if isinstance(articles, dict): articles = [articles] # Fallback for single object

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", 'B', 16)
        pdf.cell(0, 10, "Daily Senior Research", ln=True, align='C')
        pdf.ln(5)

        for item in articles:
            pdf.set_font("helvetica", 'B', 14)
            pdf.multi_cell(0, 10, str(item.get('title', 'AI News')))
            pdf.set_font("helvetica", '', 12)
            pdf.multi_cell(0, 7, str(item.get('summary', '')))
            pdf.ln(2)
            pdf.set_font("helvetica", 'I', 12)
            pdf.multi_cell(0, 7, f"Relevance: {item.get('relevance', '')}")
            pdf.ln(10)
            
        pdf.output("daily_research.pdf")
        print("✅ Success: daily_research.pdf created.")

    except Exception as e:
        print(f"❌ Critical Error: {e}")
        create_error_pdf(str(e))

if __name__ == "__main__":
    main()
