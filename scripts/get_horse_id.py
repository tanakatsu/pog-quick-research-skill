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
