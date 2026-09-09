import importlib.util
import pathlib
import pytest
from PIL import Image

TOOL = pathlib.Path("001_Architecture/Tools/Resource-Library-Visualizer")


def load(name):
    spec = importlib.util.spec_from_file_location(name, TOOL / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def rl_fixture(tmp_path):
    root = tmp_path / "007_Resource_Library"
    (root / "Tools").mkdir(parents=True)
    (root / "Tools" / "OpenCode.md").write_text(
        '---\ntitle: "OpenCode"\nsummary: "A CLI"\nurl: "https://opencode.dev"\n'
        'tags:\n  - ai\n  - github-repo\nenriched: 2026-09-05\n---\n![[OpenCode.png]]\n')
    Image.new("RGB", (600, 400), "green").save(root / "Tools" / "OpenCode.png")
    (root / "Tools" / "MisLabel.md").write_text(
        '---\ntitle: "Photoshop Plugin"\nsummary: "wrong"\noriginal_filename: "IMG_8710.PNG"\n'
        'tags:\n  - screenshot\ncreated: 2026-08-01\n---\n![[MisLabel.png]]\n')
    Image.new("RGB", (500, 500), "blue").save(root / "Tools" / "MisLabel.png")
    (root / "Tutorials").mkdir()
    (root / "Tutorials" / "Vid.md").write_text(
        '---\ntitle: "Vid"\ncreated: 2026-07-01\n---\nhttps://youtu.be/abcdefghijk\n')
    # youtube id only in frontmatter, not the body
    (root / "Tutorials" / "FmVid.md").write_text(
        '---\ntitle: "FmVid"\nurl: "https://youtu.be/zzzzzzzzzzz?si=x"\ncreated: 2026-06-01\n'
        '---\n## Summary\ntext only, no link in body\n')
    return root
