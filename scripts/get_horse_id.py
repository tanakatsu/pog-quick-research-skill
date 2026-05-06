import argparse
import asyncio
import datetime
import json
import sys

from netkeiba.browser import browser_context
from netkeiba.horse import search_horse


def load_cache(path: str) -> list[dict]:
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            print(f"Warning: キャッシュ形式エラー（配列が必要）", file=sys.stderr)
            return []
        return data
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Warning: キャッシュ読み込み失敗 ({e})", file=sys.stderr)
        return []


def save_cache(path: str, entries: list[dict]) -> None:
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Warning: キャッシュ書き込み失敗 ({e})", file=sys.stderr)


def search_cache(
    entries: list[dict],
    *,
    name: str | None,
    mare: str | None,
    age: int | None,
) -> dict | list[dict] | None:
    if name is not None:
        hits = [e for e in entries if e.get("name") == name]
    else:
        hits = [e for e in entries if e.get("mare") == mare]

    if age is not None:
        birth_year = str(datetime.date.today().year - age)
        hits = [e for e in hits if e.get("horse_id", "").startswith(birth_year)]

    if not hits:
        return None
    if len(hits) == 1:
        return hits[0]
    return hits


def add_to_cache(entries: list[dict], result: dict | list[dict]) -> list[dict]:
    if isinstance(result, dict):
        if "error" in result:
            return entries
        new_entries = [result]
    else:
        new_entries = result

    existing_ids = {e["horse_id"] for e in entries}
    added = [e for e in new_entries if e.get("horse_id") not in existing_ids]
    return entries + added


async def main(args: argparse.Namespace) -> int:
    async with browser_context() as ctx:
        try:
            result = await search_horse(ctx, name=args.name, mare=args.mare, age=args.age)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    print(json.dumps(result, ensure_ascii=False))

    # 想定外エラーは exit 1、「該当なし」は正常扱いで exit 0
    if (
        isinstance(result, dict)
        and "error" in result
        and result["error"] != "該当データが存在しません"
    ):
        return 1
    return 0


def cli() -> None:
    parser = argparse.ArgumentParser(
        description="netkeiba から馬IDを取得する"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--name", help="馬名（完全一致）")
    group.add_argument("--mare", help="母馬名")
    parser.add_argument(
        "--age",
        type=int,
        default=None,
        help="年齢（省略時: 2歳〜指定なし）",
    )
    args = parser.parse_args()
    sys.exit(asyncio.run(main(args)))


if __name__ == "__main__":
    cli()
