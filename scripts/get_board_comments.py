import argparse
import asyncio
import sys
from pathlib import Path

from netkeiba.board import fetch_all_board_comments
from netkeiba.browser import browser_context


async def main(args: argparse.Namespace) -> int:
    output_dir = Path(args.output_dir)
    async with browser_context() as ctx:
        try:
            await fetch_all_board_comments(ctx, args.horse_id, output_dir)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    return 0


def cli() -> None:
    parser = argparse.ArgumentParser(
        description="netkeiba 掲示板コメントを全ページ取得して保存する"
    )
    parser.add_argument("horse_id", help="馬ID")
    parser.add_argument("-o", "--output-dir", default="cache", help="出力ディレクトリ (デフォルト: cache)")
    args = parser.parse_args()
    sys.exit(asyncio.run(main(args)))


if __name__ == "__main__":
    cli()
