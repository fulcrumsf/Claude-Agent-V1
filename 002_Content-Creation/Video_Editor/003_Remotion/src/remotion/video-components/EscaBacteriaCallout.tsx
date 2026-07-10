import {
  AbsoluteFill,
  Img,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Easing,
} from "remotion";

// ─── Esca / Bacteria Callout ────────────────────────────────────────────────
// Standalone 5s motion-graphics insert for the anglerfish esca beat
// ("...produce that light itself. The esca glows because it is filled with
// living bacteria"). Renders as its own clip — no narration/audio — for
// manual placement in Premiere at ~2:32.
//
// Styling is intentionally NOT the channel's neon-green brand accent.
// This is a labeled scientific diagram, not channel chrome (logo/thumbnail/
// lower-third), so the color comes from the image itself: (19,245,251) /
// (4,249,254) sampled directly from the glow cluster in Fish-01.png — plus
// white label text on the image's own black background, matching the
// contrast style shown in the Fish-02 reference.

export const ESCA_CALLOUT_DURATION_FRAMES = 150; // 5s @ 30fps

const IMAGE_CYAN = "#13F5FB"; // sampled from Fish-01.png glow cluster
const WHITE = "#FFFFFF";
const FONT_BODY = "'Montserrat', Arial, sans-serif";

interface CalloutSpec {
  label: string;
  targetXPct: number;
  targetYPct: number;
  labelXPct: number; // label anchor lives in open black space, not on the subject
  labelYPct: number;
  startFrame: number;
}

// Layout mirrors the Fish-02 reference: dot on the subject, line runs OUT to
// open black space, label sits fully off the fish (never overlapping the
// glow or the body). One label from above, one from below, so the two lines
// approach the cluster from opposite directions and never cross.
const CALLOUTS: CalloutSpec[] = [
  {
    label: "ESCA",
    targetXPct: 0.55,
    targetYPct: 0.42,
    labelXPct: 0.62,
    labelYPct: 0.08, // open black space up and to the right of the dot
    startFrame: 9, // 0.3s — lands on the pause after "...produce that light itself"
  },
  {
    label: "BIOLUMINESCENT BACTERIA",
    targetXPct: 0.50,
    targetYPct: 0.58,
    labelXPct: 0.17,
    labelYPct: 0.90, // open black space down and to the far left of the dot
    startFrame: 69, // 2.3s — lands on "...filled with living bacteria"
  },
];

function AnnotationCallout({ spec }: { spec: CalloutSpec }) {
  const frame = useCurrentFrame();
  const { width, height, fps } = useVideoConfig();
  const localFrame = frame - spec.startFrame;

  if (localFrame < 0) return null;

  // Leader line draws in over 20 frames, eased out
  const drawProgress = interpolate(localFrame, [0, 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.quad),
  });

  // Label phases in: opacity ramps AND a blur-glow resolves from soft to sharp,
  // so the eye is drawn to the word materializing rather than a flat pop-in.
  const textOpacity = interpolate(localFrame, [4, 18], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const textBlur = interpolate(localFrame, [4, 22], [10, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.quad),
  });
  const textGlowOpacity = interpolate(localFrame, [4, 22, 40], [0.9, 0.55, 0.35], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Pulse beat: scale springs past 1.0 then settles back — the "reads bigger,
  // then eases down to resting size" beat. Brightness rides the same curve
  // so the glow peaks exactly when the scale peaks, not on a separate clock.
  const pulseScale = spring({
    frame: Math.max(0, localFrame - 4),
    fps,
    config: { damping: 9, stiffness: 140, mass: 0.6 },
    from: 0.82,
    to: 1,
  });
  // Driven by frame (monotonic), timed to land on the spring's overshoot peak
  // rather than by scale value directly (a spring overshoots then settles
  // back through the same values, which isn't a valid interpolate() input range).
  const pulseGlowBoost = interpolate(localFrame, [4, 12, 24], [0, 0.7, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Endpoint glow pulse once the line completes
  const glowScale = spring({
    frame: Math.max(0, localFrame - 20),
    fps,
    config: { damping: 14, stiffness: 120, mass: 0.5 },
    from: 0,
    to: 1,
  });
  const glowBreathe = interpolate(localFrame, [20, 50, 80], [0.5, 1, 0.5], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const targetX = spec.targetXPct * width;
  const targetY = spec.targetYPct * height;
  const labelX = spec.labelXPct * width;
  const labelY = spec.labelYPct * height;

  // Line runs from the label's anchor point straight to the target dot —
  // label sits in open space, line is the only thing crossing onto the subject.
  const lineStartX = labelX;
  const lineStartY = labelY;

  const currentEndX = lineStartX + (targetX - lineStartX) * drawProgress;
  const currentEndY = lineStartY + (targetY - lineStartY) * drawProgress;

  return (
    <div style={{ position: "absolute", inset: 0, pointerEvents: "none" }}>
      <svg style={{ position: "absolute", inset: 0 }} width={width} height={height}>
        <defs>
          <filter id={`glow-${spec.label}`}>
            <feGaussianBlur stdDeviation="2.2" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        <line
          x1={lineStartX}
          y1={lineStartY}
          x2={currentEndX}
          y2={currentEndY}
          stroke={IMAGE_CYAN}
          strokeWidth={1.5}
          opacity={0.9}
          filter={`url(#glow-${spec.label})`}
        />
        <circle cx={lineStartX} cy={lineStartY} r={3} fill={IMAGE_CYAN} opacity={0.8} />
        {drawProgress >= 0.95 && (
          <>
            <circle
              cx={targetX}
              cy={targetY}
              r={14 * glowScale}
              fill="none"
              stroke={IMAGE_CYAN}
              strokeWidth={1}
              opacity={0.3 * glowBreathe}
            />
            <circle
              cx={targetX}
              cy={targetY}
              r={8 * glowScale}
              fill="none"
              stroke={IMAGE_CYAN}
              strokeWidth={1.5}
              opacity={0.55 * glowBreathe}
            />
            <circle
              cx={targetX}
              cy={targetY}
              r={3 * glowScale}
              fill={IMAGE_CYAN}
              opacity={0.9 * glowBreathe}
              filter={`url(#glow-${spec.label})`}
            />
          </>
        )}
      </svg>

      <div
        style={{
          position: "absolute",
          left: labelX - 160,
          top: spec.labelYPct < 0.5 ? labelY - 40 : labelY + 14,
          textAlign: "center",
          width: 320,
          opacity: textOpacity,
          filter: `blur(${textBlur}px)`,
        }}
      >
        <span
          style={{
            display: "inline-block",
            transform: `scale(${pulseScale})`,
            transformOrigin: "center",
            fontSize: 18,
            fontFamily: FONT_BODY,
            fontWeight: 600,
            color: WHITE,
            letterSpacing: "0.06em",
            textTransform: "uppercase",
            whiteSpace: "normal",
            textShadow: `0 0 ${14 + pulseGlowBoost * 10}px rgba(19,245,251,${Math.min(1, textGlowOpacity + pulseGlowBoost)}), 0 2px 10px rgba(0,0,0,0.95)`,
          }}
        >
          {spec.label}
        </span>
      </div>
    </div>
  );
}

// Soft ambient pulse over the esca cluster — synced loosely under "filled
// with living bacteria," not a hard cue, just a slow breathing highlight.
function AmbientGlow() {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const pulse = 0.10 + 0.06 * Math.sin((frame / 30) * Math.PI * 1.1);

  return (
    <div
      style={{
        position: "absolute",
        left: width * 0.5 - 260,
        top: height * 0.42 - 200,
        width: 520,
        height: 400,
        background: `radial-gradient(circle, rgba(19,245,251,${pulse}) 0%, rgba(19,245,251,0) 70%)`,
        pointerEvents: "none",
      }}
    />
  );
}

export function EscaBacteriaCallout() {
  return (
    <AbsoluteFill style={{ backgroundColor: "#000000" }}>
      <Img
        src={staticFile("bioluminescence_weapon/Images/Fish-01.png")}
        style={{ width: "100%", height: "100%", objectFit: "cover" }}
      />
      <AmbientGlow />
      {CALLOUTS.map((spec) => (
        <AnnotationCallout key={spec.label} spec={spec} />
      ))}
    </AbsoluteFill>
  );
}
