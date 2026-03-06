import os
import json
from datetime import datetime
from fpdf import FPDF
from dotenv import load_dotenv
from tavily import TavilyClient
from google import genai
from google.genai import types

load_dotenv()

# Explicitly set the client to use the stable 'v1' API version
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options=types.HttpOptions(api_version='v1')
)
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

class SeniorPDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            self.set_font("helvetica", 'B', 22)
            self.cell(0, 10, "Daily AI Research Report", ln=True, align='C')
            self.set_font("helvetica", '', 12)
            self.cell(0, 10, f"Date: {datetime.now().strftime('%B %d, %Y')}", ln=True, align='C')
            self.line(10, 32, 200, 32) 
            self.ln(10)

def create_senior_pdf(research_items, filename):
    pdf = SeniorPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)
    for index, item in enumerate(research_items):
        pdf.set_font("helvetica", 'B', 18)
        pdf.set_text_color(0, 51, 102) 
        pdf.multi_cell(0, 10, item.get('title', 'AI Update'))
        pdf.ln(2)
        pdf.set_font("helvetica", '', 14)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 9, item.get('summary', ''))
        pdf.ln(4)
        pdf.set_font("helvetica", 'B', 14)
        pdf.multi_cell(0, 9, "Why this matters for you:")
        pdf.set_font("helvetica", '', 14)
        pdf.multi_cell(0, 9, item.get('relevance', ''))
        if index < len(research_items) - 1:
            pdf.ln(12)
            pdf.set_draw_color(200, 200, 200)
            pdf.line(20, pdf.get_y(), 190, pdf.get_y())
            pdf.ln(12)
    pdf.output(filename)

def main():
    output_filename = "daily_research.pdf"
    # Using the current stable workhorse model
    model_id = "gemini-2.5-flash"
    
    try:
        search_results = tavily.search(query="2026 AI gadgets for seniors", max_results=3)
        
        response = client.models.generate_content(
            model=model_id,
            contents=f"Context: {json.dumps(search_results['results'])}",
            config=types.GenerateContentConfig(
                system_instruction="Explain AI to seniors. Output ONLY a JSON array with: title, summary (4-5 sentences), and relevance.",
                response_mime_type="application/json"
            )
        )
        
        final_data = json.loads(response.text)
        create_senior_pdf(final_data, output_filename)
        print(f"✅ Success! Generated with {model_id}")

    except Exception as e:
        print(f"❌ Error: {e}")
        # Generate Error PDF so the workflow doesn't fail
        error_pdf = SeniorPDF()
        error_pdf.add_page()
        error_pdf.set_font("helvetica", 'B', 12)
        error_pdf.multi_cell(0, 10, f"Critical Error: {str(e)}")
        error_pdf.output(output_filename)

if __name__ == "__main__":
    main()
