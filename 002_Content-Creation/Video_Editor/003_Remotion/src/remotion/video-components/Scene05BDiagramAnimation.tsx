import React from "react";
import { AbsoluteFill, Img, OffthreadVideo, useCurrentFrame, staticFile } from "remotion";
import { kf } from "../video-lib/motion_graphics_presets";

// ─── Scene05BDiagramAnimation ──────────────────────────────────────────────
// Approach B (Motion-Graphics-Compositing skill): the facing-off shrimp pair
// (static image) crossfades into a full-bleed animated signal-glyph video
// once the narration turns to "signal to each other in a code."
//
// 2026-08-23 revision: the static Signal_Code_Pattern.png (a small centered
// inset) is replaced with Signal_Grid_FullBleed_animated.mp4 — a Seedance
// 1.5 Pro generation, image-to-video from a GPT-Image-2 extension of that
// same original glyph pattern out to full 16:9 (same glyph shapes/gradient,
// just more of them, edge to edge), animated so each glyph independently
// brightens/dims on its own timing (Tony's "communicating" read). The scene
// now also fades in from black at its own start (F0), handing off cleanly
// from the external live-action mantis shrimp clip that now precedes it in
// the assembly (see Report_Card.md 2026-08-23 entry).
//
// Beat boundaries tied to real narration word timestamps
// (Narration_Audio/scene_05b_beat_sheet.json), fps=30:
const FADE_IN_END = 20;  // 0.67s — quick fade-in from black at scene start
const F1 = 105;           // 3.5s  — "...use this hidden channel" ends; grid begins its slow reveal
const GRID_FULL = 215;    // 7.17s — grid reaches full opacity (deliberately slow — Tony asked for
                           // more drama here than the original ~2s crossfade)
const F3 = 217;           // 7.23s — "...no predator can read," ends
const F4 = 298;           // 9.938s — end (hold on the full grid through the close)

const ASSET_DIR = "0002_mantis_shrimp_color_vision/scene_05b_components_alpha";

interface ImgLayerProps {
  src: string;
  opacity: number;
  scale: number;
}

const ImgLayer: React.FC<ImgLayerProps> = ({ src, opacity, scale }) => (
  <AbsoluteFill>
    <Img
      src={staticFile(`${ASSET_DIR}/${src}`)}
      style={{
        width: "100%",
        height: "100%",
        objectFit: "contain",
        opacity,
        transform: `scale(${scale})`,
        transformOrigin: "center center",
      }}
    />
  </AbsoluteFill>
);

export const Scene05BDiagramAnimation: React.FC = () => {
  const frame = useCurrentFrame();

  // Whole-scene fade-in from black — hands off cleanly from the preceding
  // live-action clip instead of hard-cutting in at full brightness.
  const sceneFadeIn = kf(frame, [[0, 0], [FADE_IN_END, 1]]);

  // Shrimp pair: fades in with the scene, present as the initial "next
  // diagram" beat, then dims as the signal pattern becomes the visual focus.
  const pairOpacity = kf(frame, [[0, 0], [FADE_IN_END, 1], [F1, 1], [GRID_FULL, 0.15]]);
  const pairScale = kf(frame, [[0, 1.0], [F4, 1.08]]);

  // Signal grid video: absent until "signal to each other in a code" lands,
  // then a deliberately slow ~3.7s fade to full opacity (not the original
  // ~2s) for a more dramatic reveal, holding at full brightness through the
  // close since it's now the full-bleed dominant visual.
  const gridOpacity = kf(frame, [[F1, 0], [GRID_FULL, 1], [F4, 1]]);

  return (
    <AbsoluteFill style={{ backgroundColor: "#050b10" }}>
      <ImgLayer src="Mantis_Pair_FacingOff.png" opacity={pairOpacity} scale={pairScale} />

      <AbsoluteFill style={{ opacity: gridOpacity }}>
        <OffthreadVideo
          src={staticFile(`${ASSET_DIR}/Signal_Grid_FullBleed_animated.mp4`)}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
          muted
        />
      </AbsoluteFill>

      {/* Vignette — matches Scene02DiagramTest.tsx's cinematic depth treatment */}
      <AbsoluteFill
        style={{
          background: "radial-gradient(ellipse at center, transparent 40%, rgba(0,0,0,0.55) 100%)",
          pointerEvents: "none",
        }}
      />

      {/* Whole-scene fade-in-from-black overlay */}
      <AbsoluteFill style={{ backgroundColor: "#000000", opacity: 1 - sceneFadeIn, pointerEvents: "none" }} />
    </AbsoluteFill>
  );
};
