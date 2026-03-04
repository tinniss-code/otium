import os
import requests
import json
import time
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
# 2. PDF GENERATION LOGIC
# ---------------------------------------------------------
class SeniorPDF(FPDF):
    def header(self):
        self.set_font("helvetica", 'B', 22)
        self.cell(0, 15, "Daily AI Research for Seniors", align='C', new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(0, 0, 0)
        self.line(10, 25, 200, 25) 
        self.ln(10)

def create_senior_pdf(research_items, filename="daily_research.pdf"):
    pdf = SeniorPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    for item in research_items:
        pdf.add_page()
        pdf.set_font("helvetica", 'B', 20)
        pdf.set_text_color(0, 51, 102) 
        pdf.multi_cell(0, 12, item.get('title', 'AI Update'))
        pdf.ln(5)
        if item.get('image_url'):
            try:
                img_data = requests.get(item['image_url'], timeout=10).content
                with open("temp.jpg", "wb") as f: f.write(img_data)
                pdf.image("temp.jpg", x=25, w=160)
                pdf.ln(4)
                pdf.set_font("helvetica", 'I', 11)
                pdf.set_text_color(80, 80, 80)
                pdf.multi_cell(0, 7, f"Image: {item.get('visual_desc', 'Technology visual.')}")
                pdf.set_text_color(0, 0, 0)
                pdf.ln(5)
            except: pass
        pdf.set_font("helvetica", '', 14)
        pdf.multi_cell(0, 9, item.get('summary', ''))
        pdf.ln(8)
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("helvetica", 'B', 14)
        pdf.cell(0, 10, " Why this matters for you:", fill=True, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("helvetica", '', 13)
        pdf.multi_cell(0, 8, item.get('relevance', ''), fill=True)
    pdf.output(filename)
    if os.path.exists("temp.jpg"): os.remove("temp.jpg")

# ---------------------------------------------------------
# 3. MAIN WORKFLOW WITH RETRY LOGIC
# ---------------------------------------------------------
def main():
    print("🔍 Searching news...")
    search_results = tavily.search(
        query="latest helpful AI technology for elderly 2026",
        include_images=True,
        max_results=3
    )

    # UPDATED MODEL: 2.5-flash-lite (Higher free quota in 2026)
    model_name = "gemini-2.5-flash-lite"
    
    system_prompt = (
        "You are a senior tech assistant. Output ONLY a JSON array. "
        "Fields: title, summary, image_url, visual_desc, relevance."
    )

    print(f"🤖 Calling {model_name}...")
    
    # Simple Retry Loop for 429 Errors
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=f"Context: {json.dumps(search_results['results'])}",
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                )
            )
            final_data = json.loads(response.text)
            create_senior_pdf(final_data)
            print("✅ PDF Created Successfully.")
            return # Exit successfully
        except errors.ClientError as e:
            if "429" in str(e):
                wait = (attempt + 1) * 30
                print(f"⚠️ Quota hit. Waiting {wait} seconds before retry...")
                time.sleep(wait)
            else:
                print(f"❌ Error: {e}")
                break
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")
            break

if __name__ == "__main__":
    main()
