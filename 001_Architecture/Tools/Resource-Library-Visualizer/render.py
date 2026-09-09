import re
import html
from markdown_it import MarkdownIt

_md = MarkdownIt("commonmark", {"html": False, "linkify": True, "breaks": True})

YT = re.compile(r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([A-Za-z0-9_-]{11})")


def _iframe(vid):
    return (f'<iframe class="yt" src="https://www.youtube.com/embed/{vid}" '
            f'frameborder="0" allowfullscreen></iframe>')


def render_body(body, note_rel_dir):
    body = body or ""
    blocks = []

    def stash(html_str, block=True):
        token = f"@@RLV{len(blocks)}@@"
        blocks.append(html_str)
        return ("\n\n" + token + "\n\n") if block else token

    # collect unique youtube ids up front (order preserved)
    yt_ids = list(dict.fromkeys(YT.findall(body)))

    # --- image embeds:  ![[name.png]]  /  ![[...youtube...]] ---
    def img_sub(m):
        name = m.group(1).strip().split("|")[0]
        y = YT.search(name)
        if y:
            return stash(_iframe(y.group(1)))
        return stash(f'<img src="/img?path={html.escape(note_rel_dir)}/'
                     f'{html.escape(name)}" loading="lazy">')
    body = re.sub(r"!\[\[([^\]]+?)\]\]", img_sub, body)

    # --- wikilinks (inline) ---
    def wl(m):
        inner = m.group(1)
        alias = inner.split("|", 1)[1] if "|" in inner else inner
        return stash(f'<span class="wikilink">{html.escape(alias)}</span>', block=False)
    body = re.sub(r"\[\[([^\]]+?)\]\]", wl, body)

    # --- callouts:  > [!type] Title / > body ... ---
    lines = body.split("\n")
    out, i = [], 0
    while i < len(lines):
        m = re.match(r">\s*\[!(\w+)\]\s*(.*)", lines[i])
        if not m:
            out.append(lines[i])
            i += 1
            continue
        typ, title = m.group(1).lower(), m.group(2).strip()
        i += 1
        inner = []
        while i < len(lines) and lines[i].lstrip().startswith(">"):
            inner.append(lines[i].lstrip().lstrip(">").strip())
            i += 1
        inner_html = _md.render("\n".join(inner)) if any(inner) else ""
        out.append(stash(f'<div class="callout callout-{typ}">'
                         f'<b>{html.escape(title)}</b>{inner_html}</div>'))
    body = "\n".join(out)

    rendered = _md.render(body)
    for idx, blk in enumerate(blocks):
        rendered = rendered.replace(f"@@RLV{idx}@@", blk)

    # --- append playable embeds for every unique youtube link in the note ---
    already = "".join(blocks)
    extra = [vid for vid in yt_ids if _iframe(vid) not in already]
    if extra:
        rendered += ('<h3 style="margin-top:18px">Videos</h3>'
                     + "".join(_iframe(v) for v in extra))
    return rendered


def frontmatter_html(fm):
    rows = []
    for k, v in (fm or {}).items():
        if k == "url" and isinstance(v, str) and v.startswith("http"):
            val = f'<a href="{html.escape(v)}" target="_blank">{html.escape(v)}</a>'
        elif isinstance(v, list):
            val = ", ".join(html.escape(str(x)) for x in v)
        else:
            val = html.escape(str(v))
        rows.append(f"<dt>{html.escape(str(k))}</dt><dd>{val}</dd>")
    return "<dl class='fm'>" + "".join(rows) + "</dl>"
