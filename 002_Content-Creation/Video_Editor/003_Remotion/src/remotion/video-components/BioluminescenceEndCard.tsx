import React from "react";
import { AbsoluteFill, useCurrentFrame, interpolate, Easing } from "remotion";

/**
 * scene_12 — HOOK FORWARD / END CARD (6:00–6:10)
 * Black screen. Single bioluminescent pulse appears, glows, fades.
 * Channel watermark fades in bottom-right.
 */
export const BioluminescenceEndCard: React.FC = () => {
  const frame = useCurrentFrame();

  // The pulse: appears at frame 20, peaks at 35, fades by 60
  const pulseOpacity = interpolate(
    frame,
    [15, 25, 40, 70],
    [0, 1, 0.7, 0],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.inOut(Easing.sin),
    }
  );

  // Pulse size — breathes slightly
  const pulseScale = interpolate(
    frame,
    [15, 35, 60],
    [0.4, 1, 1.4],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.out(Easing.cubic),
    }
  );

  // Watermark fades in as pulse fades
  const watermarkOpacity = interpolate(frame, [50, 80], [0, 0.45], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "#000000" }}>
      {/* Bioluminescent glow orb — centered */}
      <div
        style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: `translate(-50%, -50%) scale(${pulseScale})`,
          opacity: pulseOpacity,
          width: 20,
          height: 20,
          borderRadius: "50%",
          backgroundColor: "#8FEFFF",
          boxShadow: `
            0 0 8px 4px rgba(143,239,255,0.9),
            0 0 30px 15px rgba(143,239,255,0.5),
            0 0 80px 40px rgba(97,45,216,0.3),
            0 0 160px 80px rgba(97,45,216,0.15)
          `,
        }}
      />

      {/* Channel watermark — bottom right */}
      <div
        style={{
          position: "absolute",
          bottom: 40,
          right: 60,
          opacity: watermarkOpacity,
          display: "flex",
          flexDirection: "column",
          alignItems: "flex-end",
          gap: 4,
        }}
      >
        <div
          style={{
            fontSize: 18,
            fontFamily: "Montserrat, Arial, sans-serif",
            fontWeight: 700,
            color: "#FFFFFF",
            letterSpacing: "0.2em",
            textTransform: "uppercase",
          }}
        >
          ANOMALOUS WILD
        </div>
        <div
          style={{
            width: 60,
            height: 2,
            backgroundColor: "#8AFA47",
            boxShadow: "0 0 8px #8AFA47",
            marginLeft: "auto",
          }}
        />
      </div>
    </AbsoluteFill>
  );
};
