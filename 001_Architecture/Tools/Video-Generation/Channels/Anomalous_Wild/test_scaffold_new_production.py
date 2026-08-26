from pathlib import Path
from scaffold_new_production import scaffold, END_CARD_PATH


def test_scaffold_creates_typed_folders(tmp_path):
    prod_root = tmp_path / "0002_Test_Production"
    scaffold(prod_root)
    for folder in ["Scripts", "Production", "Images", "Video_Clips", "Narration_Audio", "Audio_Stems", "Assembly", "Package", "Data"]:
        assert (prod_root / folder).is_dir()


def test_end_card_is_locked_constant():
    assert END_CARD_PATH.name == "Anomalos_Wild_End-Card_Hero.mp4"


def test_scaffold_creates_generation_log_and_report_card(tmp_path):
    prod_root = tmp_path / "0002_Test_Production"
    scaffold(prod_root)
    assert (prod_root / "Data" / "Generation_Log.json").is_file()
    assert (prod_root / "Data" / "Report_Card.md").is_file()


def test_scaffold_does_not_overwrite_existing_data_files(tmp_path):
    prod_root = tmp_path / "0002_Test_Production"
    scaffold(prod_root)
    log_path = prod_root / "Data" / "Generation_Log.json"
    log_path.write_text('{"production": "already populated"}')
    scaffold(prod_root)
    assert log_path.read_text() == '{"production": "already populated"}'
