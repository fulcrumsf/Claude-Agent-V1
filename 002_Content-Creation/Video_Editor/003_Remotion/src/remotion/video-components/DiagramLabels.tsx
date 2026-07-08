// DiagramLabels.tsx
import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate } from "remotion";
import { z } from "zod";

export const diagramLabelsSchema = z.object({
  labels: z.array(
    z.object({
      feature: z.string(),
      // Optional: a "not_found" entry (see detect_label_coordinates.py) legitimately
      // omits x_pct/y_pct rather than guessing a coordinate. The render logic below
      // filters those entries out before ever reading x_pct/y_pct.
      x_pct: z.number().optional(),
      y_pct: z.number().optional(),
      confidence: z.enum(["high", "low", "not_found"]),
    }),
  ),
  labelStaggerS: z.number(), // seconds between each label appearing — must respect the 3-5s max-static rule upstream
  displayNames: z.record(z.string(), z.string()), // e.g. {"esca": "Esca (light lure)"}
});

type DiagramLabel = z.infer<typeof diagramLabelsSchema>["labels"][number];

// Narrows a label to one that is guaranteed to have coordinates — true for every
// entry that survives the `confidence !== "not_found"` filter, since "not_found"
// is the only confidence value that can legitimately lack x_pct/y_pct.
function hasCoordinates(label: DiagramLabel): label is DiagramLabel & { x_pct: number; y_pct: number } {
  return label.confidence !== "not_found";
}

const LABEL_COLOR = "#E8FFE0";
const LINE_COLOR = "#8AFA47";

export const DiagramLabels: React.FC<z.infer<typeof diagramLabelsSchema>> = ({ labels, labelStaggerS, displayNames }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();

  const visibleLabels = labels.filter(hasCoordinates);

  return (
    <AbsoluteFill>
      {visibleLabels.map((label, i) => {
        const startFrame = i * labelStaggerS * fps;
        const opacity = interpolate(frame, [startFrame, startFrame + fps * 0.5], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
        const x = (label.x_pct / 100) * width;
        const y = (label.y_pct / 100) * height;
        // Label sits offset from the point, with a line drawn back to the point
        const labelX = x + 120;
        const labelY = y - 60;

        return (
          <svg key={label.feature} width={width} height={height} style={{ position: "absolute", top: 0, left: 0, opacity }}>
            <line x1={x} y1={y} x2={labelX} y2={labelY} stroke={LINE_COLOR} strokeWidth={1.5} opacity={0.8} />
            <circle cx={x} cy={y} r={4} fill={LINE_COLOR} />
            <text x={labelX + 8} y={labelY} fill={LABEL_COLOR} fontSize={20} fontFamily="Arial, sans-serif">
              {displayNames[label.feature] ?? label.feature}
            </text>
          </svg>
        );
      })}
    </AbsoluteFill>
  );
};
