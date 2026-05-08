import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path


def parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y%m%d").date()


def comment_date(comment: dict) -> date:
    return datetime.strptime(comment["date"], "%Y/%m/%d %H:%M").date()


def filter_comments(
    comments: list[dict],
    from_date: date | None,
    to_date: date | None,
) -> list[dict]:
    result = []
    for c in comments:
        d = comment_date(c)
        if from_date and d < from_date:
            continue
        if to_date and d > to_date:
            continue
        result.append(c)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="cache/{horse_id}.json から期間指定でコメントを抽出して JSON 出力する"
    )
    parser.add_argument("horse_id", help="馬ID")
    parser.add_argument(
        "--from",
        dest="from_date",
        metavar="YYYYMMDD",
        type=parse_date,
        default=None,
        help="開始日（当日を含む）",
    )
    parser.add_argument(
        "--to",
        dest="to_date",
        metavar="YYYYMMDD",
        type=parse_date,
        default=None,
        help="終了日（当日を含む）",
    )
    args = parser.parse_args()

    cache_path = Path(__file__).parent.parent / "cache" / f"{args.horse_id}.json"
    if not cache_path.exists():
        print(f"Error: {cache_path} が見つかりません", file=sys.stderr)
        return 1

    with cache_path.open(encoding="utf-8") as f:
        comments = json.load(f)

    filtered = filter_comments(comments, args.from_date, args.to_date)
    print(json.dumps(filtered, ensure_ascii=False, indent=2))
    print(f"{len(filtered)} 件 (全 {len(comments)} 件中)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
