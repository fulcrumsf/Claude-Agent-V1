import React from "react";
import { AbsoluteFill, Img, useCurrentFrame, staticFile } from "remotion";
import { kf } from "../video-lib/motion_graphics_presets";

// ─── Scene02DiagramTest ───────────────────────────────────────────────────
// Test composition — Approach B (Diagram-Generation skill): 4 clean, isolated
// component assets (generated separately, no drift) composited with
// opacity/scale/position keyframes instead of asking a video model to
// animate a single baked illustration. Timing matches the real
// Scene_02_Diagram_Animation_Storyboard.png panel timestamps.
// Built 2026-08-18 as a direct comparison against the Seedance 1.5 Pro
// start/end-frame test, which hallucinated badly on this same beat.

// 2026-08-18: switched from the flat-background component assets to Recraft
// AI-matted true-alpha versions (kie-cli recraft_remove_background). The
// screen-blend-mode workaround on the flat assets removed the hard black
// seam but still left a faint grayish edge, because the baked-in background
// wasn't literally pure black — screen blend of two near-black-but-not-equal
// colors still adds a little brightness at the boundary. Real alpha
// transparency has no seam by construction: there's no pixel data at all
// outside the subject, so there's nothing for two layers to disagree about.
const ASSET_DIR = "0002_mantis_shrimp_color_vision/scene_02_components_alpha";

// kf() now imported from the shared Motion-Graphics-Compositing preset lib
// (video-lib/motion_graphics_presets.ts) — this file was the original source
// it was extracted from, now dogfooding the shared version. No behavior change.

// Beat boundaries in frames, fps=30, matching the storyboard's real timestamps:
// 0.0-0.4s "Human" | 0.4-3.1s "eyes carry three..." | 3.6-5.0s "every color..."
// 5.0-7.0s "was built from those three" | 7.0-7.5s transition (pull back)
// 7.5-8.5s "The mantis shrimp" | 8.5-9.5s "carries up to" | 9.5-10.5s "sixteen"
const T1 = 12;   // 0.4s
const T2 = 93;   // 3.1s
const T3 = 108;  // 3.6s
const T5 = 210;  // 7.0s
const T6 = 225;  // 7.5s
const T7 = 255;  // 8.5s
const T8 = 285;  // 9.5s
const T9 = 315;  // 10.5s (end)

interface LayerProps {
  src: string;
  opacity: number;
  scale: number;
  translateXPct: number;
}

// Now using Recraft-matted true-alpha assets, so normal alpha compositing
// (no mixBlendMode hack) is correct — and actually required: screen blend
// would incorrectly wash out/over-brighten moments where two subjects
// genuinely overlap on screen at once (e.g. the mantis eye and receptor fan
// both partially visible during the pull-back), since screen mode adds
// color values instead of properly occluding via alpha.
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

export const Scene02DiagramTest: React.FC = () => {
  const frame = useCurrentFrame();

  // Mantis external eye: paired+dimmed at open, gone through the human
  // cross-section hold, reappears solo-focal for "The mantis shrimp",
  // fades as the receptor fan takes over.
  const mantisEyeOpacity = kf(frame, [
    [0, 0.55], [T1, 0.55], [T2, 0], [T6, 1], [T7, 1], [T8, 0.15],
  ]);
  const mantisEyeScale = kf(frame, [[0, 1.0], [T6, 1.0], [T8, 1.08]]);
  const mantisEyeTranslateX = kf(frame, [[0, -22], [T1, -22], [T6, 0]]);

  // Human external eye: paired+full at open, push-in focal through the
  // "three color receptor" line, fades out as the cross-section takes over.
  const humanEyeOpacity = kf(frame, [[0, 1], [T2, 1], [T3, 0]]);
  const humanEyeScale = kf(frame, [[0, 1.0], [T2, 1.15]]);
  const humanEyeTranslateX = kf(frame, [[0, 18], [T1, 18], [T2, 0]]);

  // Human eye cross-section: crossfades in as the external eye fades out,
  // holds and pushes in through "built from those three," fades during pull-back.
  const crossSectionOpacity = kf(frame, [[T2, 0], [T3, 1], [T5, 1], [T6, 0]]);
  const crossSectionScale = kf(frame, [[T3, 1.0], [T5, 1.2]]);

  // Mantis receptor fan: faint peek during pull-back, grows to dominant as
  // "carries up to sixteen" lands, continuous push-in through the close.
  const fanOpacity = kf(frame, [[T6, 0], [T7, 0.3], [T8, 1]]);
  const fanScale = kf(frame, [[T6, 1.0], [T9, 1.35]]);

  return (
    <AbsoluteFill style={{ backgroundColor: "#050b10" }}>
      <Layer src="Mantis_Eye_External.png" opacity={mantisEyeOpacity} scale={mantisEyeScale} translateXPct={mantisEyeTranslateX} />
      <Layer src="Human_Eye_External.png" opacity={humanEyeOpacity} scale={humanEyeScale} translateXPct={humanEyeTranslateX} />
      <Layer src="Human_Eye_CrossSection.png" opacity={crossSectionOpacity} scale={crossSectionScale} translateXPct={0} />
      <Layer src="Mantis_Receptor_Fan.png" opacity={fanOpacity} scale={fanScale} translateXPct={0} />
      {/* Vignette — matches KenBurns.tsx's cinematic depth treatment */}
      <AbsoluteFill
        style={{
          background: "radial-gradient(ellipse at center, transparent 40%, rgba(0,0,0,0.55) 100%)",
          pointerEvents: "none",
        }}
      />
    </AbsoluteFill>
  );
};
