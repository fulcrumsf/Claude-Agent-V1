"""Pipeline steps, in config/pipeline.json order. Built: generate_art (checks the approved art), upscale and
resize (stage 3, app/prints.py). Still stubs (production stage, not built): mockups, package, listing_text,
etsy_draft."""
import shutil

from .base import NotConfigured


def generate_art(ctx):
    # Art is made and approved in stage 2 (app/art.py); this step only checks it is there.
    from .. import prints
    return prints.check_art(ctx)


def upscale(ctx):
    # Upscayl CLI (upscayl-ncnn), model from settings `upscale_model` (remacri-4x, chosen 2026-11-05).
    from .. import prints
    return prints.upscale(ctx)


def resize(ctx):
    # 5 print JPGs at 300 DPI into Designs/<NNNNN>-<Name>/01-Printables (smart crop, never stretched).
    from .. import prints
    return prints.resize(ctx)


def mockups(ctx):
    # Slots 1, 2, 7 from the PSDs via PhotoCraft (app/mockups.py) plus the fixed images 3-6 and 20. Since 2026-11-08
    # this runs right after resize (prints_make_listing_images) and never makes room images: rooms 8-19 are made one
    # card at a time in the Production tab (app/production.py + app/scene_templates.py). Still to build: the video(s).
    import functools
    from .. import mockups, prints
    con, lid, lst, idea, img = prints._ctx_listing(ctx)
    settings = ctx.get("settings") or {}
    folder = prints.design_dir(settings, lst["folder_seq"], lst["title"])
    design = {"title": lst["title"], "description": f"{idea['title']}. {idea['description'] or ''}"}
    rec = (ctx.get("mockup_build") or functools.partial(mockups.build, rooms=False))(folder, settings, design=design)
    with prints.LOCK:
        r = prints._record(con, lid)
        r["mockups"] = rec
        ap = r.get("mockup_approvals") or {}                  # a file made again goes back to waiting
        for f in rec["files"]:
            ap.pop(f["file"], None)
        r["mockup_approvals"] = ap
        prints._save_record(con, lid, r)
    msg = f"{len(rec['files'])} listing images in {folder.name}/03-Etsy Images (slots 1, 2, 7 made; 3-6 and 20 copied); {rec['pending']}."
    if rec["notes"]:
        msg += " " + "; ".join(rec["notes"]) + "."
    return msg


def package(ctx):
    # Sequential folder per listing, share link into templated PDF (Tony supplies template).
    # Template: <listing_templates_dir>/Download_PDF_Template_Reference.pdf (settings, ../Listing_Templates).
    raise NotConfigured("Packaging (zip, Drive, Thank You PDF) is not built yet.")


def listing_text(ctx):
    # Template-driven; only the opening SEO paragraph is unique. 13 tags. AI disclosure stays in template.
    # Templates: <listing_templates_dir>/Description_Template_AI.md / _Originals.md and Digital_Note_To_Buyers.md;
    # rules: <rules_dir>/Etsy_Rules_Bible.md (settings, ../Listing_Templates and ../Rules_And_Policies).
    raise NotConfigured("Listing text is not built yet.")


def etsy_draft(ctx):
    # Etsy Open API v3 draft. Until approved, the finished folder is uploaded manually.
    raise NotConfigured("The Etsy draft step is not built yet.")
