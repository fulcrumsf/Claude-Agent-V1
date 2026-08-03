// POVShort.tsx
import React from "react";
import { AbsoluteFill, OffthreadVideo, staticFile } from "remotion";
import { POVCaption, TimedCaption } from "./POVCaption";

export const POVShort: React.FC<{
  backgroundVideoFile: string;
  captions: TimedCaption[];
}> = ({ backgroundVideoFile, captions }) => (
  <AbsoluteFill style={{ backgroundColor: "#000" }}>
    <OffthreadVideo src={staticFile(backgroundVideoFile)} />
    {captions.map((c, i) => (
      <POVCaption key={i} text={c.text} startS={c.startS} durationS={c.durationS} variant={c.variant} />
    ))}
  </AbsoluteFill>
);
