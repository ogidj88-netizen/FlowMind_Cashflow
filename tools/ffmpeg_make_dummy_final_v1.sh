#!/usr/bin/env bash
set -euo pipefail

# FlowMind — Dummy Final Generator v1.3 (FFmpeg Stability Standard v1.2)
# Output target:
# - video: 1920x1080, 30 FPS CFR, H.264 (libx264), yuv420p, setsar=1, +faststart, threads=2
# - audio: AAC, 48kHz, stereo, 192k
#
# Usage:
#   tools/ffmpeg_make_dummy_final_v1.sh <OUT_MP4> <DURATION_SECONDS>

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <OUT_MP4> <DURATION_SECONDS>" >&2
  exit 2
fi

OUT_MP4="$1"
DUR="$2"

command -v ffmpeg >/dev/null 2>&1 || { echo "[FAIL] ffmpeg not found" >&2; exit 3; }
command -v ffprobe >/dev/null 2>&1 || { echo "[FAIL] ffprobe not found" >&2; exit 3; }

# Duration validation (0 < dur <= 3600)
python3 -c 'import sys; s=sys.argv[1]; v=float(s); assert 0 < v <= 3600' "$DUR" >/dev/null 2>&1 \
  || { echo "[FAIL] invalid duration: $DUR" >&2; exit 2; }

mkdir -p "$(dirname "$OUT_MP4")"
TMP_MP4="${OUT_MP4}.tmp.$RANDOM.$RANDOM.mp4"

# NOTE:
# - do NOT use deprecated -vsync
# - enforce CFR via -fps_mode cfr
ffmpeg -hide_banner -y \
  -f lavfi -i "color=c=black:s=1920x1080:r=30:d=${DUR}" \
  -f lavfi -i "anullsrc=channel_layout=stereo:sample_rate=48000" \
  -shortest \
  -c:v libx264 -pix_fmt yuv420p -r 30 -fps_mode cfr -preset veryfast -crf 23 \
  -c:a aac -b:a 192k -ar 48000 -ac 2 \
  -movflags +faststart \
  -vf "setsar=1" \
  -threads 2 \
  "$TMP_MP4"

# Hard validation via ffprobe JSON (no fragile line-order parsing)
ffprobe -v error -print_format json -show_streams -show_format "$TMP_MP4" \
| python3 -c '
import json, sys
j=json.load(sys.stdin)
streams=j.get("streams", [])
v=[s for s in streams if s.get("codec_type")=="video"]
a=[s for s in streams if s.get("codec_type")=="audio"]
if not v:
  print("[FAIL] no video stream", file=sys.stderr); sys.exit(10)
if not a:
  print("[FAIL] no audio stream", file=sys.stderr); sys.exit(11)

vs=v[0]
w=int(vs.get("width",0)); h=int(vs.get("height",0))
rfr=vs.get("r_frame_rate","")
afr=vs.get("avg_frame_rate","")
pix=vs.get("pix_fmt","")

if (w,h)!=(1920,1080):
  print(f"[FAIL] bad resolution: {w}x{h}", file=sys.stderr); sys.exit(12)
if rfr!="30/1":
  print(f"[FAIL] bad r_frame_rate: {rfr}", file=sys.stderr); sys.exit(13)
if afr!="30/1":
  print(f"[FAIL] bad avg_frame_rate: {afr}", file=sys.stderr); sys.exit(14)
if pix!="yuv420p":
  print(f"[FAIL] bad pix_fmt: {pix}", file=sys.stderr); sys.exit(15)

as0=a[0]
sr=str(as0.get("sample_rate",""))
ch=int(as0.get("channels",0))
if sr!="48000":
  print(f"[FAIL] bad sample_rate: {sr}", file=sys.stderr); sys.exit(16)
if ch!=2:
  print(f"[FAIL] bad channels: {ch}", file=sys.stderr); sys.exit(17)

print(f"[OK] ffprobe PASS: {w}x{h} r={rfr} avg={afr} pix={pix} audio_sr={sr} ch={ch}")
' >/dev/null

mv -f "$TMP_MP4" "$OUT_MP4"
echo "[OK] Dummy final created (30fps CFR + audio): $OUT_MP4"
