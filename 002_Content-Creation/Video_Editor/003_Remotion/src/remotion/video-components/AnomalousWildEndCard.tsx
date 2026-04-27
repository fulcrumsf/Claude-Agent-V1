/**
 * AnomalousWildEndCard — 10-second YouTube end card (300 frames @ 30fps)
 *
 * Background: AI-generated (Nano Banana Pro) — all four channel animals,
 *   no text, cinematic dark atmospheric. File: public/anomalous_wild_bg.jpg
 *
 * Elements:
 *   - "THANK YOU / FOR WATCHING" — spring drop-in, staggered lines
 *   - Subscribe button — bubble pop-in, top-right, bouncy spring
 *   - "LIKE, COMMENT" CTA — fades up from below
 *   - Master fade-out at end
 *
 * All animations: useCurrentFrame() + interpolate/spring — no CSS transitions.
 */

import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Easing,
  Img,
  staticFile,
} from "remotion";

// ─── Brand palette ─────────────────────────────────────────────────────────────
const C = {
  bg: "#050210",
  purple: "#6B35FF",
  lime: "#8AFA47",
  white: "#FFFFFF",
  redYT: "#FF0000",
  fbBlue: "#1877F2",
};

// ─── Background (AI-generated image + atmospheric overlays) ───────────────────
const Background: React.FC<{ frame: number }> = ({ frame }) => {
  const fadeIn = interpolate(frame, [0, 22], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  // Slow breathing glow pulse on the center
  const breathe = 0.55 + Math.sin(frame * 0.04) * 0.08;

  return (
    <div style={{ position: "absolute", inset: 0, opacity: fadeIn }}>
      {/* AI-generated animal background — full bleed */}
      <Img
        src={staticFile("anomalous_wild_bg.jpg")}
        style={{
          position: "absolute",
          inset: 0,
          width: "100%",
          height: "100%",
          objectFit: "cover",
          objectPosition: "center",
        }}
      />

      {/* Center vignette — darkens the middle for UI readability,
          keeps animals glowing at the edges */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `radial-gradient(ellipse 55% 65% at 50% 50%,
            rgba(5,2,16,${breathe.toFixed(2)}) 0%,
            rgba(5,2,16,0.72) 45%,
            rgba(5,2,16,0.08) 100%)`,
        }}
      />

      {/* Bottom dark bar — grounds the like/comment CTA */}
      <div
        style={{
          position: "absolute",
          bottom: 0,
          left: 0,
          right: 0,
          height: 180,
          background: `linear-gradient(to top, rgba(5,2,16,0.85) 0%, transparent 100%)`,
        }}
      />

      {/* Top dark bar — grounds the subscribe button */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          height: 160,
          background: `linear-gradient(to bottom, rgba(5,2,16,0.8) 0%, transparent 100%)`,
        }}
      />

      {/* Purple brand glow overlay — center pulse */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `radial-gradient(ellipse 40% 50% at 50% 50%, rgba(107,53,255,0.12) 0%, transparent 70%)`,
          opacity: 0.6 + Math.sin(frame * 0.07) * 0.2,
        }}
      />
    </div>
  );
};

// ─── Title lines ───────────────────────────────────────────────────────────────
const AnimatedTitle: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const line1Spring = spring({
    frame: frame - 6,
    fps,
    config: { damping: 18, stiffness: 130 },
  });
  const line2Spring = spring({
    frame: frame - 20,
    fps,
    config: { damping: 18, stiffness: 130 },
  });

  const line1Y = interpolate(line1Spring, [0, 1], [-55, 0]);
  const line1O = interpolate(frame, [6, 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const line2Y = interpolate(line2Spring, [0, 1], [-55, 0]);
  const line2O = interpolate(frame, [20, 35], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const titleBase: React.CSSProperties = {
    fontFamily: "'Bebas Neue', Impact, 'Arial Black', sans-serif",
    fontWeight: 900,
    fontSize: 110,
    color: C.white,
    letterSpacing: "0.05em",
    lineHeight: 1.05,
    textShadow: `0 0 50px ${C.purple}80, 0 0 100px ${C.purple}40, 0 4px 28px rgba(0,0,0,0.95)`,
    display: "block",
    textAlign: "center",
  };

  return (
    <div style={{ textAlign: "center" }}>
      <div style={{ ...titleBase, opacity: line1O, transform: `translateY(${line1Y}px)` }}>
        THANK YOU
      </div>
      <div style={{ ...titleBase, opacity: line2O, transform: `translateY(${line2Y}px)` }}>
        FOR WATCHING
      </div>
    </div>
  );
};

// ─── Subscribe button (top-right, bubble pop-in) ───────────────────────────────
const SubscribeButton: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const popSpring = spring({
    frame: frame - 15,
    fps,
    config: { damping: 7, stiffness: 220 },
  });
  const scale = interpolate(popSpring, [0, 1], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Bell jiggle on entry
  const jiggle =
    frame > 55
      ? Math.sin((frame - 55) * 0.22) * 12 * Math.max(0, 1 - (frame - 55) / 30)
      : 0;

  // Continuous glow pulse
  const glowPulse = 0.3 + Math.sin(frame * 0.12) * 0.15;

  return (
    <div
      style={{
        transformOrigin: "center",
        transform: `scale(${scale})`,
        position: "relative",
      }}
    >
      {/* Glow halo */}
      <div
        style={{
          position: "absolute",
          inset: -7,
          borderRadius: 9,
          background: `rgba(255,0,0,${(glowPulse * 0.35).toFixed(2)})`,
          filter: "blur(10px)",
        }}
      />

      {/* Button — 30% smaller than original */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 7,
          backgroundColor: C.redYT,
          borderRadius: 7,
          padding: "13px 24px",
          position: "relative",
          boxShadow: `0 3px 16px rgba(255,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.22)`,
        }}
      >
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="white"
          style={{ transform: `rotate(${jiggle}deg)`, transformOrigin: "top center" }}
        >
          <path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.9 2 2 2zm6-6V11c0-3.07-1.64-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.63 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z" />
        </svg>
        <span
          style={{
            fontSize: 25,
            fontFamily: "'Bebas Neue', Impact, 'Arial Black', sans-serif",
            fontWeight: 700,
            color: C.white,
            letterSpacing: "0.14em",
          }}
        >
          SUBSCRIBE
        </span>
      </div>
    </div>
  );
};

// ─── Like / Comment CTA ────────────────────────────────────────────────────────
const LikeCommentCTA: React.FC<{ frame: number }> = ({ frame }) => {
  const opacity = interpolate(frame, [55, 72], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.quad),
  });
  const translateY = interpolate(frame, [55, 72], [22, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const thumbBounce = 1 + Math.sin(frame * 0.18) * 0.07;

  const arrow = (i: number) =>
    interpolate(frame, [60 + i * 6, 72 + i * 6], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });

  const arrowStyle = (i: number, flip?: boolean): React.CSSProperties => ({
    opacity: arrow(i),
    fontSize: 36,
    color: C.lime,
    fontWeight: 900,
    fontFamily: "sans-serif",
    lineHeight: 1,
    textShadow: `0 0 14px ${C.lime}`,
    transform: flip ? "scaleX(-1)" : undefined,
  });

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 16,
        opacity,
        transform: `translateY(${translateY}px)`,
      }}
    >
      <div style={{ display: "flex", gap: 3 }}>
        {[0, 1, 2].map((i) => <span key={i} style={arrowStyle(i)}>›</span>)}
      </div>

      <div
        style={{
          width: 56,
          height: 56,
          borderRadius: "50%",
          backgroundColor: C.fbBlue,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          transform: `scale(${thumbBounce})`,
          boxShadow: "0 4px 20px rgba(24,119,242,0.6)",
          fontSize: 28,
        }}
      >
        👍
      </div>

      <span
        style={{
          fontSize: 32,
          fontFamily: "'Bebas Neue', Impact, 'Arial Black', sans-serif",
          fontWeight: 700,
          color: C.white,
          letterSpacing: "0.16em",
          textShadow: `0 0 24px ${C.purple}, 0 2px 20px rgba(0,0,0,0.9)`,
        }}
      >
        LIKE, COMMENT
      </span>

      <div style={{ display: "flex", gap: 3 }}>
        {[0, 1, 2].map((i) => <span key={i} style={arrowStyle(i, true)}>›</span>)}
      </div>
    </div>
  );
};

// ─── Root composition ──────────────────────────────────────────────────────────
export const AnomalousWildEndCard: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const masterOpacity = interpolate(frame, [278, 300], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{ backgroundColor: C.bg, overflow: "hidden", opacity: masterOpacity }}
    >
      <Background frame={frame} />

      <AbsoluteFill
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: 60,
          padding: "100px 120px 90px",
        }}
      >
        <SubscribeButton frame={frame} fps={fps} />
        <AnimatedTitle frame={frame} fps={fps} />
        <LikeCommentCTA frame={frame} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
