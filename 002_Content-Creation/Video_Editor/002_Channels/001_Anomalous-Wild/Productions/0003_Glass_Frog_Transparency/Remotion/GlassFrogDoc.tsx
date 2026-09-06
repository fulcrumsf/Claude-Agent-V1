import React from "react";
import { Audio } from "@remotion/media";
import {
  AbsoluteFill,
  OffthreadVideo,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  Easing,
} from "remotion";
import { DiagramLabels } from "../../../../../003_Remotion/src/remotion/video-components/DiagramLabels";
import { SceneOverlays, TimedOverlay } from "../../../../../003_Remotion/src/remotion/video-components/SceneOverlay";

// ─── Setup ─────────────────────────────────────────────────────────────────
const FPS = 30;
const s = (seconds: number) => Math.round(seconds * FPS);
const ASSET_ROOT = "glass_frog_transparency"; // public/glass_frog_transparency -> Production folder (symlinked)

// ─── Real scene durations (seconds, measured via ffprobe on Narration_Audio/scene_0N.mp3 —
// the master clock per task instructions, not Script.md's drafted second-marks) ───────────
const AUDIO = {
  scene_01: 3.854512,
  scene_02: 14.396372,
  scene_03: 50.898141,
  scene_04: 35.526531,
  scene_05: 73.003537,
  scene_06: 50.433741,
  scene_07: 4.736871,
};

// ─── Cumulative scene start times ─────────────────────────────────────────
let _t = 0;
const T: Record<string, number> = {};
function nextScene(key: string, dur: number) {
  T[key] = _t;
  _t += dur;
}
nextScene("scene_01", AUDIO.scene_01);
nextScene("scene_02", AUDIO.scene_02);
nextScene("scene_03", AUDIO.scene_03);
nextScene("scene_04", AUDIO.scene_04);
nextScene("scene_05", AUDIO.scene_05);
nextScene("scene_06", AUDIO.scene_06);
nextScene("scene_07", AUDIO.scene_07);

export const GLASS_FROG_DURATION_FRAMES = s(_t);

// ─── Small helpers ─────────────────────────────────────────────────────────

function SceneAudio({ sceneId }: { sceneId: string }) {
  return <Audio src={staticFile(`${ASSET_ROOT}/Narration_Audio/${sceneId}.mp3`)} volume={1} />;
}

function VideoClip({ file, muted = true }: { file: string; muted?: boolean }) {
  return (
    <AbsoluteFill>
      <OffthreadVideo
        src={staticFile(`${ASSET_ROOT}/Video_Clips/${file}`)}
        style={{ width: "100%", height: "100%", objectFit: "cover" }}
        volume={muted ? 0 : 1}
      />
    </AbsoluteFill>
  );
}

// ─── DiagramCamera — continuous crop/zoom/pan over a static illustration ───
// Implements Phase 7's mandatory static-hold rule: interpolates scale + focus point
// continuously across the whole clip lifetime driven by real word-timestamp-derived
// keyframes from Diagram_Blocking_Plans.md — never a fresh AI regeneration, never a
// static hold longer than the plan's own segmentation allows.
interface CamKeyframe {
  t: number; // seconds from this component's own Sequence start
  scale: number;
  fx: number; // focus x, 0-100 (matches label_coordinates.json's x_pct convention)
  fy: number; // focus y, 0-100
}

function DiagramCamera({ src, keyframes }: { src: string; keyframes: CamKeyframe[] }) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const xs = keyframes.map((k) => k.t * fps);
  const scale = interpolate(frame, xs, keyframes.map((k) => k.scale), {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const fx = interpolate(frame, xs, keyframes.map((k) => k.fx), {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const fy = interpolate(frame, xs, keyframes.map((k) => k.fy), {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#0B0F1A" }}>
      <img
        src={staticFile(src)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `scale(${scale})`,
          transformOrigin: `${fx}% ${fy}%`,
        }}
      />
    </AbsoluteFill>
  );
}

// A diagram segment: continuous camera motion + optional coordinate labels,
// nested as its own Sequence at an absolute offset within the parent scene.
interface DiagramSegment {
  fromS: number;
  durS: number;
  src: string; // path relative to public/ (already includes ASSET_ROOT)
  keyframes: CamKeyframe[];
  labels?: { feature: string; x_pct: number; y_pct: number; confidence: "high" | "low" | "not_found" }[];
  displayNames?: Record<string, string>;
  labelOffsetsS?: Record<string, number>;
  lineColor?: string;
  labelColor?: string;
}

function DiagramSeg(seg: DiagramSegment) {
  return (
    <Sequence key={`${seg.src}-${seg.fromS}`} from={s(seg.fromS)} durationInFrames={s(seg.durS)} layout="none">
      <AbsoluteFill>
        <DiagramCamera src={seg.src} keyframes={seg.keyframes} />
        {seg.labels && (
          <DiagramLabels
            labels={seg.labels}
            labelStaggerS={1.5}
            displayNames={seg.displayNames ?? {}}
            labelOffsetsS={seg.labelOffsetsS}
            lineColor={seg.lineColor}
            labelColor={seg.labelColor}
          />
        )}
      </AbsoluteFill>
    </Sequence>
  );
}

interface VideoSegment {
  fromS: number;
  durS: number;
  file: string;
}
function VideoSeg(seg: VideoSegment) {
  return (
    <Sequence key={`${seg.file}-${seg.fromS}`} from={s(seg.fromS)} durationInFrames={s(seg.durS)} layout="none">
      <VideoClip file={seg.file} />
    </Sequence>
  );
}

// ─── Location Card (Anomalous-Wild-Hybrid.md On-Screen Graphics System) ────
function LocationCard({ text, startS, durS }: { text: string; startS: number; durS: number }) {
  const frame = useCurrentFrame();
  const startFrame = s(startS);
  const endFrame = s(startS + durS);
  const opacity = interpolate(
    frame,
    [startFrame, startFrame + 12, endFrame - 15, endFrame],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );
  if (opacity <= 0) return null;
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div
        style={{
          position: "absolute",
          top: 90,
          left: "50%",
          transform: "translateX(-50%)",
          opacity,
          display: "flex",
          alignItems: "center",
          gap: 12,
          background: "rgba(11,15,26,0.55)",
          border: "1px solid rgba(138,250,71,0.5)",
          borderRadius: 8,
          padding: "10px 22px",
        }}
      >
        <div style={{ width: 10, height: 10, borderRadius: "50%", background: "#8AFA47", boxShadow: "0 0 10px #8AFA47" }} />
        <div style={{ fontFamily: "'Montserrat', Arial, sans-serif", fontWeight: 700, color: "#FFFFFF", fontSize: 24, letterSpacing: "0.04em" }}>
          {text}
        </div>
      </div>
    </AbsoluteFill>
  );
}

// ─── Anomaly Level Meter (Anomalous-Wild-Hybrid.md) ────────────────────────
function AnomalyMeter({ value, startS, durS }: { value: number; startS: number; durS: number }) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const startFrame = s(startS);
  const endFrame = s(startS + durS);
  const visOpacity = interpolate(
    frame,
    [startFrame, startFrame + 10, endFrame - 15, endFrame],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );
  const fillFrac = interpolate(frame, [startFrame, startFrame + fps * 1.5], [0, value / 10], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  if (visOpacity <= 0) return null;
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div style={{ position: "absolute", bottom: 110, left: "50%", transform: "translateX(-50%)", opacity: visOpacity, textAlign: "center" }}>
        <div style={{ fontFamily: "'Montserrat', Arial, sans-serif", fontWeight: 700, color: "#FFFFFF", fontSize: 18, letterSpacing: "0.12em", marginBottom: 8 }}>
          ANOMALY LEVEL: {Math.round(fillFrac * 10)}/10
        </div>
        <div style={{ width: 320, height: 14, borderRadius: 7, background: "rgba(255,255,255,0.15)", overflow: "hidden", border: "1px solid rgba(138,250,71,0.5)" }}>
          <div style={{ width: `${fillFrac * 100}%`, height: "100%", background: "#8AFA47", boxShadow: "0 0 12px #8AFA47" }} />
        </div>
      </div>
    </AbsoluteFill>
  );
}

// ─── Range Map Animation (scene_04A) ───────────────────────────────────────
// Stylized animated range map: Central America -> Andes/Amazon outline with a
// dashed path drawing on and a pulsing location dot, per style guide's
// "2-3s animated range map" spec. Simplified geography (not survey-accurate),
// intentional per time constraints of this autonomous assembly pass.
function RangeMapAnimation() {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const drawProgress = interpolate(frame, [0, fps * 2.2], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const pathLen = 900;
  const pulse = 0.6 + 0.4 * Math.sin(frame / 6);
  return (
    <AbsoluteFill style={{ backgroundColor: "#0B0F1A", justifyContent: "center", alignItems: "center" }}>
      <svg width={900} height={700} viewBox="0 0 900 700">
        {/* simplified landmass outline: southern Mexico -> Central America -> Andes -> Amazon */}
        <path
          d="M 300 40 L 260 140 L 300 220 L 260 300 L 320 380 L 300 470 L 360 560 L 420 650"
          fill="none"
          stroke="rgba(255,255,255,0.25)"
          strokeWidth={3}
        />
        {/* animated range path (glass frog distribution) */}
        <path
          d="M 300 40 L 260 140 L 300 220 L 260 300 L 320 380 L 300 470 L 360 560 L 420 650"
          fill="none"
          stroke="#8AFA47"
          strokeWidth={6}
          strokeDasharray={pathLen}
          strokeDashoffset={pathLen * (1 - drawProgress)}
          style={{ filter: "drop-shadow(0 0 8px #8AFA47)" }}
        />
        <circle cx={420} cy={650} r={10 * pulse} fill="none" stroke="#8AFA47" strokeWidth={2} opacity={pulse} />
        <circle cx={420} cy={650} r={5} fill="#8AFA47" />
      </svg>
      <div
        style={{
          position: "absolute",
          bottom: 90,
          fontFamily: "'Montserrat', Arial, sans-serif",
          fontWeight: 700,
          color: "#FFFFFF",
          fontSize: 22,
          letterSpacing: "0.08em",
          opacity: interpolate(frame, [fps * 0.5, fps * 1.2], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          textAlign: "center",
        }}
      >
        SOUTHERN MEXICO → CENTRAL AMERICA → ANDES → AMAZON BASIN
      </div>
    </AbsoluteFill>
  );
}

// ─── Overlay definitions per scene (Fact Callouts / Species Card via SceneOverlays) ─
const OV: Record<string, TimedOverlay[]> = {
  scene_02: [
    { data: { type: "species", name: "Glass Frog", scientific: "Centrolenidae", position: "bottom" }, startS: 1, durationS: 4 },
  ],
  scene_03: [
    { data: { type: "callout", text: "Mirrored organ pouches", position: "bottom" }, startS: 33.2, durationS: 6 },
  ],
  scene_05: [
    { data: { type: "callout", text: "90% of red blood cells hidden", position: "bottom" }, startS: 18.6, durationS: 6 },
    { data: { type: "callout", text: "2–3x more transparent", position: "bottom" }, startS: 30.0, durationS: 6 },
  ],
  scene_06: [
    { data: { type: "callout", text: "Studied for human blood-clot research", position: "bottom" }, startS: 42.0, durationS: 8.4 },
  ],
};

// ─── SCENE 03 diagram segments (Diagram_Blocking_Plans.md, tied to real word timestamps) ──
const S03_DISP = {
  heart: "Heart",
  liver: "Liver",
  lungs: "Lungs",
  intestines: "Intestines",
  mirrored_pouch: "Mirrored Pouch",
  guanine_crystal_surface: "Guanine Crystal Surface",
};
const ORGAN_CUTAWAY = `${ASSET_ROOT}/Images/scene_03/organ_cutaway/illustration.png`;
const MIRRORED_POUCH_03 = `${ASSET_ROOT}/Images/scene_03/mirrored_pouch/illustration.png`;
const SPECIES_MONTAGE = `${ASSET_ROOT}/Images/scene_03/species_montage/illustration.png`;

function Scene03Diagram() {
  return (
    <>
      {DiagramSeg({
        fromS: 0.0,
        durS: 4.72,
        src: ORGAN_CUTAWAY,
        keyframes: [
          { t: 0, scale: 1.0, fx: 50, fy: 50 },
          { t: 4.72, scale: 1.3, fx: 50.2, fy: 39.5 },
        ],
        labels: [{ feature: "heart", x_pct: 50.2, y_pct: 39.5, confidence: "high" }],
        displayNames: S03_DISP,
        labelOffsetsS: { heart: 2.2 },
        lineColor: "#5FD8D8",
        labelColor: "#FFFFFF",
      })}
      {DiagramSeg({
        fromS: 4.79,
        durS: 1.77,
        src: ORGAN_CUTAWAY,
        keyframes: [
          { t: 0, scale: 1.3, fx: 50.2, fy: 39.5 },
          { t: 0.88, scale: 1.3, fx: 50.1, fy: 47.3 },
          { t: 1.77, scale: 1.3, fx: 43.4, fy: 41.0 },
        ],
        labels: [
          { feature: "liver", x_pct: 50.1, y_pct: 47.3, confidence: "high" },
          { feature: "lungs", x_pct: 43.4, y_pct: 41.0, confidence: "high" },
        ],
        displayNames: S03_DISP,
        labelOffsetsS: { liver: 0.2, lungs: 0.9 },
        lineColor: "#5FD8D8",
        labelColor: "#FFFFFF",
      })}
      {DiagramSeg({
        fromS: 6.88,
        durS: 2.36,
        src: ORGAN_CUTAWAY,
        keyframes: [
          { t: 0, scale: 1.3, fx: 43.4, fy: 41.0 },
          { t: 2.36, scale: 1.3, fx: 50.1, fy: 62.0 },
        ],
        labels: [{ feature: "intestines", x_pct: 50.1, y_pct: 62.0, confidence: "high" }],
        displayNames: S03_DISP,
        labelOffsetsS: { intestines: 0.2 },
        lineColor: "#5FD8D8",
        labelColor: "#FFFFFF",
      })}
      {DiagramSeg({
        fromS: 9.52,
        durS: 5.17,
        src: ORGAN_CUTAWAY,
        keyframes: [
          { t: 0, scale: 1.3, fx: 50.1, fy: 62.0 },
          { t: 5.17, scale: 1.0, fx: 50, fy: 50 },
        ],
      })}
      {DiagramSeg({
        fromS: 15.49,
        durS: 9.0,
        src: SPECIES_MONTAGE,
        keyframes: [
          { t: 0, scale: 1.15, fx: 15, fy: 50 },
          { t: 9.0, scale: 1.15, fx: 85, fy: 50 },
        ],
      })}
      {DiagramSeg({
        fromS: 25.18,
        durS: 7.33,
        src: ORGAN_CUTAWAY,
        keyframes: [
          { t: 0, scale: 1.0, fx: 50.1, fy: 47.3 },
          { t: 7.33, scale: 1.6, fx: 50.1, fy: 47.3 },
        ],
      })}
      {DiagramSeg({
        fromS: 33.2,
        durS: 8.04,
        src: MIRRORED_POUCH_03,
        keyframes: [
          { t: 0, scale: 1.0, fx: 59.2, fy: 50.1 },
          { t: 8.04, scale: 1.35, fx: 55.0, fy: 49.0 },
        ],
        labels: [
          { feature: "mirrored_pouch", x_pct: 59.2, y_pct: 50.1, confidence: "high" },
          { feature: "guanine_crystal_surface", x_pct: 51.1, y_pct: 47.9, confidence: "high" },
        ],
        displayNames: S03_DISP,
        labelOffsetsS: { mirrored_pouch: 0.8, guanine_crystal_surface: 4.3 },
        lineColor: "#5FD8D8",
        labelColor: "#FFFFFF",
      })}
      {DiagramSeg({
        fromS: 41.94,
        durS: 5.71,
        src: MIRRORED_POUCH_03,
        keyframes: [
          { t: 0, scale: 1.35, fx: 55.0, fy: 49.0 },
          { t: 5.71, scale: 1.0, fx: 50, fy: 50 },
        ],
      })}
      {/* 47.86-50.90s: deliberate near-silence beat, true static hold under the 5.0s cap
          per Diagram_Blocking_Plans.md — intentional, held on the pulled-back mirrored_pouch frame. */}
      {DiagramSeg({
        fromS: 47.86,
        durS: 3.04,
        src: MIRRORED_POUCH_03,
        keyframes: [
          { t: 0, scale: 1.0, fx: 50, fy: 50 },
          { t: 3.04, scale: 1.03, fx: 50, fy: 50 },
        ],
      })}
    </>
  );
}

// ─── SCENE 05 diagram segments ──────────────────────────────────────────────
const BLOOD_CELL = `${ASSET_ROOT}/Images/scene_05/blood_cell_concentration/illustration.png`;
const MIRRORED_POUCH_CAM = `${ASSET_ROOT}/Images/scene_05/mirrored_pouch_camouflage/illustration.png`;
const VESSEL_CROSS = `${ASSET_ROOT}/Images/scene_05/vessel_cross_section/illustration.png`;
const SIDE_BY_SIDE = `${ASSET_ROOT}/Images/scene_05/side_by_side/illustration.png`;
const PHOTOACOUSTIC = `${ASSET_ROOT}/Images/scene_05/photoacoustic_insert/illustration.png`;

const S05_DISP = {
  red_blood_cells_awake: "Red Blood Cells (Awake)",
  red_blood_cells_asleep: "Red Blood Cells (Asleep)",
  liver: "Liver",
  mirrored_surface: "Mirrored Surface",
  red_blood_cells: "Red Blood Cells",
  vessel_wall: "Vessel Wall",
};

function Scene05Diagram() {
  return (
    <>
      {DiagramSeg({ fromS: 0.0, durS: 5.07, src: SIDE_BY_SIDE, keyframes: [
        { t: 0, scale: 1.0, fx: 50, fy: 50 },
        { t: 5.07, scale: 1.15, fx: 50, fy: 50 },
      ] })}
      {DiagramSeg({
        fromS: 5.77, durS: 12.24, src: BLOOD_CELL,
        keyframes: [
          { t: 0, scale: 1.2, fx: 25.1, fy: 50.1 },
          { t: 4.0, scale: 1.2, fx: 25.1, fy: 50.1 },
          { t: 12.24, scale: 1.3, fx: 75.3, fy: 50.5 },
        ],
        labels: [
          { feature: "red_blood_cells_awake", x_pct: 25.1, y_pct: 50.1, confidence: "high" },
          { feature: "red_blood_cells_asleep", x_pct: 75.3, y_pct: 50.5, confidence: "high" },
        ],
        displayNames: S05_DISP,
        labelOffsetsS: { red_blood_cells_awake: 1.0, red_blood_cells_asleep: 9.0 },
        lineColor: "#5FD8D8", labelColor: "#FFFFFF",
      })}
      {DiagramSeg({ fromS: 18.45, durS: 6.98, src: BLOOD_CELL, keyframes: [
        { t: 0, scale: 1.3, fx: 75.3, fy: 50.5 },
        { t: 6.98, scale: 1.6, fx: 75.3, fy: 50.5 },
      ] })}
      {DiagramSeg({
        fromS: 25.87, durS: 2.93, src: MIRRORED_POUCH_CAM,
        keyframes: [
          { t: 0, scale: 1.0, fx: 51.5, fy: 42.5 },
          { t: 2.93, scale: 1.25, fx: 51.5, fy: 42.5 },
        ],
        labels: [{ feature: "liver", x_pct: 51.5, y_pct: 42.5, confidence: "high" }],
        displayNames: S05_DISP,
        labelOffsetsS: { liver: 2.17 },
        lineColor: "#5FD8D8", labelColor: "#FFFFFF",
      })}
      {DiagramSeg({
        fromS: 29.25, durS: 8.31, src: MIRRORED_POUCH_CAM,
        keyframes: [
          { t: 0, scale: 1.25, fx: 51.5, fy: 42.5 },
          { t: 2.0, scale: 1.35, fx: 40.0, fy: 28.0 },
          { t: 6.0, scale: 1.4, fx: 43.1, fy: 53.2 },
          { t: 8.31, scale: 1.4, fx: 43.1, fy: 53.2 },
        ],
        labels: [
          { feature: "mirrored_surface", x_pct: 40.0, y_pct: 28.0, confidence: "high" },
          { feature: "red_blood_cells", x_pct: 43.1, y_pct: 53.2, confidence: "high" },
        ],
        displayNames: S05_DISP,
        labelOffsetsS: { mirrored_surface: 2.0, red_blood_cells: 6.0 },
        lineColor: "#5FD8D8", labelColor: "#FFFFFF",
      })}
      {DiagramSeg({ fromS: 38.07, durS: 5.89, src: SIDE_BY_SIDE, keyframes: [
        { t: 0, scale: 1.1, fx: 20, fy: 50 },
        { t: 5.89, scale: 1.1, fx: 80, fy: 50 },
      ] })}
      {DiagramSeg({
        fromS: 44.56, durS: 6.90, src: VESSEL_CROSS,
        keyframes: [
          { t: 0, scale: 1.0, fx: 50, fy: 50 },
          { t: 6.90, scale: 1.3, fx: 47.9, fy: 53.6 },
        ],
        labels: [
          { feature: "red_blood_cells", x_pct: 47.9, y_pct: 53.6, confidence: "high" },
          { feature: "vessel_wall", x_pct: 39.5, y_pct: 28.5, confidence: "high" },
        ],
        displayNames: S05_DISP,
        labelOffsetsS: { red_blood_cells: 0.5, vessel_wall: 3.5 },
        lineColor: "#5FD8D8", labelColor: "#FFFFFF",
      })}
      {DiagramSeg({ fromS: 52.15, durS: 5.09, src: VESSEL_CROSS, keyframes: [
        { t: 0, scale: 1.3, fx: 47.9, fy: 53.6 },
        { t: 5.09, scale: 1.0, fx: 50, fy: 50 },
      ] })}
      {DiagramSeg({ fromS: 57.84, durS: 15.16, src: PHOTOACOUSTIC, keyframes: [
        { t: 0, scale: 1.0, fx: 50, fy: 50 },
        { t: 7.0, scale: 1.05, fx: 50, fy: 50 },
        { t: 15.16, scale: 1.3, fx: 50, fy: 45 },
      ] })}
    </>
  );
}

// ─── SCENE 06 mixed content, sequenced per Clip_Plan.json's letter order ───
const CIRCULATORY_INFOGRAPHIC = `${ASSET_ROOT}/Images/scene_06B_circulatory_infographic/illustration.png`;
const LAB_INSERT_06C = `${ASSET_ROOT}/Images/scene_06C_lab_insert/illustration.png`;
const S06B_DISP = { clot_formation: "Clot Formation", platelets: "Platelets", normal_blood_flow: "Normal Blood Flow" };

function Scene06Content() {
  return (
    <>
      {VideoSeg({ fromS: 0.0, durS: 6.3, file: "scene_06/Scene_06A_looped.mp4" })}
      {DiagramSeg({
        fromS: 6.3, durS: 6.3, src: CIRCULATORY_INFOGRAPHIC,
        keyframes: [
          { t: 0, scale: 1.15, fx: 36.0, fy: 47.0 },
          { t: 3.0, scale: 1.25, fx: 36.0, fy: 47.0 },
          { t: 6.3, scale: 1.25, fx: 75.6, fy: 59.8 },
        ],
        labels: [
          { feature: "clot_formation", x_pct: 36.9, y_pct: 49.3, confidence: "high" },
          { feature: "platelets", x_pct: 35.0, y_pct: 44.1, confidence: "high" },
          { feature: "normal_blood_flow", x_pct: 75.6, y_pct: 59.8, confidence: "high" },
        ],
        displayNames: S06B_DISP,
        labelOffsetsS: { clot_formation: 0.3, platelets: 1.0, normal_blood_flow: 4.0 },
        // scene_06B color-codes its own meaning (red=clot, blue=normal flow) per
        // Diagram_Blocking_Plans.md — do not sample those colors for the label lines,
        // fall back to white-on-black per Rule 1's fallback instead.
        lineColor: "#FFFFFF", labelColor: "#FFFFFF",
      })}
      {DiagramSeg({ fromS: 12.6, durS: 5.0, src: LAB_INSERT_06C, keyframes: [
        { t: 0, scale: 1.0, fx: 50, fy: 50 },
        { t: 5.0, scale: 1.25, fx: 50, fy: 45 },
      ] })}
      {VideoSeg({ fromS: 17.6, durS: 6.3, file: "scene_06/Scene_06D_looped.mp4" })}
      {VideoSeg({ fromS: 23.9, durS: 8.0, file: "scene_06/Scene_06E_looped.mp4" })}
      {VideoSeg({ fromS: 31.9, durS: 7.6, file: "scene_06/Scene_06F_looped.mp4" })}
      {VideoSeg({ fromS: 39.5, durS: 6.0, file: "scene_06/Scene_06G_looped.mp4" })}
      {VideoSeg({ fromS: 45.5, durS: 4.934, file: "scene_06/Scene_06H_looped.mp4" })}
    </>
  );
}

// ─── Main Composition ───────────────────────────────────────────────────────
export const GlassFrogDoc: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: "#0B0F1A" }}>
    {/* SCENE 01 — Glitch Hook — 3.855s (trimmed from the 4s generation floor per RESUME_NOTES) */}
    <Sequence from={s(T["scene_01"])} durationInFrames={s(AUDIO.scene_01)} layout="none">
      <AbsoluteFill>
        <SceneAudio sceneId="scene_01" />
        <VideoClip file="scene_01/Scene_01A_looped.mp4" />
      </AbsoluteFill>
    </Sequence>

    {/* SCENE 02 — Setup — 14.396s — Species Name Card */}
    <Sequence from={s(T["scene_02"])} durationInFrames={s(AUDIO.scene_02)} layout="none">
      <AbsoluteFill>
        <SceneAudio sceneId="scene_02" />
        {VideoSeg({ fromS: 0.0, durS: 7.2, file: "scene_02/Scene_02A_looped.mp4" })}
        {VideoSeg({ fromS: 7.2, durS: 7.196, file: "scene_02/Scene_02B_looped.mp4" })}
        <SceneOverlays overlays={OV.scene_02} />
      </AbsoluteFill>
    </Sequence>

    {/* SCENE 03 — Tease #1 — 50.898s — Scientific Diagram sub-pipeline, camera/reveal blocking plan */}
    <Sequence from={s(T["scene_03"])} durationInFrames={s(AUDIO.scene_03)} layout="none">
      <AbsoluteFill>
        <SceneAudio sceneId="scene_03" />
        <Scene03Diagram />
        <SceneOverlays overlays={OV.scene_03} />
      </AbsoluteFill>
    </Sequence>

    {/* SCENE 04 — Context Loop — 35.526s — Range Map + Location Card */}
    <Sequence from={s(T["scene_04"])} durationInFrames={s(AUDIO.scene_04)} layout="none">
      <AbsoluteFill>
        <SceneAudio sceneId="scene_04" />
        <Sequence from={0} durationInFrames={s(5.9)} layout="none">
          <RangeMapAnimation />
        </Sequence>
        {VideoSeg({ fromS: 5.9, durS: 5.9, file: "scene_04/Scene_04B_looped.mp4" })}
        {VideoSeg({ fromS: 11.8, durS: 5.9, file: "scene_04/Scene_04C_looped.mp4" })}
        {VideoSeg({ fromS: 17.7, durS: 5.9, file: "scene_04/Scene_04D_looped.mp4" })}
        {VideoSeg({ fromS: 23.6, durS: 7.4, file: "scene_04/Scene_04E_looped.mp4" })}
        {VideoSeg({ fromS: 31.0, durS: 4.526, file: "scene_04/Scene_04F_looped.mp4" })}
        <LocationCard text="Cloud Forests, Central & South America" startS={6.5} durS={3} />
      </AbsoluteFill>
    </Sequence>

    {/* SCENE 05 — Tease #2 — 73.004s — longest diagram beat, Fact Callouts + Anomaly Meter */}
    <Sequence from={s(T["scene_05"])} durationInFrames={s(AUDIO.scene_05)} layout="none">
      <AbsoluteFill>
        <SceneAudio sceneId="scene_05" />
        <Scene05Diagram />
        <SceneOverlays overlays={OV.scene_05} />
        <AnomalyMeter value={9} startS={44.8} durS={6} />
      </AbsoluteFill>
    </Sequence>

    {/* SCENE 06 — Reward — 50.434s — mixed live_footage + diagram, sequenced per Clip_Plan.json */}
    <Sequence from={s(T["scene_06"])} durationInFrames={s(AUDIO.scene_06)} layout="none">
      <AbsoluteFill>
        <SceneAudio sceneId="scene_06" />
        <Scene06Content />
        <SceneOverlays overlays={OV.scene_06} />
      </AbsoluteFill>
    </Sequence>

    {/* SCENE 07 — Hook Forward — 4.737s — no overlay */}
    <Sequence from={s(T["scene_07"])} durationInFrames={s(AUDIO.scene_07)} layout="none">
      <AbsoluteFill>
        <SceneAudio sceneId="scene_07" />
        <VideoClip file="scene_07/Scene_07A_looped.mp4" />
      </AbsoluteFill>
    </Sequence>
  </AbsoluteFill>
);
