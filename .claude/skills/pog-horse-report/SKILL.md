---
name: pog-horse-report
description: POGの馬レポートを作成する
---

# POGの馬レポートを作成する

## 手順

1. 対象馬の馬IDを取得する
    - 馬ID取得のPythonスクリプトを実行して、対象馬の馬IDを取得する
    - 馬IDが複数取得できた場合は、ユーザーが選択して対象馬を特定する
    - 馬IDが取得できない場合は、ユーザーに再度馬名や母馬名、年齢などの条件を入力してもらい、再度馬IDの取得を試みる
2. 対象馬の情報を取得する
    - 馬情報取得のPythonスクリプトを実行して、対象馬の基本情報を取得する
3. 対象馬の母馬の繁殖成績を取得する
    - 馬情報から母馬IDを抜き出し、母馬の繁殖成績取得のPythonスクリプトを実行して、母馬の繁殖成績を取得する
4. 掲示板コメントの取得
    - `cache`ディレクトリに`{馬ID}.json`が保存されていればキャッシュデータを使う
    - キャッシュデータが存在しない、もしくは"最新情報"、"キャッシュ更新"、"キャッシュなし"などのキーワードによりキャッシュ使用なしをユーザーが選択したとき、掲示板コメント取得のPythonスクリプトを実行する
5. 取得できた全ページのテキストから主観的なコメントは除外し、客観的なコメントを抜き出す
6. ポジティブな内容とネガティブな内容をまとめ、references以下の資料の内容も踏まえレポートにする
    - レポートの内容の形式
        - 基本情報
        - 近況（時系列）
        - ポジティブな評価
        - ポジティブな評価に含まれる潜在的リスク（期待先行コメントなど）
        - ネガティブ・懸念点
        - 総評
7. レポートの内容を`{馬名}_{日付(YYYYMMDD)}.txt`に保存する

## Available scripts

- 馬IDの取得
    - 馬名から検索: `uv run python scripts/get_horse_id.py --name {馬名} --age {年齢:省略可}`
    - 母馬名から検索: `uv run python scripts/get_horse_id.py --mare {母馬名} --age {年齢:省略可}`
- 掲示板コメントの取得: `uv run python scripts/get_board_comments.py {馬ID}`
- 馬情報の取得: `uv run python scripts/get_horse_info.py {馬ID}`
- 母馬の繁殖成績の取得: `uv run python scripts/get_breeding_performance.py {母馬ID}`

## Additional resources

- 判断ポイントの優先度: [references/checklist.md](references/checklist.md)
- POG向き種牡馬: [references/sire.md](references/sire.md)
- POG向き母父: [references/bms.md](references/bms.md)
- POG向き母馬: [references/mare.md](references/mare.md)
- POG向き配合: [references/nix.md](references/nix.md)
- POG向き調教師: [references/trainer.md](references/trainer.md)
- POG向き馬主: [references/owner.md](references/owner.md)
- POG向き馬体: [references/body.md](references/body.md)
- 生年月日によるPOG診断ポイント: [references/birthdate.md](references/birthdate.md)
- 関係者コメントの読み取り方: [references/comment.md](references/comment.md)
