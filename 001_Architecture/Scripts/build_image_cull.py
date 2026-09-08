"""
Build a visual culling page for every image in 007_Resource_Library.

Generates downscaled thumbnails and one HTML page where you browse all ~10k
images, filter by area (OpenAI_History / Visual_Assets / OpenAI_Images /
Videos-Keyframes / Undetermined), bulk-mark for deletion, and export the list.

Marking an image for deletion also implies its note (the .md that embeds it)
gets removed — apply_image_cull.py handles both.

Nothing in the vault is touched here — this only reads and writes to <out>.

Writes:
  <out>/image_thumbs/...        280px JPEG thumbnails, mirrored path structure
  <out>/image_cull.html         the page
  <out>/image_index.json        image path + bytes + note path, for the apply step

Usage:
  python3 001_Architecture/Scripts/build_image_cull.py
  python3 001_Architecture/Scripts/build_image_cull.py --out ~/Desktop/Resource_Library_Review
"""
import os
import re
import json
import glob
import html
import argparse
from concurrent.futures import ProcessPoolExecutor

from PIL import Image, ImageOps

WORKSPACE = "/Users/tonymacbook2025/Documents/Agent-OS"
RESOURCE_LIB = os.path.join(WORKSPACE, "007_Resource_Library")
IMG_EXT = (".png", ".jpg", ".jpeg", ".webp", ".gif")
THUMB_W = 280

AREAS = {
    "OpenAI_History": "OpenAI_History",
    "Visual_Assets": "Obsidian_Attachments/Visual_Assets",
    "OpenAI_Images": "Obsidian_Attachments/OpenAI_Images",
    "Videos_Keyframes": "Videos",
    "Undetermined": "Undetermined",
}


def build_reference_map():
    """lowercase image filename -> note path (relative to RESOURCE_LIB), for notes that embed it."""
    m = {}
    for f in glob.glob(f"{WORKSPACE}/**/*.md", recursive=True):
        if "/.git/" in f:
            continue
        try:
            t = open(f, encoding="utf-8", errors="ignore").read()
        except Exception:
            continue
        rel = os.path.relpath(f, RESOURCE_LIB) if f.startswith(RESOURCE_LIB) else f
        for mm in re.finditer(r'!\[\[([^\]|]+?\.(?:png|jpg|jpeg|webp|gif))', t, re.I):
            m.setdefault(mm.group(1).strip().lower(), rel)
        for mm in re.finditer(r'!\[[^\]]*\]\(([^)]+?\.(?:png|jpg|jpeg|webp|gif))\)', t, re.I):
            m.setdefault(os.path.basename(mm.group(1).strip()).lower(), rel)
    return m


def make_thumb(args):
    src, dst = args
    if os.path.exists(dst):
        return True
    try:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        im = Image.open(src)
        im = ImageOps.exif_transpose(im).convert("RGB")
        if im.width > THUMB_W:
            im = im.resize((THUMB_W, max(1, int(im.height * THUMB_W / im.width))))
        im.save(dst, "JPEG", quality=55)
        return True
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.expanduser("~/Desktop/Resource_Library_Review"))
    args = ap.parse_args()
    out = args.out
    thumbs_root = os.path.join(out, "image_thumbs")
    os.makedirs(thumbs_root, exist_ok=True)

    print("mapping notes -> images ...")
    ref = build_reference_map()

    items = []
    jobs = []
    for area, sub in AREAS.items():
        root = os.path.join(RESOURCE_LIB, sub)
        if not os.path.isdir(root):
            continue
        for r, _, files in os.walk(root):
            for fn in files:
                if not fn.lower().endswith(IMG_EXT):
                    continue
                src = os.path.join(r, fn)
                rel = os.path.relpath(src, RESOURCE_LIB)
                thumb_rel = os.path.join("image_thumbs", rel) + ".jpg"
                thumb_abs = os.path.join(out, thumb_rel)
                try:
                    size = os.path.getsize(src)
                except OSError:
                    continue
                note = ref.get(fn.lower())
                items.append({
                    "rel": rel, "area": area, "bytes": size,
                    "thumb": thumb_rel, "note": note,
                })
                jobs.append((src, thumb_abs))

    print(f"{len(items)} images across {len(AREAS)} areas — generating thumbnails ...")
    ok = 0
    with ProcessPoolExecutor() as ex:
        for i, res in enumerate(ex.map(make_thumb, jobs, chunksize=32)):
            ok += bool(res)
            if (i + 1) % 500 == 0:
                print(f"  {i + 1}/{len(jobs)}")
    print(f"thumbnails: {ok} ok, {len(jobs) - ok} failed")

    # drop items whose thumb failed
    items = [it for it in items if os.path.exists(os.path.join(out, it["thumb"]))]

    with open(os.path.join(out, "image_index.json"), "w") as f:
        json.dump(items, f)

    with open(os.path.join(out, "image_cull.html"), "w") as f:
        f.write(render(items))
    print(f"\nwrote {os.path.join(out, 'image_cull.html')}  ({len(items)} images)")
    total_gb = sum(it["bytes"] for it in items) / 1e9
    print(f"total on disk: {total_gb:.2f} GB")
    print(f"\nopen '{os.path.join(out, 'image_cull.html')}'")


def render(items):
    from collections import Counter
    by_area = Counter(it["area"] for it in items)
    gb_area = {a: sum(it["bytes"] for it in items if it["area"] == a) / 1e9 for a in by_area}
    data = json.dumps(items, ensure_ascii=False)

    area_chips = "".join(
        f'<button class="chip" data-area="{html.escape(a)}">{html.escape(a)} '
        f'<b>{by_area[a]} · {gb_area[a]:.1f}GB</b></button>'
        for a in AREAS if a in by_area)

    return f"""<!doctype html><html><head><meta charset="utf-8">
<title>Resource Library — Image Cull</title>
<style>
  :root {{ color-scheme: light dark; }}
  * {{ box-sizing: border-box; }}
  body {{ font: 13px/1.4 -apple-system, system-ui, sans-serif; margin: 0; background:#f4f4f5; color:#18181b; }}
  @media (prefers-color-scheme: dark) {{ body {{ background:#18181b; color:#e4e4e7; }} }}
  header {{ position: sticky; top: 0; z-index: 9; background: inherit; padding: 10px 14px; border-bottom: 1px solid #8884; }}
  h1 {{ font-size: 14px; margin: 0 0 6px; }}
  #stat {{ font-size: 13px; margin-bottom: 6px; }}
  #stat b {{ color: #dc2626; }}
  .row {{ display: flex; flex-wrap: wrap; gap: 5px; align-items: center; margin-bottom: 5px; }}
  .chip {{ font: inherit; font-size: 12px; padding: 3px 8px; border: 1px solid #8886; border-radius: 999px; background: #8881; cursor: pointer; }}
  .chip.on {{ background: #2563eb; color: #fff; border-color: #2563eb; }}
  .chip b {{ opacity: .65; font-weight: 600; }}
  .act {{ font: inherit; font-size: 12px; padding: 4px 10px; border-radius: 6px; cursor: pointer; border: 1px solid #8886; background: #8881; }}
  .act.del {{ background:#dc2626; color:#fff; border-color:#dc2626; }}
  .act.exp {{ background:#2563eb; color:#fff; border-color:#2563eb; }}
  input[type=search] {{ font: inherit; padding: 4px 8px; border: 1px solid #8886; border-radius: 6px; background: #8881; min-width: 180px; }}
  main {{ padding: 10px; display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 8px; }}
  .cell {{ position: relative; border: 2px solid transparent; border-radius: 6px; overflow: hidden; background: #8881; cursor: pointer; }}
  .cell img {{ width: 100%; display: block; aspect-ratio: 1 / 1; object-fit: cover; }}
  .cell .cap {{ font-size: 10px; padding: 2px 4px; opacity: .6; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  .cell .nb {{ position: absolute; top: 3px; left: 3px; font-size: 9px; background: #000a; color: #fff; padding: 1px 4px; border-radius: 3px; }}
  .cell.del {{ border-color: #dc2626; }}
  .cell.del::after {{ content: "✕ DELETE"; position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; background: #dc2626bb; color: #fff; font-weight: 700; font-size: 13px; }}
  #more {{ grid-column: 1/-1; padding: 12px; font: inherit; border: 1px dashed #8886; border-radius: 8px; background: #8881; cursor: pointer; }}
  dialog {{ max-width: 680px; width: 92%; border: 1px solid #8886; border-radius: 10px; }}
  textarea {{ width: 100%; height: 320px; font: 11px ui-monospace, monospace; }}
</style></head><body>
<header>
  <h1>Image Cull — {len(items)} images</h1>
  <div id="stat"></div>
  <div class="row"><span style="font-size:11px;opacity:.55;width:44px">Area</span>{area_chips}</div>
  <div class="row">
    <input type="search" id="q" placeholder="filename contains…">
    <button class="chip" id="onlyNoNote">only images with no note</button>
  </div>
  <div class="row">
    <button class="act del" id="delShown">Mark all shown for delete</button>
    <button class="act" id="keepShown">Unmark all shown</button>
    <button class="act exp" id="copy">Copy delete list</button>
    <button class="act exp" id="download">⬇ Download delete list</button>
    <span id="shown" style="font-size:12px;opacity:.6"></span>
  </div>
</header>
<main id="main"></main>
<dialog id="dlg"><div style="padding:14px">
  <p>These images + their notes will be moved to <code>~/Desktop/Delete/</code>. Paste back to Claude or use the downloaded file.</p>
  <textarea id="outbox" readonly></textarea>
  <div style="margin-top:8px"><button class="act" onclick="dlg.close()">Close</button></div>
</div></dialog>
<script>
const IMGS = {data};
const KEY = 'rl_image_cull_v1';
let del = {{}};
try {{ del = JSON.parse(localStorage.getItem(KEY) || '{{}}'); }} catch(e) {{}}
const save = () => {{ try {{ localStorage.setItem(KEY, JSON.stringify(del)); }} catch(e) {{}} }};

const areas = new Set();
let query = '', noNoteOnly = false;
const PAGE = 300;
let limit = PAGE;
const main = document.getElementById('main');
const esc = s => (s||'').replace(/[&<>"]/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]));

function visible() {{
  return IMGS.filter(it => {{
    if (areas.size && !areas.has(it.area)) return false;
    if (noNoteOnly && it.note) return false;
    if (query && !it.rel.toLowerCase().includes(query)) return false;
    return true;
  }});
}}

function fmtGB(b) {{ return (b/1e9).toFixed(2) + ' GB'; }}

function refreshStat() {{
  const keys = Object.keys(del);
  const bytes = IMGS.filter(it => del[it.rel]).reduce((s,it)=>s+it.bytes,0);
  const notes = IMGS.filter(it => del[it.rel] && it.note).length;
  document.getElementById('stat').innerHTML =
    IMGS.length + ' images · <b>' + keys.length + ' marked for delete</b> (' + fmtGB(bytes) + ', ' + notes + ' notes)';
}}

function render() {{
  const vis = visible();
  document.getElementById('shown').textContent = vis.length + ' shown';
  main.innerHTML = vis.slice(0, limit).map(it => `
    <div class="cell ${{del[it.rel] ? 'del' : ''}}" data-rel="${{esc(it.rel)}}">
      <img loading="lazy" src="${{esc(it.thumb)}}" alt="">
      <div class="nb">${{it.note ? 'note' : 'no note'}}</div>
      <div class="cap">${{esc(it.rel.split('/').pop())}}</div>
    </div>`).join('')
    + (vis.length > limit ? `<button id="more">Show ${{Math.min(PAGE, vis.length-limit)}} more (${{vis.length-limit}} hidden)</button>` : '');
  refreshStat();
}}

main.addEventListener('click', e => {{
  if (e.target.id === 'more') {{ limit += PAGE; render(); return; }}
  const cell = e.target.closest('.cell');
  if (!cell) return;
  const rel = cell.dataset.rel;
  if (del[rel]) delete del[rel]; else del[rel] = 1;
  save();
  cell.classList.toggle('del');
  refreshStat();
}});

document.querySelectorAll('.chip[data-area]').forEach(c => c.addEventListener('click', () => {{
  const a = c.dataset.area;
  if (areas.has(a)) {{ areas.delete(a); c.classList.remove('on'); }}
  else {{ areas.add(a); c.classList.add('on'); }}
  limit = PAGE; render();
}}));
document.getElementById('q').addEventListener('input', e => {{ query = e.target.value.toLowerCase().trim(); limit = PAGE; render(); }});
document.getElementById('onlyNoNote').addEventListener('click', e => {{
  noNoteOnly = !noNoteOnly; e.target.classList.toggle('on', noNoteOnly); limit = PAGE; render();
}});

function bulk(mark) {{
  const vis = visible();
  if (vis.length > 100 && !confirm(`${{mark ? 'Mark' : 'Unmark'}} ${{vis.length}} shown images?`)) return;
  vis.forEach(it => {{ if (mark) del[it.rel] = 1; else delete del[it.rel]; }});
  save(); render();
}}
document.getElementById('delShown').onclick = () => bulk(true);
document.getElementById('keepShown').onclick = () => bulk(false);

function listText() {{
  return IMGS.filter(it => del[it.rel])
    .map(it => 'DELETE\\t' + it.rel + (it.note ? '\\t' + it.note : ''))
    .join('\\n') || '(nothing marked)';
}}
document.getElementById('copy').onclick = () => {{
  const t = listText();
  document.getElementById('outbox').value = t;
  document.getElementById('dlg').showModal();
  try {{ navigator.clipboard.writeText(t); }} catch(e) {{}}
}};
document.getElementById('download').onclick = () => {{
  const blob = new Blob([listText()], {{ type: 'text/plain' }});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'rl_image_cull.txt';
  document.body.appendChild(a); a.click(); a.remove();
}};

render();
</script>
</body></html>"""


if __name__ == "__main__":
    main()
