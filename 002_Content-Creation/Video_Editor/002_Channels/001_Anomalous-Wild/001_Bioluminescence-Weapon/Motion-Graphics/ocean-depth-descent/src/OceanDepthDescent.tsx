import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Easing,
} from "remotion";

const TOTAL_FRAMES = 360;
const CAM_TRAVEL = 2200; // total px scrolled across the virtual world

// World-space Y positions of depth markers in the scrolling layer
const MARKER_200M_Y = 400;
const MARKER_1000M_Y = 1200;

// Frame at which each marker crosses screen center (eased travel approximation)
const FRAME_200M = Math.round((MARKER_200M_Y / CAM_TRAVEL) * TOTAL_FRAMES); // ~65
const FRAME_1000M = Math.round((MARKER_1000M_Y / CAM_TRAVEL) * TOTAL_FRAMES); // ~196

export const OceanDepthDescent: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();

  // Master scroll progress — eased inOut for cinematic feel
  const scrollProgress = interpolate(frame, [0, TOTAL_FRAMES], [0, 1], {
    easing: Easing.inOut(Easing.quad),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const scroll = scrollProgress * CAM_TRAVEL;

  // Parallax layer offsets (lower multiplier = further away = less movement)
  const bgOffset = -scroll * 0.1;
  const lightRayOffset = -scroll * 0.25;
  const terrainOffset = -scroll * 0.7;
  const markerOffset = -scroll; // 1:1 with world — locked depth lines

  // Ambient light: bright at surface, gone by 60% scroll
  const ambientLight = interpolate(scrollProgress, [0, 0.35, 0.6], [1, 0.25, 0], {
    extrapolateRight: "clamp",
  });

  // Bio particles: emerge in the deep dark
  const bioOpacity = interpolate(scrollProgress, [0.55, 0.8], [0, 0.8], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Current depth readout (0 → 1000 m)
  const currentDepthM = Math.round(scrollProgress * 1000);

  // 200m label: springs in, then fades out before 1000m label arrives
  const label200In = spring({
    frame: frame - (FRAME_200M - 12),
    fps,
    config: { damping: 200 },
  });
  const label200Out = interpolate(
    frame,
    [FRAME_200M + 60, FRAME_200M + 90],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );
  const label200Opacity = label200In * (1 - label200Out);
  const label200SlideY = interpolate(label200In, [0, 1], [24, 0]);

  // 1000m label: springs in, stays through end
  const label1000In = spring({
    frame: frame - (FRAME_1000M - 12),
    fps,
    config: { damping: 200 },
  });
  const label1000SlideY = interpolate(label1000In, [0, 1], [24, 0]);

  const svgH = height + CAM_TRAVEL + 400;

  return (
    <AbsoluteFill style={{ backgroundColor: "#010408", overflow: "hidden" }}>

      {/* ─── LAYER 1 — BACKGROUND GRADIENT ─────────────────────────── */}
      <AbsoluteFill style={{ transform: `translateY(${bgOffset}px)` }}>
        <svg width={width} height={svgH} style={{ position: "absolute", top: 0 }}>
          <defs>
            <linearGradient id="oceanGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%"   stopColor="#4AAFDF" />
              <stop offset="6%"   stopColor="#1B6B9E" />
              <stop offset="20%"  stopColor="#0D3B5E" />
              <stop offset="40%"  stopColor="#061828" />
              <stop offset="60%"  stopColor="#020C18" />
              <stop offset="100%" stopColor="#010408" />
            </linearGradient>
          </defs>
          <rect x={0} y={0} width={width} height={svgH} fill="url(#oceanGrad)" />
        </svg>
      </AbsoluteFill>

      {/* ─── LAYER 2 — SURFACE LIGHT RAYS ───────────────────────────── */}
      <AbsoluteFill
        style={{
          transform: `translateY(${lightRayOffset}px)`,
          opacity: ambientLight,
        }}
      >
        <svg width={width} height={height} style={{ position: "absolute", top: 0 }}>
          <defs>
            <radialGradient id="sunGlow" cx="50%" cy="-10%" r="80%">
              <stop offset="0%"   stopColor="#B8DCF0" stopOpacity="0.35" />
              <stop offset="100%" stopColor="#B8DCF0" stopOpacity="0" />
            </radialGradient>
            <linearGradient id="rayFade" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%"   stopColor="#CCEEFF" stopOpacity="0.22" />
              <stop offset="100%" stopColor="#CCEEFF" stopOpacity="0" />
            </linearGradient>
          </defs>
          <rect x={0} y={0} width={width} height={height} fill="url(#sunGlow)" />
          {(
            [
              [780, 600, 70, 300],
              [960, 920, 55, 200],
              [1100, 1160, 45, 170],
              [1260, 1310, 35, 130],
              [680, 480, 60, 260],
            ] as [number, number, number, number][]
          ).map(([x1, x2, w1, w2], i) => (
            <polygon
              key={i}
              points={`${x1},0 ${x1 + w1},0 ${x2 + w2},${height} ${x2},${height}`}
              fill="url(#rayFade)"
              opacity={0.55 - i * 0.08}
            />
          ))}
        </svg>
      </AbsoluteFill>

      {/* ─── LAYER 3 — TERRAIN (continental shelf) ──────────────────── */}
      <AbsoluteFill style={{ transform: `translateY(${terrainOffset}px)` }}>
        <svg width={width} height={height + 800} style={{ position: "absolute", top: 0 }}>
          <path
            d={`M ${width * 0.74},0 L ${width},0 L ${width},900
                C ${width * 0.92},820 ${width * 0.86},750 ${width * 0.8},680
                C ${width * 0.76},630 ${width * 0.74},600 ${width * 0.74},560 Z`}
            fill="#112218"
            opacity={0.9}
          />
          <path
            d={`M ${width * 0.78},0 L ${width},0 L ${width},700
                C ${width * 0.94},650 ${width * 0.88},590 ${width * 0.82},540
                L ${width * 0.78},500 Z`}
            fill="#0D1B13"
            opacity={0.95}
          />
        </svg>
      </AbsoluteFill>

      {/* ─── LAYER 4 — DEPTH MARKER LINES (world-locked) ────────────── */}
      <AbsoluteFill style={{ transform: `translateY(${markerOffset}px)` }}>
        <svg
          width={width}
          height={height + CAM_TRAVEL + 200}
          style={{ position: "absolute", top: 0 }}
        >
          {/* 200 m dashed line */}
          <line
            x1={0} y1={MARKER_200M_Y}
            x2={width * 0.55} y2={MARKER_200M_Y}
            stroke="#5BC0E8" strokeWidth={1.5}
            strokeDasharray="14 8" opacity={0.55}
          />
          {/* 200 m descending arrow */}
          <polygon
            points={`
              ${width * 0.06 - 8},${MARKER_200M_Y - 10}
              ${width * 0.06 + 8},${MARKER_200M_Y - 10}
              ${width * 0.06},${MARKER_200M_Y + 6}
            `}
            fill="#5BC0E8" opacity={0.75}
          />

          {/* 1000 m dashed line */}
          <line
            x1={0} y1={MARKER_1000M_Y}
            x2={width * 0.55} y2={MARKER_1000M_Y}
            stroke="#3A8FBF" strokeWidth={1.5}
            strokeDasharray="14 8" opacity={0.45}
          />
          {/* 1000 m descending arrow */}
          <polygon
            points={`
              ${width * 0.06 - 8},${MARKER_1000M_Y - 10}
              ${width * 0.06 + 8},${MARKER_1000M_Y - 10}
              ${width * 0.06},${MARKER_1000M_Y + 6}
            `}
            fill="#3A8FBF" opacity={0.65}
          />
        </svg>
      </AbsoluteFill>

      {/* ─── LAYER 5 — 200 m LABEL ──────────────────────────────────── */}
      <AbsoluteFill
        style={{
          opacity: label200Opacity,
          transform: `translateY(${label200SlideY}px)`,
        }}
      >
        <div
          style={{
            position: "absolute",
            left: 120,
            top: "50%",
            transform: "translateY(-50%)",
          }}
        >
          <div
            style={{
              fontSize: 16,
              letterSpacing: "0.32em",
              color: "#5BC0E8",
              fontFamily: "Arial, sans-serif",
              fontWeight: 300,
              textTransform: "uppercase",
              marginBottom: 10,
            }}
          >
            200 m
          </div>
          <div
            style={{
              fontSize: 44,
              fontWeight: 700,
              fontFamily: "Georgia, serif",
              letterSpacing: "0.03em",
              color: "#FFFFFF",
              lineHeight: 1.25,
            }}
          >
            Sunlight
            <br />
            disappears.
          </div>
          <div
            style={{
              width: 52,
              height: 2,
              backgroundColor: "#5BC0E8",
              marginTop: 16,
              opacity: 0.7,
            }}
          />
        </div>
      </AbsoluteFill>

      {/* ─── LAYER 6 — 1000 m LABEL ─────────────────────────────────── */}
      <AbsoluteFill
        style={{
          opacity: label1000In,
          transform: `translateY(${label1000SlideY}px)`,
        }}
      >
        <div
          style={{
            position: "absolute",
            left: 120,
            top: "50%",
            transform: "translateY(-50%)",
          }}
        >
          <div
            style={{
              fontSize: 16,
              letterSpacing: "0.32em",
              color: "#3A9FD0",
              fontFamily: "Arial, sans-serif",
              fontWeight: 300,
              textTransform: "uppercase",
              marginBottom: 10,
            }}
          >
            1,000 m
          </div>
          <div
            style={{
              fontSize: 44,
              fontWeight: 700,
              fontFamily: "Georgia, serif",
              letterSpacing: "0.03em",
              color: "#FFFFFF",
              lineHeight: 1.25,
            }}
          >
            No sunlight.
            <br />
            Ever.
          </div>
          <div
            style={{
              width: 52,
              height: 2,
              backgroundColor: "#3A9FD0",
              marginTop: 16,
              opacity: 0.7,
            }}
          />
        </div>
      </AbsoluteFill>

      {/* ─── LAYER 7 — DEPTH HUD (right side) ──────────────────────── */}
      <AbsoluteFill>
        <div
          style={{
            position: "absolute",
            right: 80,
            top: "50%",
            transform: "translateY(-50%)",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 10,
          }}
        >
          <div
            style={{
              fontSize: 10,
              letterSpacing: "0.28em",
              color: "rgba(255,255,255,0.28)",
              fontFamily: "Arial, sans-serif",
              textTransform: "uppercase",
            }}
          >
            Depth
          </div>

          {/* Vertical track */}
          <div
            style={{
              width: 2,
              height: 220,
              backgroundColor: "rgba(255,255,255,0.1)",
              borderRadius: 2,
              position: "relative",
            }}
          >
            {/* 200 m tick on track */}
            <div
              style={{
                position: "absolute",
                left: -5,
                top: "20%",
                width: 12,
                height: 1,
                backgroundColor: "#5BC0E8",
                opacity: 0.45,
              }}
            />
            {/* 1000 m tick on track */}
            <div
              style={{
                position: "absolute",
                left: -5,
                top: "100%",
                width: 12,
                height: 1,
                backgroundColor: "#3A8FBF",
                opacity: 0.38,
              }}
            />
            {/* Moving indicator */}
            <div
              style={{
                position: "absolute",
                left: -5,
                top: `${Math.min(scrollProgress * 100, 100)}%`,
                width: 12,
                height: 12,
                borderRadius: "50%",
                backgroundColor: "#5BC0E8",
                boxShadow: "0 0 10px 3px rgba(91,192,232,0.5)",
                transform: "translate(-25%, -50%)",
              }}
            />
          </div>

          {/* Depth counter */}
          <div
            style={{
              fontSize: 14,
              letterSpacing: "0.1em",
              color: "rgba(91,192,232,0.65)",
              fontFamily: "'Courier New', monospace",
              fontWeight: 700,
            }}
          >
            {currentDepthM}m
          </div>
        </div>
      </AbsoluteFill>

      {/* ─── LAYER 8 — BIOLUMINESCENT PARTICLES ─────────────────────── */}
      <AbsoluteFill style={{ opacity: bioOpacity }}>
        {(
          [
            [0.14, 0.32, 3, 0],
            [0.38, 0.58, 2, 22],
            [0.62, 0.42, 4, 8],
            [0.22, 0.72, 2, 37],
            [0.5,  0.2,  3, 14],
            [0.74, 0.62, 2, 28],
            [0.32, 0.5,  3, 19],
            [0.58, 0.78, 2, 6],
            [0.84, 0.38, 4, 33],
            [0.08, 0.55, 2, 11],
            [0.46, 0.85, 3, 44],
            [0.9,  0.25, 2, 17],
          ] as [number, number, number, number][]
        ).map(([x, y, size, delay], i) => {
          const pulse = interpolate(
            (frame + delay * 8) % 70,
            [0, 35, 70],
            [0.25, 1, 0.25],
          );
          return (
            <div
              key={i}
              style={{
                position: "absolute",
                left: `${x * 100}%`,
                top: `${y * 100}%`,
                width: size * 2,
                height: size * 2,
                borderRadius: "50%",
                backgroundColor: "#4ABADF",
                boxShadow: `0 0 ${size * 5}px ${size * 2}px rgba(74,186,223,0.35)`,
                opacity: pulse,
              }}
            />
          );
        })}
      </AbsoluteFill>

      {/* ─── LAYER 9 — VIGNETTE ─────────────────────────────────────── */}
      <AbsoluteFill style={{ pointerEvents: "none" }}>
        <svg
          width={width}
          height={height}
          style={{ position: "absolute", top: 0, left: 0 }}
        >
          <defs>
            <radialGradient id="vignette" cx="50%" cy="50%" r="70%">
              <stop offset="55%"  stopColor="black" stopOpacity="0" />
              <stop offset="100%" stopColor="black" stopOpacity="0.72" />
            </radialGradient>
          </defs>
          <rect x={0} y={0} width={width} height={height} fill="url(#vignette)" />
        </svg>
      </AbsoluteFill>

    </AbsoluteFill>
  );
};
