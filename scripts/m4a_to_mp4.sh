#!/bin/bash
# m4a_to_mp4.sh - 音声(m4a) + サムネ(cover.jpg) を YouTube用 mp4 にする
# Usage:
#   ./scripts/m4a_to_mp4.sh <episode_number>    # 1本だけ
#   ./scripts/m4a_to_mp4.sh all                  # audio/ の全m4a
#
# 出力先: youtube_uploads/NN.mp4

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
COVER="$REPO_DIR/cover.jpg"
AUDIO_DIR="$REPO_DIR/audio"
OUT_DIR="$REPO_DIR/youtube_uploads"

if [ $# -lt 1 ]; then
  echo "Usage: $0 <episode_number|all>"
  echo "  例: $0 5"
  echo "      $0 all"
  exit 1
fi

if [ ! -f "$COVER" ]; then
  echo "サムネ画像が見つからない: $COVER"
  exit 1
fi

mkdir -p "$OUT_DIR"

convert_one() {
  local n="$1"
  local nn
  nn=$(printf "%02d" "$n")
  local audio="$AUDIO_DIR/${nn}.m4a"
  local out="$OUT_DIR/${nn}.mp4"

  if [ ! -f "$audio" ]; then
    echo "skip: $audio が無い"
    return 0
  fi

  echo "→ ${nn}.m4a → ${nn}.mp4"
  ffmpeg -y -loop 1 -framerate 2 -i "$COVER" -i "$audio" \
    -c:v libx264 -tune stillimage -preset veryfast \
    -c:a copy -pix_fmt yuv420p -shortest \
    "$out" 2>&1 | tail -2

  ls -lh "$out" | awk '{print "  →", $5, $9}'
}

if [ "$1" = "all" ]; then
  for f in "$AUDIO_DIR"/*.m4a; do
    [ -e "$f" ] || continue
    base=$(basename "$f" .m4a)
    convert_one "$((10#$base))"
  done
else
  convert_one "$1"
fi

echo ""
echo "完了。アップロード対象: $OUT_DIR/"
