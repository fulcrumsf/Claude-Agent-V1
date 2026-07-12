from pathlib import Path
from scaffold_product_folder import scaffold, slugify


def test_slugify_converts_spaces_to_dashes():
    assert slugify("Colorsmart Pens") == "Colorsmart-Pens"


def test_slugify_strips_extra_whitespace():
    assert slugify("  Colorsmart   Pens  ") == "Colorsmart-Pens"


def test_scaffold_creates_typed_subfolders(tmp_path):
    product_dir = scaffold(tmp_path, 1, "Colorsmart Pens")
    assert product_dir == tmp_path / "0001_Colorsmart-Pens"
    for folder in ["Edit", "Compliance/Vision-Scan", "Compliance/Transcript-Scan", "Package"]:
        assert (product_dir / folder).is_dir()


def test_scaffold_writes_intake_template(tmp_path):
    product_dir = scaffold(tmp_path, 2, "Next Product")
    intake = product_dir / "Intake.md"
    assert intake.is_file()
    content = intake.read_text()
    assert "Next Product" in content
    assert "Source Ingest folder" in content


def test_scaffold_is_idempotent(tmp_path):
    scaffold(tmp_path, 1, "Colorsmart Pens")
    product_dir = scaffold(tmp_path, 1, "Colorsmart Pens")  # run twice, should not error
    assert product_dir.is_dir()


def test_scaffold_writes_ledger_scan_stub(tmp_path):
    product_dir = scaffold(tmp_path, 1, "Colorsmart Pens")
    stub = product_dir / "Compliance" / "Ledger-Scan-Results.md"
    assert stub.is_file()
    assert "Colorsmart Pens" in stub.read_text()
