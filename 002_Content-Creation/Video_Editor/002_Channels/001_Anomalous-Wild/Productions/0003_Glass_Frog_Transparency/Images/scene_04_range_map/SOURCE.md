# scene_04 range map — asset provenance

**basemap.png** — derived from **Natural Earth II with Shaded Relief (NE2_50M_SR_W)**,
50m raster, naturalearthdata.com.

- License: **PUBLIC DOMAIN.** Natural Earth terms of use: "All versions of Natural
  Earth raster + vector map data found on this website are in the public domain.
  No permission is needed to use Natural Earth. Crediting the authors is
  unnecessary." → **no on-screen attribution required.**
- Processing (scratchpad script, 2026-09-02): cropped to lon [-112,-38] / lat
  [-13,28.6] (16:9), blue-channel ocean mask → navy ocean + desaturated dark-green
  relief land in the Anomalous Wild palette, thin coastline, vignette. 1920x1080.
- Used as the static background layer in `RangeMapAnimation` (GlassFrogDoc.tsx).
  The glowing range path is drawn over it in Remotine tracing real geography:
  S. Mexico → Central America (Pacific side) → Panama → Colombian Andes → down the
  Andes → western Amazon basin (end dot).

`_route_preview.png` — reference only: the styled basemap with the planned path
baked in, used to check geography before wiring the Remotion waypoints.
