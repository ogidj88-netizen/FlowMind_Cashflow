#!/usr/bin/env python3
"""
FlowMind Cashflow — ENV Audit (SAFE)
- Checks all keys listed in .env (by name)
- Prints ✅/❌ without exposing values
- Optionally validates OpenAI key with a live call (models.list)
"""

import os
import sys
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"


def load_env_file(path: Path) -> None:
    if not path.exists():
        print(f"⛔ .env not found at: {path}")
        sys.exit(1)

    from dotenv import load_dotenv
    load_dotenv(dotenv_path=str(path), override=True)


def read_env_key_names(path: Path) -> list[str]:
    names = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if "=" not in s:
            continue
        k = s.split("=", 1)[0].strip()
        if k:
            names.append(k)
    # unique while preserving order
    seen = set()
    out = []
    for k in names:
        if k not in seen:
            seen.add(k)
            out.append(k)
    return out


def validate_openai() -> bool:
    key = (os.getenv("OPENAI_API_KEY") or "").strip()
    if not key:
        print("⛔ OPENAI_API_KEY missing -> FAIL")
        return False
    try:
        from openai import OpenAI
        client = OpenAI(api_key=key)
        _ = client.models.list()
        print("✅ OPENAI live check: OK")
        return True
    except Exception as e:
        msg = str(e)
        if len(msg) > 220:
            msg = msg[:220] + "..."
        print(f"⛔ OPENAI live check: FAIL -> {msg}")
        return False


def main():
    load_env_file(ENV_PATH)
    keys = read_env_key_names(ENV_PATH)

    print(f"=== ENV AUDIT: {ENV_PATH} ===")
    missing = []
    present = []

    for k in keys:
        v = os.getenv(k)
        ok = bool(v and str(v).strip())
        if ok:
            present.append(k)
            print(f"✅ {k}")
        else:
            missing.append(k)
            print(f"❌ {k}")

    print("\n=== SUMMARY ===")
    print(f"Present: {len(present)}")
    print(f"Missing: {len(missing)}")

    # Critical-now set (for current working pipeline)
    critical_now = ["OPENAI_API_KEY", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
    critical_missing = [k for k in critical_now if k in missing]
    print("\n=== CRITICAL NOW ===")
    if critical_missing:
        print("⛔ Missing critical keys:", ", ".join(critical_missing))
        sys.exit(2)
    else:
        print("✅ All critical keys present")

    print("\n=== OPENAI LIVE CHECK ===")
    if not validate_openai():
        sys.exit(3)

    print("\n✅ ENV AUDIT PASSED")


if __name__ == "__main__":
    main()
