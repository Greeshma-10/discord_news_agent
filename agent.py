# agent.py

import os
import requests
import google.generativeai as genai
import schedule
import time
from dotenv import load_dotenv

# --- PART A: Imports and Configuration ---
# Why: This section imports all the libraries we need and loads our secret keys
# from the .env file so we can use them securely.
print("Agent starting up...")
load_dotenv()

try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    GNEWS_API_KEY = os.environ["GNEWS_API_KEY"]
    DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]
except KeyError as e:
    print(f"🛑 FATAL ERROR: Missing secret key in .env file: {e}")
    exit()

gemini_model = genai.GenerativeModel('gemini-1.5-flash')
print("Configuration loaded successfully.")


# agent.py

# --- PART B: Function to Fetch News (REVISED FOR GNEWS) ---
# Why: This new version uses GNews, which works reliably on a local machine
# for development and testing. The API structure is slightly different, but the
# goal is the same: get a list of headlines.
def fetch_important_headlines():
    """Fetches top 10 headlines from India using GNews."""
    gnews_api_key = os.environ["GNEWS_API_KEY"]
    country_code = 'in' # India
    lang = 'en' # English
    print(f"🔍 Fetching top headlines for country: {country_code.upper()} using GNews...")
    
    url = (f"https://gnews.io/api/v4/top-headlines?"
           f"token={gnews_api_key}&lang={lang}&country={country_code}&max=10")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        headlines = [article['title'] for article in data.get('articles', []) if article['title']]
        print(f"✅ Found {len(headlines)} headlines.")
        return headlines
    except requests.exceptions.RequestException as e:
        print(f"🛑 Error fetching news: {e}")
        return []

# --- PART C: Function for AI Summarization ---
# Why: This is the 'AI' part of our agent. It takes the list of raw headlines,
# sends them to Google's Gemini model with a specific instruction (a 'prompt'),
# and gets back a nicely formatted summary.
def create_briefing_from_headlines(headlines):
    """Uses Gemini to create a briefing from a list of headlines."""
    if not headlines:
        return "No headlines found to create a briefing."

    print("🧠 Creating daily briefing with Gemini...")
    headlines_str = "\n".join(f"- {h}" for h in headlines)
    prompt = f"""
    You are a world-class editor for an intelligent news service in Bengaluru.
    Your task is to analyze the following list of top headlines from India and create a concise morning briefing.
    Select the 4-5 most critical stories that a busy professional must know.
    For each selected headline, write a single, impactful sentence summarizing the key takeaway.
    Format the entire output for Discord using Markdown. Use * for bolding headlines.

    Here are today's headlines:
    {headlines_str}
    """
    try:
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"🛑 Error creating briefing with Gemini: {e}")
        return "Could not generate the briefing due to an API error."


# --- PART D: Function to Send to Discord ---
# Why: This function's only job is to take the final text and send it to the
# Discord webhook URL we got in Step 1.
def send_discord_message(briefing_text):
    """Sends the briefing message to the configured Discord webhook."""
    data = {"content": briefing_text} # Discord webhooks expect this JSON format
    print(f"📲 Sending briefing to Discord...")
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=data)
        response.raise_for_status()
        print("✅ Message sent successfully to Discord!")
    except requests.exceptions.RequestException as e:
        print(f"🛑 Failed to send Discord message: {e}")


# --- PART E: The Main Orchestrator Job ---
# Why: This function brings everything together. It calls the other functions
# in the correct order: first fetch, then summarize, then send.
def run_agent_job():
    """The main job that orchestrates the agent's tasks."""
    print("\n--- Running AI News Agent Job ---")
    today_date_str = time.strftime("%A, %B %d, %Y")
    greeting = f"## 🇮🇳 Your Morning Briefing: {today_date_str}\n"

    headlines = fetch_important_headlines()
    if headlines:
        briefing = create_briefing_from_headlines(headlines)
        full_message = greeting + briefing
        send_discord_message(full_message)
    else:
        print("No headlines to process. Skipping Discord message.")
    print("--- Agent Job Finished ---\n")


# --- PART F: The Scheduler ---
# Why: This final block of code is the trigger. It tells the script to
# run the main job once immediately, and then sets up a schedule to run it
# automatically every day at 7:30 AM. The 'while' loop keeps the script
# alive to check the schedule.
if __name__ == "__main__":
    run_agent_job() # Run once on startup
    schedule.every().day.at("07:30").do(run_agent_job)
    print("✅ Agent is now scheduled to run every day at 07:30 AM.")
    print("Keep this terminal window running. Press Ctrl+C to exit.")
    while True:
        schedule.run_pending()
        time.sleep(60) # Wait 60 seconds between checking the schedule