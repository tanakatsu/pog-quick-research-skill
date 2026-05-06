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


def test_load_cache_non_list_json(tmp_path, capsys):
    cache_file = tmp_path / "horse_list.json"
    cache_file.write_text('{"name": "テスト馬"}', encoding="utf-8")

    result = load_cache(str(cache_file))
    assert result == []
    captured = capsys.readouterr()
    assert "Warning" in captured.err


from unittest.mock import patch
from get_horse_id import save_cache


def test_save_cache_writes_file(tmp_path):
    data = [{"name": "テスト馬", "mare": "テスト母", "horse_id": "2023001001"}]
    cache_file = tmp_path / "horse_list.json"

    save_cache(str(cache_file), data)

    written = json.loads(cache_file.read_text(encoding="utf-8"))
    assert written == data


def test_save_cache_write_failure_warns(tmp_path, capsys):
    data = [{"name": "テスト馬", "mare": "テスト母", "horse_id": "2023001001"}]
    cache_file = tmp_path / "horse_list.json"

    with patch("builtins.open", side_effect=IOError("disk full")):
        save_cache(str(cache_file), data)

    captured = capsys.readouterr()
    assert "Warning" in captured.err
