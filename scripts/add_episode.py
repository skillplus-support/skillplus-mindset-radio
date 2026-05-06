#!/usr/bin/env python3
"""
マインドセットラジオに新エピソードを追加する自動化スクリプト。

使い方:
    python3 scripts/add_episode.py <音声ファイル> <番号> "<タイトル>" "<説明>"

例:
    python3 scripts/add_episode.py ~/Desktop/マインドセット⑤.m4a 5 "他人と比べた瞬間、人生は他人のもの" "他人と比べる時間を、自分の歩幅を確かめる時間に使え。"

実行内容:
    1. 音声ファイルを audio/05.m4a にコピー
    2. ファイルサイズと再生時間を取得
    3. podcast.xml に <item> 要素を挿入
    4. （オプション）git commit & push
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta


REPO_ROOT = Path(__file__).resolve().parent.parent
PODCAST_XML = REPO_ROOT / "podcast.xml"
AUDIO_DIR = REPO_ROOT / "audio"


def get_duration(audio_path: Path) -> str:
    """ffprobeで再生時間を取得し MM:SS 形式で返す。"""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(audio_path)],
        capture_output=True, text=True, check=True,
    )
    total_seconds = int(float(result.stdout.strip()))
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes:02d}:{seconds:02d}"


def get_size_bytes(audio_path: Path) -> int:
    return audio_path.stat().st_size


def build_item_xml(num: int, title: str, description: str,
                   filename: str, size: int, duration: str,
                   pub_date: str) -> str:
    """新しい <item> ブロックを生成。"""
    num2 = f"{num:02d}"
    return f"""    <item>
      <title>#{num2} {title}</title>
      <description><![CDATA[{description}]]></description>
      <enclosure url="https://skillplus-support.github.io/skillplus-mindset-radio/audio/{filename}" length="{size}" type="audio/x-m4a"/>
      <guid isPermaLink="false">skillplus-mindset-radio-{num2}</guid>
      <pubDate>{pub_date}</pubDate>
      <itunes:author>みかみ（三上功太）</itunes:author>
      <itunes:duration>{duration}</itunes:duration>
      <itunes:episode>{num}</itunes:episode>
      <itunes:explicit>false</itunes:explicit>
    </item>

"""


def insert_item(item_xml: str) -> None:
    """podcast.xml の </channel> の直前に新 <item> を挿入。"""
    text = PODCAST_XML.read_text(encoding="utf-8")
    marker = "  </channel>"
    if marker not in text:
        sys.exit("podcast.xml に </channel> が見つかりません")
    new_text = text.replace(marker, item_xml + marker)
    PODCAST_XML.write_text(new_text, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio", type=Path, help="追加する音声ファイル")
    ap.add_argument("number", type=int, help="エピソード番号（例: 5）")
    ap.add_argument("title", help="エピソードタイトル（# は不要）")
    ap.add_argument("description", help="エピソードの説明（一言で）")
    ap.add_argument("--push", action="store_true",
                    help="commit & push まで自動で行う")
    args = ap.parse_args()

    if not args.audio.exists():
        sys.exit(f"音声ファイルが見つかりません: {args.audio}")

    num2 = f"{args.number:02d}"
    target_filename = f"{num2}.m4a"
    target_path = AUDIO_DIR / target_filename

    if target_path.exists():
        sys.exit(f"同じ番号のファイルが既に存在します: {target_path}")

    # 1. 音声コピー
    AUDIO_DIR.mkdir(exist_ok=True)
    shutil.copy2(args.audio, target_path)
    print(f"[1/3] コピー完了: {target_path}")

    # 2. メタデータ取得
    duration = get_duration(target_path)
    size = get_size_bytes(target_path)
    print(f"[2/3] メタデータ: 再生時間={duration}, サイズ={size} bytes")

    # 3. <item> 挿入
    jst = timezone(timedelta(hours=9))
    pub_date = datetime.now(jst).strftime("%a, %d %b %Y %H:%M:%S %z")
    item_xml = build_item_xml(args.number, args.title, args.description,
                               target_filename, size, duration, pub_date)
    insert_item(item_xml)
    print(f"[3/3] podcast.xml に #{num2} の <item> を追加")

    # 4. オプション: git push
    if args.push:
        print("[git] commit & push 実行中...")
        subprocess.run(["git", "add", "-A"], cwd=REPO_ROOT, check=True)
        subprocess.run(["git", "commit", "-m", f"Add episode #{num2} {args.title}"],
                       cwd=REPO_ROOT, check=True)
        subprocess.run(["git", "push"], cwd=REPO_ROOT, check=True)
        print("[完了] GitHub Pages に反映されるまで1〜3分お待ちください")
        print("確認URL: https://skillplus-support.github.io/skillplus-mindset-radio/podcast.xml")
    else:
        print()
        print("=" * 50)
        print("podcast.xml の更新完了。次の手順で公開：")
        print("  cd ~/dev/skillplus-mindset-radio")
        print(f'  git add -A && git commit -m "Add episode #{num2}" && git push')
        print("=" * 50)


if __name__ == "__main__":
    main()
