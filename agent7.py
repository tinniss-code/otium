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
    pdf.multi_cell(0, 10, f"Error: {msg}")
    pdf.output("daily_research.pdf")

def main():
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        create_error_pdf("OPENROUTER_API_KEY is missing.")
        return

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    try:
        search_results = tavily.search(query="2026 AI gadgets for seniors", max_results=3)
        
        response = client.chat.completions.create(
          model="google/gemini-2.0-flash-001",
          messages=[
            {"role": "system", "content": "Return ONLY a JSON list of objects. Each with 'title', 'summary', and 'relevance'."},
            {"role": "user", "content": f"Summarize: {json.dumps(search_results['results'])}"}
          ],
          response_format={ "type": "json_object" }
        )
        
        raw_content = response.choices[0].message.content
        data = json.loads(raw_content)

        if isinstance(data, list): articles = data
        elif isinstance(data, dict): articles = data.get('articles', data.get('items', [data]))
        else: articles = []

        pdf = FPDF()
        pdf.add_page()
        
        # Effective Page Width (epw) is safer than 0
        width = pdf.epw 

        pdf.set_font("helvetica", 'B', 20)
        # --- FIX 1: Explicitly set X to margin before printing ---
        pdf.set_x(pdf.l_margin) 
        pdf.cell(width, 10, "Daily Senior AI Report", ln=True, align='C')
        pdf.ln(10)

        for item in articles:
            if not isinstance(item, dict): continue
            
            # --- FIX 2: Reset X for every section to prevent cumulative drift ---
            pdf.set_x(pdf.l_margin)
            pdf.set_font("helvetica", 'B', 16)
            pdf.multi_cell(width, 10, str(item.get('title', 'AI Update')))
            
            pdf.set_x(pdf.l_margin)
            pdf.set_font("helvetica", '', 14)
            pdf.multi_cell(width, 8, str(item.get('summary', '')))
            
            pdf.ln(2)
            pdf.set_x(pdf.l_margin)
            pdf.set_font("helvetica", 'B', 14)
            pdf.cell(width, 8, "Why this matters:", ln=True)
            
            pdf.set_x(pdf.l_margin)
            pdf.set_font("helvetica", '', 14)
            pdf.multi_cell(width, 8, str(item.get('relevance', '')))
            pdf.ln(10)
            
        pdf.output("daily_research.pdf")
        print("✅ SUCCESS")

    except Exception as e:
        create_error_pdf(str(e))

if __name__ == "__main__":
    main()
