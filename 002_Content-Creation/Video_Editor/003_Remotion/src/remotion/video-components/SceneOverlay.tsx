import React from "react";
import {
  useCurrentFrame,
  interpolate,
  spring,
  useVideoConfig,
  Easing,
  random,
} from "remotion";

// ─── Types ────────────────────────────────────────────────────────────────────

export type OverlayType = "species" | "callout" | "fact_flash" | "annotation";

export interface SpeciesOverlayData {
  type: "species";
  name: string;
  scientific: string;
  fact?: string;
  position?: "bottom" | "top" | "center";
}

export interface CalloutOverlayData {
  type: "callout";
  text: string;
  subtext?: string;
  position?: "bottom" | "center" | "top";
}

export interface FactFlashData {
  type: "fact_flash";
  text: string;
  position?: "bottom" | "center";
}

// Annotation: a self-drawing SVG line from label to a point on screen.
// target_x_pct / target_y_pct are 0–1 fractions of the composition width/height.
export interface AnnotationData {
  type: "annotation";
  label: string;
  targetXPct: number;   // 0–1, where to point the arrow (the creature feature)
  targetYPct: number;
}

export type OverlayData =
  | SpeciesOverlayData
  | CalloutOverlayData
  | FactFlashData
  | AnnotationData;

export interface TimedOverlay {
  data: OverlayData;
  startS: number;
  durationS: number;
}

// ─── Constants ────────────────────────────────────────────────────────────────

const FADE_IN_FRAMES = 10;
const FADE_OUT_FRAMES = 10;
const GREEN = "#8AFA47";
const WHITE = "#FFFFFF";
const FONT_TITLE = "'Bebas Neue', 'Impact', Arial, sans-serif";
const FONT_BODY = "'Montserrat', Arial, sans-serif";

// Characters cycled through for odometer animation
const ODOMETER_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%&";

// ─── Shared visibility hook ───────────────────────────────────────────────────

function useVisibility(startS: number, durationS: number) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const startFrame = Math.round(startS * fps);
  const endFrame = Math.round((startS + durationS) * fps);

  const opacity = interpolate(
    frame,
    [startFrame, startFrame + FADE_IN_FRAMES, endFrame - FADE_OUT_FRAMES, endFrame],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const visible = frame >= startFrame && frame < endFrame;
  const localFrame = frame - startFrame;

  return { opacity, visible, localFrame, startFrame, endFrame, fps };
}

// ─── OdometerText ─────────────────────────────────────────────────────────────
// Each character cycles through random chars then snaps to the real char.
// Per-letter stagger: letter i starts at localFrame = i * staggerFrames.
// Settle time: each letter takes settleFrames to snap.

interface OdometerTextProps {
  text: string;
  localFrame: number;
  fps: number;
  fontSize: number;
  color: string;
  fontFamily?: string;
  letterSpacing?: string;
  staggerFrames?: number;
  settleFrames?: number;
}

function OdometerText({
  text,
  localFrame,
  fps,
  fontSize,
  color,
  fontFamily = FONT_TITLE,
  letterSpacing = "0.08em",
  staggerFrames = 3,
  settleFrames = 12,
}: OdometerTextProps) {
  return (
    <span style={{ display: "inline-flex", gap: 0 }}>
      {text.split("").map((char, i) => {
        if (char === " ") {
          return (
            <span key={i} style={{ fontSize, fontFamily, color, letterSpacing, display: "inline-block", width: "0.4em" }}>
              &nbsp;
            </span>
          );
        }

        const letterStart = i * staggerFrames;
        const letterSettle = letterStart + settleFrames;
        const isSettled = localFrame >= letterSettle;
        const isActive = localFrame >= letterStart;

        let displayChar = char;
        if (!isActive) {
          displayChar = " ";
        } else if (!isSettled) {
          // Cycle through odometer characters deterministically
          const cycleIndex = Math.floor((localFrame - letterStart) * 2.5) % ODOMETER_CHARS.length;
          const seed = i * 100 + cycleIndex;
          const charIndex = Math.floor(random(seed) * ODOMETER_CHARS.length);
          displayChar = ODOMETER_CHARS[charIndex];
        }

        // Glow burst on settle frame
        const glowProgress = isSettled
          ? Math.max(0, 1 - (localFrame - letterSettle) / (fps * 0.5))
          : 0;
        const glowOpacity = glowProgress * 0.8;

        return (
          <span
            key={i}
            style={{
              display: "inline-block",
              fontSize,
              fontFamily,
              fontWeight: 900,
              color,
              letterSpacing,
              textShadow: glowProgress > 0
                ? `0 0 ${10 + glowProgress * 30}px rgba(138,250,71,${glowOpacity}), 0 0 ${40 + glowProgress * 60}px rgba(138,250,71,${glowOpacity * 0.5})`
                : undefined,
              lineHeight: 1,
            }}
          >
            {displayChar}
          </span>
        );
      })}
    </span>
  );
}

// ─── Callout ──────────────────────────────────────────────────────────────────
// Center-screen by default. Odometer letter reveal. Scale punch in.

function CalloutOverlay({
  data,
  startS,
  durationS,
}: {
  data: CalloutOverlayData;
  startS: number;
  durationS: number;
}) {
  const { opacity, visible, localFrame, fps } = useVisibility(startS, durationS);
  if (!visible && opacity === 0) return null;

  const pos = data.position ?? "center";

  const scaleIn = spring({
    frame: localFrame,
    fps,
    config: { damping: 16, stiffness: 130, mass: 0.7 },
    from: 0.82,
    to: 1,
  });

  const posStyle: React.CSSProperties =
    pos === "center"
      ? { top: "50%", left: "50%", transform: `translate(-50%, -50%) scale(${scaleIn})` }
      : pos === "top"
      ? { top: 100, left: "50%", transform: `translateX(-50%) scale(${scaleIn})` }
      : { bottom: 110, left: "50%", transform: `translateX(-50%) scale(${scaleIn})` };

  return (
    <div
      style={{
        position: "absolute",
        opacity,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 12,
        pointerEvents: "none",
        ...posStyle,
      }}
    >
      {/* Main text — odometer reveal */}
      <div style={{ textAlign: "center" }}>
        <OdometerText
          text={data.text}
          localFrame={localFrame}
          fps={fps}
          fontSize={84}
          color={GREEN}
          letterSpacing="0.08em"
        />
      </div>
      {/* Accent bar below text */}
      <div
        style={{
          width: 80,
          height: 3,
          backgroundColor: GREEN,
          boxShadow: `0 0 14px ${GREEN}, 0 0 28px rgba(138,250,71,0.4)`,
          borderRadius: 2,
        }}
      />
      {/* Subtext */}
      {data.subtext && (
        <div
          style={{
            fontSize: 26,
            fontFamily: FONT_BODY,
            fontWeight: 600,
            color: "rgba(255,255,255,0.88)",
            letterSpacing: "0.13em",
            textTransform: "uppercase",
            textShadow: "0 2px 12px rgba(0,0,0,0.9)",
            textAlign: "center",
            maxWidth: 700,
          }}
        >
          {data.subtext}
        </div>
      )}
    </div>
  );
}

// ─── Species Card ─────────────────────────────────────────────────────────────
// Center-bottom. Green accent bar. Name in Bebas, scientific in italic Montserrat.

function SpeciesCard({
  data,
  startS,
  durationS,
}: {
  data: SpeciesOverlayData;
  startS: number;
  durationS: number;
}) {
  const { opacity, visible, localFrame, fps } = useVisibility(startS, durationS);
  const { width } = useVideoConfig();

  if (!visible && opacity === 0) return null;

  const slideY = interpolate(localFrame, [0, 14], [28, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const pos = data.position ?? "bottom";

  return (
    <div
      style={{
        position: "absolute",
        ...(pos === "bottom" ? { bottom: 90 } : pos === "top" ? { top: 90 } : { top: "50%", marginTop: -60 }),
        left: "50%",
        transform: `translateX(-50%) translateY(${slideY}px)`,
        opacity,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 8,
        minWidth: 460,
        maxWidth: width * 0.7,
        pointerEvents: "none",
      }}
    >
      <div
        style={{
          width: 60,
          height: 3,
          backgroundColor: GREEN,
          boxShadow: `0 0 12px ${GREEN}, 0 0 24px rgba(138,250,71,0.4)`,
          borderRadius: 2,
          marginBottom: 4,
        }}
      />
      <div
        style={{
          fontSize: 44,
          fontFamily: FONT_TITLE,
          fontWeight: 900,
          color: WHITE,
          letterSpacing: "0.06em",
          textAlign: "center",
          textShadow: "0 2px 20px rgba(0,0,0,0.95), 0 0 40px rgba(0,0,0,0.8)",
          lineHeight: 1,
          textTransform: "uppercase",
        }}
      >
        {data.name}
      </div>
      <div
        style={{
          fontSize: 22,
          fontFamily: FONT_BODY,
          fontWeight: 500,
          fontStyle: "italic",
          color: GREEN,
          letterSpacing: "0.04em",
          textAlign: "center",
          textShadow: "0 2px 12px rgba(0,0,0,0.9)",
          opacity: 0.92,
        }}
      >
        {data.scientific}
      </div>
      {data.fact && (
        <div
          style={{
            fontSize: 18,
            fontFamily: FONT_BODY,
            fontWeight: 400,
            color: "rgba(255,255,255,0.75)",
            letterSpacing: "0.08em",
            textAlign: "center",
            textShadow: "0 2px 8px rgba(0,0,0,0.9)",
            textTransform: "uppercase",
            marginTop: 2,
          }}
        >
          {data.fact}
        </div>
      )}
    </div>
  );
}

// ─── Fact Flash ───────────────────────────────────────────────────────────────
// White bold text, center or bottom. Scale punch.

function FactFlash({
  data,
  startS,
  durationS,
}: {
  data: FactFlashData;
  startS: number;
  durationS: number;
}) {
  const { opacity, visible, localFrame } = useVisibility(startS, durationS);
  const { fps } = useVideoConfig();

  if (!visible && opacity === 0) return null;
  const atBottom = (data.position ?? "bottom") === "bottom";

  const scaleIn = spring({
    frame: localFrame,
    fps,
    config: { damping: 18, stiffness: 140, mass: 0.6 },
    from: 0.9,
    to: 1,
  });

  const slideY = interpolate(localFrame, [0, 12], [20, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  return (
    <div
      style={{
        position: "absolute",
        ...(atBottom
          ? { bottom: 100, left: "50%", transform: `translateX(-50%) translateY(${slideY}px) scale(${scaleIn})` }
          : { top: "50%", left: "50%", transform: `translate(-50%, -50%) scale(${scaleIn})` }),
        opacity,
        fontSize: 32,
        fontFamily: FONT_BODY,
        fontWeight: 700,
        color: WHITE,
        letterSpacing: "0.1em",
        textTransform: "uppercase",
        textShadow: "0 2px 20px rgba(0,0,0,0.95), 0 0 40px rgba(0,0,0,0.8)",
        textAlign: "center",
        pointerEvents: "none",
        maxWidth: 900,
        whiteSpace: "pre-wrap",
      }}
    >
      {data.text}
    </div>
  );
}

// ─── Annotation ───────────────────────────────────────────────────────────────
// A line draws itself from a text label to a target point on screen.
// The endpoint glows when the line completes.

function AnnotationOverlay({
  data,
  startS,
  durationS,
}: {
  data: AnnotationData;
  startS: number;
  durationS: number;
}) {
  const { opacity, visible, localFrame, fps } = useVisibility(startS, durationS);
  const { width, height } = useVideoConfig();

  if (!visible && opacity === 0) return null;

  // Line draws over the first 18 frames
  const drawProgress = interpolate(localFrame, [0, 18], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.quad),
  });

  // Glow pulse at endpoint after line completes
  const glowScale = spring({
    frame: Math.max(0, localFrame - 20),
    fps,
    config: { damping: 14, stiffness: 120, mass: 0.5 },
    from: 0,
    to: 1,
  });

  // Endpoint glow breathe
  const glowBreathe = interpolate(
    localFrame,
    [20, 50, 80],
    [0.5, 1, 0.5],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const targetX = data.targetXPct * width;
  const targetY = data.targetYPct * height;

  // Label positioned offset from target (left and up by default)
  const labelX = targetX - 220;
  const labelY = targetY - 70;

  // Line goes from label anchor to target
  const lineStartX = labelX + 160;
  const lineStartY = labelY + 20;

  // Current endpoint based on draw progress
  const currentEndX = lineStartX + (targetX - lineStartX) * drawProgress;
  const currentEndY = lineStartY + (targetY - lineStartY) * drawProgress;

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        opacity,
        pointerEvents: "none",
      }}
    >
      {/* SVG line */}
      <svg
        style={{ position: "absolute", inset: 0 }}
        width={width}
        height={height}
      >
        <defs>
          <filter id="annotation-glow">
            <feGaussianBlur stdDeviation="2" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        {/* Main line */}
        <line
          x1={lineStartX}
          y1={lineStartY}
          x2={currentEndX}
          y2={currentEndY}
          stroke={GREEN}
          strokeWidth={1.5}
          opacity={0.9}
          filter="url(#annotation-glow)"
        />
        {/* Dot at start */}
        <circle cx={lineStartX} cy={lineStartY} r={3} fill={GREEN} opacity={0.8} />
        {/* Glow circle at endpoint (appears when line completes) */}
        {drawProgress >= 0.95 && (
          <>
            {/* Outer glow ring */}
            <circle
              cx={targetX}
              cy={targetY}
              r={14 * glowScale}
              fill="none"
              stroke={GREEN}
              strokeWidth={1}
              opacity={0.3 * glowBreathe}
            />
            {/* Middle ring */}
            <circle
              cx={targetX}
              cy={targetY}
              r={8 * glowScale}
              fill="none"
              stroke={GREEN}
              strokeWidth={1.5}
              opacity={0.55 * glowBreathe}
            />
            {/* Core dot */}
            <circle
              cx={targetX}
              cy={targetY}
              r={3 * glowScale}
              fill={GREEN}
              opacity={0.9 * glowBreathe}
              filter="url(#annotation-glow)"
            />
          </>
        )}
      </svg>

      {/* Label text */}
      <div
        style={{
          position: "absolute",
          left: labelX,
          top: labelY,
          opacity: interpolate(localFrame, [0, 8], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
          fontSize: 18,
          fontFamily: FONT_BODY,
          fontWeight: 600,
          color: WHITE,
          letterSpacing: "0.06em",
          textTransform: "uppercase",
          textShadow: "0 2px 10px rgba(0,0,0,0.95)",
          whiteSpace: "nowrap",
          borderLeft: `2px solid ${GREEN}`,
          paddingLeft: 10,
        }}
      >
        {data.label}
      </div>
    </div>
  );
}

// ─── SceneOverlays ────────────────────────────────────────────────────────────

interface SceneOverlaysProps {
  overlays: TimedOverlay[];
}

export const SceneOverlays: React.FC<SceneOverlaysProps> = ({ overlays }) => (
  <>
    {overlays.map((o, i) => {
      if (o.data.type === "species") {
        return <SpeciesCard key={i} data={o.data} startS={o.startS} durationS={o.durationS} />;
      }
      if (o.data.type === "callout") {
        return <CalloutOverlay key={i} data={o.data} startS={o.startS} durationS={o.durationS} />;
      }
      if (o.data.type === "annotation") {
        return <AnnotationOverlay key={i} data={o.data} startS={o.startS} durationS={o.durationS} />;
      }
      return <FactFlash key={i} data={o.data as FactFlashData} startS={o.startS} durationS={o.durationS} />;
    })}
  </>
);
