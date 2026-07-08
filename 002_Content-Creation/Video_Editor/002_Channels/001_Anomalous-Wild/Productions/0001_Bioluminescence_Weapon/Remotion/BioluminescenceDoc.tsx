import React from "react";
import { Audio } from "@remotion/media";
import { AbsoluteFill, OffthreadVideo, Sequence, staticFile } from "remotion";
import { BioluminescenceTitleCard } from "./BioluminescenceTitleCard";
import { PhylogeneticTree } from "./PhylogeneticTree";
import { KenBurns } from "./KenBurns";
import { SceneOverlays, TimedOverlay } from "./SceneOverlay";

const FPS = 30;
const s = (seconds: number) => Math.round(seconds * FPS);

// ─── Audio durations (seconds, measured via ffprobe) ─────────────────────────

const AUDIO = {
  scene_01: 14.0,
  scene_03: 19.8,
  scene_04: 21.2,
  scene_05: 40.2,
  scene_06: 36.7,
  scene_07: 53.4,
  scene_08: 54.8,
  scene_09: 48.2,
  scene_10: 49.1,
  scene_11: 67.7,
};

const TITLE_CARD_S = 3;

// ─── Cumulative scene start times ─────────────────────────────────────────────

let _t = 0;
const T: Record<string, number> = {};
function nextScene(key: string, dur: number) { T[key] = _t; _t += dur; }

nextScene("scene_01", AUDIO.scene_01);
nextScene("scene_02", TITLE_CARD_S);
nextScene("scene_03", AUDIO.scene_03);
nextScene("scene_04", AUDIO.scene_04);
nextScene("scene_05", AUDIO.scene_05);
nextScene("scene_06", AUDIO.scene_06);
nextScene("scene_07", AUDIO.scene_07);
nextScene("scene_08", AUDIO.scene_08);
nextScene("scene_09", AUDIO.scene_09);
nextScene("scene_10", AUDIO.scene_10);
nextScene("scene_11", AUDIO.scene_11);

export const BIOLUMINESCENCE_DURATION_FRAMES = s(_t);

// ─── Clip types ───────────────────────────────────────────────────────────────

interface VideoClip {
  type: "video";
  sceneId: string;       // folder name under bioluminescence_weapon/
  cutStartS: number;     // seconds into the parent scene when this cut starts
  cutEndS: number;
}

interface ImageClip {
  type: "image";
  sceneId: string;
  cutStartS: number;
  cutEndS: number;
  zoomFrom?: number;
  zoomTo?: number;
  panX?: number;
  panY?: number;
}

interface RemotionClip {
  type: "remotion";
  component: React.ReactNode;
  cutStartS: number;
  cutEndS: number;
}

type Clip = VideoClip | ImageClip | RemotionClip;

// ─── MultiClipScene ───────────────────────────────────────────────────────────
// Renders an array of clips as nested Sequences within a parent scene window.
// Parent scene starts at T[sceneId], total duration = sceneDurS.

function MultiClipScene({
  sceneId,
  sceneDurS,
  audioId,
  clips,
  overlays,
}: {
  sceneId: string;
  sceneDurS: number;
  audioId?: string;
  clips: Clip[];
  overlays?: TimedOverlay[];
}) {
  return (
    <Sequence from={s(T[sceneId])} durationInFrames={s(sceneDurS)} layout="none">
      <AbsoluteFill>
        {/* Audio */}
        {audioId && (
          <Audio
            src={staticFile(`bioluminescence_weapon/${audioId}/audio.mp3`)}
            volume={1}
          />
        )}

        {/* Clips */}
        {clips.map((clip, i) => {
          const clipFrom    = s(clip.cutStartS);
          const clipDur     = s(clip.cutEndS - clip.cutStartS);

          if (clip.type === "video") {
            return (
              <Sequence key={i} from={clipFrom} durationInFrames={clipDur} layout="none">
                <AbsoluteFill>
                  <OffthreadVideo
                    src={staticFile(`bioluminescence_weapon/${clip.sceneId}/video_looped.mp4`)}
                    style={{ width: "100%", height: "100%", objectFit: "cover" }}
                    volume={0}
                  />
                </AbsoluteFill>
              </Sequence>
            );
          }

          if (clip.type === "image") {
            return (
              <Sequence key={i} from={clipFrom} durationInFrames={clipDur} layout="none">
                <AbsoluteFill>
                  <KenBurns
                    src={`bioluminescence_weapon/${clip.sceneId}/image.png`}
                    zoomFrom={clip.zoomFrom}
                    zoomTo={clip.zoomTo}
                    panX={clip.panX}
                    panY={clip.panY}
                  />
                </AbsoluteFill>
              </Sequence>
            );
          }

          if (clip.type === "remotion") {
            return (
              <Sequence key={i} from={clipFrom} durationInFrames={clipDur} layout="none">
                <AbsoluteFill>
                  {clip.component}
                </AbsoluteFill>
              </Sequence>
            );
          }

          return null;
        })}

        {/* Overlays sit on top of all clips */}
        {overlays && <SceneOverlays overlays={overlays} />}
      </AbsoluteFill>
    </Sequence>
  );
}

// Helper: shorthand clip constructors

const vid = (sceneId: string, cutStartS: number, cutEndS: number): VideoClip =>
  ({ type: "video", sceneId, cutStartS, cutEndS });

const img = (
  sceneId: string,
  cutStartS: number,
  cutEndS: number,
  zoomFrom = 1.0,
  zoomTo = 1.08,
  panX = 0,
  panY = 0
): ImageClip => ({ type: "image", sceneId, cutStartS, cutEndS, zoomFrom, zoomTo, panX, panY });

// ─── Overlay definitions ──────────────────────────────────────────────────────

const OV: Record<string, TimedOverlay[]> = {

  scene_03: [
    { data: { type: "callout", text: "< 200m — TWILIGHT ZONE",       position: "center" }, startS: 3,  durationS: 5 },
    { data: { type: "callout", text: "< 1000m — NO SUNLIGHT. EVER.", position: "center" }, startS: 9,  durationS: 5 },
  ],

  scene_04: [
    {
      data: { type: "species", name: "Sea Sparkle", scientific: "Noctiluca scintillans", fact: "Dinoflagellate" },
      startS: 6, durationS: 9,
    },
  ],

  scene_05: [
    {
      data: {
        type: "callout",
        text: "LUCIFERASE + LUCIFERIN + O₂",
        subtext: "→ cold light. zero heat wasted.",
        position: "center",
      },
      startS: 18, durationS: 10,
    },
  ],

  scene_06: [
    {
      data: { type: "callout", text: "40+", subtext: "INDEPENDENT EVOLUTIONS", position: "center" },
      startS: 28, durationS: 8,
    },
  ],

  scene_07: [
    { data: { type: "species", name: "Anglerfish", scientific: "Melanocetus johnsonii" },                  startS: 4,  durationS: 9 },
    { data: { type: "fact_flash", text: "Its light isn't its own. It's bacteria.", position: "bottom" },   startS: 20, durationS: 8 },
    {
      data: {
        type: "annotation",
        label: "Aliivibrio sp. bacteria inside esca",
        targetXPct: 0.45,
        targetYPct: 0.38,
      },
      startS: 17, durationS: 7,
    },
    { data: { type: "species", name: "Aliivibrio sp.", scientific: "Bioluminescent bacteria inside the esca" }, startS: 34, durationS: 9 },
  ],

  scene_08: [
    { data: { type: "species", name: "Hawaiian Bobtail Squid", scientific: "Euprymna scolopes" },  startS: 5,  durationS: 9 },
    {
      data: { type: "annotation", label: "Photophore light organs", targetXPct: 0.5, targetYPct: 0.65 },
      startS: 20, durationS: 7,
    },
    {
      data: { type: "callout", text: "COUNTER-ILLUMINATION", subtext: "No shadow. No silhouette. Gone.", position: "center" },
      startS: 34, durationS: 10,
    },
  ],

  scene_09: [
    { data: { type: "species", name: "Loosejaw Dragonfish", scientific: "Malacosteus niger" },              startS: 5,  durationS: 9 },
    {
      data: { type: "annotation", label: "Sub-orbital red photophore", targetXPct: 0.38, targetYPct: 0.55 },
      startS: 20, durationS: 7,
    },
    { data: { type: "callout", text: "SEES RED LIGHT.", subtext: "Nothing else in the deep can.", position: "center" }, startS: 22, durationS: 9 },
    { data: { type: "fact_flash", text: "It doesn't evolve the ability. It eats it.", position: "bottom" }, startS: 36, durationS: 8 },
  ],

  scene_10a: [
    { data: { type: "species", name: "Firefly Squid", scientific: "Watasenia scintillans" }, startS: 1, durationS: 8 },
  ],

  scene_10b: [
    { data: { type: "species", name: "Siphonophore", scientific: "Praya dubia", fact: "Can reach 40 metres in length" }, startS: 1, durationS: 8 },
  ],

  scene_10c: [
    { data: { type: "fact_flash", text: "Light as a weapon. As a decoy. As a tool.", position: "bottom" }, startS: 1, durationS: 8 },
  ],

  scene_11: [
    {
      data: { type: "callout", text: "CONVERGENT EVOLUTION", subtext: "The same solution. 40+ times. In unrelated life.", position: "center" },
      startS: 28, durationS: 12,
    },
    {
      data: { type: "callout", text: "EUROPA", subtext: "Ocean beneath 10–30km of ice", position: "center" },
      startS: 52, durationS: 12,
    },
  ],
};

// ─── scene_10 sub-clip timing ─────────────────────────────────────────────────

const CLIP_THIRD_S = AUDIO.scene_10 / 3; // ≈ 16.37s each

// ─── Main Composition ─────────────────────────────────────────────────────────

export const BioluminescenceDoc: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: "#000000" }}>

    {/* SCENE 01 — Anglerfish Hook — 14s — 3 cuts */}
    <MultiClipScene
      sceneId="scene_01"
      sceneDurS={AUDIO.scene_01}
      audioId="scene_01"
      clips={[
        vid("scene_01",  0,   5),   // Existing: ultra-macro lure in black
        vid("scene_01b", 5,  10),   // New Veo3: pull-back reveals face
        vid("scene_01c", 10, 14),   // New Kling: lure dims to black
      ]}
    />

    {/* SCENE 02 — Title Card — 3s — Remotion animation */}
    <Sequence from={s(T["scene_02"])} durationInFrames={s(TITLE_CARD_S)} layout="none">
      <AbsoluteFill>
        <BioluminescenceTitleCard />
      </AbsoluteFill>
    </Sequence>

    {/* SCENE 03 — Ocean Descent — 19.8s — 5 cuts */}
    <MultiClipScene
      sceneId="scene_03"
      sceneDurS={AUDIO.scene_03}
      audioId="scene_03"
      overlays={OV.scene_03}
      clips={[
        vid("scene_03b", 0,    4),   // New Kling: sunlit surface descending
        vid("scene_03c", 4,    8),   // New Kling: twilight zone
        vid("scene_03",  8,   12),   // Existing: descent clip
        vid("scene_03d", 12,  16),   // New Kling: midnight zone
        vid("scene_03e", 16, 19.8),  // New Kling: dense bioluminescent aggregation
      ]}
    />

    {/* SCENE 04 — Dinoflagellates — 21.2s — 5 cuts */}
    <MultiClipScene
      sceneId="scene_04"
      sceneDurS={AUDIO.scene_04}
      audioId="scene_04"
      overlays={OV.scene_04}
      clips={[
        vid("scene_04b",  0,    4),   // New Kling: beach at night, blue waves
        vid("scene_04c",  4,    8),   // New Veo3: wave close-up, blue explosion
        vid("scene_04",   8,   13),   // Existing: dinoflagellate cloud underwater
        vid("scene_04d",  13,  17),   // New Kling: individual organisms flaring
        img("scene_04e",  17, 21.2,   1.0, 1.1, 0, -20), // Flux KB: Noctiluca macro
      ]}
    />

    {/* SCENE 05 — Luciferase Chemistry — 40.2s — 7 cuts */}
    <MultiClipScene
      sceneId="scene_05"
      sceneDurS={AUDIO.scene_05}
      audioId="scene_05"
      overlays={OV.scene_05}
      clips={[
        vid("scene_05b",  0,   5),   // New Kling: wide glowing ctenophore
        vid("scene_05c",  5,  10),   // New Kling: macro bioluminescent light organ
        vid("scene_05",  10,  17),   // Existing: molecular animation
        img("scene_05e",  17, 25,  1.0, 1.06, 30, 0),  // Flux KB: luciferase diagram
        vid("scene_05d",  25, 31),   // New Kling: incandescent vs cold light
        vid("scene_05f",  31, 36),   // New Kling: wide ocean multiple species
        vid("scene_05c",  36, 40.2), // Kling: macro glow (reuse, different window)
      ]}
    />

    {/* SCENE 06 — Phylogenetic Tree — 36.7s — Full Remotion animation */}
    <Sequence from={s(T["scene_06"])} durationInFrames={s(AUDIO.scene_06)} layout="none">
      <AbsoluteFill>
        <Audio src={staticFile("bioluminescence_weapon/scene_06/audio.mp3")} volume={1} />
        <PhylogeneticTree />
      </AbsoluteFill>
    </Sequence>

    {/* SCENE 07 — Anglerfish Deep Dive — 53.4s — 12 cuts */}
    <MultiClipScene
      sceneId="scene_07"
      sceneDurS={AUDIO.scene_07}
      audioId="scene_07"
      overlays={OV.scene_07}
      clips={[
        vid("scene_07b",  0,   5),   // New Kling: wide anglerfish hovering
        vid("scene_07",   5,   9),   // Existing: macro push-in on face — HERO
        vid("scene_07c",  9,  13),   // New Kling: lure pulsing rhythmically
        vid("scene_07d",  13, 17),   // New Kling: prey fish in background
        img("scene_07e",  17, 22,  1.0, 1.08, 0, 20),   // Flux KB: esca anatomy diagram
        vid("scene_07f",  22, 27),   // New Veo3: lure dims/brightens — bacteria reveal
        vid("scene_07g",  27, 31),   // New Kling: prey fish closer
        vid("scene_07h",  31, 36),   // New Kling: anglerfish jaw detail
        vid("scene_07i",  36, 41),   // New Veo3: prey at lure — HERO tension shot
        vid("scene_07j",  41, 46),   // New Kling: near-black, only lure glow remains
        img("scene_07k",  46, 50,  1.0, 1.06, -20, 0),  // Flux KB: Aliivibrio bacteria
        vid("scene_07b",  50, 53.4), // Kling: wide anglerfish closing (reuse)
      ]}
    />

    {/* SCENE 08 — Bobtail Squid — 54.8s — 10 cuts */}
    <MultiClipScene
      sceneId="scene_08"
      sceneDurS={AUDIO.scene_08}
      audioId="scene_08"
      overlays={OV.scene_08}
      clips={[
        vid("scene_08b",  0,   5),   // New Kling: overhead moonlit water
        vid("scene_08",   5,  10),   // Existing: squid overhead/POV — HERO
        vid("scene_08c",  10, 15),   // New Kling: POV from below, squid vs moon
        vid("scene_08d",  15, 20),   // New Kling: photophores activating
        img("scene_08h",  20, 26,  1.0, 1.07, 25, 0),   // Flux KB: light organ anatomy
        vid("scene_08e",  26, 32),   // New Veo3: silhouette disappears — HERO
        vid("scene_08f",  32, 37),   // New Kling: predator POV — nothing there
        img("scene_08i",  37, 43,  1.0, 1.06, 0, -15),  // Flux KB: counter-illumination diagram
        vid("scene_08g",  43, 48),   // New Kling: squid swimming free
        vid("scene_08e",  48, 54.8), // Veo3: squid vanishes again (different window)
      ]}
    />

    {/* SCENE 09 — Dragonfish — 48.2s — 9 cuts (the centrepiece) */}
    <MultiClipScene
      sceneId="scene_09"
      sceneDurS={AUDIO.scene_09}
      audioId="scene_09"
      overlays={OV.scene_09}
      clips={[
        vid("scene_09b",  0,   5),   // New Veo3: black then red line — HERO cold open
        vid("scene_09c",  5,   9),   // New Veo3: dragonfish side profile, red photophores
        vid("scene_09",   9,  14),   // Existing: red-light POV — HERO centrepiece
        vid("scene_09d",  14, 18),   // New Kling: prey fish, oblivious
        img("scene_09e",  18, 24,  1.0, 1.05, 40, 0),   // Flux KB: visible spectrum diagram
        img("scene_09f",  24, 30,  1.05, 1.1, -20, 10), // Flux KB: dragonfish eye anatomy
        vid("scene_09g",  30, 37),   // New Veo3: full red-light POV hunt — HERO
        vid("scene_09h",  37, 42),   // New Kling: prey disappears in red flash
        vid("scene_09i",  42, 48.2), // New Kling: dragonfish fades to black
      ]}
    />

    {/* SCENE 10 — Quick-cut triptych (10a / 10b / 10c)
        One narration audio covers the full 49.1s window.
        Three sub-clips each fill their ~16.4s third. */}
    <Sequence from={s(T["scene_10"])} durationInFrames={s(AUDIO.scene_10)} layout="none">
      <AbsoluteFill>
        {/* Audio covers the whole 49.1s */}
        <Audio src={staticFile("bioluminescence_weapon/scene_10a/audio.mp3")} volume={1} />

        {/* 10a — Firefly Squid (0 → 16.37s) */}
        <Sequence from={0} durationInFrames={s(CLIP_THIRD_S)} layout="none">
          <AbsoluteFill>
            <Sequence from={0}               durationInFrames={s(4.1)} layout="none"><AbsoluteFill><OffthreadVideo src={staticFile("bioluminescence_weapon/scene_10a2/video_looped.mp4")} style={{ width: "100%", height: "100%", objectFit: "cover" }} volume={0} /></AbsoluteFill></Sequence>
            <Sequence from={s(4.1)}          durationInFrames={s(4.1)} layout="none"><AbsoluteFill><OffthreadVideo src={staticFile("bioluminescence_weapon/scene_10a/video_looped.mp4")}  style={{ width: "100%", height: "100%", objectFit: "cover" }} volume={0} /></AbsoluteFill></Sequence>
            <Sequence from={s(8.2)}          durationInFrames={s(4.1)} layout="none"><AbsoluteFill><OffthreadVideo src={staticFile("bioluminescence_weapon/scene_10a3/video_looped.mp4")} style={{ width: "100%", height: "100%", objectFit: "cover" }} volume={0} /></AbsoluteFill></Sequence>
            <Sequence from={s(12.3)}         durationInFrames={s(CLIP_THIRD_S - 12.3)} layout="none"><AbsoluteFill><OffthreadVideo src={staticFile("bioluminescence_weapon/scene_10a4/video_looped.mp4")} style={{ width: "100%", height: "100%", objectFit: "cover" }} volume={0} /></AbsoluteFill></Sequence>
            <SceneOverlays overlays={OV.scene_10a} />
          </AbsoluteFill>
        </Sequence>

        {/* 10b — Siphonophore (16.37s → 32.73s) */}
        <Sequence from={s(CLIP_THIRD_S)} durationInFrames={s(CLIP_THIRD_S)} layout="none">
          <AbsoluteFill>
            <Sequence from={0}      durationInFrames={s(4.1)} layout="none"><AbsoluteFill><OffthreadVideo src={staticFile("bioluminescence_weapon/scene_10b/video_looped.mp4")}  style={{ width: "100%", height: "100%", objectFit: "cover" }} volume={0} /></AbsoluteFill></Sequence>
            <Sequence from={s(4.1)} durationInFrames={s(4.1)} layout="none"><AbsoluteFill><OffthreadVideo src={staticFile("bioluminescence_weapon/scene_10b2/video_looped.mp4")} style={{ width: "100%", height: "100%", objectFit: "cover" }} volume={0} /></AbsoluteFill></Sequence>
            <Sequence from={s(8.2)} durationInFrames={s(4.1)} layout="none"><AbsoluteFill><OffthreadVideo src={staticFile("bioluminescence_weapon/scene_10b3/video_looped.mp4")} style={{ width: "100%", height: "100%", objectFit: "cover" }} volume={0} /></AbsoluteFill></Sequence>
            <Sequence from={s(12.3)} durationInFrames={s(CLIP_THIRD_S - 12.3)} layout="none"><AbsoluteFill><OffthreadVideo src={staticFile("bioluminescence_weapon/scene_10b4/video_looped.mp4")} style={{ width: "100%", height: "100%", objectFit: "cover" }} volume={0} /></AbsoluteFill></Sequence>
            <SceneOverlays overlays={OV.scene_10b} />
          </AbsoluteFill>
        </Sequence>

        {/* 10c — Jellyfish Decoy (32.73s → 49.1s) */}
        <Sequence from={s(CLIP_THIRD_S * 2)} durationInFrames={s(AUDIO.scene_10 - CLIP_THIRD_S * 2)} layout="none">
          <AbsoluteFill>
            <Sequence from={0}      durationInFrames={s(4.1)} layout="none"><AbsoluteFill><OffthreadVideo src={staticFile("bioluminescence_weapon/scene_10c2/video_looped.mp4")} style={{ width: "100%", height: "100%", objectFit: "cover" }} volume={0} /></AbsoluteFill></Sequence>
            <Sequence from={s(4.1)} durationInFrames={s(4.1)} layout="none"><AbsoluteFill><OffthreadVideo src={staticFile("bioluminescence_weapon/scene_10c3/video_looped.mp4")} style={{ width: "100%", height: "100%", objectFit: "cover" }} volume={0} /></AbsoluteFill></Sequence>
            <Sequence from={s(8.2)} durationInFrames={s(4.1)} layout="none"><AbsoluteFill><OffthreadVideo src={staticFile("bioluminescence_weapon/scene_10c/video_looped.mp4")}  style={{ width: "100%", height: "100%", objectFit: "cover" }} volume={0} /></AbsoluteFill></Sequence>
            <Sequence from={s(12.3)} durationInFrames={s(AUDIO.scene_10 - CLIP_THIRD_S * 2 - 12.3)} layout="none"><AbsoluteFill><OffthreadVideo src={staticFile("bioluminescence_weapon/scene_10c4/video_looped.mp4")} style={{ width: "100%", height: "100%", objectFit: "cover" }} volume={0} /></AbsoluteFill></Sequence>
            <SceneOverlays overlays={OV.scene_10c} />
          </AbsoluteFill>
        </Sequence>
      </AbsoluteFill>
    </Sequence>

    {/* SCENE 11 — Convergent Evolution / Europa — 67.7s — 12 cuts */}
    <MultiClipScene
      sceneId="scene_11"
      sceneDurS={AUDIO.scene_11}
      audioId="scene_11"
      overlays={OV.scene_11}
      clips={[
        vid("scene_11b",  0,   5),   // New Kling: callback anglerfish
        vid("scene_11c",  5,  10),   // New Kling: callback dinoflagellate wave
        vid("scene_11d",  10, 15),   // New Kling: callback bobtail squid vanishing
        vid("scene_11e",  15, 20),   // New Kling: callback dragonfish red sweep
        vid("scene_11f",  20, 28),   // New Veo3: all species glowing — the spectacle
        vid("scene_11g",  28, 35),   // New Kling: rising through water column
        vid("scene_11h",  35, 43),   // New Kling: breaking surface, pulling to space
        vid("scene_11",   43, 50),   // Existing: epic pullback — HERO
        img("scene_11i",  50, 56,  1.06, 1.0,  0,    0),    // Flux KB: Earth from space
        img("scene_11j",  56, 61,  1.0,  1.1,  -30,  10),   // Flux KB: Jupiter + Europa
        img("scene_11k",  61, 66,  1.0,  1.12,  20, -20),   // Flux KB: Europa ice crust close-up
        vid("scene_11m",  66, 67.7), // New Veo3: single bioluminescent pulse, fades — FINAL SHOT
      ]}
    />

    {/* SCENE 12 — REMOVED. User will add custom YouTube end card. */}

  </AbsoluteFill>
);
