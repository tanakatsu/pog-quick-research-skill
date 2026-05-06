import json
import sys
import os

# scripts/ を import パスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from get_horse_id import load_cache, save_cache


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


def test_save_cache_creates_directory(tmp_path):
    data = [{"name": "テスト馬", "mare": "テスト母", "horse_id": "2023001001"}]
    cache_file = tmp_path / "subdir" / "horse_list.json"  # subdir doesn't exist yet

    save_cache(str(cache_file), data)

    assert cache_file.exists()
    written = json.loads(cache_file.read_text(encoding="utf-8"))
    assert written == data


from get_horse_id import search_cache

SAMPLE_ENTRIES = [
    {"name": "アオイアサヒ", "mare": "サクラマム", "horse_id": "2023001001"},
    {"name": "ハナビスター", "mare": "サクラマム", "horse_id": "2023001002"},
    {"name": "キタノタカラ", "mare": "ユキノマム", "horse_id": "2024001003"},
]


def test_search_cache_by_name_found():
    result = search_cache(SAMPLE_ENTRIES, name="アオイアサヒ", mare=None, age=None)
    assert result == {"name": "アオイアサヒ", "mare": "サクラマム", "horse_id": "2023001001"}


def test_search_cache_by_name_not_found():
    result = search_cache(SAMPLE_ENTRIES, name="存在しない馬", mare=None, age=None)
    assert result is None


def test_search_cache_by_mare_multiple():
    result = search_cache(SAMPLE_ENTRIES, name=None, mare="サクラマム", age=None)
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["horse_id"] == "2023001001"
    assert result[1]["horse_id"] == "2023001002"


def test_search_cache_by_mare_single():
    result = search_cache(SAMPLE_ENTRIES, name=None, mare="ユキノマム", age=None)
    assert result == {"name": "キタノタカラ", "mare": "ユキノマム", "horse_id": "2024001003"}


def test_search_cache_by_mare_not_found():
    result = search_cache(SAMPLE_ENTRIES, name=None, mare="存在しない母", age=None)
    assert result is None


def test_search_cache_age_filter_match():
    import datetime
    current_year = datetime.date.today().year
    age = current_year - 2023  # SAMPLE_ENTRIES の "サクラマム" 産駒は 2023 年生まれ
    result = search_cache(SAMPLE_ENTRIES, name=None, mare="サクラマム", age=age)
    assert isinstance(result, list)
    assert len(result) == 2
    assert all(e["horse_id"].startswith("2023") for e in result)


def test_search_cache_age_filter_no_match():
    import datetime
    current_year = datetime.date.today().year
    age = current_year - 2022  # 2022 年生まれを探すが SAMPLE_ENTRIES には存在しない
    result = search_cache(SAMPLE_ENTRIES, name=None, mare="サクラマム", age=age)
    assert result is None


def test_search_cache_empty_entries():
    result = search_cache([], name="アオイアサヒ", mare=None, age=None)
    assert result is None


from get_horse_id import add_to_cache


def test_add_to_cache_single_dict():
    entries = []
    result = add_to_cache(entries, {"name": "テスト馬", "mare": "テスト母", "horse_id": "2023001001"})
    assert len(result) == 1
    assert result[0]["horse_id"] == "2023001001"


def test_add_to_cache_list():
    entries = []
    new_entries = [
        {"name": "馬A", "mare": "母X", "horse_id": "2023001001"},
        {"name": "馬B", "mare": "母X", "horse_id": "2023001002"},
    ]
    result = add_to_cache(entries, new_entries)
    assert len(result) == 2


def test_add_to_cache_skips_duplicate_horse_id():
    entries = [{"name": "テスト馬", "mare": "テスト母", "horse_id": "2023001001"}]
    result = add_to_cache(entries, {"name": "テスト馬", "mare": "テスト母", "horse_id": "2023001001"})
    assert len(result) == 1


def test_add_to_cache_skips_error_dict():
    entries = []
    result = add_to_cache(entries, {"error": "該当データが存在しません"})
    assert result == []


def test_add_to_cache_partial_duplicates():
    entries = [{"name": "馬A", "mare": "母X", "horse_id": "2023001001"}]
    new_entries = [
        {"name": "馬A", "mare": "母X", "horse_id": "2023001001"},  # duplicate
        {"name": "馬B", "mare": "母X", "horse_id": "2023001002"},  # new
    ]
    result = add_to_cache(entries, new_entries)
    assert len(result) == 2
    assert result[1]["horse_id"] == "2023001002"
