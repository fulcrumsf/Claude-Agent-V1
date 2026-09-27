"""Shot 06 environment-panel generator: reads a saved prompt file (front matter stripped), calls GPT-Image-2 via the skill's image_generation, never overwrites."""
import sys, pathlib
sys.path.insert(0,'/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/Environment-Sheet-Generation/scripts')
from image_generation import generate_image
prompt_file, out, aspect = sys.argv[1], pathlib.Path(sys.argv[2]), sys.argv[3]
refs = sys.argv[4:] or None
assert not out.exists(), f'never overwrite {out}'
txt = pathlib.Path(prompt_file).read_text().split('---\n',2)[2].strip()
generate_image(txt, out, aspect, '2K', refs)
print('generated', out)
