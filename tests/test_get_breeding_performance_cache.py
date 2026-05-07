import json
import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from get_breeding_performance import load_cache, save_cache


def test_load_cache_file_not_found(tmp_path):
    result = load_cache(str(tmp_path / "nonexistent.json"))
    assert result == {}


def test_load_cache_valid_file(tmp_path):
    data = {"2019104926": {"mare_name": "テスト母馬", "progeny_results": []}}
    cache_file = tmp_path / "horse_breeding_performance.json"
    cache_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    assert load_cache(str(cache_file)) == data


def test_load_cache_corrupted_file(tmp_path, capsys):
    cache_file = tmp_path / "horse_breeding_performance.json"
    cache_file.write_text("not valid json", encoding="utf-8")
    result = load_cache(str(cache_file))
    assert result == {}
    assert "Warning" in capsys.readouterr().err


def test_load_cache_non_dict_json(tmp_path, capsys):
    cache_file = tmp_path / "horse_breeding_performance.json"
    cache_file.write_text("[1, 2, 3]", encoding="utf-8")
    result = load_cache(str(cache_file))
    assert result == {}
    assert "Warning" in capsys.readouterr().err


def test_save_cache_writes_file(tmp_path):
    data = {"2019104926": {"mare_name": "テスト母馬", "progeny_results": []}}
    cache_file = tmp_path / "horse_breeding_performance.json"
    save_cache(str(cache_file), data)
    written = json.loads(cache_file.read_text(encoding="utf-8"))
    assert written == data


def test_save_cache_creates_directory(tmp_path):
    data = {"2019104926": {"mare_name": "テスト母馬", "progeny_results": []}}
    cache_file = tmp_path / "subdir" / "horse_breeding_performance.json"
    save_cache(str(cache_file), data)
    assert cache_file.exists()
    written = json.loads(cache_file.read_text(encoding="utf-8"))
    assert written == data


def test_save_cache_write_failure_warns(tmp_path, capsys):
    data = {"2019104926": {"mare_name": "テスト母馬", "progeny_results": []}}
    cache_file = tmp_path / "horse_breeding_performance.json"
    with patch("builtins.open", side_effect=IOError("disk full")):
        save_cache(str(cache_file), data)
    assert "Warning" in capsys.readouterr().err
