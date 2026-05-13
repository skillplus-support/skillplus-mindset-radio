# skillplus-mindset-radio

『**みかみのマインドセットラジオ｜スキルプラス**』のポッドキャスト配信用リポジトリ。
GitHub Pages で podcast.xml と音声ファイルを公開し、YouTube Music 等のRSS対応プラットフォームから受信可能にする。

---

## 構成

```
.
├── README.md           # このファイル
├── podcast.xml         # RSSフィード（YouTube Music等が読みに来る）
├── cover.jpg           # ポッドキャストカバー画像（1400x1400）
└── audio/
    ├── 01.m4a          # #01 苦しみは消せない。喜びは増やせる。
    ├── 02.m4a          # #02 世界で一番、簡単に成長できる場所。
    ├── 03.m4a          # #03 動いた人だけが、結果を出す。
    ├── 04.m4a          # #04 「忙しい」は、諦めの宣言。
    └── 05.m4a          # #05 反対は、心配の裏返し。
```

---

## デプロイ後のURL

GitHub Pagesを有効化すると、以下のURLでアクセス可能になる：

- ポッドキャストRSS：`https://skillplus-support.github.io/skillplus-mindset-radio/podcast.xml`
- カバー画像：`https://skillplus-support.github.io/skillplus-mindset-radio/cover.jpg`
- 各エピソード：`https://skillplus-support.github.io/skillplus-mindset-radio/audio/01.m4a` 等

---

## エピソードを追加する（推奨：自動化スクリプト）

```bash
cd ~/dev/skillplus-mindset-radio

# 例：マインドセット⑤を追加してそのままpushまで
python3 scripts/add_episode.py \
  ~/Desktop/マインドセット⑤.m4a \
  5 \
  "他人と比べた瞬間、人生は他人のもの" \
  "他人と比べる時間を、自分の歩幅を確かめる時間に使え。" \
  --push
```

`--push` を付けると commit & push まで自動。
GitHub Pagesは1〜3分で反映、YouTube Music は次回フィード取得時に新エピソードを認識する。

`--push` を外すと、podcast.xml 更新だけで止まる（手動pushしたい場合）。

## エピソードを追加する（手動）

スクリプト使わず手動でやる場合：

1. 新しい音声ファイルを `audio/05.m4a` として配置
2. `podcast.xml` の `<channel>` 内に新しい `<item>` ブロックを追加（既存のフォーマットを参考に）
3. ファイルサイズと再生時間を取得して入れる：
   ```bash
   ffprobe -v error -show_entries format=duration -of csv=p=0 audio/05.m4a
   ls -la audio/05.m4a
   ```
4. commit & push
