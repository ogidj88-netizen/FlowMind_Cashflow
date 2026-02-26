import os
import time
import subprocess
from pathlib import Path
from typing import List, Dict

from openai import OpenAI

from engine.alerts.telegram_gate import (
    send_topic_options,
    wait_for_topic_choice,
    send_final_package,
    wait_for_final_action,
)

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "out"
FFMPEG = (os.getenv("FFMPEG_BIN_PATH") or "ffmpeg").strip()

MODEL = (os.getenv("ROUTING_PREMIUM_MODEL") or "gpt-4o-mini").strip()
LOCALE = (os.getenv("DEFAULT_LOCALE") or "en").strip()


def _ensure_dirs(project_id: str) -> Path:
    pdir = OUT_DIR / project_id
    pdir.mkdir(parents=True, exist_ok=True)
    return pdir


def _openai_client() -> OpenAI:
    key = (os.getenv("OPENAI_API_KEY") or "").strip()
    if not key:
        raise RuntimeError("OPENAI_API_KEY missing")
    return OpenAI(api_key=key)


def generate_topics() -> List[Dict]:
    """
    Returns exactly 3 topics with decimal scores (0.0..10.0).
    No script generation here.
    """
    client = _openai_client()

    system = (
        "You are a ruthless YouTube topic selector for the niche: Money Mistakes / Invisible Costs.\n"
        "Output MUST be exactly 3 topics as JSON array.\n"
        "Each item: {\"title\": str, \"score\": float}.\n"
        "Score is 0.0..10.0 with one decimal (e.g., 8.5).\n"
        "Titles must be clickbait but plausible, include a concrete number ($), and be 7-11 words.\n"
        "No extra keys. No commentary. JSON only."
    )

    user = (
        "Generate 3 topic candidates for today.\n"
        "Constraints:\n"
        "- English titles\n"
        "- Each has a specific dollar amount\n"
        "- Focus on insurance, subscriptions, fees, or daily habits\n"
        "- Avoid YMYL medical/diagnosis claims\n"
        "- Score reflects: CPM potential + curiosity + simplicity + stock-first fit\n"
    )

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.7,
    )

    raw = resp.choices[0].message.content.strip()

    # Parse JSON safely without extra deps
    import json
    topics = json.loads(raw)
    if not isinstance(topics, list) or len(topics) != 3:
        raise RuntimeError("Topic generator returned invalid shape (expected list of 3).")

    cleaned = []
    for t in topics:
        title = str(t.get("title", "")).strip()
        score = float(t.get("score"))
        # normalize to 1 decimal
        score = round(score * 10) / 10.0
        if score < 0:
            score = 0.0
        if score > 10:
            score = 10.0
        cleaned.append({"title": title, "score": score})

    return cleaned


def _make_dummy_video(final_path: Path, seconds: int = 8):
    """
    Creates a small preview mp4 as a placeholder for the pipeline output.
    If you already have a real assembler later, swap this function only.
    """
    # Use a simple color + text. Keep it deterministic.
    cmd = [
        FFMPEG,
        "-y",
        "-f", "lavfi",
        "-i", f"color=c=black:s=1280x720:d={seconds}",
        "-vf", "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
               "text='FLOWMIND CASHFLOW PREVIEW':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=(h-text_h)/2",
        "-r", "30",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(final_path),
    ]
    subprocess.run(cmd, check=True)


def _make_thumbnail(path: Path, line1: str, line2: str):
    """
    Generates a clickbait-style thumbnail candidate (jpg).
    """
    # Two lines, big type, high contrast, deterministic layout.
    # Keep text short to avoid Telegram truncation.
    safe1 = line1.replace(":", "").replace("'", "")
    safe2 = line2.replace(":", "").replace("'", "")

    vf = (
        "scale=1280:720,"
        "drawbox=x=0:y=0:w=iw:h=ih:color=black@1:t=fill,"
        "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
        f"text='{safe1}':fontcolor=white:fontsize=78:x=(w-text_w)/2:y=200,"
        "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
        f"text='{safe2}':fontcolor=white:fontsize=64:x=(w-text_w)/2:y=330"
    )

    cmd = [
        FFMPEG,
        "-y",
        "-f", "lavfi",
        "-i", "color=c=black:s=1280x720:d=1",
        "-vf", vf,
        "-frames:v", "1",
        str(path),
    ]
    subprocess.run(cmd, check=True)


def produce_assets(project_id: str, topic_title: str) -> Dict:
    """
    Production stage:
    - Generates final.mp4
    - Generates 3 thumbnail candidates
    """
    pdir = _ensure_dirs(project_id)
    video_path = pdir / "final.mp4"

    # Minimal “production” for now
    _make_dummy_video(video_path, seconds=8)

    # 3 clickbait-ish angles (text-only templates for now)
    # Later we can swap to Cloudinary/Remotion/real image generation.
    t1 = pdir / "thumb_A.jpg"
    t2 = pdir / "thumb_B.jpg"
    t3 = pdir / "thumb_C.jpg"

    # Derive number from title if possible, else force a big number hook
    num = "$3,000"
    for token in ["$5", "$10", "$99", "$300", "$1,800", "$3,000", "$7,200"]:
        if token in topic_title:
            num = token
            break

    _make_thumbnail(t1, f"STOP LOSING {num}", "ONE HIDDEN TRICK")
    _make_thumbnail(t2, f"{num} GONE?", "YOU DID THIS DAILY")
    _make_thumbnail(t3, f"THE {num} TRAP", "NOBODY WARNED YOU")

    return {
        "project_id": project_id,
        "video_path": str(video_path),
        "thumbs": [str(t1), str(t2), str(t3)],
    }


def main():
    # 1) Create a project id and send ONLY topics
    project_id = f"FM_{int(time.time())}"
    print("🧠 Generating auto-scored topics...")
    topics = generate_topics()

    msg_id = send_topic_options(project_id, topics)
    print("Waiting for topic selection...")

    idx = wait_for_topic_choice(msg_id, timeout_sec=600)
    if idx is None:
        print("⛔ Timeout waiting for topic selection.")
        return

    selected = topics[idx]["title"]
    print(f"✅ Selected topic: {selected}")
    print(f"🎯 Topic Approved: {selected}")

    # 2) Production
    assets = produce_assets(project_id, selected)
    print("📦 Sending final package preview to Telegram...")

    approval_msg_id = send_final_package(
        project_id=project_id,
        title=selected,
        video_path=assets["video_path"],
        thumbs=assets["thumbs"],
    )

    # 3) Final approval loop (approve / regen thumbs / reject)
    while True:
        action = wait_for_final_action(project_id, approval_msg_id, timeout_sec=900)
        if action is None:
            print("⛔ Timeout waiting for final approval action.")
            return

        if action == "APPROVE":
            print("\n🚀 FINAL APPROVAL RECEIVED — STARTING PRODUCTION...\n")
            # Here we already created the assets; in real pipeline we'd lock + finalize.
            print(f"✅ Production Completed.")
            return

        if action == "REGEN_THUMBS":
            print("🔁 Regenerating thumbnails...")
            pdir = _ensure_dirs(project_id)
            # regenerate with slight variation in text hooks
            t1 = pdir / "thumb_A.jpg"
            t2 = pdir / "thumb_B.jpg"
            t3 = pdir / "thumb_C.jpg"
            _make_thumbnail(t1, "INVISIBLE FEES", "STEAL YOUR MONEY")
            _make_thumbnail(t2, "SUBSCRIPTION TRAP", "YOU FORGOT THIS")
            _make_thumbnail(t3, "INSURANCE HACK", "SAVES THOUSANDS")

            approval_msg_id = send_final_package(
                project_id=project_id,
                title=selected,
                video_path=assets["video_path"],
                thumbs=[str(t1), str(t2), str(t3)],
            )
            continue

        if action == "REJECT":
            print("⛔ Final package rejected.")
            return


if __name__ == "__main__":
    main()
