import React from "react";
import { Composition, getStaticFiles } from "remotion";
import { DynamicComp } from "./DynamicComp";
import { Overlay } from "./Overlay";
import { AIVideo, aiVideoSchema } from "./video-components/AIVideo";
import { BioluminescenceDoc, BIOLUMINESCENCE_DURATION_FRAMES } from "./video-components/BioluminescenceDoc";
import { CinematicTitleCard } from "./video-components/CinematicTitleCard";
import { AnomalousWildEndCard } from "./video-components/AnomalousWildEndCard";
import { NeonParcelTitleOverlay } from "./video-components/NeonParcelTitleOverlay";
import { FPS, INTRO_DURATION } from "./video-lib/constants";
import { getTimelinePath, loadTimelineFromFile } from "./video-lib/utils";

const defaultCode = `import { AbsoluteFill } from "remotion";
export const MyAnimation = () => <AbsoluteFill style={{ backgroundColor: "#000" }} />;`;

export const RemotionRoot: React.FC = () => {
  const staticFiles = getStaticFiles();
  const timelines = staticFiles
    .filter((file) => file.name.endsWith("timeline.json"))
    .map((file) => file.name.split("/")[1]);

  return (
    <>
      {/* AI Motion Graphics — prompt-driven dynamic composition */}
      <Composition
        id="DynamicComp"
        component={DynamicComp}
        durationInFrames={180}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{ code: defaultCode }}
        calculateMetadata={({ props }) => ({
          durationInFrames: props.durationInFrames as number,
          fps: props.fps as number,
        })}
      />

      {/* Overlay — animated lower-thirds / title cards */}
      <Composition
        id="Overlay"
        component={Overlay}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
      />

      {/* 001 Anomalous Wild — Bioluminescence Weapon documentary */}
      <Composition
        id="BioluminescenceDoc"
        component={BioluminescenceDoc}
        durationInFrames={BIOLUMINESCENCE_DURATION_FRAMES}
        fps={30}
        width={1920}
        height={1080}
      />

      {/* CinematicTitleCard — reusable channel-agnostic title card template */}
      <Composition
        id="CinematicTitleCard"
        component={CinematicTitleCard}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          titleLine1: "ANOMALOUS WILD",
          titleLine2: "PREVIEW",
          subtitle: "— SET YOUR OWN PROPS —",
          channelTag: "YOUR CHANNEL",
          accentColor: "#4CF8FF",
          bgColor: "#00030A",
          ambientSrc: "",
          ambientVolume: 0.55,
          durationFrames: 150,
          particleCount: 250,
        }}
      />

      {/* Anomalous Wild — YouTube end card (10s, 1920×1080, 30fps) */}
      <Composition
        id="AnomalousWildEndCard"
        component={AnomalousWildEndCard}
        durationInFrames={300}
        fps={30}
        width={1920}
        height={1080}
      />

      {/* 0002 Neon Parcel Cats — title card overlay version */}
      <Composition
        id="NeonParcelTitleOverlay"
        component={NeonParcelTitleOverlay}
        durationInFrames={655}
        fps={24}
        width={1080}
        height={1920}
      />

      {/* Prompt to Video — AI-generated stories with images + voiceover */}
      {timelines.map((storyName) => (
        <Composition
          key={storyName}
          id={storyName}
          component={AIVideo}
          fps={FPS}
          width={1080}
          height={1920}
          schema={aiVideoSchema}
          defaultProps={{ timeline: null }}
          calculateMetadata={async ({ props }) => {
            const { lengthFrames, timeline } = await loadTimelineFromFile(
              getTimelinePath(storyName),
            );
            return {
              durationInFrames: lengthFrames + INTRO_DURATION,
              props: { ...props, timeline },
            };
          }}
        />
      ))}
    </>
  );
};
