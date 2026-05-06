import argparse
import asyncio
import json
import sys
from pathlib import Path

from netkeiba.board import fetch_all_board_comments
from netkeiba.browser import browser_context


async def main(args: argparse.Namespace) -> int:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    async with browser_context() as ctx:
        try:
            comments = await fetch_all_board_comments(ctx, args.horse_id)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    output_path = output_dir / f"{args.horse_id}.json"
    output_path.write_text(
        json.dumps(comments, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"保存: {output_path} ({len(comments)} 件)")
    return 0


def cli() -> None:
    parser = argparse.ArgumentParser(
        description="netkeiba 掲示板コメントを全ページ取得して JSON に保存する"
    )
    parser.add_argument("horse_id", help="馬ID")
    parser.add_argument("-o", "--output-dir", default="cache", help="出力ディレクトリ (デフォルト: cache)")
    args = parser.parse_args()
    sys.exit(asyncio.run(main(args)))


if __name__ == "__main__":
    cli()
