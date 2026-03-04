import os
import requests
import json
from fpdf import FPDF
from dotenv import load_dotenv
from tavily import TavilyClient
from google import genai
from google.genai import types

# 1. INITIALIZATION & SECRETS
load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not TAVILY_API_KEY or not GEMINI_API_KEY:
    print("❌ ERROR: API keys not found! Ensure they are set in GitHub Secrets.")
    exit(1)

# Initialize Clients
tavily = TavilyClient(api_key=TAVILY_API_KEY)
client = genai.Client(api_key=GEMINI_API_KEY)

# ---------------------------------------------------------
# 2. SENIOR-FRIENDLY PDF CLASS & FUNCTION
# ---------------------------------------------------------
class SeniorPDF(FPDF):
    def header(self):
        # Header with large, clear text
        self.set_font("Arial", 'B', 22)
        self.set_text_color(0, 0, 0)
        self.cell(0, 15, "Daily AI Research for Seniors", ln=True, align='C')
        self.set_draw_color(0, 0, 0)
        self.line(10, 25, 200, 25) # High-contrast separator line
        self.ln(10)

def create_senior_pdf(research_items, filename="daily_research.pdf"):
    pdf = SeniorPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    
    for item in research_items:
        pdf.add_page()
        
        # 1. Headline (20pt Bold)
        pdf.set_font("Arial", 'B', 20)
        pdf.set_text_color(0, 51, 102) # Dark blue for distinction
        pdf.multi_cell(0, 12, item.get('title', 'Untitled News'))
        pdf.ln(5)

        # 2. Image & Description
        if item.get('image_url'):
            try:
                img_data = requests.get(item['image_url'], timeout=10).content
                with open("temp.jpg", "wb") as f:
                    f.write(img_data)
                
                # Center image: page width is 210mm, margins 10mm. 160mm wide image.
                pdf.image("temp.jpg", x=25, w=160)
                pdf.ln(2)
                
                # Text description for accessibility (Italics)
                pdf.set_font("Arial", 'I', 11)
                pdf.set_text_color(80, 80, 80)
                pdf.multi_cell(0, 7, f"Visual Description: {item.get('visual_desc', 'AI Technology in use.')}")
                pdf.set_text_color(0, 0, 0) # Reset to black
                pdf.ln(5)
            except Exception as e:
                print(f"Skipping image for {item['title']}: {e}")

        # 3. Summary (14pt Regular)
        pdf.set_font("Arial", '', 14)
        pdf.multi_cell(0, 9, item.get('summary', 'No summary available.'))
        pdf.ln(10)

        # 4. "Why it Matters" Section (Grey Highlight Box)
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, " Why this matters for you:", ln=True, fill=True)
        pdf.set_font("Arial", '', 13)
        pdf.multi_cell(0, 8, item.get('relevance', 'This helps you stay informed.'), fill=True)

    pdf.output(filename)
    if os.path.exists("temp.jpg"):
        os.remove("temp.jpg")

# ---------------------------------------------------------
# 3. MAIN EXECUTION LOGIC
# ---------------------------------------------------------
def main():
    print("🚀 Starting Daily Research...")

    # A. Search for news
    search_query = "latest user-friendly AI technology for seniors 2026"
    search_results = tavily.search(query=search_query, include_images=True, max_results=5)
    
    # B. Process with Gemini 3.1 using Senior-Friendly Prompt
    system_instruction = (
        "You are the Otium Senior Tech Research Agent. Summarize news for people aged 70+.\n"
        "Rules:\n"
        "1. NO abstract/neon AI art. Choose real photos from provided context.\n"
        "2. Provide a 'visual_desc' for accessibility.\n"
        "3. Focus on 'Why this matters for you' regarding safety or family connection.\n"
        "4. Use JSON format."
    )
    
    # Defining the structure we want back
    response_schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "summary": {"type": "string"},
                "image_url": {"type": "string"},
                "visual_desc": {"type": "string"},
                "relevance": {"type": "string"}
            },
            "required": ["title", "summary", "relevance"]
        }
    }

    print("🤖 Analyzing findings with Gemini...")
    response = client.models.generate_content(
        model="gemini-2.0-flash", # Or gemini-1.5-pro
        contents=f"Research these results: {json.dumps(search_results['results'])}",
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=response_schema
        )
    )

    research_data = json.loads(response.text)

    # C. GENERATE THE PDF
    print(f"📄 Creating PDF for {len(research_data)} items...")
    create_senior_pdf(research_data)
    
    print("✅ Done! File saved as daily_research.pdf")

if __name__ == "__main__":
    main()
