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
    # hero, video, flat poster, ~20x detail zoom, room scenes. Static via PhotoCraft headless.
    # Fidelity check per AI room mockup (compare art region to original) or composite art by code.
    if not shutil.which("photocraft-cli"):
        raise NotConfigured("mockups: photocraft-cli not on PATH; first task is proving it opens the PSDs")
    raise NotConfigured("Mockups are not built yet.")


def package(ctx):
    # Sequential folder per listing, share link into templated PDF (Tony supplies template).
    raise NotConfigured("Packaging (zip, Drive, Thank You PDF) is not built yet.")


def listing_text(ctx):
    # Template-driven; only the opening SEO paragraph is unique. 13 tags. AI disclosure stays in template.
    raise NotConfigured("Listing text is not built yet.")


def etsy_draft(ctx):
    # Etsy Open API v3 draft. Until approved, the finished folder is uploaded manually.
    raise NotConfigured("The Etsy draft step is not built yet.")
