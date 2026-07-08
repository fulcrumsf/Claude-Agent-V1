import React from "react";
import { Composition } from "remotion";
import { OceanDepthDescent } from "./OceanDepthDescent";

export const Root: React.FC = () => {
  return (
    <Composition
      id="OceanDepthDescent"
      component={OceanDepthDescent}
      durationInFrames={360}
      fps={30}
      width={1920}
      height={1080}
    />
  );
};
