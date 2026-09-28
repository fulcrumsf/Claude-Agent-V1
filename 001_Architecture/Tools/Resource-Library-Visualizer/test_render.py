from conftest import load


render = load("render")


def test_embed_image_becomes_img_tag():
    out = render.render_body("![[Shot-1.png]]", "Tools")
    assert '<img src="/img?path=Tools/Shot-1.png"' in out


def test_youtube_url_becomes_iframe():
    out = render.render_body("https://youtu.be/abcdefghijk", "Tutorials")
    assert "<iframe" in out and "abcdefghijk" in out


def test_wikilink_alias_rendered():
    out = render.render_body("see [[Some Note|that note]] ok", "Tools")
    assert "that note" in out and "[[" not in out


def test_callout_block():
    out = render.render_body("> [!info] Heads up\n> body text", "Tools")
    assert "callout" in out and "Heads up" in out


def test_frontmatter_html_links_url():
    out = render.frontmatter_html({"title": "A", "url": "https://x.com"})
    assert '<a href="https://x.com"' in out
