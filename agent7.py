import os
import requests
import json
from fpdf import FPDF
from dotenv import load_dotenv
from tavily import TavilyClient
from google import genai
from google.genai import types

# 1. INITIALIZATION
load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not TAVILY_API_KEY or not GEMINI_API_KEY:
    print("❌ ERROR: API keys missing. Check your .env or GitHub Secrets.")
    exit(1)

# Initialize Modern Clients
tavily = TavilyClient(api_key=TAVILY_API_KEY)
# The new Client automatically looks for GEMINI_API_KEY env var
client = genai.Client(api_key=GEMINI_API_KEY)

# ---------------------------------------------------------
# 2. SENIOR-FRIENDLY PDF LOGIC
# ---------------------------------------------------------
class SeniorPDF(FPDF):
    def header(self):
        self.set_font("helvetica", 'B', 22)
        self.set_text_color(0, 0, 0)
        self.cell(0, 15, "Daily AI Research for Seniors", align='C', new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(0, 0, 0)
        self.line(10, 25, 200, 25) 
        self.ln(10)

def create_senior_pdf(research_items, filename="daily_research.pdf"):
    pdf = SeniorPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    
    for item in research_items:
        pdf.add_page()
        
        # Title: Blue 20pt Bold
        pdf.set_font("helvetica", 'B', 20)
        pdf.set_text_color(0, 51, 102) 
        pdf.multi_cell(0, 12, item.get('title', 'AI Update'))
        pdf.ln(5)

        # Image Handling
        if item.get('image_url'):
            try:
                img_data = requests.get(item['image_url'], timeout=10).content
                with open("temp.jpg", "wb") as f: f.write(img_data)
                pdf.image("temp.jpg", x=25, w=160)
                pdf.ln(4)
                
                # Visual Description
                pdf.set_font("helvetica", 'I', 11)
                pdf.set_text_color(80, 80, 80)
                pdf.multi_cell(0, 7, f"Image Description: {item.get('visual_desc', 'Technology visual.')}")
                pdf.set_text_color(0, 0, 0)
                pdf.ln(5)
            except: 
                print(f"Skipping image for: {item['title']}")

        # Body: 14pt Regular
        pdf.set_font("helvetica", '', 14)
        pdf.multi_cell(0, 9, item.get('summary', ''))
        pdf.ln(8)

        # Relevance Box
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("helvetica", 'B', 14)
        pdf.cell(0, 10, " Why this matters for you:", fill=True, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("helvetica", '', 13)
        pdf.multi_cell(0, 8, item.get('relevance', ''), fill=True)

    pdf.output(filename)
    if os.path.exists("temp.jpg"): os.remove("temp.jpg")

# ---------------------------------------------------------
# 3. MAIN WORKFLOW
# ---------------------------------------------------------
def main():
    print("🔍 Searching for Senior-Friendly AI News...")
    
    # Updated Tavily parameters for 2026
    search_results = tavily.search(
        query="latest helpful AI technology for elderly simple daily use 2026",
        search_depth="advanced",
        include_images=True,
        include_image_descriptions=True,
        max_results=3
    )

    # Gemini Processing with Strict JSON Schema
    system_prompt = (
        "You are an expert at explaining tech to seniors. Output ONLY a JSON array. "
        "Summarize each news item. Provide a 'visual_desc' for the image. "
        "Keep language simple and text large (high focus on safety/ease of use)."
    )

    print("🤖 Processing with Gemini 2.0 Flash...")
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=f"Context: {json.dumps(search_results['results'])}",
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            response_schema={
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
        )
    )

    try:
        final_data = json.loads(response.text)
        print(f"📄 Creating PDF with {len(final_data)} articles...")
        create_senior_pdf(final_data)
        print("✅ Success! daily_research.pdf is ready.")
    except Exception as e:
        print(f"❌ Failed to parse Gemini response: {e}")

if __name__ == "__main__":
    main()
