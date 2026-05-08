#!/bin/bash
ln -s .claude/skills/pog-horse-report/references/*.md .claude/skills/pog-bitter-lesson/references
echo "シンボリックリンクを作成しました"

uv sync
echo "依存関係をインストールしました"
