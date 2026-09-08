"""
Bulk review page for the Resource Library notes that were auto-excluded from the
knowledge graph (triage bucket 3: garbled-title / missing-image / no-signal).

These are ~1,000 tiny notes. The page is built for fast bulk decisions:
  - grouped + filterable by reason and by folder
  - "Junk all shown" / "Keep all shown" / "Clear all shown" act on the current filter
  - per-card override, decisions saved in the browser
  - full note text is embedded (avg 300 bytes each), no images (none resolve)
  - "Copy decisions" hands back a KEEP/JUNK + path list

Nothing in the vault is touched — this only reads.

Reads:  007_Resource_Library/_Stub_Triage.json  (run resource_library_stub_triage.py first)
Writes: <out>/review_excluded.html   (default ~/Desktop/Resource_Library_Review/)

Usage:
  python3 001_Architecture/Scripts/note_review_excluded.py
"""
import os
import re
import json
import html
import argparse
from collections import Counter

WORKSPACE = "/Users/tonymacbook2025/Documents/Agent-OS"
RESOURCE_LIB = os.path.join(WORKSPACE, "007_Resource_Library")
TRIAGE = os.path.join(RESOURCE_LIB, "_Stub_Triage.json")

REASON_LABEL = {
    "garbled-title": "Garbled title (OCR junk — TikTok nav bars, phone home screens)",
    "missing-image": "Missing image (note points to an image file that's gone)",
    "no-signal": "No signal (under 40 words, no image, no link)",
}


def note_title(text, fallback):
    m = re.search(r'^title:\s*"?(.*?)"?\s*$', text, re.M)
    return m.group(1).strip() if m else fallback


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.expanduser("~/Desktop/Resource_Library_Review"))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    items = json.load(open(TRIAGE))["bucket3_dead"]
    cards = []
    for it in items:
        p = os.path.join(RESOURCE_LIB, it["note"])
        if not os.path.exists(p):
            continue
        text = open(p, encoding="utf-8", errors="ignore").read()
        cards.append({
            "path": it["note"],
            "folder": it["note"].split("/")[0],
            "reason": it["reason"],
            "title": note_title(text, os.path.basename(it["note"])[:-3]),
            "text": text.strip()[:1400],
        })

    out_html = os.path.join(args.out, "review_excluded.html")
    with open(out_html, "w") as f:
        f.write(render(cards))
    print(f"wrote {out_html}  ({len(cards)} notes)")
    print("reasons:", dict(Counter(c["reason"] for c in cards)))
    print("folders:", dict(Counter(c["folder"] for c in cards)))
    print(f"\nopen '{out_html}'")


def render(cards):
    reasons = Counter(c["reason"] for c in cards)
    folders = Counter(c["folder"] for c in cards)
    data = json.dumps(cards, ensure_ascii=False)

    reason_chips = "".join(
        f'<button class="chip" data-dim="reason" data-v="{html.escape(r)}">{html.escape(r)} '
        f'<b>{reasons[r]}</b></button>'
        for r in sorted(reasons))
    folder_chips = "".join(
        f'<button class="chip" data-dim="folder" data-v="{html.escape(fo)}">{html.escape(fo)} '
        f'<b>{folders[fo]}</b></button>'
        for fo, _ in folders.most_common())

    return f"""<!doctype html><html><head><meta charset="utf-8">
<title>Resource Library — Excluded Notes Review</title>
<style>
  :root {{ color-scheme: light dark; }}
  * {{ box-sizing: border-box; }}
  body {{ font: 13px/1.5 -apple-system, system-ui, sans-serif; margin: 0; background:#f4f4f5; color:#18181b; }}
  @media (prefers-color-scheme: dark) {{ body {{ background:#18181b; color:#e4e4e7; }} }}
  header {{ position: sticky; top: 0; z-index: 9; background: inherit; padding: 12px 16px; border-bottom: 1px solid #8884; }}
  h1 {{ font-size: 15px; margin: 0 0 8px; }}
  #stat {{ font-size: 13px; opacity: .85; margin-bottom: 8px; }}
  .row {{ display: flex; flex-wrap: wrap; gap: 6px; align-items: center; margin-bottom: 6px; }}
  .row > .lbl {{ font-size: 11px; text-transform: uppercase; opacity: .55; width: 54px; }}
  .chip {{ font: inherit; font-size: 12px; padding: 4px 9px; border: 1px solid #8886; border-radius: 999px; background: #8881; cursor: pointer; }}
  .chip.on {{ background: #2563eb; color: #fff; border-color: #2563eb; }}
  .chip b {{ opacity: .6; font-weight: 600; }}
  input[type=search] {{ font: inherit; padding: 5px 9px; border: 1px solid #8886; border-radius: 6px; background: #8881; min-width: 200px; }}
  .act {{ font: inherit; font-size: 12px; padding: 5px 11px; border-radius: 6px; cursor: pointer; border: 1px solid #8886; background: #8881; }}
  .act.junk {{ background:#dc2626; color:#fff; border-color:#dc2626; }}
  .act.keep {{ background:#16a34a; color:#fff; border-color:#16a34a; }}
  .act.exp  {{ background:#2563eb; color:#fff; border-color:#2563eb; }}
  main {{ padding: 12px 16px; }}
  .card {{ border: 1px solid #8883; border-left: 4px solid #8886; border-radius: 7px; padding: 8px 10px; margin-bottom: 7px; background: #fff2; }}
  .card.keep {{ border-left-color: #16a34a; }}
  .card.junk {{ border-left-color: #dc2626; opacity: .5; }}
  .card .top {{ display: flex; gap: 8px; align-items: baseline; flex-wrap: wrap; }}
  .card .ttl {{ font-weight: 600; }}
  .card .pth {{ font-size: 11px; opacity: .5; }}
  .card .rsn {{ font-size: 10px; text-transform: uppercase; letter-spacing: .04em; opacity: .55; margin-left: auto; }}
  .card pre {{ white-space: pre-wrap; font: 11px/1.4 ui-monospace, monospace; background: #8881; padding: 6px 8px; border-radius: 4px; margin: 6px 0 4px; max-height: 3.6em; overflow: hidden; cursor: pointer; }}
  .card pre.open {{ max-height: none; }}
  .card .btns button {{ font: inherit; font-size: 11px; padding: 3px 9px; margin-right: 5px; border: 1px solid #8886; border-radius: 5px; background: #8881; cursor: pointer; }}
  .card.keep .b-keep {{ background:#16a34a; color:#fff; }}
  .card.junk .b-junk {{ background:#dc2626; color:#fff; }}
  #more {{ display:block; width:100%; padding:10px; margin-top:8px; font:inherit; border:1px dashed #8886; border-radius:8px; background:#8881; cursor:pointer; }}
  dialog {{ max-width: 640px; width: 92%; border: 1px solid #8886; border-radius: 10px; }}
  textarea {{ width: 100%; height: 300px; font: 11px ui-monospace, monospace; }}
</style></head><body>
<header>
  <h1>Resource Library — Excluded Notes ({len(cards)})</h1>
  <div id="stat"></div>
  <div class="row"><span class="lbl">Reason</span>{reason_chips}</div>
  <div class="row"><span class="lbl">Folder</span>{folder_chips}</div>
  <div class="row">
    <span class="lbl">Show</span>
    <button class="chip" data-dim="decision" data-v="undecided">undecided</button>
    <button class="chip" data-dim="decision" data-v="junk">junk</button>
    <button class="chip" data-dim="decision" data-v="keep">keep</button>
    <input type="search" id="q" placeholder="search title / path / text">
  </div>
  <div class="row">
    <span class="lbl">Bulk</span>
    <button class="act junk" id="bulkJunk">Junk all shown</button>
    <button class="act keep" id="bulkKeep">Keep all shown</button>
    <button class="act" id="bulkClear">Clear all shown</button>
    <button class="act exp" id="export">Copy decisions</button>
    <button class="act exp" id="download">⬇ Download decisions.txt</button>
    <span id="shown" style="font-size:12px;opacity:.6"></span>
  </div>
</header>
<main id="main"></main>
<dialog id="dlg">
  <div style="padding:14px">
    <p>Copied to clipboard. Paste back to Claude. <code>JUNK</code> / <code>KEEP</code> + note path, one per line.</p>
    <textarea id="outbox" readonly></textarea>
    <div style="margin-top:8px"><button class="act" onclick="dlg.close()">Close</button></div>
  </div>
</dialog>
<script>
const CARDS = {data};
const KEY = 'rl_excluded_review_v1';
let state = {{}};
try {{ state = JSON.parse(localStorage.getItem(KEY) || '{{}}'); }} catch(e) {{}}
const save = () => {{ try {{ localStorage.setItem(KEY, JSON.stringify(state)); }} catch(e) {{}} }};

const filt = {{ reason: new Set(), folder: new Set(), decision: new Set() }};
let query = '';
const PAGE = 150;
let shownLimit = PAGE;

const main = document.getElementById('main');
const esc = s => (s||'').replace(/[&<>]/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;'}}[c]));

function decideOf(p) {{ return state[p] || 'undecided'; }}

function matches(c) {{
  if (filt.reason.size && !filt.reason.has(c.reason)) return false;
  if (filt.folder.size && !filt.folder.has(c.folder)) return false;
  if (filt.decision.size && !filt.decision.has(decideOf(c.path))) return false;
  if (query) {{
    const h = (c.title + ' ' + c.path + ' ' + c.text).toLowerCase();
    if (!h.includes(query)) return false;
  }}
  return true;
}}

function visibleCards() {{ return CARDS.filter(matches); }}

function render() {{
  const vis = visibleCards();
  document.getElementById('shown').textContent = vis.length + ' shown';
  const slice = vis.slice(0, shownLimit);
  main.innerHTML = slice.map(c => {{
    const d = decideOf(c.path);
    return `<div class="card ${{d}}" data-p="${{esc(c.path)}}">
      <div class="top">
        <span class="ttl">${{esc(c.title)}}</span>
        <span class="pth">${{esc(c.path)}}</span>
        <span class="rsn">${{esc(c.reason)}}</span>
      </div>
      <pre>${{esc(c.text)}}</pre>
      <div class="btns">
        <button class="b-keep" data-v="keep">✔ Keep</button>
        <button class="b-junk" data-v="junk">✕ Junk</button>
        <button class="b-clr" data-v="">undo</button>
      </div>
    </div>`;
  }}).join('') + (vis.length > shownLimit
      ? `<button id="more">Show ${{Math.min(PAGE, vis.length - shownLimit)}} more (${{vis.length - shownLimit}} hidden)</button>` : '');
  refreshStat();
}}

function refreshStat() {{
  const vals = Object.values(state);
  const j = vals.filter(v => v === 'junk').length;
  const k = vals.filter(v => v === 'keep').length;
  document.getElementById('stat').textContent =
    `${{CARDS.length}} notes  ·  ${{j}} junk  ·  ${{k}} keep  ·  ${{CARDS.length - j - k}} undecided`;
}}

main.addEventListener('click', e => {{
  const card = e.target.closest('.card');
  if (e.target.id === 'more') {{ shownLimit += PAGE; render(); return; }}
  if (e.target.tagName === 'PRE') {{ e.target.classList.toggle('open'); return; }}
  if (card && e.target.dataset.v !== undefined) {{
    const v = e.target.dataset.v, p = card.dataset.p;
    if (v) state[p] = v; else delete state[p];
    save();
    card.className = 'card ' + decideOf(p);
    refreshStat();
  }}
}});

document.querySelectorAll('.chip[data-dim]').forEach(ch => ch.addEventListener('click', () => {{
  const dim = ch.dataset.dim, v = ch.dataset.v;
  if (filt[dim].has(v)) {{ filt[dim].delete(v); ch.classList.remove('on'); }}
  else {{ filt[dim].add(v); ch.classList.add('on'); }}
  shownLimit = PAGE; render();
}}));
document.getElementById('q').addEventListener('input', e => {{
  query = e.target.value.toLowerCase().trim(); shownLimit = PAGE; render();
}});

function bulk(v) {{
  const vis = visibleCards();
  if (vis.length > 40 && !confirm(`${{v || 'clear'}} ${{vis.length}} shown notes?`)) return;
  vis.forEach(c => {{ if (v) state[c.path] = v; else delete state[c.path]; }});
  save(); render();
}}
document.getElementById('bulkJunk').onclick = () => bulk('junk');
document.getElementById('bulkKeep').onclick = () => bulk('keep');
document.getElementById('bulkClear').onclick = () => bulk('');

function decisionsText() {{
  const lines = CARDS.map(c => {{
    const v = state[c.path];
    return v ? `${{v.toUpperCase()}}\\t${{c.path}}` : null;
  }}).filter(Boolean);
  return lines.join('\\n') || '(no decisions yet)';
}}
document.getElementById('export').onclick = () => {{
  const txt = decisionsText();
  document.getElementById('outbox').value = txt;
  document.getElementById('dlg').showModal();
  try {{ navigator.clipboard.writeText(txt); }} catch(e) {{}}
}};
document.getElementById('download').onclick = () => {{
  const blob = new Blob([decisionsText()], {{ type: 'text/plain' }});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'rl_excluded_decisions.txt';
  document.body.appendChild(a); a.click(); a.remove();
}};

render();
</script>
</body></html>"""


if __name__ == "__main__":
    main()
