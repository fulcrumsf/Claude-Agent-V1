"""Sales channels behind one small interface. Etsy is the only channel today; Shopify, Lemon Squeezy
or Tony's own site can be added as another class without touching the Studio module.
Pick the active one with "sales_channel" in config/settings.json."""
from .pipeline.base import NotConfigured


class SalesChannel:
    id = "base"
    label = "Sales channel"

    def create_draft(self, listing: dict) -> dict:
        """Create an unpublished draft listing. Never publishes."""
        raise NotConfigured(f"{self.label}: draft upload not built yet")


class EtsyChannel(SalesChannel):
    id = "etsy"
    label = "Etsy"
    # Drafts only (never state=active). Wired in the production stage via steps.etsy_draft.


CHANNELS = {c.id: c for c in (EtsyChannel,)}


def get_channel(settings) -> SalesChannel:
    return CHANNELS[(settings or {}).get("sales_channel", "etsy")]()
