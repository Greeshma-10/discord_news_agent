# AI News Agent for Discord

A fully automated Python agent that fetches the latest news from curated RSS feeds, uses Google's Gemini AI to create an analytical daily briefing, and delivers it directly to a Discord channel every morning.

![GitHub Actions Workflow Status](https://github.com/Greeshma-10/discord_news_agent/actions/workflows/run-agent.yml/badge.svg)

---

## 🌟 Special Features

* **Curated News Sources**: Instead of relying on a single API, the agent pulls news from a hand-picked list of trusted RSS feeds (e.g., BBC, Times of India, Reuters, Wired).
* **Intelligent Categorization**: The agent's code pre-sorts headlines into "General News" and "AI & Tech News" *before* sending them to the AI, ensuring accurate and relevant categorization in the final briefing.
* **AI-Powered Analytical Insights**: The agent doesn't just summarize. It uses a sophisticated prompt to instruct Google's Gemini model to provide a "**Why it matters:**" analysis for each key AI development, adding significant value beyond a simple headline list.
* **Automated Daily Delivery**: Deployed via GitHub Actions, the agent runs automatically on a set schedule (e.g., 7:30 AM IST every day) without needing a local machine to be running.
* **Secure & Robust**: All secret keys and webhook URLs are securely managed using GitHub Repository Secrets, not hardcoded in the script.

---

## 🚀 How It Works

The workflow is simple yet powerful:

1.  **Scheduled Trigger**: A GitHub Actions workflow (`.github/workflows/run-agent.yml`) triggers the script on a daily schedule.
2.  **Fetch & Sort**: The Python script (`agent.py`) fetches the latest articles from the predefined list of RSS feeds and sorts them into two categories: `general` and `ai`.
3.  **Analyze & Summarize**: The sorted lists of headlines are sent to the Google Gemini API with a detailed prompt, instructing it to create a two-part analytical briefing.
4.  **Deliver to Discord**: The final, formatted Markdown message is sent to a specified Discord channel via a secure webhook.

---

## 📸 Demo

Here is an example of the daily briefing delivered to Discord:

![Example Discord Message](https://github.com/user-attachments/assets/c9d9d518-ff0f-4856-ba78-89715bac2cef) <!-- Replace this with your own image link -->

---

## 🛠️ Setup for Local Development

To run this agent on your local machine for testing:

1.  **Clone the repository:**
    ```bash
    git clone (https://github.com/Greeshma-10/discord_news_agent.git)
    cd discord_news_agent
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: You may need to create a `requirements.txt` file first by running `pip freeze > requirements.txt`)*

4.  **Create a `.env` file:**
    Create a file named `.env` in the root of the project and add your secret keys:
    ```
    DISCORD_WEBHOOK_URL="YOUR_DISCORD_WEBHOOK_URL"
    GOOGLE_API_KEY="YOUR_GOOGLE_AI_API_KEY"
    ```

5.  **Run the agent:**
    ```bash
    python agent.py
    ```

---

## 💻 Technologies Used

* **Language**: Python
* **AI Model**: Google Gemini
* **News Sources**: RSS Feeds (via `feedparser` library)
* **Delivery**: Discord Webhooks (via `requests` library)
* **Automation/Deployment**: GitHub Actions
* **Scheduling**: `cron` (within GitHub Actions workflow)
* **Dependencies**: `google-generativeai`, `python-dotenv`, `requests`, `feedparser`
