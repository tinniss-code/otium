import requests
from tavily import TavilyClient

# --- CONFIGURATION ---
TAVILY_API_KEY = "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"
BEEHIIV_API_KEY = "Bisi4UucnT8osgQmNNXTnJynqZZrt6yZHr0FSaMGZm9MI3L35Sm7OYv48mh7a0p0"
PUBLICATION_ID = "pub_578bd008-9ade-408b-8cb1-e6457df80601" # Found in beehiiv Settings

tavily = TavilyClient(api_key=TAVILY_API_KEY)

def conduct_research(topic):
    print(f"🔎 Researching: {topic}...")
    # 'advanced' depth gives you better quality for newsletters
    search_result = tavily.search(query=topic, search_depth="advanced", max_results=5)
    
    # Format the results into a newsletter-style string
    content_blocks = []
    for result in search_result['results']:
        block = f"### {result['title']}\n\n{result['content']}\n\n[Read more]({result['url']})\n\n---\n"
        content_blocks.append(block)
    
    return "\n".join(content_blocks)

def push_to_beehiiv(title, body):
    url = f"https://api.beehiiv.com/v2/publications/{PUBLICATION_ID}/posts"
    
    headers = {
        "Authorization": f"Bearer {BEEHIIV_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "title": title,
        "body_content": body,
        "status": "draft"  # Always keep as draft for a final human check
    }

    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 201:
        print("✅ Success! Draft created in beehiiv.")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")

# --- EXECUTION ---
topic_of_the_day = "Breakthroughs in Agentic AI and physical robotics automation March 2026"
research_data = conduct_research(topic_of_the_day)
push_to_beehiiv(f"Research Report: {topic_of_the_day}", research_data)