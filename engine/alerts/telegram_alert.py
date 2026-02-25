import os
import urllib.request
import urllib.parse
import json
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()


def send_telegram_message(text: str):
    if not TELEGRAM_BOT_TOKEN:
        return {"sent": False, "error": "Missing TELEGRAM_BOT_TOKEN"}

    if not TELEGRAM_CHAT_ID:
        return {"sent": False, "error": "Missing TELEGRAM_CHAT_ID"}

    try:
        chat_id = int(TELEGRAM_CHAT_ID)
    except ValueError:
        return {"sent": False, "error": "TELEGRAM_CHAT_ID must be integer"}

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text
    }

    data = urllib.parse.urlencode(payload).encode()

    try:
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())
            if result.get("ok"):
                return {"sent": True}
            else:
                return {"sent": False, "error": result}
    except Exception as e:
        return {"sent": False, "error": str(e)}
