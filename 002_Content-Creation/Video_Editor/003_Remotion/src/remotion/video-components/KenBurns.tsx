import React from "react";
import { Img, interpolate, useCurrentFrame, useVideoConfig, staticFile } from "remotion";

interface KenBurnsProps {
  src: string;         // path passed to staticFile()
  zoomFrom?: number;   // starting scale, default 1.0
  zoomTo?: number;     // ending scale, default 1.08
  panX?: number;       // total horizontal drift in px, default 0
  panY?: number;       // total vertical drift in px (positive = down), default 0
}

// ─── KenBurns ────────────────────────────────────────────────────────────────
// Wraps a static image with a slow animated scale + pan to add cinematic motion.
// Used for Flux-generated images and scientific diagrams throughout the doc.
// Duration comes from the parent <Sequence durationInFrames>.

export const KenBurns: React.FC<KenBurnsProps> = ({
  src,
  zoomFrom = 1.0,
  zoomTo = 1.08,
  panX = 0,
  panY = 0,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames, width, height } = useVideoConfig();

  const scale = interpolate(frame, [0, durationInFrames], [zoomFrom, zoomTo], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const translateX = interpolate(frame, [0, durationInFrames], [0, panX], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const translateY = interpolate(frame, [0, durationInFrames], [0, panY], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div style={{ width, height, position: "relative", overflow: "hidden", backgroundColor: "#000000" }}>
      {/* Image layer */}
      <Img
        src={staticFile(src)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `scale(${scale}) translate(${translateX}px, ${translateY}px)`,
          transformOrigin: "center center",
        }}
      />
      {/* Vignette overlay — darkens edges for cinematic depth */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(ellipse at center, transparent 40%, rgba(0,0,0,0.55) 100%)",
          pointerEvents: "none",
        }}
      />
    </div>
  );
};
