import React, { useMemo } from "react";
import { useCurrentFrame, useVideoConfig, interpolate, spring, random } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import * as THREE from "three";

// ─── Ocean Particle Field (Three.js) ─────────────────────────────────────────
// 300 cold-blue bioluminescent particles drifting with sine wave motion.
// Uses deterministic random() from Remotion for reproducible per-frame output.

function OceanParticles({ frame }: { frame: number }) {
  const COUNT = 300;

  const meta = useMemo(() => {
    const pos: number[] = [];
    const spd: number[] = [];
    const phs: number[] = [];
    for (let i = 0; i < COUNT; i++) {
      pos.push(
        (random(`px${i}`) - 0.5) * 16,
        (random(`py${i}`) - 0.5) * 9,
        (random(`pz${i}`) - 0.5) * 4
      );
      spd.push(0.002 + random(`sp${i}`) * 0.004);
      phs.push(random(`ph${i}`) * Math.PI * 2);
    }
    return { pos, spd, phs };
  }, []);

  const posArray = useMemo(() => {
    const arr = new Float32Array(COUNT * 3);
    for (let i = 0; i < COUNT; i++) {
      const t = frame * meta.spd[i];
      arr[i * 3]     = meta.pos[i * 3]     + Math.sin(t + meta.phs[i]) * 0.3;
      arr[i * 3 + 1] = meta.pos[i * 3 + 1] + Math.cos(t * 0.7 + meta.phs[i]) * 0.2;
      arr[i * 3 + 2] = meta.pos[i * 3 + 2];
    }
    return arr;
  }, [frame, meta]);

  const { geometry, material } = useMemo(() => {
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(COUNT * 3), 3));
    const m = new THREE.PointsMaterial({
      color: new THREE.Color(0x4cf8ff),
      size: 0.04,
      transparent: true,
      opacity: 0.55,
      sizeAttenuation: true,
    });
    return { geometry: g, material: m };
  }, []);

  // Update positions each frame
  geometry.getAttribute("position").array.set(posArray);
  geometry.getAttribute("position").needsUpdate = true;

  const points = useMemo(() => new THREE.Points(geometry, material), [geometry, material]);

  return <primitive object={points} />;
}

function ParticleScene({ frame }: { frame: number }) {
  return (
    <>
      <ambientLight intensity={0.05} />
      <OceanParticles frame={frame} />
    </>
  );
}

// ─── Title Text — Letter Drop-In ──────────────────────────────────────────────
// Each letter springs down from above, staggered 2 frames per letter.
// After landing: a slow sine wave glow breath on cold blue shadow.

const LINE_1 = "THE DEEP-SEA ANIMAL";
const LINE_2 = "THAT MAKES ITS OWN LIGHT";
const SUBTITLE = "— AND USES IT TO KILL —";

function buildLetterDelay(line: string, baseDelay: number): number[] {
  let idx = 0;
  return line.split("").map((c) => {
    const d = baseDelay + idx * 2;
    if (c !== " ") idx++;
    return d;
  });
}

const LINE_1_DELAYS = buildLetterDelay(LINE_1, 0);
const LINE_2_DELAYS = buildLetterDelay(LINE_2, LINE_1.replace(/ /g, "").length * 2 + 6);
const SUBTITLE_DELAY = LINE_2_DELAYS[LINE_2_DELAYS.length - 1] + 16;

function TitleLine({
  text,
  delays,
  frame,
  fps,
  fontSize,
}: {
  text: string;
  delays: number[];
  frame: number;
  fps: number;
  fontSize: number;
}) {
  return (
    <div style={{ display: "flex", justifyContent: "center", alignItems: "flex-end" }}>
      {text.split("").map((char, i) => {
        if (char === " ") {
          return <span key={i} style={{ width: fontSize * 0.28, display: "inline-block" }} />;
        }

        const d = delays[i];

        const opacity = interpolate(frame, [d, d + 6], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });

        const dropY = spring({
          frame: frame - d,
          fps,
          config: { damping: 14, stiffness: 120, mass: 0.45 },
          from: -70,
          to: 0,
        });

        // Cold glow breathes in after landing
        const breatheOffset = (frame - (d + 18)) * 0.04;
        const glow = Math.max(0, (Math.sin(breatheOffset) * 0.5 + 0.5) * 0.6);

        return (
          <span
            key={i}
            style={{
              display: "inline-block",
              fontSize,
              fontFamily: "'Bebas Neue', Impact, Arial, sans-serif",
              fontWeight: 900,
              color: "#FFFFFF",
              letterSpacing: "0.06em",
              lineHeight: 1,
              opacity,
              transform: `translateY(${dropY}px)`,
              textShadow: [
                `0 0 ${12 + glow * 24}px rgba(76,248,255,${glow * 0.7})`,
                `0 0 ${30 + glow * 40}px rgba(76,248,255,${glow * 0.3})`,
                "0 2px 20px rgba(0,0,0,0.95)",
              ].join(", "),
            }}
          >
            {char}
          </span>
        );
      })}
    </div>
  );
}

// ─── Main Export ──────────────────────────────────────────────────────────────

export const BioluminescenceTitleCard: React.FC = () => {
  const frame = useCurrentFrame();
  const { width, height, fps } = useVideoConfig();

  // Subtitle fade + RGB split
  const subtitleOpacity = interpolate(frame, [SUBTITLE_DELAY, SUBTITLE_DELAY + 10], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const rgbOffset = Math.sin(frame / 8) * 3;
  const glitchY    = Math.sin(frame / 5) * 1.5;

  return (
    <div style={{ width, height, position: "relative", backgroundColor: "#00030A", overflow: "hidden" }}>

      {/* Three.js particle ocean */}
      <ThreeCanvas width={width} height={height} style={{ position: "absolute", inset: 0 }}>
        <ParticleScene frame={frame} />
      </ThreeCanvas>

      {/* Deep vignette — keeps edges dark */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "radial-gradient(ellipse at center, transparent 25%, rgba(0,3,10,0.75) 100%)",
          pointerEvents: "none",
        }}
      />

      {/* Title text */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: 6,
          padding: "0 80px",
        }}
      >
        <TitleLine text={LINE_1} delays={LINE_1_DELAYS} frame={frame} fps={fps} fontSize={78} />
        <TitleLine text={LINE_2} delays={LINE_2_DELAYS} frame={frame} fps={fps} fontSize={78} />

        {/* Accent bar */}
        <div
          style={{
            width: interpolate(frame, [SUBTITLE_DELAY - 4, SUBTITLE_DELAY + 8], [0, 120], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
            height: 2,
            backgroundColor: "#4CF8FF",
            boxShadow: "0 0 12px #4CF8FF, 0 0 24px rgba(76,248,255,0.4)",
            borderRadius: 1,
            marginTop: 8,
          }}
        />

        {/* Subtitle with RGB glitch effect */}
        <div style={{ position: "relative", opacity: subtitleOpacity, marginTop: 4 }}>
          <div
            style={{
              position: "absolute",
              color: "cyan",
              transform: `translate(${rgbOffset}px, ${glitchY}px)`,
              mixBlendMode: "screen",
              fontSize: 26,
              fontFamily: "'Montserrat', Arial, sans-serif",
              fontWeight: 300,
              letterSpacing: "0.28em",
            }}
          >
            {SUBTITLE}
          </div>
          <div
            style={{
              position: "absolute",
              color: "magenta",
              transform: `translate(${-rgbOffset}px, ${-glitchY}px)`,
              mixBlendMode: "screen",
              fontSize: 26,
              fontFamily: "'Montserrat', Arial, sans-serif",
              fontWeight: 300,
              letterSpacing: "0.28em",
            }}
          >
            {SUBTITLE}
          </div>
          <div
            style={{
              color: "rgba(255,255,255,0.82)",
              fontSize: 26,
              fontFamily: "'Montserrat', Arial, sans-serif",
              fontWeight: 300,
              letterSpacing: "0.28em",
              textShadow: "0 2px 12px rgba(0,0,0,0.9)",
            }}
          >
            {SUBTITLE}
          </div>
        </div>
      </div>
    </div>
  );
};
