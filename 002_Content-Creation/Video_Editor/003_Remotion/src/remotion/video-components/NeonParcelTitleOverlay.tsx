import { loadFont } from "@remotion/google-fonts/Bangers";
import React from "react";
import { Audio } from "@remotion/media";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  OffthreadVideo,
  Sequence,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

const { fontFamily } = loadFont();

// ── Timing constants (24 fps) ──────────────────────────────────────────────
const START_FRAME = 24;        // graphic appears at exactly 1 second
const VISIBLE_FRAMES = 48;     // stays fully visible for 2 seconds
const FADE_FRAMES = 10;        // fades out over this many frames
const SEQUENCE_DURATION = VISIBLE_FRAMES + FADE_FRAMES; // 58 frames total

// ── The animated text pill ─────────────────────────────────────────────────
const TitlePill: React.FC = () => {
  const frame = useCurrentFrame(); // relative to Sequence
  const { fps } = useVideoConfig();

  // Slide in from the left — snappy spring with slight bounce
  const slideProgress = spring({
    fps,
    frame,
    config: { mass: 0.35, damping: 10, stiffness: 220 },
    durationInFrames: 16,
  });
  const translateX = interpolate(slideProgress, [0, 1], [-900, 0]);

  // Slight scale pop on entry (1.08 → 1.0) for extra punch
  const scaleProgress = spring({
    fps,
    frame,
    config: { mass: 0.5, damping: 14, stiffness: 260 },
    durationInFrames: 14,
  });
  const scale = interpolate(scaleProgress, [0, 1], [1.08, 1.0]);

  // Fade out after VISIBLE_FRAMES
  const opacity = interpolate(
    frame,
    [VISIBLE_FRAMES, VISIBLE_FRAMES + FADE_FRAMES],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  return (
    <div
      style={{
        position: "absolute",
        // Centered horizontally, upper portion of the frame
        top: 260,
        left: 0,
        right: 0,
        display: "flex",
        justifyContent: "center",
        opacity,
      }}
    >
      <div
        style={{
          transform: `translateX(${translateX}px) scale(${scale})`,
          transformOrigin: "center center",
        }}
      >
      {/* Colored pill — tight to text width */}
      <div
        style={{
          display: "inline-block",
          backgroundColor: "#E63500",
          borderRadius: 10,
          // Retro hard shadow = no blur, offset
          boxShadow: "6px 6px 0px #000000",
          paddingTop: 14,
          paddingBottom: 10,
          paddingLeft: 28,
          paddingRight: 28,
        }}
      >
        <div
          style={{
            fontFamily,
            fontSize: 88,
            fontWeight: 400, // Bangers is a display face — 400 is already heavy
            color: "#FFFFFF",
            textTransform: "uppercase",
            letterSpacing: "0.06em",
            lineHeight: 1.05,
            // Retro double-stroke shadow effect
            textShadow: "3px 3px 0px rgba(0,0,0,0.55)",
            whiteSpace: "nowrap",
          }}
        >
          cats being
        </div>
        <div
          style={{
            fontFamily,
            fontSize: 88,
            fontWeight: 400,
            color: "#FFFFFF",
            textTransform: "uppercase",
            letterSpacing: "0.06em",
            lineHeight: 1.05,
            textShadow: "3px 3px 0px rgba(0,0,0,0.55)",
            whiteSpace: "nowrap",
          }}
        >
          strange &amp; cute
        </div>
      </div>
      </div>
    </div>
  );
};

// ── Full composition ───────────────────────────────────────────────────────
export const NeonParcelTitleOverlay: React.FC = () => {
  return (
    <AbsoluteFill>
      {/* Base video — plays the full stitched output */}
      <OffthreadVideo src={staticFile("0002-Neon_Parcel_Cats_Real.mp4")} />

      {/* Background music — Suno "Sneaky Little Paws", ease-out from 19s → 0% at 27s */}
      <Sequence durationInFrames={648}>
        <Audio
          src={staticFile("0002_bg_music.mp3")}
          volume={(frame) => {
            const FADE_START = 456; // 19s at 24fps
            const FADE_END = 648;   // 27s at 24fps
            if (frame < FADE_START) return 1;
            return interpolate(frame, [FADE_START, FADE_END], [1, 0], {
              easing: Easing.out(Easing.poly(4)),
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            });
          }}
        />
      </Sequence>

      {/* Animated title card — starts at 1s, on for 2s, fades out */}
      <AbsoluteFill style={{ pointerEvents: "none" }}>
        <Sequence from={START_FRAME} durationInFrames={SEQUENCE_DURATION}>
          <TitlePill />
        </Sequence>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
