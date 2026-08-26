import React from "react";
import { AbsoluteFill, Img, useCurrentFrame, staticFile } from "remotion";
import { kf } from "../video-lib/motion_graphics_presets";

// ─── Scene05DiagramAnimation ───────────────────────────────────────────────
// Approach B (Motion-Graphics-Compositing skill): 3 isolated component assets
// (2 waves, 1 filter) composited with opacity/scale/position keyframes.
//
// 2026-08-23 revision: removed the Eye_CrossSection layer (was a generic
// human-eyeball anatomy diagram, factually wrong for the line it illustrated
// — it appeared while narration specifically credited the mantis shrimp with
// unique polarization detection). The scene now ends on a fade-to-black at
// 1:09 in the full assembly, handing off to a live-action mantis shrimp
// clip spliced in externally (see Report_Card.md 2026-08-23 entry). Also
// added a grounded label/arrow overlay: anchor coordinates for each label
// come from detect_label_coordinates.py run against the actual asset PNGs
// (see *_coords.json siblings in this asset folder), not eyeballed — the
// prior complaint was that labels/arrows in earlier diagram passes pointed
// at the wrong spot. Each label's screen position is recomputed every frame
// by applying the SAME scale/translateX transform as its parent layer, so
// it tracks correctly through the pan/scale animation instead of drifting.
//
// Beat boundaries tied to real narration word timestamps
// (Narration_Audio/scene_05_beat_sheet.json), fps=30:
const F0 = 0;
const F1 = 134;  // 4.46s  — "...see light only as color." ends
const F2 = 280;  // 9.33s  — "...twist through" ends (twisting wave fully replaces plain wave)
const F3 = 452;  // 15.07s — "...invisible to nearly every other eye on Earth." ends
const F4 = 560;  // 18.67s — filter fully assembled (moved earlier than the old 20.63s so it
                  // holds fully visible, with its label, before the cut — was mid-fade at cut before)
const CUT_START = 595; // 19.83s — matches 1:09 in the full assembly; fade to black begins
const CUT_END = 615;   // 20.5s  — fully black; external live-action clip takes over from here

const ASSET_DIR = "0002_mantis_shrimp_color_vision/scene_05_components_alpha";

interface LayerProps {
  src: string;
  opacity: number;
  scale: number;
  translateXPct: number;
}

const Layer: React.FC<LayerProps> = ({ src, opacity, scale, translateXPct }) => (
  <AbsoluteFill>
    <Img
      src={staticFile(`${ASSET_DIR}/${src}`)}
      style={{
        width: "100%",
        height: "100%",
        objectFit: "contain",
        opacity,
        transform: `scale(${scale}) translateX(${translateXPct}%)`,
        transformOrigin: "center center",
      }}
    />
  </AbsoluteFill>
);

// Composition is 1920x1080. Converts a label's detected (x_pct, y_pct) on the
// UNTRANSFORMED source image into composition-space pixels once objectFit:
// "contain" has placed it in the 1920x1080 box, given the asset's own pixel
// dimensions (accounts for the Polarization_Filter asset's slight aspect-
// ratio mismatch vs. the two Wave assets, which match 16:9 exactly).
function baseScreenPos(xPct: number, yPct: number, assetW: number, assetH: number) {
  const compW = 1920;
  const compH = 1080;
  const assetAspect = assetW / assetH;
  const compAspect = compW / compH;
  let dispW: number, dispH: number, offX: number, offY: number;
  if (assetAspect > compAspect) {
    dispW = compW;
    dispH = compW / assetAspect;
    offX = 0;
    offY = (compH - dispH) / 2;
  } else {
    dispH = compH;
    dispW = compH * assetAspect;
    offY = 0;
    offX = (compW - dispW) / 2;
  }
  return { x: offX + (xPct / 100) * dispW, y: offY + (yPct / 100) * dispH };
}

// Applies the same `scale(s) translateX(t%)` transform (transform-origin:
// center center, around composition center 960,540) that the Layer's <Img>
// uses, so a label tracks its parent layer's pan/scale exactly.
function trackedPos(base: { x: number; y: number }, scale: number, translateXPct: number) {
  const translatedX = base.x + (translateXPct / 100) * 1920;
  const x = 960 + (translatedX - 960) * scale;
  const y = 540 + (base.y - 540) * scale;
  return { x, y };
}

interface LabelProps {
  x: number;
  y: number;
  text: string;
  opacity: number; // 0-1, drives both the resolve-blur and the fade
  labelDx?: number;
  labelDy?: number;
}

// Blur-to-sharp + opacity resolve (design-rules-learned.md Rule 2) — never a
// flat opacity-only pop. `opacity` here is expected to already be a ramped
// 0->1 value from kf(), so the blur derives directly from it.
const Label: React.FC<LabelProps> = ({ x, y, text, opacity, labelDx = 130, labelDy = -55 }) => {
  const blurPx = (1 - opacity) * 10;
  const labelX = x + labelDx;
  const labelY = y + labelDy;
  return (
    <svg width={1920} height={1080} style={{ position: "absolute", top: 0, left: 0 }}>
      <line
        x1={x} y1={y} x2={labelX} y2={labelY}
        stroke="#8AFA47" strokeWidth={1.5}
        opacity={opacity * 0.8}
        strokeDasharray={200}
        strokeDashoffset={200 * (1 - opacity)}
      />
      <circle cx={x} cy={y} r={4} fill="#8AFA47" opacity={opacity} />
      <text
        x={labelX + 8}
        y={labelY}
        fill="#E8FFE0"
        fontSize={22}
        fontFamily="Arial, sans-serif"
        opacity={opacity}
        style={{ filter: `blur(${blurPx}px)` }}
      >
        {text}
      </text>
    </svg>
  );
};

export const Scene05DiagramAnimation: React.FC = () => {
  const frame = useCurrentFrame();

  // Plain wave: establishes ordinary color-only light, crossfades out as the
  // twisting wave takes over on "twist through."
  const plainWaveOpacity = kf(frame, [[F0, 1], [F1, 1], [F2, 0]]);
  const plainWaveScale = 1.0;
  const plainWaveTranslateX = 0;

  // Twisting polarized wave: crossfades in as the plain wave fades, holds
  // centered through "invisible to nearly every other eye," then shifts
  // left as the filter assembles beside it. No further push-in — the old
  // push-into-the-eye motion doesn't apply now that the eye layer is gone.
  const twistWaveOpacity = kf(frame, [[F1, 0], [F2, 1], [CUT_START, 1], [CUT_END, 0]]);
  const twistWaveScale = 1.0;
  const twistWaveTranslateX = kf(frame, [[F3, 0], [F4, -14]]);

  // Filter: fades in as "only a small handful can detect this directly"
  // lands, now fully assembled by F4 (18.67s) with room to hold before the
  // cut, instead of still mid-fade when the scene used to end.
  const filterOpacity = kf(frame, [[F3, 0], [F4, 1], [CUT_START, 1], [CUT_END, 0]]);
  const filterScale = kf(frame, [[F3, 0.85], [F4, 1.0]]);
  const filterTranslateX = kf(frame, [[F3, 5], [F4, 2]]);

  // Fade-to-black tail — hands off to the external live-action shrimp clip.
  const blackOpacity = kf(frame, [[CUT_START, 0], [CUT_END, 1]]);

  // ── Label anchor points ──
  // 2026-08-23: the detect_label_coordinates.py-derived points were correctly
  // grounded to real features, but two of the three placements still read
  // badly on screen — the twist-wave label's rightmost-crest anchor sat right
  // at the frame edge and ran off-screen once offset, and the filter label
  // text sat too close to (and briefly over) the glass. Tony reviewed static
  // mockups of the fix (measured directly off real rendered frames — see
  // scratchpad mockup_*_v2.jpg) and approved: labels live in open black
  // space, one clean leader line to a single on-target point, never text
  // over the diagram itself. Anchor points below are those same
  // frame-measured pixel positions, not re-guessed.
  const plainWaveBase = { x: 906, y: 417 }; // measured wave-crest peak, plain wave never transforms
  const plainWaveLabelPos = trackedPos(plainWaveBase, plainWaveScale, plainWaveTranslateX);
  const plainWaveLabelOpacity = kf(frame, [[20, 0], [40, 1], [F1 - 15, 1], [F1, 0]]);

  // Interior crest (not the rightmost one) — stays safely on-screen. The
  // label's whole visible window (F2+20..F3) is before twistWaveTranslateX
  // starts moving (that shift only begins at F3), so no transform to track yet.
  const twistWaveBase = { x: 1122, y: 379 };
  const twistWaveLabelPos = trackedPos(twistWaveBase, twistWaveScale, twistWaveTranslateX);
  const twistWaveLabelOpacity = kf(frame, [[F2 + 20, 0], [F2 + 40, 1], [F3 - 15, 1], [F3, 0]]);

  const filterAxisTopBase = baseScreenPos(42.1, 21.0, 2688, 1520); // transmission_axis_top
  const filterAxisBottomBase = baseScreenPos(57.9, 79.0, 2688, 1520); // transmission_axis_bottom
  const filterAxisTop = trackedPos(filterAxisTopBase, filterScale, filterTranslateX);
  const filterAxisBottom = trackedPos(filterAxisBottomBase, filterScale, filterTranslateX);
  const filterLabelOpacity = kf(frame, [[F4 - 30, 0], [F4 - 10, 1], [CUT_START, 1], [CUT_START + 10, 0]]);
  // Label text position — pulled well clear of the disc into open black space
  // (measured: disc's own right edge sits ~x=1225; text now starts at 1330,
  // splitting the difference between the disc edge and the old over-far
  // clipped position rather than crowding either).
  const filterLabelTextPos = { x: 1330, y: 108 };

  return (
    <AbsoluteFill style={{ backgroundColor: "#050b10" }}>
      <Layer src="Wave_Plain_Linear.png" opacity={plainWaveOpacity} scale={plainWaveScale} translateXPct={plainWaveTranslateX} />
      <Layer src="Wave_Polarized_Twist.png" opacity={twistWaveOpacity} scale={twistWaveScale} translateXPct={twistWaveTranslateX} />
      <Layer src="Polarization_Filter.png" opacity={filterOpacity} scale={filterScale} translateXPct={filterTranslateX} />

      {/* Labels sit directly above their target in open black space — matches the
          straight-drop leader-line convention from Tony's reference examples. */}
      <Label x={plainWaveLabelPos.x} y={plainWaveLabelPos.y} text="Ordinary light — one flat plane" opacity={plainWaveLabelOpacity} labelDx={-146} labelDy={-277} />
      <Label x={twistWaveLabelPos.x} y={twistWaveLabelPos.y} text="Twisting = polarization" opacity={twistWaveLabelOpacity} labelDx={-42} labelDy={-249} />

      {/* Filter: the diagonal line ON the glass is the actual transmission axis (real
          feature, drawn where it really is) — a separate short callout line then carries
          the eye from that axis out to the label text, which lives entirely in the open
          black space to the upper right, never over the disc itself. */}
      <svg width={1920} height={1080} style={{ position: "absolute", top: 0, left: 0 }}>
        <line
          x1={filterAxisTop.x} y1={filterAxisTop.y} x2={filterAxisBottom.x} y2={filterAxisBottom.y}
          stroke="#8AFA47" strokeWidth={2} opacity={filterLabelOpacity * 0.85}
          strokeDasharray={220} strokeDashoffset={220 * (1 - filterLabelOpacity)}
        />
        <line
          x1={filterAxisTop.x} y1={filterAxisTop.y} x2={filterLabelTextPos.x - 12} y2={filterLabelTextPos.y - 8}
          stroke="#8AFA47" strokeWidth={1.5} opacity={filterLabelOpacity * 0.8}
          strokeDasharray={200} strokeDashoffset={200 * (1 - filterLabelOpacity)}
        />
        <circle cx={filterAxisTop.x} cy={filterAxisTop.y} r={4} fill="#8AFA47" opacity={filterLabelOpacity} />
        <text
          x={filterLabelTextPos.x} y={filterLabelTextPos.y}
          fill="#E8FFE0" fontSize={26} fontFamily="Arial, sans-serif"
          opacity={filterLabelOpacity}
          style={{ filter: `blur(${(1 - filterLabelOpacity) * 10}px)` }}
        >
          Polarizing filter — transmission axis
        </text>
      </svg>

      {/* Vignette — matches Scene02DiagramTest.tsx's cinematic depth treatment */}
      <AbsoluteFill
        style={{
          background: "radial-gradient(ellipse at center, transparent 40%, rgba(0,0,0,0.55) 100%)",
          pointerEvents: "none",
        }}
      />

      {/* Fade-to-black tail, hands off to the external live-action shrimp clip at CUT_END */}
      <AbsoluteFill style={{ backgroundColor: "#000000", opacity: blackOpacity, pointerEvents: "none" }} />
    </AbsoluteFill>
  );
};
