from dotenv import load_dotenv
load_dotenv()  # This loads the keys from the .env file automatically

import os
import datetime
import google.generativeai as genai
from tavily import TavilyClient

# --- 1. CONFIGURATION ---
# Pulls keys from GitHub Secrets or your computer's Environment Variables
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Public link for your beehiiv RSS feed (update with your actual repo name if different)
FEED_LINK = "https://tinniss-code.github.io/otium/"

# Safety Check
if not TAVILY_API_KEY or not GEMINI_API_KEY:
    print("❌ ERROR: API keys not found in environment variables.")
    print("Local fix: $env:GEMINI_API_KEY='your_key' (Windows) or export GEMINI_API_KEY='your_key' (Mac/Linux)")
    exit(1)

# --- 2. INITIALIZE CLIENTS ---
tavily = TavilyClient(api_key=TAVILY_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)

def get_best_model():
    """Automatically finds the best available model to prevent 404 errors."""
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # 2026 Priority List (Stable production names)
        priorities = ['gemini-3.1-flash-lite', 'gemini-3-flash', 'gemini-2.5-flash', 'gemini-1.5-flash']
        
        for p in priorities:
            if f"models/{p}" in available_models:
                print(f"✅ Using Model: {p}")
                return genai.GenerativeModel(p)
        
        # Fallback to whatever is first in the list
        fallback = available_models[0].replace('models/', '')
        return genai.GenerativeModel(fallback)
    except Exception as e:
        print(f"❌ Failed to list models: {e}")
        return genai.GenerativeModel('gemini-1.5-flash') # Hard fallback

model = get_best_model()

# --- 3. LOGIC FUNCTIONS ---

def rewrite_for_seniors(raw_data):
    """Processes technical text into a clear, high-contrast HTML format."""
    print("🤖 AI is simplifying the research for your readers...")
    
    prompt = f"""
    You are a friendly editor for a technology newsletter for seniors. 
    Rewrite the research below into a warm, readable, and highly accessible format.

    RULES:
    1. Use <h2> tags for LARGE, BOLD, ALL-CAPS headlines.
    2. Use <p> tags for the body text. Keep sentences short.
    3. NO technical jargon. (e.g., use 'Helpful robot' instead of 'Agentic AI').
    4. For every story, add: '<strong>Why this matters to you:</strong>'.
    5. Separate stories with a <hr/> line.
    6. Return ONLY the HTML code. Do NOT use markdown code blocks (```html).
    
    RESEARCH DATA:
    {raw_data}
    """
    
    response = model.generate_content(prompt)
    content = response.text
    # Clean up any AI markdown formatting
    return content.replace("```html", "").replace("```", "").strip()

def generate_rss(topic):
    """Main pipeline: Search -> Rewrite -> Save RSS."""
    try:
        print(f"🔎 Researching: {topic}...")
        search = tavily.search(query=topic, search_depth="advanced", max_results=3)
        
        raw_context = ""
        for res in search['results']:
            raw_context += f"Title: {res['title']}\nContent: {res['content']}\nLink: {res['url']}\n\n"
        
        senior_content = rewrite_for_seniors(raw_context)
        
        # RFC 822 Date Format for RSS
        now = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
        
        rss_xml = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
  <title>The Simple Tech Report</title>
  <link>{FEED_LINK}</link>
  <description>Technology made easy for everyone.</description>
  <lastBuildDate>{now}</lastBuildDate>
  <item>
    <title>Today's Update: {topic}</title>
    <link>{FEED_LINK}</link>
    <description><![CDATA[ {senior_content} ]]></description>
    <pubDate>{now}</pubDate>
    <guid isPermaLink="false">{int(datetime.datetime.now().timestamp())}</guid>
  </item>
</channel>
</rss>"""

        # Save to local file
        with open("research.xml", "w", encoding="utf-8") as f:
            f.write(rss_xml)
        
        print(f"✅ Success! 'research.xml' is ready at {datetime.datetime.now()}")

    except Exception as e:
        print(f"❌ Error during execution: {e}")

# --- 4. EXECUTION ---
if __name__ == "__main__":
    # Feel free to change this topic to anything your readers care about!
    generate_rss("Helpful AI assistants and home safety for seniors")