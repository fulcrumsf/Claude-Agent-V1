// POVCaption.tsx
import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate } from "remotion";

export interface TimedCaption {
  text: string;
  startS: number;
  durationS: number;
  variant: "title" | "label";
}

const FADE_FRAMES = 8;

function useCaptionVisibility(startS: number, durationS: number) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const startFrame = Math.round(startS * fps);
  const endFrame = Math.round((startS + durationS) * fps);

  const opacity = interpolate(
    frame,
    [startFrame, startFrame + FADE_FRAMES, endFrame - FADE_FRAMES, endFrame],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  return { opacity, visible: frame >= startFrame && frame < endFrame };
}

export const POVCaption: React.FC<{
  text: string;
  startS: number;
  durationS: number;
  variant: "title" | "label";
}> = ({ text, startS, durationS, variant }) => {
  const { opacity, visible } = useCaptionVisibility(startS, durationS);
  if (!visible && opacity === 0) return null;

  const isTitle = variant === "title";

  return (
    <div
      style={{
        position: "absolute",
        top: "18%",
        left: "50%",
        transform: "translateX(-50%)",
        opacity,
        maxWidth: "88%",
        textAlign: "center",
        pointerEvents: "none",
        color: "#FFFFFF",
        fontFamily: "'Arial', 'Helvetica Neue', sans-serif",
        fontWeight: 700,
        letterSpacing: "0.02em",
        textTransform: "uppercase",
        fontSize: isTitle ? 64 : 40,
        lineHeight: 1.2,
        textShadow: "0 2px 10px rgba(0,0,0,0.85), 0 4px 24px rgba(0,0,0,0.6)",
      }}
    >
      {text}
    </div>
  );
};
