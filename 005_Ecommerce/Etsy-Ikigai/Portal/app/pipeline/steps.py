"""Stubs. Fill in on the Mac once tools are connected. Order of build (time sinks first):
mockups, resize, package, listing_text, then upscale, etsy_draft."""
import shutil

from .base import NotConfigured


def generate_art(ctx):
    raise NotConfigured("generate_art: engine adapters not wired (see config/engines.json)")


def upscale(ctx):
    # Default Upscayl; check headless CLI. Backup: Magnific MCP. Two stages: generate -> upscale -> quality check.
    if not shutil.which("upscayl-bin"):
        raise NotConfigured("upscale: Upscayl CLI not found; connect on the Mac")
    raise NotConfigured("upscale: adapter not implemented")


def mockups(ctx):
    # hero, video, flat poster, ~20x detail zoom, room scenes. Static via PhotoCraft headless.
    # Fidelity check per AI room mockup (compare art region to original) or composite art by code.
    if not shutil.which("photocraft-cli"):
        raise NotConfigured("mockups: photocraft-cli not on PATH; first task is proving it opens the PSDs")
    raise NotConfigured("mockups: adapter not implemented")


def resize(ctx):
    # Centre-crop to config/print_sizes.json at 300 DPI. Port ideas from ikigai_cropper_fixed.py.
    raise NotConfigured("resize: not implemented (needs verified print sizes)")


def package(ctx):
    # Sequential folder per listing, share link into templated PDF (Tony supplies template).
    raise NotConfigured("package: PDF template and Drive credentials missing")


def listing_text(ctx):
    # Template-driven; only the opening SEO paragraph is unique. 13 tags. AI disclosure stays in template.
    raise NotConfigured("listing_text: description template missing")


def etsy_draft(ctx):
    # Etsy Open API v3 draft. Until approved, the finished folder is uploaded manually.
    raise NotConfigured("etsy_draft: Etsy developer app not approved yet")
