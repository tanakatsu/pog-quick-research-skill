import json
import sys
import os

# scripts/ を import パスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from get_horse_id import load_cache


def test_load_cache_file_not_found(tmp_path):
    result = load_cache(str(tmp_path / "nonexistent.json"))
    assert result == []


def test_load_cache_valid_file(tmp_path):
    data = [{"name": "テスト馬", "mare": "テスト母", "horse_id": "2023001001"}]
    cache_file = tmp_path / "horse_list.json"
    cache_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    result = load_cache(str(cache_file))
    assert result == data


def test_load_cache_corrupted_file(tmp_path, capsys):
    cache_file = tmp_path / "horse_list.json"
    cache_file.write_text("not valid json", encoding="utf-8")

    result = load_cache(str(cache_file))
    assert result == []
    captured = capsys.readouterr()
    assert "Warning" in captured.err
