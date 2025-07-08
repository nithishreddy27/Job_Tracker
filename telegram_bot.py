# telegram_bot.py

import requests
from config import CONFIG

def send_job_to_telegram(job_data):
    """Send a job listing to the Telegram channel"""
    token = CONFIG["TELEGRAM"]["BOT_TOKEN"]
    channel_id = CONFIG["TELEGRAM"]["CHANNEL_ID"]

    message = (
        f"🆕 *{job_data['title']}*\n"
        f"🏢 {job_data['company']}\n"
        f"📍 {job_data['location']}\n"
        f"📅 Posted: {job_data.get('date_posted', 'N/A')}\n"
        f"🔗 Source: {job_data.get('source', '')}"
    )

    payload = {
        "chat_id": channel_id,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    print("sending to telegram")
    response = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=payload
    )

    if not response.ok:
        print(f"❌ Failed to send Telegram message: {response.text}")
