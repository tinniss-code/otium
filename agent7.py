import datetime
import os
import datetime
import google.generativeai as genai
from tavily import TavilyClient


# --- CONFIG (Updated for 2026 Security Standards) ---
# This looks for secrets in your GitHub Settings or Local Environment
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# The public URL where your GitHub Page hosts the file
FEED_LINK = "https://tinniss-code.github.io/otium/"

# Validate that keys are actually loaded to prevent silent crashes
if not TAVILY_API_KEY or not GEMINI_API_KEY:
    print("❌ ERROR: API keys not found! Ensure they are set in GitHub Secrets.")
# Setup Clients
tavily = TavilyClient(api_key=TAVILY_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)

def get_best_model():
    """Finds the best available flash model to avoid 404 errors."""
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    # Priority list for 2026
    priorities = ['gemini-3.1-flash-lite', 'gemini-3-flash', 'gemini-2.5-flash', 'gemini-2.0-flash']
    
    for p in priorities:
        full_name = f"models/{p}"
        if full_name in available_models:
            print(f"✅ Found and using: {full_name}")
            return genai.GenerativeModel(p)
    
    # Fallback if none of our priorities are found
    if available_models:
        fallback = available_models[0].replace('models/', '')
        print(f"🔄 Fallback to available model: {fallback}")
        return genai.GenerativeModel(fallback)
    
    raise Exception("No generative models found for this API key.")

# Initialize the 'Brain'
model = get_best_model()

def rewrite_for_seniors(raw_data):
    """Uses Gemini to simplify tech news into senior-friendly HTML."""
    print("🤖 Simplifying the news for your readers...")
    
    prompt = f"""
    You are a friendly editor for a senior-focused newsletter.
    Rewrite this news into a warm, readable format:
    1. <h2> tags for LARGE HEADLINES.
    2. <p> tags for the body (use font-size: 18px in style if possible). 
    3. No technical jargon. 
    4. Include 'Why this matters for your daily life:' for each story.
    5. Return ONLY the HTML code. No markdown code blocks.
    
    DATA: {raw_data}
    """
    
    response = model.generate_content(prompt)
    content = response.text
    # Strip any accidental Markdown wrappers
    return content.replace("```html", "").replace("```", "").strip()

def generate_rss(topic):
    try:
        print(f"🔎 Researching: {topic}...")
        search = tavily.search(query=topic, search_depth="advanced", max_results=3)
        
        raw_context = ""
        for res in search['results']:
            raw_context += f"Title: {res['title']}\nContent: {res['content']}\nLink: {res['url']}\n\n"
        
        senior_friendly_html = rewrite_for_seniors(raw_context)
        
        # Build RSS with RFC 822 Date format
        now = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
        
        rss = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
  <title>The Simple Tech Report</title>
  <link>{FEED_LINK}</link>
  <description>Technology made easy.</description>
  <item>
    <title>Today's Update: {topic}</title>
    <description><![CDATA[ {senior_friendly_html} ]]></description>
    <pubDate>{now}</pubDate>
    <guid isPermaLink="false">{int(datetime.datetime.now().timestamp())}</guid>
  </item>
</channel>
</rss>"""

        with open("research.xml", "w", encoding="utf-8") as f:
            f.write(rss)
        print("✅ research.xml updated successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_rss("Latest AI helpers for the home")






