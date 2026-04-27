import React from "react";
import {
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Easing,
} from "remotion";

// ─── Tree Structure ────────────────────────────────────────────────────────────
// SVG-based phylogenetic tree of life. Branches draw themselves via strokeDashoffset.
// Bioluminescent nodes flash across unrelated branches — 40+ independent evolutions.
// No text baked into any asset — labels and callouts are Remotion components.

const GREEN = "#8AFA47";
const BRANCH_COLOR = "rgba(255,255,255,0.12)";

// ─── Branch definitions ────────────────────────────────────────────────────────
// Each branch: [x1,y1,x2,y2] normalised 0–1 of SVG viewbox.
// Drawn in timed waves: branches in the same wave appear together.

const BRANCHES = [
  // Trunk
  { id: "trunk", x1: 0.5, y1: 0.92, x2: 0.5, y2: 0.55, wave: 0 },
  // Level 1 splits
  { id: "b1l", x1: 0.5, y1: 0.55, x2: 0.22, y2: 0.35, wave: 1 },
  { id: "b1r", x1: 0.5, y1: 0.55, x2: 0.78, y2: 0.35, wave: 1 },
  // Level 2 splits
  { id: "b2ll", x1: 0.22, y1: 0.35, x2: 0.1,  y2: 0.18, wave: 2 },
  { id: "b2lm", x1: 0.22, y1: 0.35, x2: 0.25, y2: 0.18, wave: 2 },
  { id: "b2lmr",x1: 0.22, y1: 0.35, x2: 0.37, y2: 0.22, wave: 2 },
  { id: "b2rl", x1: 0.78, y1: 0.35, x2: 0.63, y2: 0.22, wave: 2 },
  { id: "b2rm", x1: 0.78, y1: 0.35, x2: 0.75, y2: 0.18, wave: 2 },
  { id: "b2rr", x1: 0.78, y1: 0.35, x2: 0.9,  y2: 0.18, wave: 2 },
  // Level 3 — tips
  { id: "t1",  x1: 0.1,  y1: 0.18, x2: 0.06, y2: 0.07, wave: 3 },
  { id: "t2",  x1: 0.1,  y1: 0.18, x2: 0.13, y2: 0.07, wave: 3 },
  { id: "t3",  x1: 0.25, y1: 0.18, x2: 0.2,  y2: 0.07, wave: 3 },
  { id: "t4",  x1: 0.25, y1: 0.18, x2: 0.28, y2: 0.07, wave: 3 },
  { id: "t5",  x1: 0.37, y1: 0.22, x2: 0.33, y2: 0.08, wave: 3 },
  { id: "t6",  x1: 0.37, y1: 0.22, x2: 0.4,  y2: 0.08, wave: 3 },
  { id: "t7",  x1: 0.63, y1: 0.22, x2: 0.59, y2: 0.08, wave: 3 },
  { id: "t8",  x1: 0.63, y1: 0.22, x2: 0.65, y2: 0.08, wave: 3 },
  { id: "t9",  x1: 0.75, y1: 0.18, x2: 0.71, y2: 0.07, wave: 3 },
  { id: "t10", x1: 0.75, y1: 0.18, x2: 0.78, y2: 0.07, wave: 3 },
  { id: "t11", x1: 0.9,  y1: 0.18, x2: 0.87, y2: 0.07, wave: 3 },
  { id: "t12", x1: 0.9,  y1: 0.18, x2: 0.93, y2: 0.07, wave: 3 },
  // Extra branches for density
  { id: "e1",  x1: 0.5,  y1: 0.68, x2: 0.5,  y2: 0.55, wave: 1 },
  { id: "e2",  x1: 0.5,  y1: 0.68, x2: 0.44, y2: 0.48, wave: 2 },
  { id: "e3",  x1: 0.5,  y1: 0.68, x2: 0.56, y2: 0.48, wave: 2 },
  { id: "e4",  x1: 0.44, y1: 0.48, x2: 0.41, y2: 0.32, wave: 3 },
  { id: "e5",  x1: 0.56, y1: 0.48, x2: 0.59, y2: 0.32, wave: 3 },
];

// ─── Node definitions ─────────────────────────────────────────────────────────
// Each node: tip of a branch where bioluminescence evolved independently.
// Spread across unrelated lineages — that is the point.

const NODES = [
  { x: 0.06, y: 0.07 }, { x: 0.13, y: 0.07 },
  { x: 0.2,  y: 0.07 }, { x: 0.28, y: 0.07 },
  { x: 0.33, y: 0.08 }, { x: 0.4,  y: 0.08 },
  { x: 0.59, y: 0.08 }, { x: 0.65, y: 0.08 },
  { x: 0.71, y: 0.07 }, { x: 0.78, y: 0.07 },
  { x: 0.87, y: 0.07 }, { x: 0.93, y: 0.07 },
  // Mid-branch nodes (scattered — not at tips)
  { x: 0.1,  y: 0.18 }, { x: 0.25, y: 0.18 },
  { x: 0.37, y: 0.22 }, { x: 0.63, y: 0.22 },
  { x: 0.75, y: 0.18 }, { x: 0.9,  y: 0.18 },
  { x: 0.22, y: 0.35 }, { x: 0.78, y: 0.35 },
  { x: 0.41, y: 0.32 }, { x: 0.59, y: 0.32 },
  // Deep trunk nodes (rare deep-sea lineages)
  { x: 0.5,  y: 0.62 }, { x: 0.44, y: 0.48 },
  { x: 0.56, y: 0.48 },
  // Additional scattered nodes to reach 40+
  { x: 0.16, y: 0.13 }, { x: 0.31, y: 0.15 },
  { x: 0.46, y: 0.14 }, { x: 0.53, y: 0.14 },
  { x: 0.69, y: 0.15 }, { x: 0.83, y: 0.13 },
  { x: 0.08, y: 0.25 }, { x: 0.32, y: 0.3  },
  { x: 0.5,  y: 0.42 }, { x: 0.68, y: 0.3  },
  { x: 0.92, y: 0.25 }, { x: 0.19, y: 0.42 },
  { x: 0.81, y: 0.42 }, { x: 0.5,  y: 0.78 },
  { x: 0.35, y: 0.6  }, { x: 0.65, y: 0.6  },
];

// Timing constants (in seconds)
const WAVE_STARTS = [0, 1.5, 3.5, 5.5];  // when each branch wave starts drawing
const BRANCH_DRAW_S = 1.2;                // seconds to draw a single branch
const NODE_FLASH_START_S = 8;             // when nodes start flashing
const NODE_STAGGER_S = 0.45;              // seconds between each node flash
const NODE_FLASH_DURATION_S = 1.2;        // how long each node holds glow
const COUNTER_START_S = 28;               // when the "40+" counter appears

export const PhylogeneticTree: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const W = width;
  const H = height;

  // ── Branch draw progress ──────────────────────────────────────────────────
  function branchProgress(wave: number): number {
    const startFrame = WAVE_STARTS[wave] * fps;
    const endFrame = startFrame + BRANCH_DRAW_S * fps;
    return interpolate(frame, [startFrame, endFrame], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.out(Easing.cubic),
    });
  }

  const waveProgress = [0, 1, 2, 3].map(branchProgress);

  // ── Node flash ────────────────────────────────────────────────────────────
  function nodeGlow(nodeIndex: number): number {
    const startFrame = (NODE_FLASH_START_S + nodeIndex * NODE_STAGGER_S) * fps;
    const peakFrame  = startFrame + 0.2 * fps;
    const endFrame   = startFrame + NODE_FLASH_DURATION_S * fps;
    return interpolate(
      frame,
      [startFrame, peakFrame, endFrame, endFrame + fps * 0.5],
      [0, 1, 0.55, 0.2],
      { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
    );
  }

  // ── "40+" counter odometer ────────────────────────────────────────────────
  const counterStart = COUNTER_START_S * fps;
  const counterOpacity = interpolate(frame, [counterStart, counterStart + 10], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const counterScale = spring({
    frame: frame - counterStart,
    fps,
    config: { damping: 14, stiffness: 120, mass: 0.6 },
    from: 0.7,
    to: 1,
  });

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div style={{ width: W, height: H, position: "relative", backgroundColor: "#000510", overflow: "hidden" }}>

      {/* Subtle background gradient — deep ocean feel */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "radial-gradient(ellipse at 50% 90%, rgba(76,248,255,0.04) 0%, transparent 65%)",
          pointerEvents: "none",
        }}
      />

      {/* SVG Tree */}
      <svg
        style={{ position: "absolute", inset: 0 }}
        viewBox={`0 0 ${W} ${H}`}
        width={W}
        height={H}
      >
        <defs>
          <filter id="node-glow" x="-100%" y="-100%" width="300%" height="300%">
            <feGaussianBlur stdDeviation="6" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <filter id="line-glow" x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur stdDeviation="1.5" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Branches */}
        {BRANCHES.map((b) => {
          const prog = waveProgress[b.wave];
          const x1 = b.x1 * W;
          const y1 = b.y1 * H;
          const x2 = b.x2 * W;
          const y2 = b.y2 * H;
          const curEndX = x1 + (x2 - x1) * prog;
          const curEndY = y1 + (y2 - y1) * prog;

          if (prog <= 0) return null;

          return (
            <line
              key={b.id}
              x1={x1} y1={y1}
              x2={curEndX} y2={curEndY}
              stroke={BRANCH_COLOR}
              strokeWidth={1.5}
              filter="url(#line-glow)"
            />
          );
        })}

        {/* Nodes */}
        {NODES.map((n, i) => {
          const glow = nodeGlow(i);
          if (glow <= 0) return null;
          const nx = n.x * W;
          const ny = n.y * H;
          const r = 4 + glow * 4;

          return (
            <g key={i} filter="url(#node-glow)">
              {/* Outer glow ring */}
              <circle cx={nx} cy={ny} r={r * 2.5} fill="none" stroke={GREEN} strokeWidth={0.8} opacity={glow * 0.25} />
              {/* Mid ring */}
              <circle cx={nx} cy={ny} r={r * 1.5} fill="none" stroke={GREEN} strokeWidth={1} opacity={glow * 0.5} />
              {/* Core */}
              <circle cx={nx} cy={ny} r={r} fill={GREEN} opacity={glow * 0.9} />
            </g>
          );
        })}
      </svg>

      {/* "40+" counter — center-bottom */}
      <div
        style={{
          position: "absolute",
          bottom: 120,
          left: "50%",
          transform: `translateX(-50%) scale(${counterScale})`,
          opacity: counterOpacity,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 10,
          pointerEvents: "none",
        }}
      >
        <div
          style={{
            fontSize: 110,
            fontFamily: "'Bebas Neue', Impact, Arial, sans-serif",
            fontWeight: 900,
            color: GREEN,
            letterSpacing: "0.06em",
            lineHeight: 1,
            textShadow: `0 0 30px ${GREEN}, 0 0 60px rgba(138,250,71,0.4), 0 4px 20px rgba(0,0,0,0.95)`,
          }}
        >
          40+
        </div>
        <div
          style={{
            fontSize: 24,
            fontFamily: "'Montserrat', Arial, sans-serif",
            fontWeight: 600,
            color: "rgba(255,255,255,0.85)",
            letterSpacing: "0.2em",
            textTransform: "uppercase",
            textShadow: "0 2px 12px rgba(0,0,0,0.9)",
            textAlign: "center",
          }}
        >
          INDEPENDENT EVOLUTIONS
        </div>
      </div>
    </div>
  );
};
