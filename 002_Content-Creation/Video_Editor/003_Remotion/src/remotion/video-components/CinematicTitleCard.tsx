/**
 * CinematicTitleCard — reusable title card template (George Lucas / Pixar standard)
 *
 * USAGE
 * ─────
 * Drop this into a <Sequence> at the start of any documentary composition.
 * Pass channel-specific colors and titles via props — never hardcode here.
 *
 * AMBIENT AUDIO SLOT (mandatory — title cards must never be silent)
 * ─────────────────
 * `ambientSrc` is REQUIRED. Pass a path to an ambient audio file (e.g. underwater
 * hum, forest atmosphere, city texture). The card crossfades in at the start and
 * crossfades out at the end so audio blends seamlessly into the main timeline.
 *
 * TIMING
 * ──────
 * Default 150 frames (5s at 30fps). Override with `durationFrames` prop.
 * Letter drop-in completes at ~frame 80. Subtitle enters at ~frame 90.
 * Fade-out begins at `durationFrames - 30`.
 *
 * PROPS
 * ─────
 * titleLine1     — first title line (caps recommended)
 * titleLine2     — second title line (can be empty string)
 * subtitle       — italic sub-tag below the accent bar (e.g. "— AND USES IT TO KILL —")
 * channelTag     — small channel name watermark, bottom-right (e.g. "ANOMALOUS WILD")
 * accentColor    — hex string for the channel accent (default: "#4CF8FF" — deep teal)
 * bgColor        — solid background fallback (default: "#00030A" — near-black)
 * backgroundSrc  — optional: path to a looping video or still image shown behind
 *                  the particles. Pass staticFile("path/to/bg.mp4") or similar.
 * ambientSrc     — REQUIRED: path to ambient audio file. Use staticFile().
 * durationFrames — total length of the title card in frames (default: 150)
 * particleCount  — number of atmospheric particles (default: 250)
 */

import React, { useMemo } from "react";
import {
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  random,
  Img,
  AbsoluteFill,
  OffthreadVideo,
} from "remotion";
import { Audio } from "@remotion/media";
import { ThreeCanvas } from "@remotion/three";
import * as THREE from "three";

// ─── Props ────────────────────────────────────────────────────────────────────

export interface CinematicTitleCardProps {
  titleLine1?: string;          // first title line (caps recommended)
  titleLine2?: string;
  subtitle?: string;
  channelTag?: string;
  accentColor?: string;
  bgColor?: string;
  backgroundSrc?: string;
  backgroundIsVideo?: boolean;
  ambientSrc?: string;          // path to ambient audio — title cards must never be silent
  ambientVolume?: number;       // 0–1, default 0.55
  durationFrames?: number;      // default 150 (5s @ 30fps)
  particleCount?: number;       // default 250
}

// ─── Atmospheric Particles (Three.js) ─────────────────────────────────────────

function AtmosphereParticles({
  frame,
  count,
  color,
}: {
  frame: number;
  count: number;
  color: string;
}) {
  const meta = useMemo(() => {
    const pos: number[] = [];
    const spd: number[] = [];
    const phs: number[] = [];
    for (let i = 0; i < count; i++) {
      pos.push(
        (random(`ax${i}`) - 0.5) * 18,
        (random(`ay${i}`) - 0.5) * 10,
        (random(`az${i}`) - 0.5) * 5
      );
      spd.push(0.0015 + random(`as${i}`) * 0.004);
      phs.push(random(`ap${i}`) * Math.PI * 2);
    }
    return { pos, spd, phs };
  }, [count]);

  const posArray = useMemo(() => {
    const arr = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const t = frame * meta.spd[i];
      arr[i * 3]     = meta.pos[i * 3]     + Math.sin(t + meta.phs[i]) * 0.35;
      arr[i * 3 + 1] = meta.pos[i * 3 + 1] + Math.cos(t * 0.7 + meta.phs[i]) * 0.25;
      arr[i * 3 + 2] = meta.pos[i * 3 + 2];
    }
    return arr;
  }, [frame, meta, count]);

  const { geometry, material } = useMemo(() => {
    const c = new THREE.Color(color);
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(count * 3), 3));
    const m = new THREE.PointsMaterial({
      color: c,
      size: 0.035,
      transparent: true,
      opacity: 0.5,
      sizeAttenuation: true,
    });
    return { geometry: g, material: m };
  }, [color, count]);

  geometry.getAttribute("position").array.set(posArray);
  geometry.getAttribute("position").needsUpdate = true;

  const points = useMemo(
    () => new THREE.Points(geometry, material),
    [geometry, material]
  );

  return <primitive object={points} />;
}

// ─── Letter Drop-In ──────────────────────────────────────────────────────────

/**
 * Build per-letter delays for a title line.
 * Only non-space characters count toward the delay increment.
 */
function buildLetterDelays(text: string, startDelay: number): number[] {
  let nonSpaceCount = 0;
  return text.split("").map((char) => {
    const d = startDelay + nonSpaceCount * 2;
    if (char !== " ") nonSpaceCount++;
    return d;
  });
}

function TitleLine({
  text,
  delays,
  frame,
  fps,
  fontSize,
  accentColor,
}: {
  text: string;
  delays: number[];
  frame: number;
  fps: number;
  fontSize: number;
  accentColor: string;
}) {
  return (
    <div style={{ display: "flex", justifyContent: "center", alignItems: "flex-end" }}>
      {text.split("").map((char, i) => {
        if (char === " ") {
          return (
            <span
              key={i}
              style={{ width: fontSize * 0.28, display: "inline-block" }}
            />
          );
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

        // Glow breathes in after landing
        const breatheOffset = (frame - (d + 18)) * 0.04;
        const glow = Math.max(0, Math.sin(breatheOffset) * 0.5 + 0.5) * 0.6;

        // Parse hex accent to rgb for shadow
        const r = parseInt(accentColor.slice(1, 3), 16);
        const g2 = parseInt(accentColor.slice(3, 5), 16);
        const b = parseInt(accentColor.slice(5, 7), 16);

        return (
          <span
            key={i}
            style={{
              display: "inline-block",
              fontSize,
              fontFamily: "'Bebas Neue', Impact, Arial Black, sans-serif",
              fontWeight: 900,
              color: "#FFFFFF",
              letterSpacing: "0.06em",
              lineHeight: 1,
              opacity,
              transform: `translateY(${dropY}px)`,
              textShadow: [
                `0 0 ${12 + glow * 24}px rgba(${r},${g2},${b},${glow * 0.75})`,
                `0 0 ${30 + glow * 40}px rgba(${r},${g2},${b},${glow * 0.35})`,
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

// ─── Main Component ───────────────────────────────────────────────────────────

export const CinematicTitleCard: React.FC<CinematicTitleCardProps> = ({
  titleLine1 = "TITLE LINE ONE",
  titleLine2 = "",
  subtitle = "",
  channelTag = "",
  accentColor = "#4CF8FF",
  bgColor = "#00030A",
  backgroundSrc,
  backgroundIsVideo = false,
  ambientSrc = "",
  ambientVolume = 0.55,
  durationFrames = 150,
  particleCount = 250,
}) => {
  const frame = useCurrentFrame();
  const { width, height, fps } = useVideoConfig();

  // ── Letter delay timings ──────────────────────────────────────────────────
  const line1Delays = useMemo(
    () => buildLetterDelays(titleLine1, 0),
    [titleLine1]
  );

  const line2StartDelay = useMemo(
    () => titleLine1.replace(/ /g, "").length * 2 + 6,
    [titleLine1]
  );

  const line2Delays = useMemo(
    () => buildLetterDelays(titleLine2, line2StartDelay),
    [titleLine2, line2StartDelay]
  );

  const lastLine2Delay =
    titleLine2.length > 0
      ? line2Delays[line2Delays.length - 1]
      : line1Delays[line1Delays.length - 1];

  const subtitleDelay = lastLine2Delay + 16;
  const accentBarDelay = subtitleDelay - 4;

  // ── Global fade in / out ──────────────────────────────────────────────────
  const fadeIn = interpolate(frame, [0, 12], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const fadeOut = interpolate(
    frame,
    [durationFrames - 30, durationFrames - 6],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const masterOpacity = Math.min(fadeIn, fadeOut);

  // ── Subtitle animations ───────────────────────────────────────────────────
  const subtitleOpacity = interpolate(
    frame,
    [subtitleDelay, subtitleDelay + 10],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const rgbOffset = Math.sin(frame / 8) * 2.5;
  const glitchY = Math.sin(frame / 5) * 1.2;

  // ── Accent bar width ──────────────────────────────────────────────────────
  const accentBarWidth = interpolate(
    frame,
    [accentBarDelay, accentBarDelay + 12],
    [0, 120],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // ── Channel tag fade-in ───────────────────────────────────────────────────
  const channelTagOpacity = interpolate(
    frame,
    [subtitleDelay + 20, subtitleDelay + 35],
    [0, 0.45],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // ── Audio crossfades ──────────────────────────────────────────────────────
  const audioVolume =
    Math.min(fadeIn, fadeOut) * ambientVolume;

  // Parse accent for accent bar shadow
  const [ar, ag, ab] = [
    parseInt(accentColor.slice(1, 3), 16),
    parseInt(accentColor.slice(3, 5), 16),
    parseInt(accentColor.slice(5, 7), 16),
  ];

  return (
    <AbsoluteFill
      style={{
        backgroundColor: bgColor,
        overflow: "hidden",
        opacity: masterOpacity,
      }}
    >
      {/* ── Mandatory ambient audio — title cards must never be silent ── */}
      {ambientSrc && <Audio src={ambientSrc} volume={audioVolume} />}

      {/* ── Optional background video or image ── */}
      {backgroundSrc && backgroundIsVideo && (
        <OffthreadVideo
          src={backgroundSrc}
          style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover", opacity: 0.35 }}
          volume={0}
        />
      )}
      {backgroundSrc && !backgroundIsVideo && (
        <Img
          src={backgroundSrc}
          style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover", opacity: 0.35 }}
        />
      )}

      {/* ── Atmospheric particles ── */}
      <ThreeCanvas
        width={width}
        height={height}
        style={{ position: "absolute", inset: 0 }}
      >
        <>
          <ambientLight intensity={0.05} />
          <AtmosphereParticles
            frame={frame}
            count={particleCount}
            color={accentColor}
          />
        </>
      </ThreeCanvas>

      {/* ── Vignette — keep edges dark for cinematic weight ── */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `radial-gradient(ellipse at center, transparent 20%, ${bgColor}CC 100%)`,
          pointerEvents: "none",
        }}
      />

      {/* ── Title + subtitle ── */}
      <AbsoluteFill
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: 6,
          padding: "0 80px",
        }}
      >
        <TitleLine
          text={titleLine1}
          delays={line1Delays}
          frame={frame}
          fps={fps}
          fontSize={80}
          accentColor={accentColor}
        />

        {titleLine2 && (
          <TitleLine
            text={titleLine2}
            delays={line2Delays}
            frame={frame}
            fps={fps}
            fontSize={80}
            accentColor={accentColor}
          />
        )}

        {/* Accent bar */}
        <div
          style={{
            width: accentBarWidth,
            height: 2,
            backgroundColor: accentColor,
            boxShadow: `0 0 12px ${accentColor}, 0 0 28px rgba(${ar},${ag},${ab},0.45)`,
            borderRadius: 1,
            marginTop: 10,
          }}
        />

        {/* Subtitle with RGB glitch */}
        {subtitle && (
          <div style={{ position: "relative", opacity: subtitleOpacity, marginTop: 6 }}>
            {/* Red channel */}
            <div
              style={{
                position: "absolute",
                color: "cyan",
                transform: `translate(${rgbOffset}px, ${glitchY}px)`,
                mixBlendMode: "screen",
                fontSize: 24,
                fontFamily: "'Montserrat', 'Helvetica Neue', Arial, sans-serif",
                fontWeight: 300,
                letterSpacing: "0.28em",
              }}
            >
              {subtitle}
            </div>
            {/* Blue channel */}
            <div
              style={{
                position: "absolute",
                color: "magenta",
                transform: `translate(${-rgbOffset}px, ${-glitchY}px)`,
                mixBlendMode: "screen",
                fontSize: 24,
                fontFamily: "'Montserrat', 'Helvetica Neue', Arial, sans-serif",
                fontWeight: 300,
                letterSpacing: "0.28em",
              }}
            >
              {subtitle}
            </div>
            {/* Main */}
            <div
              style={{
                color: "rgba(255,255,255,0.82)",
                fontSize: 24,
                fontFamily: "'Montserrat', 'Helvetica Neue', Arial, sans-serif",
                fontWeight: 300,
                letterSpacing: "0.28em",
                textShadow: "0 2px 12px rgba(0,0,0,0.9)",
              }}
            >
              {subtitle}
            </div>
          </div>
        )}
      </AbsoluteFill>

      {/* ── Channel tag — bottom-right watermark ── */}
      {channelTag && (
        <div
          style={{
            position: "absolute",
            bottom: 42,
            right: 60,
            opacity: channelTagOpacity,
            fontSize: 16,
            fontFamily: "'Montserrat', 'Helvetica Neue', Arial, sans-serif",
            fontWeight: 600,
            letterSpacing: "0.22em",
            color: "rgba(255,255,255,0.6)",
            textTransform: "uppercase",
          }}
        >
          {channelTag}
        </div>
      )}
    </AbsoluteFill>
  );
};
