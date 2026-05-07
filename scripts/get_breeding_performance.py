import argparse
import asyncio
import json
import os
import sys

from netkeiba.browser import browser_context
from netkeiba.breeding import fetch_breeding_performance


def load_cache(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            print("Warning: キャッシュ形式エラー（辞書が必要）", file=sys.stderr)
            return {}
        return data
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"Warning: キャッシュ読み込み失敗 ({e})", file=sys.stderr)
        return {}


def save_cache(path: str, data: dict) -> None:
    try:
        dir_name = os.path.dirname(path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Warning: キャッシュ書き込み失敗 ({e})", file=sys.stderr)


async def main(args: argparse.Namespace) -> int:
    cache = load_cache(args.cache)

    if args.mare_id in cache:
        print(json.dumps(cache[args.mare_id], ensure_ascii=False))
        return 0

    async with browser_context() as ctx:
        try:
            result = await fetch_breeding_performance(ctx, args.mare_id)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    print(json.dumps(result, ensure_ascii=False))
    cache[args.mare_id] = result
    save_cache(args.cache, cache)
    return 0


def cli() -> None:
    parser = argparse.ArgumentParser(description="netkeiba から繁殖成績を取得する")
    parser.add_argument("mare_id", help="母馬ID")
    parser.add_argument(
        "--cache",
        default="cache/horse_breeding_performance.json",
        help="キャッシュファイルのパス（デフォルト: cache/horse_breeding_performance.json）",
    )
    args = parser.parse_args()
    sys.exit(asyncio.run(main(args)))


if __name__ == "__main__":
    cli()
