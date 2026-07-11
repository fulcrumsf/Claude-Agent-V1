import json
from pathlib import Path
from extract_compliance_sources import extract_knowledge_ids, write_sources_json


def test_extracts_unique_knowledge_id(tmp_path):
    (tmp_path / "doc1.md").write_text(
        "See [policy](https://seller-us.tiktok.com/university/essay?knowledge_id=123&role=1&from=search)"
    )
    result = extract_knowledge_ids(tmp_path)
    assert result == {"123": "https://seller-us.tiktok.com/university/essay?knowledge_id=123"}


def test_dedupes_same_knowledge_id_with_different_tracking_params(tmp_path):
    (tmp_path / "doc1.md").write_text(
        "https://seller-us.tiktok.com/university/essay?knowledge_id=555&role=1&identity=1"
    )
    (tmp_path / "doc2.md").write_text(
        "https://seller-us.tiktok.com/university/essay?knowledge_id=555#some-anchor"
    )
    result = extract_knowledge_ids(tmp_path)
    assert result == {"555": "https://seller-us.tiktok.com/university/essay?knowledge_id=555"}


def test_extracts_multiple_distinct_ids(tmp_path):
    (tmp_path / "doc1.md").write_text(
        "a: https://seller-us.tiktok.com/university/essay?knowledge_id=111\n"
        "b: https://seller-us.tiktok.com/university/essay?knowledge_id=222&lang=en"
    )
    result = extract_knowledge_ids(tmp_path)
    assert set(result.keys()) == {"111", "222"}


def test_write_sources_json(tmp_path):
    out_path = tmp_path / "Compliance-Sources.json"
    write_sources_json({"123": "https://seller-us.tiktok.com/university/essay?knowledge_id=123"}, out_path)
    loaded = json.loads(out_path.read_text())
    assert loaded == {"123": "https://seller-us.tiktok.com/university/essay?knowledge_id=123"}
