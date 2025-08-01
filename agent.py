# agent.py (Final Resilient Version)

import os
import requests
import google.generativeai as genai
import schedule
import time
from dotenv import load_dotenv
import feedparser

# --- PART A: Configuration ---
print("RSS Agent starting up...")
load_dotenv()

try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]
except KeyError as e:
    print(f"🛑 FATAL ERROR: Missing secret key in .env file: {e}")
    exit()

gemini_model = genai.GenerativeModel('gemini-1.5-flash')

# --- **UPGRADED**: Added more high-quality AI/Tech RSS feeds ---
# Why: This increases the chances of finding fresh AI news every day,
# making the agent more resilient to stale feeds.
RSS_FEEDS = {
    "The Times of India": {"url": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms", "type": "general"},
    "BBC World News": {"url": "http://feeds.bbci.co.uk/news/world/rss.xml", "type": "general"},
    "The Verge": {"url": "https://www.theverge.com/rss/index.xml", "type": "ai"},
    "Ars Technica": {"url": "http://feeds.arstechnica.com/arstechnica/index/", "type": "ai"},
    "Wired Top Stories": {"url": "https://www.wired.com/feed/rss", "type": "ai"}
}

print("Configuration loaded successfully.")


# --- PART B: Function to Fetch and Pre-Sort News ---
def fetch_news_from_rss():
    general_headlines = []
    ai_headlines = []
    print("🔍 Fetching and sorting news from RSS feeds...")
    for name, feed_info in RSS_FEEDS.items():
        try:
            print(f"  - Parsing '{name}' ({feed_info['type']})...")
            feed = feedparser.parse(feed_info['url'])
            # Limit to the most recent 5 entries from each feed
            for entry in feed.entries[:5]:
                if feed_info['type'] == 'general':
                    general_headlines.append(entry.title)
                elif feed_info['type'] == 'ai':
                    ai_headlines.append(entry.title)
        except Exception as e:
            print(f"  - 🛑 Could not parse feed {name}: {e}")
    
    print(f"✅ Found {len(general_headlines)} general and {len(ai_headlines)} AI headlines.")
    return general_headlines, ai_headlines


# --- PART C: **UPGRADED** Function for AI Summarization ---
# Why: This new prompt is more robust. It's explicitly told to ignore dates
# within headlines and has instructions for what to do if the AI list is empty.
def create_briefing_from_headlines(general_headlines, ai_headlines):
    print("🧠 Creating analytical briefing with Gemini...")
    general_headlines_str = "\n".join(f"- {h}" for h in general_headlines)
    ai_headlines_str = "\n".join(f"- {h}" for h in ai_headlines)
    
    prompt = f"""
    You are a senior news editor creating a daily briefing.
    Your task is to create a two-part briefing from the headline lists below.
    IMPORTANT: Ignore any dates found within the headlines themselves.

    **Part 1: Top Headlines**
    From the "General News Headlines" list, select the 3-4 most critical stories. For each, provide a concise one-sentence summary.

    **Part 2: AI & Tech Insights**
    Review the "AI & Tech Headlines" list.
    - If the list is NOT empty, select the 2-3 most significant developments. For each, provide a one-sentence summary and a brief "**Why it matters:**" insight.
    - If the list IS empty, simply write: "No major AI & Tech updates to report today."

    Format the entire output for Discord using Markdown.

    ---
    **General News Headlines:**
    {general_headlines_str}

    **AI & Tech Headlines:**
    {ai_headlines_str}
    ---
    """
    
    try:
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"🛑 Error creating briefing with Gemini: {e}")
        return "Could not generate the briefing due to an API error."


# --- PART D: Function to Send to Discord ---
def send_discord_message(briefing_text):
    data = {"content": briefing_text}
    print(f"📲 Sending briefing to Discord...")
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=data)
        response.raise_for_status()
        print("✅ Message sent successfully to Discord!")
    except requests.exceptions.RequestException as e:
        print(f"🛑 Failed to send Discord message: {e}")


# --- PART E: Main Orchestrator Job ---
def run_agent_job():
    print("\n--- Running RSS News Agent Job ---")
    today_date_str = time.strftime("%A, %B %d, %Y")
    greeting = f"## 🇮🇳 Your Analytical Briefing: {today_date_str}\n"

    general_headlines, ai_headlines = fetch_news_from_rss()

    if not general_headlines and not ai_headlines:
        print("No news found from any source. Skipping.")
        return

    briefing = create_briefing_from_headlines(general_headlines, ai_headlines)
    full_message = greeting + briefing
    send_discord_message(full_message)
    print("--- Agent Job Finished ---\n")


# --- PART F: The Scheduler ---
if __name__ == "__main__":
    run_agent_job()
    schedule.every().day.at("07:30").do(run_agent_job)
    print("✅ Agent is now scheduled to run every day at 07:30 AM.")
    print("Keep this terminal window running. Press Ctrl+C to exit.")
    while True:
        schedule.run_pending()
        time.sleep(60)