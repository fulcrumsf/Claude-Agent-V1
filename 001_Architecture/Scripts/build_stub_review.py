"""
Build a visual review folder for the Resource Library stub notes that automation
couldn't enrich (triage buckets 1 + 2 that still lack an `enriched:` marker).

Creates ~/Desktop/Resource_Library_Review/ containing:
  - notes/   copies of every unenriched .md note (originals untouched)
  - images/  copies of the full-size screenshots for the image notes
  - review.html   one page: each note as a card with its image or link + text,
                  Keep / Junk buttons per card (saved in the browser), and a
                  "Copy decisions" button that hands back a plain list.

Nothing in the vault is moved or deleted. This only copies OUT for review.

Usage:
  python3 001_Architecture/Scripts/resource_library_stub_triage.py   # refresh first
  python3 001_Architecture/Scripts/build_stub_review.py
  python3 001_Architecture/Scripts/build_stub_review.py --out ~/Desktop/RL_Review
"""
import os
import re
import json
import html
import base64
import shutil
import argparse
from io import BytesIO

from PIL import Image

WORKSPACE = "/Users/tonymacbook2025/Documents/Agent-OS"
RESOURCE_LIB = os.path.join(WORKSPACE, "007_Resource_Library")
TRIAGE = os.path.join(RESOURCE_LIB, "_Stub_Triage.json")
THUMB_MAX_W = 900


def note_body(text):
    body = re.sub(r"^---.*?---", "", text, count=1, flags=re.S).strip()
    body = re.sub(r"!\[\[.*?\]\]", "", body).strip()
    return body[:1200]


def note_frontmatter_title(text, fallback):
    m = re.search(r'^title:\s*"?(.*?)"?\s*$', text, re.M)
    return m.group(1) if m else fallback


def thumb_data_uri(img_path):
    try:
        im = Image.open(img_path)
        im = im.convert("RGB")
        if im.width > THUMB_MAX_W:
            im = im.resize((THUMB_MAX_W, int(im.height * THUMB_MAX_W / im.width)))
        buf = BytesIO()
        im.save(buf, format="JPEG", quality=78)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.expanduser("~/Desktop/Resource_Library_Review"))
    args = ap.parse_args()

    triage = json.load(open(TRIAGE))
    img_items = triage["bucket1_revision"]
    url_items = triage["bucket2_url_enrich"]

    out = args.out
    notes_dir = os.path.join(out, "notes")
    images_dir = os.path.join(out, "images")
    os.makedirs(notes_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)

    cards = []

    for it in img_items:
        note_path = os.path.join(RESOURCE_LIB, it["note"])
        if not os.path.exists(note_path):
            continue
        text = open(note_path, encoding="utf-8", errors="ignore").read()
        shutil.copy2(note_path, os.path.join(notes_dir, os.path.basename(note_path)))
        img_src = it["image"]
        uri = None
        if os.path.exists(img_src):
            shutil.copy2(img_src, os.path.join(images_dir, os.path.basename(img_src)))
            uri = thumb_data_uri(img_src)
        cards.append({
            "kind": "image",
            "path": it["note"],
            "title": note_frontmatter_title(text, os.path.basename(it["note"])[:-3]),
            "body": note_body(text),
            "img": uri,
            "imgname": os.path.basename(img_src),
        })

    for it in url_items:
        note_path = os.path.join(RESOURCE_LIB, it["note"])
        if not os.path.exists(note_path):
            continue
        text = open(note_path, encoding="utf-8", errors="ignore").read()
        shutil.copy2(note_path, os.path.join(notes_dir, os.path.basename(note_path)))
        cards.append({
            "kind": "link",
            "path": it["note"],
            "title": note_frontmatter_title(text, os.path.basename(it["note"])[:-3]),
            "body": note_body(text),
            "url": it["url"],
        })

    html_path = os.path.join(out, "review.html")
    with open(html_path, "w") as f:
        f.write(render(cards))

    print(f"wrote {html_path}")
    print(f"  {sum(1 for c in cards if c['kind']=='image')} image notes, "
          f"{sum(1 for c in cards if c['kind']=='link')} link notes")
    print(f"  note copies:  {notes_dir}")
    print(f"  image copies: {images_dir}")
    print(f"\nOpen in a browser:  open '{html_path}'")


def render(cards):
    def esc(s):
        return html.escape(s or "")

    rows = []
    for i, c in enumerate(cards):
        if c["kind"] == "image":
            media = (f'<img loading="lazy" src="{c["img"]}" alt="">'
                     if c["img"] else '<div class="noimg">image unreadable</div>')
            media += f'<div class="fn">{esc(c["imgname"])}</div>'
        else:
            u = esc(c["url"])
            media = f'<div class="linkbox"><a href="{u}" target="_blank" rel="noopener">{u}</a></div>'
        rows.append(f"""
      <div class="card" data-path="{esc(c['path'])}" data-i="{i}">
        <div class="media">{media}</div>
        <div class="meta">
          <div class="ttl">{esc(c['title'])}</div>
          <div class="pth">{esc(c['path'])}</div>
          <pre class="body">{esc(c['body'])}</pre>
          <div class="btns">
            <button class="keep" data-v="keep">✔ Keep</button>
            <button class="junk" data-v="junk">✕ Junk</button>
            <button class="clear" data-v="">undo</button>
          </div>
        </div>
      </div>""")

    return f"""<!doctype html><html><head><meta charset="utf-8">
<title>Resource Library — Stub Review</title>
<style>
  :root {{ color-scheme: light dark; }}
  body {{ font: 14px/1.5 -apple-system, system-ui, sans-serif; margin: 0; background: #f4f4f5; color: #18181b; }}
  @media (prefers-color-scheme: dark) {{ body {{ background:#18181b; color:#e4e4e7; }} }}
  header {{ position: sticky; top: 0; background: inherit; padding: 14px 20px; border-bottom: 1px solid #8884; z-index: 5; }}
  h1 {{ font-size: 16px; margin: 0 0 6px; }}
  .stat {{ font-size: 13px; opacity: .8; }}
  .filters button, .exportbtn {{ font: inherit; padding: 5px 10px; margin-right: 6px; border: 1px solid #8886; border-radius: 6px; background: #8881; cursor: pointer; }}
  .exportbtn {{ background:#2563eb; color:#fff; border-color:#2563eb; }}
  main {{ padding: 16px; display: grid; grid-template-columns: repeat(auto-fill, minmax(420px, 1fr)); gap: 14px; }}
  .card {{ border: 2px solid #8883; border-radius: 10px; overflow: hidden; background: #fff2; display: flex; flex-direction: column; }}
  .card.keep {{ border-color: #16a34a; }}
  .card.junk {{ border-color: #dc2626; opacity: .55; }}
  .media {{ background: #0002; padding: 8px; text-align: center; }}
  .media img {{ max-width: 100%; max-height: 340px; border-radius: 4px; }}
  .noimg, .linkbox {{ padding: 24px; font-size: 13px; opacity: .7; }}
  .linkbox a {{ word-break: break-all; }}
  .fn {{ font-size: 11px; opacity: .6; margin-top: 4px; word-break: break-all; }}
  .meta {{ padding: 10px 12px; display: flex; flex-direction: column; gap: 6px; }}
  .ttl {{ font-weight: 600; }}
  .pth {{ font-size: 11px; opacity: .55; }}
  .body {{ white-space: pre-wrap; font: 12px/1.45 ui-monospace, monospace; background: #8881; padding: 8px; border-radius: 5px; margin: 0; max-height: 180px; overflow: auto; }}
  .btns {{ display: flex; gap: 6px; }}
  .btns button {{ font: inherit; padding: 5px 12px; border: 1px solid #8886; border-radius: 6px; background: #8881; cursor: pointer; }}
  .card.keep .keep {{ background: #16a34a; color: #fff; }}
  .card.junk .junk {{ background: #dc2626; color: #fff; }}
  dialog {{ max-width: 640px; width: 90%; border: 1px solid #8886; border-radius: 10px; padding: 16px; }}
  textarea {{ width: 100%; height: 260px; font: 12px ui-monospace, monospace; }}
</style></head><body>
<header>
  <h1>Resource Library — Stub Review</h1>
  <div class="stat" id="stat"></div>
  <div style="margin-top:8px">
    <span class="filters">
      <button data-f="all">All</button>
      <button data-f="undecided">Undecided</button>
      <button data-f="keep">Keep</button>
      <button data-f="junk">Junk</button>
      <button data-f="image">Images</button>
      <button data-f="link">Links</button>
    </span>
    <button class="exportbtn" id="export">Copy decisions</button>
  </div>
</header>
<main id="main">{''.join(rows)}</main>
<dialog id="dlg">
  <p>Copied to clipboard. Paste this back to Claude. Lines are <code>KEEP</code> / <code>JUNK</code> + the note path.</p>
  <textarea id="out" readonly></textarea>
  <div style="margin-top:8px"><button onclick="document.getElementById('dlg').close()">Close</button></div>
</dialog>
<script>
  const KEY = 'rl_stub_review_v1';
  let state = {{}};
  try {{ state = JSON.parse(localStorage.getItem(KEY) || '{{}}'); }} catch (e) {{}}
  const cards = [...document.querySelectorAll('.card')];

  function save() {{ try {{ localStorage.setItem(KEY, JSON.stringify(state)); }} catch (e) {{}} }}
  function apply(card) {{
    const p = card.dataset.path, v = state[p] || '';
    card.classList.toggle('keep', v === 'keep');
    card.classList.toggle('junk', v === 'junk');
  }}
  function refreshStat() {{
    const k = Object.values(state).filter(v => v === 'keep').length;
    const j = Object.values(state).filter(v => v === 'junk').length;
    document.getElementById('stat').textContent =
      cards.length + ' notes  ·  ' + k + ' keep  ·  ' + j + ' junk  ·  ' + (cards.length - k - j) + ' undecided';
  }}
  cards.forEach(card => {{
    apply(card);
    card.querySelectorAll('.btns button').forEach(b => b.addEventListener('click', () => {{
      const v = b.dataset.v;
      if (v) state[card.dataset.path] = v; else delete state[card.dataset.path];
      save(); apply(card); refreshStat();
    }}));
  }});
  refreshStat();

  document.querySelectorAll('.filters button').forEach(b => b.addEventListener('click', () => {{
    const f = b.dataset.f;
    cards.forEach(card => {{
      const v = state[card.dataset.path] || 'undecided';
      const kind = card.querySelector('.linkbox') ? 'link' : 'image';
      let show = true;
      if (f === 'undecided') show = v === 'undecided';
      else if (f === 'keep') show = v === 'keep';
      else if (f === 'junk') show = v === 'junk';
      else if (f === 'image') show = kind === 'image';
      else if (f === 'link') show = kind === 'link';
      card.style.display = show ? '' : 'none';
    }});
  }}));

  document.getElementById('export').addEventListener('click', () => {{
    const lines = cards.map(card => {{
      const v = state[card.dataset.path];
      return v ? (v.toUpperCase() + '\\t' + card.dataset.path) : null;
    }}).filter(Boolean);
    const txt = lines.join('\\n') || '(no decisions yet)';
    const ta = document.getElementById('out');
    ta.value = txt;
    document.getElementById('dlg').showModal();
    try {{ navigator.clipboard.writeText(txt); }} catch (e) {{}}
    ta.select();
  }});
</script>
</body></html>"""


if __name__ == "__main__":
    main()
