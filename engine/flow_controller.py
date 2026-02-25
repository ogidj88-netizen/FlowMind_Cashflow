"""
FlowMind — Flow Controller v6
Topic Approval → Final Package Approval → Production
"""

import time
from engine.alerts.telegram_gate import send_for_approval, wait_for_approval


# ---------------- SCORING ---------------- #

def calculate_score(topic_title: str) -> float:

    score = 5.0
    title = topic_title.lower()

    if any(word in title for word in ["insurance", "loan", "credit"]):
        score += 2.5
    if "$" in title or "cost" in title:
        score += 0.7
    if any(word in title for word in ["trick", "nobody", "hidden", "never"]):
        score += 1.5
    if any(word in title for word in ["lose", "draining", "costs"]):
        score += 1.0
    if any(char.isdigit() for char in title):
        score += 0.5

    return round(min(score, 10.0), 1)


# ---------------- TOPIC GENERATION ---------------- #

def generate_topics():

    raw_titles = [
        "The Insurance Trick That Saves $3,000",
        "The $5 Daily Habit That Costs You $1,800",
        "Hidden Fees You Never Notice"
    ]

    topics = []

    for title in raw_titles:
        topics.append({
            "title": title,
            "score": calculate_score(title)
        })

    topics.sort(key=lambda x: x["score"], reverse=True)

    return topics[:3]


# ---------------- FINAL PACKAGE STUB ---------------- #

def generate_final_package(topic: str):

    script_preview = f"Opening hook for: {topic}\n\nThis video reveals..."
    thumbnail_preview = f"[THUMBNAIL PREVIEW for {topic}]"

    return script_preview, thumbnail_preview


# ---------------- MAIN FLOW ---------------- #

def main():

    print("🧠 Generating auto-scored topics...")

    topics = generate_topics()
    project_id = f"FM_{int(time.time())}"

    # Gate 1 — Topic
    message_id = send_for_approval(project_id, topics)
    selected_topic = wait_for_approval(project_id, message_id)

    print(f"\n🎯 Topic Approved: {selected_topic}\n")

    # Generate package preview
    script_preview, thumbnail_preview = generate_final_package(selected_topic)

    final_topics = [{
        "title": "Approve Final Package",
        "score": 10
    }]

    print("📦 Sending final package preview to Telegram...")

    # Надсилаємо превʼю окремим повідомленням
    from engine.alerts.telegram_gate import BOT_TOKEN, CHAT_ID
    import requests

    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": f"📜 Script Preview:\n\n{script_preview}\n\n🖼 Thumbnail:\n{thumbnail_preview}"
        }
    )

    # Gate 2 — Final Approval
    message_id = send_for_approval(project_id, final_topics)
    wait_for_approval(project_id, message_id)

    print("\n🚀 FINAL APPROVAL RECEIVED — STARTING PRODUCTION...\n")

    print("✅ Production Completed.")


if __name__ == "__main__":
    main()
