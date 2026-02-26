import os
import time
import json
import requests
from typing import List, Dict, Optional, Tuple

BOT_TOKEN = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
CHAT_ID = (os.getenv("TELEGRAM_CHAT_ID") or "").strip()

API_BASE = "https://api.telegram.org/bot{token}".format(token=BOT_TOKEN)


def _require_env():
    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN missing")
    if not CHAT_ID:
        raise RuntimeError("TELEGRAM_CHAT_ID missing")


def _api(method: str, data: Optional[dict] = None, files: Optional[dict] = None) -> dict:
    _require_env()
    url = f"{API_BASE}/{method}"
    r = requests.post(url, data=data or {}, files=files, timeout=60)
    r.raise_for_status()
    payload = r.json()
    if not payload.get("ok"):
        raise RuntimeError(f"Telegram API error: {payload}")
    return payload


def _build_topic_keyboard(topics: List[Dict]) -> dict:
    # topics: [{"title": str, "score": float}]
    # callback_data is index
    inline = []
    for i, t in enumerate(topics):
        score = t.get("score")
        title = t.get("title", "").strip()
        if score is None:
            btn_text = f"{title}"
        else:
            # decimal scoring e.g. 8.5/10
            btn_text = f"{score:.1f}/10 — {title}"
        inline.append([{"text": btn_text[:60], "callback_data": f"TOPIC::{i}"}])
    return {"inline_keyboard": inline}


def send_topic_options(project_id: str, topics: List[Dict]) -> int:
    """
    Sends ONLY topics (no script preview).
    Returns message_id.
    """
    text_lines = [
        f"🧠 Topics for approval",
        f"PROJECT_ID: {project_id}",
        "",
        "Обери 1 тему кнопкою нижче:",
    ]
    kb = _build_topic_keyboard(topics)
    payload = _api(
        "sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": "\n".join(text_lines),
            "reply_markup": json.dumps(kb),
            "disable_web_page_preview": "true",
        },
    )
    return int(payload["result"]["message_id"])


def wait_for_topic_choice(message_id: int, timeout_sec: int = 300) -> Optional[int]:
    """
    Waits for callback TOPIC::<idx> tied to the message_id.
    Returns idx or None on timeout.
    """
    start = time.time()
    offset = None

    while time.time() - start < timeout_sec:
        params = {"timeout": 20}
        if offset is not None:
            params["offset"] = offset

        r = requests.get(f"{API_BASE}/getUpdates", params=params, timeout=30)
        r.raise_for_status()
        payload = r.json()
        if not payload.get("ok"):
            time.sleep(1)
            continue

        for upd in payload.get("result", []):
            offset = upd["update_id"] + 1

            cq = upd.get("callback_query")
            if not cq:
                continue

            try:
                cq_msg = cq.get("message") or {}
                cq_mid = cq_msg.get("message_id")
                data = (cq.get("data") or "").strip()

                # Always ack to stop Telegram spinner
                _api("answerCallbackQuery", data={"callback_query_id": cq.get("id")})

                if cq_mid != message_id:
                    continue

                if data.startswith("TOPIC::"):
                    idx = int(data.split("::", 1)[1])
                    return idx
            except Exception:
                # ignore malformed
                continue

        time.sleep(0.3)

    return None


def _final_keyboard(project_id: str) -> dict:
    return {
        "inline_keyboard": [
            [{"text": "✅ Approve Final Package", "callback_data": f"FINAL::APPROVE::{project_id}"}],
            [{"text": "🔁 Regenerate Thumbnails", "callback_data": f"FINAL::REGEN_THUMBS::{project_id}"}],
            [{"text": "⛔ Reject", "callback_data": f"FINAL::REJECT::{project_id}"}],
        ]
    }


def send_video(project_id: str, video_path: str, caption: str) -> int:
    with open(video_path, "rb") as f:
        payload = _api(
            "sendVideo",
            data={"chat_id": CHAT_ID, "caption": caption},
            files={"video": f},
        )
    return int(payload["result"]["message_id"])


def send_photo(project_id: str, photo_path: str, caption: str = "") -> int:
    with open(photo_path, "rb") as f:
        payload = _api(
            "sendPhoto",
            data={"chat_id": CHAT_ID, "caption": caption},
            files={"photo": f},
        )
    return int(payload["result"]["message_id"])


def send_final_package(project_id: str, title: str, video_path: str, thumbs: List[str]) -> int:
    """
    Sends:
    - 3 thumbnails (photos)
    - 1 video
    - final approval message with buttons
    Returns approval message_id (the one with buttons).
    """
    # Thumbs first (so user sees options immediately)
    for i, p in enumerate(thumbs, start=1):
        send_photo(project_id, p, caption=f"🖼 Thumbnail {i}/3 — {title}")

    vid_mid = send_video(
        project_id,
        video_path,
        caption=f"🎬 Video Preview — {title}\nPROJECT_ID: {project_id}",
    )

    kb = _final_keyboard(project_id)
    approval_msg = _api(
        "sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": f"📦 Final package ready\nPROJECT_ID: {project_id}\n\nПогодити фінальний пакет?",
            "reply_markup": json.dumps(kb),
        },
    )
    return int(approval_msg["result"]["message_id"])


def wait_for_final_action(project_id: str, message_id: int, timeout_sec: int = 600) -> Optional[str]:
    """
    Waits for FINAL::<ACTION>::<project_id> callback tied to message_id.
    Returns action in {"APPROVE","REGEN_THUMBS","REJECT"} or None on timeout.
    """
    start = time.time()
    offset = None

    while time.time() - start < timeout_sec:
        params = {"timeout": 20}
        if offset is not None:
            params["offset"] = offset

        r = requests.get(f"{API_BASE}/getUpdates", params=params, timeout=30)
        r.raise_for_status()
        payload = r.json()
        if not payload.get("ok"):
            time.sleep(1)
            continue

        for upd in payload.get("result", []):
            offset = upd["update_id"] + 1
            cq = upd.get("callback_query")
            if not cq:
                continue

            try:
                cq_msg = cq.get("message") or {}
                cq_mid = cq_msg.get("message_id")
                data = (cq.get("data") or "").strip()

                _api("answerCallbackQuery", data={"callback_query_id": cq.get("id")})

                if cq_mid != message_id:
                    continue

                if data.startswith("FINAL::"):
                    parts = data.split("::")
                    if len(parts) == 3 and parts[2] == project_id:
                        return parts[1]
            except Exception:
                continue

        time.sleep(0.3)

    return None
