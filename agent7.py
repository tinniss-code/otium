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
# 2. SENIOR-FRIENDLY PDF LOGIC (FLOWING PARAGRAPHS)
# ---------------------------------------------------------
class SeniorPDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            self.set_font("helvetica", 'B', 22)
            self.set_text_color(0, 0, 0)
            # Title
            self.cell(0, 10, "Daily AI Research Report", ln=True, align='C')
            # Current Date
            self.set_font("helvetica", '', 12)
            current_date = datetime.now().strftime("%B %d, %Y")
            self.cell(0, 10, f"Report Date: {current_date}", ln=True, align='C')
            # Visual Separator
            self.set_draw_color(0, 0, 0)
            self.line(10, 32, 200, 32) 
            self.ln(10)

def create_senior_pdf(research_items, filename):
    pdf = SeniorPDF()
    pdf.add_page() # Start the document
    pdf.set_auto_page_break(auto=True, margin=20)
    
    for index, item in enumerate(research_items):
        # --- ARTICLE HEADER ---
        pdf.set_font("helvetica", 'B', 18)
        pdf.set_text_color(0, 51, 102) # Professional Blue
        pdf.multi_cell(0, 10, item.get('title', 'AI Update'))
        pdf.ln(2) 

        # --- IMAGE (Optional) ---
        if item.get('image_url'):
            try:
                img_data = requests.get(item['image_url'], timeout=10).content
                temp_img = "temp_capture.jpg"
                with open(temp_img, "wb") as f: f.write(img_data)
                # Centers image slightly
                pdf.image(temp_img, x=25, w=150)
                pdf.ln(4)
                os.remove(temp_img)
            except: 
                pass

        # --- SUMMARY PARAGRAPH ---
        pdf.set_font("helvetica", '', 14)
        pdf.set_text_color(0, 0, 0)
        # Detailed summary
        pdf.multi_cell(0, 9, item.get('summary', ''))
        pdf.ln(4)

        # --- WHY IT MATTERS PARAGRAPH ---
        pdf.set_font("helvetica", 'B', 14)
        pdf.multi_cell(0, 9, "Why this matters for you:")
        pdf.set_font("helvetica", '', 14)
        pdf.multi_cell(0, 9, item.get('relevance', ''))
        
        # --- SPACING BETWEEN ARTICLES ---
        # Don't add a divider after the very last article
        if index < len(research_items) - 1:
            pdf.ln(12) 
            pdf.set_draw_color(200, 200, 200) # Light grey line
            pdf.line(20, pdf.get_y(), 190, pdf.get_y()) 
            pdf.ln(12)

    pdf.output(filename)

# ---------------------------------------------------------
# 3. MAIN WORKFLOW
# ---------------------------------------------------------
def main():
    print("🔍 Searching for news...")
    # Specifically looking for high-detail senior-tech topics
    search_results = tavily.search(
        query="2026 AI gadgets for elderly independence safety features detailed",
        include_images=True,
        max_results=3
    )

    model_id = "gemini-2.0-flash" 
    
    system_prompt = (
        "You are an expert tech educator for seniors. Output ONLY a JSON array. "
        "For each article, provide: "
        "1. A clear, descriptive 'title'. "
        "2. A detailed 'summary' (at least 4-5 sentences) covering specific features. "
        "3. An 'image_url' from the context. "
        "4. A 'relevance' section explaining the direct benefit to a senior's daily life."
    )

    print(f"🤖 Processing with {model_id}...")
    
    try:
        response = client.models.generate_content(
            model=model_id,
            contents=f"Context: {json.dumps(search_results['results'])}",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json"
            )
        )
        
        final_data = json.loads(response.text)
        output_filename = os.path.join(os.getcwd(), "daily_research.pdf")
        
        create_senior_pdf(final_data, output_filename)
        print(f"✅ Success! Detailed PDF created at {output_filename}")
            
    except Exception as e:
        print(f"❌ Error during execution: {e}")

if __name__ == "__main__":
    main()
