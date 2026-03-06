import os
import requests
import json
import time
from datetime import datetime
from fpdf import FPDF
from dotenv import load_dotenv
from tavily import TavilyClient
from google import genai
from google.genai import types, errors

# 1. INITIALIZATION
load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

tavily = TavilyClient(api_key=TAVILY_API_KEY)
client = genai.Client(api_key=GEMINI_API_KEY)

# ---------------------------------------------------------
# 2. SENIOR-FRIENDLY PDF LOGIC
# ---------------------------------------------------------
class SeniorPDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            self.set_font("helvetica", 'B', 22)
            self.cell(0, 10, "Daily AI Research Report", ln=True, align='C')
            self.set_font("helvetica", '', 12)
            current_date = datetime.now().strftime("%B %d, %Y")
            self.cell(0, 10, f"Report Date: {current_date}", ln=True, align='C')
            self.set_draw_color(0, 0, 0)
            self.line(10, 32, 200, 32) 
            self.ln(10)

def create_senior_pdf(research_items, filename):
    pdf = SeniorPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)
    
    for index, item in enumerate(research_items):
        # Header (New Paragraph style)
        pdf.set_font("helvetica", 'B', 18)
        pdf.set_text_color(0, 51, 102) 
        pdf.multi_cell(0, 10, item.get('title', 'AI Update'))
        pdf.ln(2) 

        # Summary
        pdf.set_font("helvetica", '', 14)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 9, item.get('summary', ''))
        pdf.ln(4)

        # Relevance
        pdf.set_font("helvetica", 'B', 14)
        pdf.multi_cell(0, 9, "Why this matters for you:")
        pdf.set_font("helvetica", '', 14)
        pdf.multi_cell(0, 9, item.get('relevance', ''))
        
        # Divider
        if index < len(research_items) - 1:
            pdf.ln(12) 
            pdf.set_draw_color(200, 200, 200)
            pdf.line(20, pdf.get_y(), 190, pdf.get_y()) 
            pdf.ln(12)

    # Force the file to write to the current directory
    pdf.output(filename)

# ---------------------------------------------------------
# 3. MAIN WORKFLOW
# ---------------------------------------------------------
def main():
    print("🔍 Searching for news...")
    search_results = tavily.search(
        query="2026 AI gadgets for elderly independence safety features detailed",
        max_results=3
    )

    model_id = "gemini-2.0-flash" 
    
    try:
        response = client.models.generate_content(
            model=model_id,
            contents=f"Context: {json.dumps(search_results['results'])}",
            config=types.GenerateContentConfig(
                system_instruction="You are a senior tech educator. Output ONLY a JSON array with title, summary (4-5 sentences), and relevance.",
                response_mime_type="application/json"
            )
        )
        
        final_data = json.loads(response.text)
        
        # USE SIMPLE FILENAME (YAML will find it)
        output_filename = "daily_research.pdf"
        
        print(f"📂 Current Directory: {os.getcwd()}")
        create_senior_pdf(final_data, output_filename)
        
        # Final Verification before exiting Python
        if os.path.isfile(output_filename):
            print(f"✅ SUCCESS: {output_filename} exists. Size: {os.path.getsize(output_filename)} bytes")
        else:
            print("❌ ERROR: PDF was not found after creation.")
            
    except Exception as e:
        print(f"❌ Critical Error: {e}")

if __name__ == "__main__":
    main()
