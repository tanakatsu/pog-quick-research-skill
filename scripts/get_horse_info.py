import argparse
import asyncio
import json
import os
import sys

from netkeiba.browser import browser_context
from netkeiba.horse_info import fetch_horse_info


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

    if args.horse_id in cache:
        print(json.dumps(cache[args.horse_id], ensure_ascii=False))
        return 0

    async with browser_context() as ctx:
        try:
            info = await fetch_horse_info(ctx, args.horse_id)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    print(json.dumps(info, ensure_ascii=False))
    cache[args.horse_id] = info
    save_cache(args.cache, cache)
    return 0


def cli() -> None:
    parser = argparse.ArgumentParser(description="netkeiba から馬情報を取得する")
    parser.add_argument("horse_id", help="馬ID")
    parser.add_argument(
        "--cache",
        default="cache/horse_info.json",
        help="キャッシュファイルのパス（デフォルト: cache/horse_info.json）",
    )
    args = parser.parse_args()
    sys.exit(asyncio.run(main(args)))


if __name__ == "__main__":
    cli()
