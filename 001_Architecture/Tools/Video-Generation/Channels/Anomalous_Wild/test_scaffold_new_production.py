from pathlib import Path
from scaffold_new_production import scaffold, END_CARD_PATH


def test_scaffold_creates_typed_folders(tmp_path):
    prod_root = tmp_path / "0002_Test_Production"
    scaffold(prod_root)
    for folder in ["Scripts", "Production", "Images", "Video_Clips", "Narration_Audio", "Audio_Stems", "Assembly", "Package"]:
        assert (prod_root / folder).is_dir()


def test_end_card_is_locked_constant():
    assert END_CARD_PATH.name == "end_card_v3.mp4"
