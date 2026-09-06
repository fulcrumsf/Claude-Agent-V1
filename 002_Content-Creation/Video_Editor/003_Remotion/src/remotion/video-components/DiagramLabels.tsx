// DiagramLabels.tsx
//
// Animated callout overlay for scientific-diagram beats. Rebuilt 2026-09-01 to the
// aesthetic in Reference_Examples/Label_Aesthetic_Red_Blood_Cells.png:
//   - large clean white sans-serif term
//   - optional parenthetical qualifier on its own line in an accent colour
//   - optional 2-3 line white description
//   - thin white leader line that DRAWS ON from the feature outward, ending in a dot
//   - soft glowing target ring at the feature
//   - high contrast via size + weight + a black outline/glow, no backing box needed
// Plus collision avoidance so stacked labels never overlap (Glass Frog note 6).
//
// The camera must hold STILL while any label is on screen — that is enforced in the
// diagram camera keyframes (GlassFrogDoc renderDiagramChain), not here.
import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, Easing } from "remotion";
import { z } from "zod";

export const diagramLabelsSchema = z.object({
  labels: z.array(
    z.object({
      feature: z.string(),
      x_pct: z.number().optional(),
      y_pct: z.number().optional(),
      confidence: z.enum(["high", "low", "not_found"]),
    }),
  ),
  labelStaggerS: z.number(),
  displayNames: z.record(z.string(), z.string()),
  lineColor: z.string().optional(),
  labelColor: z.string().optional(),
  labelOffsetsS: z.record(z.string(), z.number()).optional(),
  // NEW: accent colour for the parenthetical qualifier (e.g. "(awake)"); optional
  // short description shown under the term.
  accentColor: z.string().optional(),
  descriptions: z.record(z.string(), z.string()).optional(),
  // NEW: overall scale multiplier for the whole label system (default 1).
  scale: z.number().optional(),
  // NEW: how long each label stays fully visible before fading out (seconds from
  // its own start). Omit = stay visible to the end of the segment. When set, the
  // diagram camera should hold still across [start, start + labelHoldS] and only
  // move again once the label has faded (Glass Frog note 4).
  labelHoldS: z.number().optional(),
});

type DiagramLabel = z.infer<typeof diagramLabelsSchema>["labels"][number];

function hasCoordinates(label: DiagramLabel): label is DiagramLabel & { x_pct: number; y_pct: number } {
  return label.confidence !== "not_found";
}

const DEFAULT_LABEL_COLOR = "#FFFFFF";
const DEFAULT_LINE_COLOR = "rgba(255,255,255,0.95)";
const DEFAULT_ACCENT = "#FF5A4E";

// Split "Mirrored Pouch (awake)" -> { term: "Mirrored Pouch", qualifier: "awake" }
function splitTerm(text: string): { term: string; qualifier: string | null } {
  const m = text.match(/^(.*?)\s*\(([^)]+)\)\s*$/);
  if (m) return { term: m[1].trim(), qualifier: m[2].trim() };
  return { term: text, qualifier: null };
}

export const DiagramLabels: React.FC<z.infer<typeof diagramLabelsSchema>> = ({
  labels,
  labelStaggerS,
  displayNames,
  lineColor,
  labelColor,
  labelOffsetsS,
  accentColor,
  descriptions,
  scale = 1,
  labelHoldS,
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();

  const resolvedLine = lineColor ?? DEFAULT_LINE_COLOR;
  const resolvedText = labelColor ?? DEFAULT_LABEL_COLOR;
  const resolvedAccent = accentColor ?? DEFAULT_ACCENT;

  const S = scale;
  const TERM_SIZE = 40 * S;
  const QUAL_SIZE = 24 * S;
  const DESC_SIZE = 21 * S;
  const LEADER_LEN = 150 * S; // horizontal run of the leader line
  const RISE = 70 * S; // vertical rise of the leader line
  const DOT_CORE = 8 * S;
  const DOT_RING = 20 * S;
  const LINE_W = 3 * S;
  const MIN_GAP = 64 * S; // minimum vertical spacing between stacked label anchors

  const visibleLabels = labels
    .filter(hasCoordinates)
    .map((label, i) => {
      const startS = labelOffsetsS?.[label.feature] ?? i * labelStaggerS;
      const x = (label.x_pct / 100) * width;
      const y = (label.y_pct / 100) * height;
      // Label block goes to whichever side has more room; default right/up.
      const toLeft = x > width * 0.62;
      return { label, i, startS, x, y, toLeft };
    })
    // Collision avoidance: process top-to-bottom, push each label block's Y down
    // so blocks keep MIN_GAP between them. Only the text block moves — the leader
    // still targets the true (x, y).
    .sort((a, b) => a.y - b.y);

  let lastBlockY = -Infinity;
  const placed = visibleLabels.map((v) => {
    let blockY = v.y - RISE;
    if (blockY - lastBlockY < MIN_GAP) blockY = lastBlockY + MIN_GAP;
    lastBlockY = blockY;
    const blockX = v.toLeft ? v.x - LEADER_LEN : v.x + LEADER_LEN;
    return { ...v, blockX, blockY };
  });

  return (
    <AbsoluteFill>
      <svg width={width} height={height} style={{ position: "absolute", top: 0, left: 0 }}>
        <defs>
          <filter id="dl-glow" x="-60%" y="-60%" width="220%" height="220%">
            <feDropShadow dx="0" dy="0" stdDeviation={4 * S} floodColor="#000000" floodOpacity="0.9" />
          </filter>
          <filter id="dl-dotglow" x="-150%" y="-150%" width="400%" height="400%">
            <feGaussianBlur stdDeviation={5 * S} result="b" />
            <feMerge>
              <feMergeNode in="b" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {placed.map((v) => {
          const drawIn = interpolate(frame, [v.startS * fps, v.startS * fps + fps * 0.45], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.out(Easing.cubic),
          });
          const textIn = interpolate(
            frame,
            [v.startS * fps + fps * 0.3, v.startS * fps + fps * 0.8],
            [0, 1],
            { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
          );
          // Fade out after labelHoldS (if set), so the camera can move on.
          const outStart = labelHoldS != null ? (v.startS + labelHoldS) * fps : Infinity;
          const fadeOut = labelHoldS != null
            ? interpolate(frame, [outStart, outStart + fps * 0.45], [1, 0], {
                extrapolateLeft: "clamp",
                extrapolateRight: "clamp",
              })
            : 1;
          if (drawIn <= 0 || fadeOut <= 0) return null;

          // Leader: from the feature point, out to the label block, drawn on.
          const midX = v.blockX;
          const pathLen = Math.abs(v.blockX - v.x) + Math.abs(v.blockY - v.y);
          const dash = pathLen;
          const textAnchor = v.toLeft ? "end" : "start";
          const labelEdgeX = v.toLeft ? v.blockX - 12 * S : v.blockX + 12 * S;
          const dn = displayNames[v.label.feature] ?? v.label.feature;
          const { term, qualifier } = splitTerm(dn);
          const desc = descriptions?.[v.label.feature];

          return (
            <g key={v.label.feature} opacity={fadeOut}>
              {/* leader line + end dot */}
              <path
                d={`M ${v.x} ${v.y} L ${midX} ${v.y} L ${midX} ${v.blockY}`}
                fill="none"
                stroke={resolvedLine}
                strokeWidth={LINE_W}
                strokeDasharray={dash}
                strokeDashoffset={dash * (1 - drawIn)}
                filter="url(#dl-glow)"
              />
              <circle cx={midX} cy={v.blockY} r={3.5 * S} fill={resolvedLine} opacity={drawIn} />
              {/* glowing target ring at the feature */}
              <g filter="url(#dl-dotglow)" opacity={drawIn}>
                <circle cx={v.x} cy={v.y} r={DOT_RING} fill="none" stroke={resolvedLine} strokeWidth={2 * S} opacity={0.5} />
                <circle cx={v.x} cy={v.y} r={DOT_CORE} fill={resolvedText} />
              </g>
              {/* term + qualifier + description */}
              <g opacity={textIn} transform={`translate(0, ${(1 - textIn) * 6 * S})`}>
                <text
                  x={labelEdgeX}
                  y={v.blockY - 6 * S}
                  textAnchor={textAnchor}
                  fill={resolvedText}
                  stroke="#000000"
                  strokeWidth={5 * S}
                  paintOrder="stroke"
                  fontSize={TERM_SIZE}
                  fontWeight={700}
                  fontFamily="'Montserrat', 'Helvetica Neue', Arial, sans-serif"
                  style={{ letterSpacing: `${0.5 * S}px` }}
                >
                  {term}
                </text>
                {qualifier && (
                  <text
                    x={labelEdgeX}
                    y={v.blockY - 6 * S + QUAL_SIZE + 6 * S}
                    textAnchor={textAnchor}
                    fill={resolvedAccent}
                    stroke="#000000"
                    strokeWidth={4 * S}
                    paintOrder="stroke"
                    fontSize={QUAL_SIZE}
                    fontWeight={600}
                    fontFamily="'Montserrat', 'Helvetica Neue', Arial, sans-serif"
                  >
                    ({qualifier})
                  </text>
                )}
                {desc &&
                  desc.split("\n").map((ln, li) => (
                    <text
                      key={li}
                      x={labelEdgeX}
                      y={v.blockY - 6 * S + (qualifier ? QUAL_SIZE + 12 * S : 0) + (li + 1) * (DESC_SIZE + 5 * S) + 8 * S}
                      textAnchor={textAnchor}
                      fill={resolvedText}
                      stroke="#000000"
                      strokeWidth={3.5 * S}
                      paintOrder="stroke"
                      fontSize={DESC_SIZE}
                      fontWeight={400}
                      fontFamily="'Helvetica Neue', Arial, sans-serif"
                      opacity={0.92}
                    >
                      {ln}
                    </text>
                  ))}
              </g>
            </g>
          );
        })}
      </svg>
    </AbsoluteFill>
  );
};
