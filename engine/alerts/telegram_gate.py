"""
FlowMind — Telegram Approval Gate (Final Score Only v6)
Clean producer decision format.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_for_approval(project_id: str, topics: list):

    if not BOT_TOKEN or not CHAT_ID:
        raise Exception("Telegram credentials missing")

    topics = topics[:3]

    keyboard = {
        "inline_keyboard": []
    }

    for topic in topics:

        button_text = f"⭐ {topic['score']}/10 — {topic['title']}"

        keyboard["inline_keyboard"].append([
            {
                "text": button_text,
                "callback_data": topic["title"]
            }
        ])

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    response = requests.post(
        url,
        json={
            "chat_id": CHAT_ID,
            "text": "🔥 Select a topic:",
            "reply_markup": keyboard
        }
    )

    if response.status_code != 200:
        raise Exception(f"Telegram send failed: {response.text}")

    return response.json()["result"]["message_id"]


def wait_for_approval(project_id: str, message_id: int):

    print("Waiting for topic selection...")

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    offset = None

    while True:
        response = requests.get(url, params={"timeout": 10, "offset": offset})
        data = response.json()

        for update in data.get("result", []):
            offset = update["update_id"] + 1

            if "callback_query" in update:
                query = update["callback_query"]

                if query["message"]["message_id"] == message_id:
                    selected_title = query["data"]
                    print(f"✅ Selected topic: {selected_title}")
                    return selected_title

