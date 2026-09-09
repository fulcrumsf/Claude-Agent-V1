"""
Review page for Resource Library notes whose embedded image is gone.

These notes still have a text description (that's why they survived earlier
purges) and still work in the graph — they just render a broken-image
placeholder in Obsidian. There's no image to show; the page shows the note's
text + the filename it wanted, with Keep / Junk / Strip-embed buttons.

  Keep        - leave the note as-is
  Strip embed - keep the note but remove the dead ![[...]] line (clean text bookmark)
  Junk        - the note isn't worth keeping without its image

Reads:  a JSON array of note paths (relative to 007_Resource_Library)
Writes: <out>/broken_image_review.html + a decisions download

Usage:
  python3 build_broken_image_review.py <notes.json>
"""
import os
import re
import sys
import json
import html
import argparse
from collections import Counter

RL = "/Users/tonymacbook2025/Documents/Agent-OS/007_Resource_Library"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("notes_json")
    ap.add_argument("--out", default=os.path.expanduser("~/Desktop/Resource_Library_Review"))
    ap.add_argument("--title", default="Notes with a missing image")
    ap.add_argument("--outfile", default="broken_image_review.html")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    WS = os.path.dirname(RL)
    paths = json.load(open(args.notes_json))
    cards = []
    for p in paths:
        if os.path.isabs(p):
            full = p
        elif p.startswith("007_Resource_Library/"):
            full = os.path.join(WS, p)
        else:
            full = os.path.join(RL, p)
        if not os.path.exists(full):
            continue
        rel = os.path.relpath(full, RL)
        t = open(full, encoding="utf-8", errors="ignore").read()
        m = re.search(r'!\[\[([^\]|]+?\.(?:png|jpg|jpeg|webp|gif))\]\]', t, re.I)
        title_m = re.search(r'^title:\s*"?(.*?)"?\s*$', t, re.M)
        cards.append({
            "path": rel,
            "folder": rel.split("/")[0],
            "title": title_m.group(1).strip() if title_m else os.path.basename(rel)[:-3],
            "wanted": m.group(1) if m else "",
            "text": t.strip()[:1400],
        })

    out_html = os.path.join(args.out, args.outfile)
    open(out_html, "w").write(render(cards, args.title))
    print(f"wrote {out_html}  ({len(cards)} notes)")
    print("by folder:", dict(Counter(c["folder"] for c in cards)))
    print(f"\nopen '{out_html}'")


def render(cards, page_title="Notes"):
    folders = Counter(c["folder"] for c in cards)
    data = json.dumps(cards, ensure_ascii=False)
    folder_chips = "".join(
        f'<button class="chip" data-f="{html.escape(k)}">{html.escape(k)} <b>{v}</b></button>'
        for k, v in folders.most_common())

    return f"""<!doctype html><html><head><meta charset="utf-8">
<title>Broken-Image Notes Review</title>
<style>
  :root {{ color-scheme: light dark; }}
  * {{ box-sizing: border-box; }}
  body {{ font: 13px/1.5 -apple-system, system-ui, sans-serif; margin: 0; background:#f4f4f5; color:#18181b; }}
  @media (prefers-color-scheme: dark) {{ body {{ background:#18181b; color:#e4e4e7; }} }}
  header {{ position: sticky; top: 0; z-index: 9; background: inherit; padding: 12px 16px; border-bottom: 1px solid #8884; }}
  h1 {{ font-size: 15px; margin: 0 0 6px; }}
  #stat {{ font-size: 13px; margin-bottom: 6px; }}
  .row {{ display: flex; flex-wrap: wrap; gap: 6px; align-items: center; margin-bottom: 6px; }}
  .chip {{ font: inherit; font-size: 12px; padding: 3px 9px; border: 1px solid #8886; border-radius: 999px; background: #8881; cursor: pointer; }}
  .chip.on {{ background: #2563eb; color: #fff; border-color: #2563eb; }}
  .chip b {{ opacity: .6; }}
  .act {{ font: inherit; font-size: 12px; padding: 5px 11px; border-radius: 6px; cursor: pointer; border: 1px solid #8886; background: #8881; }}
  .act.junk {{ background:#dc2626;color:#fff;border-color:#dc2626; }}
  .act.strip {{ background:#d97706;color:#fff;border-color:#d97706; }}
  .act.exp {{ background:#2563eb;color:#fff;border-color:#2563eb; }}
  input[type=search] {{ font: inherit; padding: 4px 8px; border: 1px solid #8886; border-radius: 6px; background: #8881; min-width: 200px; }}
  main {{ padding: 12px 16px; }}
  .card {{ border: 1px solid #8883; border-left: 4px solid #8886; border-radius: 7px; padding: 8px 10px; margin-bottom: 7px; background: #fff2; }}
  .card.keep {{ border-left-color:#16a34a; }}
  .card.strip {{ border-left-color:#d97706; }}
  .card.junk {{ border-left-color:#dc2626; opacity:.5; }}
  .card .top {{ display:flex; gap:8px; align-items:baseline; flex-wrap:wrap; }}
  .card .ttl {{ font-weight:600; }}
  .card .pth {{ font-size:11px; opacity:.5; }}
  .card .want {{ font-size:10px; opacity:.55; margin-left:auto; }}
  .card pre {{ white-space:pre-wrap; font:11px/1.4 ui-monospace,monospace; background:#8881; padding:6px 8px; border-radius:4px; margin:6px 0 4px; max-height:none; }}
  .card .btns button {{ font:inherit; font-size:11px; padding:3px 9px; margin-right:5px; border:1px solid #8886; border-radius:5px; background:#8881; cursor:pointer; }}
  .card.keep .b-keep {{ background:#16a34a;color:#fff; }}
  .card.strip .b-strip {{ background:#d97706;color:#fff; }}
  .card.junk .b-junk {{ background:#dc2626;color:#fff; }}
  #more {{ display:block; width:100%; padding:10px; margin-top:8px; font:inherit; border:1px dashed #8886; border-radius:8px; background:#8881; cursor:pointer; }}
  dialog {{ max-width:680px; width:92%; border:1px solid #8886; border-radius:10px; }}
  textarea {{ width:100%; height:300px; font:11px ui-monospace,monospace; }}
</style></head><body>
<header>
  <h1>{html.escape(page_title)} ({len(cards)})</h1>
  <div id="stat"></div>
  <div class="row"><span style="font-size:11px;opacity:.55;width:44px">Folder</span>{folder_chips}</div>
  <div class="row">
    <input type="search" id="q" placeholder="search title / path / text">
    <button class="chip" data-d="undecided">undecided</button>
    <button class="chip" data-d="keep">keep</button>
    <button class="chip" data-d="strip">strip</button>
    <button class="chip" data-d="junk">junk</button>
  </div>
  <div class="row">
    <button class="act junk" id="bJunk">Junk all shown</button>
    <button class="act strip" id="bStrip">Strip all shown</button>
    <button class="act" id="bKeep">Keep all shown</button>
    <button class="act" id="bClear">Clear all shown</button>
    <button class="act exp" id="copy">Copy decisions</button>
    <button class="act exp" id="dl">⬇ Download</button>
    <span id="shown" style="font-size:12px;opacity:.6"></span>
  </div>
</header>
<main id="main"></main>
<dialog id="dlg"><div style="padding:14px">
  <p>Paste back to Claude, or use the downloaded file. Columns: <code>KEEP</code>/<code>STRIP</code>/<code>JUNK</code> + note path.</p>
  <textarea id="outbox" readonly></textarea>
  <div style="margin-top:8px"><button class="act" onclick="dlg.close()">Close</button></div>
</div></dialog>
<script>
const CARDS = {data};
const KEY = 'rl_broken_img_review_v1';
let state = {{}};
try {{ state = JSON.parse(localStorage.getItem(KEY) || '{{}}'); }} catch(e) {{}}
const save = () => {{ try {{ localStorage.setItem(KEY, JSON.stringify(state)); }} catch(e) {{}} }};
const fdim = new Set(), ddim = new Set();
let query = '';
const PAGE = 200; let limit = PAGE;
const main = document.getElementById('main');
const esc = s => (s||'').replace(/[&<>]/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;'}}[c]));
const dOf = p => state[p] || 'undecided';

function vis() {{
  return CARDS.filter(c => {{
    if (fdim.size && !fdim.has(c.folder)) return false;
    if (ddim.size && !ddim.has(dOf(c.path))) return false;
    if (query) {{
      const h = (c.title + ' ' + c.path + ' ' + c.text).toLowerCase();
      if (!h.includes(query)) return false;
    }}
    return true;
  }});
}}
function stat() {{
  const v = Object.values(state);
  document.getElementById('stat').textContent =
    CARDS.length + ' notes · ' + v.filter(x=>x==='keep').length + ' keep · '
    + v.filter(x=>x==='strip').length + ' strip · ' + v.filter(x=>x==='junk').length + ' junk · '
    + (CARDS.length - v.length) + ' undecided';
}}
function render() {{
  const list = vis();
  document.getElementById('shown').textContent = list.length + ' shown';
  main.innerHTML = list.slice(0, limit).map(c => {{
    const d = dOf(c.path);
    return `<div class="card ${{d}}" data-p="${{esc(c.path)}}">
      <div class="top"><span class="ttl">${{esc(c.title)}}</span>
        <span class="pth">${{esc(c.path)}}</span>
        <span class="want">${{c.wanted ? "missing: " + esc(c.wanted) : ""}}</span></div>
      <pre>${{esc(c.text)}}</pre>
      <div class="btns">
        <button class="b-keep" data-v="keep">✔ Keep</button>
        <button class="b-strip" data-v="strip">⌫ Strip embed</button>
        <button class="b-junk" data-v="junk">✕ Junk</button>
        <button data-v="">undo</button>
      </div></div>`;
  }}).join('') + (list.length > limit
    ? `<button id="more">Show ${{Math.min(PAGE, list.length-limit)}} more (${{list.length-limit}} hidden)</button>` : '');
  stat();
}}
main.addEventListener('click', e => {{
  if (e.target.id === 'more') {{ limit += PAGE; render(); return; }}
  if (e.target.tagName === 'PRE') {{ e.target.classList.toggle('open'); return; }}
  const card = e.target.closest('.card');
  if (card && e.target.dataset.v !== undefined) {{
    const v = e.target.dataset.v, p = card.dataset.p;
    if (v) state[p] = v; else delete state[p];
    save(); card.className = 'card ' + dOf(p); stat();
  }}
}});
document.querySelectorAll('.chip[data-f]').forEach(c => c.onclick = () => {{
  const f = c.dataset.f;
  fdim.has(f) ? (fdim.delete(f), c.classList.remove('on')) : (fdim.add(f), c.classList.add('on'));
  limit = PAGE; render();
}});
document.querySelectorAll('.chip[data-d]').forEach(c => c.onclick = () => {{
  const d = c.dataset.d;
  ddim.has(d) ? (ddim.delete(d), c.classList.remove('on')) : (ddim.add(d), c.classList.add('on'));
  limit = PAGE; render();
}});
document.getElementById('q').oninput = e => {{ query = e.target.value.toLowerCase().trim(); limit = PAGE; render(); }};
function bulk(v) {{
  const list = vis();
  if (list.length > 50 && !confirm(`${{v||'clear'}} ${{list.length}} shown?`)) return;
  list.forEach(c => {{ if (v) state[c.path] = v; else delete state[c.path]; }});
  save(); render();
}}
document.getElementById('bJunk').onclick = () => bulk('junk');
document.getElementById('bStrip').onclick = () => bulk('strip');
document.getElementById('bKeep').onclick = () => bulk('keep');
document.getElementById('bClear').onclick = () => bulk('');
function txt() {{
  return CARDS.map(c => state[c.path] ? state[c.path].toUpperCase() + '\\t' + c.path : null)
    .filter(Boolean).join('\\n') || '(nothing decided)';
}}
document.getElementById('copy').onclick = () => {{
  document.getElementById('outbox').value = txt();
  document.getElementById('dlg').showModal();
  try {{ navigator.clipboard.writeText(txt()); }} catch(e) {{}}
}};
document.getElementById('dl').onclick = () => {{
  const b = new Blob([txt()], {{type:'text/plain'}});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(b); a.download = 'rl_broken_image_decisions.txt';
  document.body.appendChild(a); a.click(); a.remove();
}};
render();
</script>
</body></html>"""


if __name__ == "__main__":
    main()
