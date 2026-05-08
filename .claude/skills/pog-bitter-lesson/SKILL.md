---
name: pog-bitter-lesson
description: POGで期待ほど活躍できなかった馬についてポストモーテムを行い、学びを提供するレポートを作成する
---

# POGの事後検証を目的とした馬レポートを作成する

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
    - キャッシュデータが存在しない場合、掲示板コメント取得のPythonスクリプトを実行する
5. 分析期間のコメントの抽出
    - {馬IDの最初の4桁の数字 + 2}年5月末までのコメント情報を取得する。それ以後のコメントは分析対象外とする
    - 掲示板コメントデータの期間フィルタリングのPythonスクリプトを実行して、分析期間のコメントを抽出する
6. 取得できた全ページのテキストから主観的なコメントは除外し、客観的なコメントを抜き出す
7. 対象馬が活躍しなかったと仮定し、コメントのどこに不安要素が隠れていたか、そのサインを注意深く分析し、レポートとしてまとめる
    - レポートの内容の形式
        - 基本情報
        - ポジティブな客観的コメント
        - 不安要素・ネガティブな客観的コメント（後から見れば「サイン」だったもの）
        - 総合分析：隠れていた不安のサイン
        - 結論
8. レポートの内容を`{馬名}_{日付(YYYYMMDD)}.txt`に保存する

## Available scripts

- 馬IDの取得
    - 馬名から検索: `uv run python scripts/get_horse_id.py --name {馬名} --age {年齢:省略可}`
    - 母馬名から検索: `uv run python scripts/get_horse_id.py --mare {母馬名} --age {年齢:省略可}`
- 掲示板コメントの取得: `uv run python scripts/get_board_comments.py {馬ID}`
- 馬情報の取得: `uv run python scripts/get_horse_info.py {馬ID}`
- 母馬の繁殖成績の取得: `uv run python scripts/get_breeding_performance.py {母馬ID}`
- 掲示板コメントデータの期間フィルタリング: `uv run python scripts/filter_comments.py {馬ID} --to {YYYMMDD}`

## Additional resources

- 判断ポイントの優先度: [references/checklist.md](references/checklist.md)
- POG向き種牡馬: [references/sire.md](references/sire.md)
- POG向き母父: [references/bms.md](references/bms.md)
- POG向き母馬: [references/mare.md](references/mare.md)
- POG向き配合: [references/nix.md](references/nix.md)
- POG向き調教師: [references/trainer.md](references/trainer.md)
- POG向き馬主: [references/owner.md](references/owner.md)
- POG向き馬体: [references/body.md](references/body.md)
- 関係者コメントの読み取り方: [references/comment.md](references/comment.md)
