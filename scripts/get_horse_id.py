import argparse
import asyncio
import json
import sys

from netkeiba.browser import browser_context
from netkeiba.horse import search_horse


async def main(args: argparse.Namespace) -> int:
    async with browser_context() as ctx:
        try:
            result = await search_horse(ctx, name=args.name, mare=args.mare)
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
        description="netkeiba から 2歳馬の馬IDを取得する"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--name", help="馬名（完全一致）")
    group.add_argument("--mare", help="母馬名")
    args = parser.parse_args()
    sys.exit(asyncio.run(main(args)))


if __name__ == "__main__":
    cli()
