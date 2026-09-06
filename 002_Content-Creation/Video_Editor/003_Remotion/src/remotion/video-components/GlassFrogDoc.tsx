import React from "react";
import { Audio } from "@remotion/media";
import {
  AbsoluteFill,
  Freeze,
  Img,
  OffthreadVideo,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  Easing,
} from "remotion";
import { DiagramLabels } from "./DiagramLabels";
import { SceneOverlays, TimedOverlay } from "./SceneOverlay";

// ─── Setup ─────────────────────────────────────────────────────────────────
const FPS = 30;
const s = (seconds: number) => Math.round(seconds * FPS);
// Frame-exact seconds: pass a whole frame count where a Seg wants seconds, so
// s(F(n)) === n with no rounding drift. Used by the 2026-08-30 systemic duration
// fix so every VideoSeg is laid out in integer frames against real clip lengths.
const F = (frames: number) => frames / FPS;
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

// ─── Cumulative scene start frames ───────────────────────────────────────
// Accumulate in whole FRAMES, not seconds: each scene's start is the previous
// scene's start plus its rounded duration, so scene N ends on exactly the frame
// scene N+1 begins. Summing seconds then rounding (s(a+b) vs s(a)+s(b)) left a
// 1-frame navy gap at some scene cuts (2026-08-31 black-frame scan).
const SCENE_FRAMES: Record<string, number> = {};
let _f = 0;
function nextScene(key: string, durS: number) {
  SCENE_FRAMES[key] = _f;
  _f += s(durS);
}
nextScene("scene_01", AUDIO.scene_01);
nextScene("scene_02", AUDIO.scene_02);
nextScene("scene_03", AUDIO.scene_03);
nextScene("scene_04", AUDIO.scene_04);
nextScene("scene_05", AUDIO.scene_05);
nextScene("scene_06", AUDIO.scene_06);
nextScene("scene_07", AUDIO.scene_07);

export const GLASS_FROG_DURATION_FRAMES = _f;

// ─── Small helpers ─────────────────────────────────────────────────────────

// Narration track — all 7 scene VOs laid back-to-back with HARD boundaries (the
// visual layer crossfades between scenes, the narration must not — Glass Frog
// note 1). A 3-frame edge fade on each clip kills the click at the joins without
// clipping any words.
const NARRATION_EDGE_FADE_F = 3;
function NarrationTrack() {
  const order = ["scene_01", "scene_02", "scene_03", "scene_04", "scene_05", "scene_06", "scene_07"] as const;
  return (
    <>
      {order.map((sceneId) => {
        const durF = s(AUDIO[sceneId]);
        return (
          <Sequence key={sceneId} from={SCENE_FRAMES[sceneId]} durationInFrames={durF} layout="none">
            <Audio
              src={staticFile(`${ASSET_ROOT}/Narration_Audio/${sceneId}.mp3`)}
              volume={(f) =>
                interpolate(
                  f,
                  [0, NARRATION_EDGE_FADE_F, durF - NARRATION_EDGE_FADE_F, durF],
                  [0, 1, 1, 0],
                  { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
                )
              }
            />
          </Sequence>
        );
      })}
    </>
  );
}

// Visual layer for one scene: extends DIAGRAM_XFADE_S past the scene's nominal end
// and fades out there while the next scene (starting exactly on the nominal
// boundary) fades in — so every scene cut is a ~0.5s cross-dissolve (note 1),
// nominal boundaries stay frame-exact, and the total stays locked.
const SCENE_XFADE_S = 0.5;
function SceneVisual({
  scene,
  isFirst,
  isLast,
  children,
}: {
  scene: keyof typeof AUDIO;
  isFirst?: boolean;
  isLast?: boolean;
  children: React.ReactNode;
}) {
  const startF = SCENE_FRAMES[scene];
  const nominalEndF = startF + s(AUDIO[scene]);
  const xf = s(SCENE_XFADE_S);
  // extend past nominal end by xf so this scene stays fully opaque underneath the
  // next scene's fade-in (true crossfade, no background bleed).
  const durF = (isLast ? nominalEndF : nominalEndF + xf) - startF;
  const holdEndF = nominalEndF - startF;
  return (
    <Sequence from={startF} durationInFrames={durF} layout="none">
      <SceneFade fadeInF={isFirst ? 0 : xf} holdEndF={isLast ? Infinity : holdEndF}>
        {children}
      </SceneFade>
    </Sequence>
  );
}
// The outgoing scene FREEZES on its last real frame for the xf tail (video clips
// would otherwise loop past their real footage), staying fully opaque while the
// next scene fades in on top — a true cross-dissolve with no loop, no bg bleed.
function SceneFade({ children, fadeInF, holdEndF }: { children: React.ReactNode; fadeInF: number; holdEndF: number }) {
  const frame = useCurrentFrame();
  const opIn = fadeInF > 0 ? interpolate(frame, [0, fadeInF], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) : 1;
  const frozen = Number.isFinite(holdEndF) && frame >= holdEndF;
  return (
    <AbsoluteFill style={{ opacity: opIn }}>
      <Freeze active={frozen} frame={Math.max(0, (Number.isFinite(holdEndF) ? holdEndF : 1) - 1)}>
        {children}
      </Freeze>
    </AbsoluteFill>
  );
}

function VideoClip({ file, muted = true, fadeInS = 0 }: { file: string; muted?: boolean; fadeInS?: number }) {
  const frame = useCurrentFrame();
  const opacity = fadeInS > 0
    ? interpolate(frame, [0, s(fadeInS)], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })
    : 1;
  return (
    <AbsoluteFill style={{ opacity }}>
      <OffthreadVideo
        src={staticFile(`${ASSET_ROOT}/Video_Clips/${file}`)}
        style={{ width: "100%", height: "100%", objectFit: "cover" }}
        volume={muted ? 0 : 1}
      />
    </AbsoluteFill>
  );
}

// Holding a shot past its real footage is done by VideoSegFilled (below) via
// Remotion's <Freeze> — no pre-extracted still frame needed. (Superseded the
// earlier FreezeFrame/FreezeSeg PNG approach on 2026-08-30.)

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

// Per-segment eased interpolation: find the keyframe pair the current frame sits
// between and ease (in-out) within it. Identical consecutive keyframes = a true
// hold. This replaces Remotion's straight `interpolate` over the whole range, so
// EVERY camera move eases in and out and the camera can sit perfectly still under
// a label (Glass Frog note 4).
function easedTrack(frame: number, fps: number, keyframes: CamKeyframe[], pick: (k: CamKeyframe) => number): number {
  if (keyframes.length === 1) return pick(keyframes[0]);
  const f = frame / fps;
  if (f <= keyframes[0].t) return pick(keyframes[0]);
  const last = keyframes[keyframes.length - 1];
  if (f >= last.t) return pick(last);
  for (let i = 0; i < keyframes.length - 1; i++) {
    const a = keyframes[i];
    const b = keyframes[i + 1];
    if (f >= a.t && f <= b.t) {
      if (b.t === a.t) return pick(b);
      const raw = (f - a.t) / (b.t - a.t);
      const e = Easing.inOut(Easing.ease)(raw);
      return pick(a) + (pick(b) - pick(a)) * e;
    }
  }
  return pick(last);
}

function DiagramCamera({ src, keyframes }: { src: string; keyframes: CamKeyframe[] }) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const kf = keyframes.length ? keyframes : [{ t: 0, scale: 1, fx: 50, fy: 50 }];
  const scale = easedTrack(frame, fps, kf, (k) => k.scale);
  const fx = easedTrack(frame, fps, kf, (k) => k.fx);
  const fy = easedTrack(frame, fps, kf, (k) => k.fy);
  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#0B0F1A" }}>
      {/* Remotion's <Img> (not a raw <img>) — it suspends the frame until the
          image is decoded, so a diagram never flashes the navy background for a
          few frames at a segment boundary while a new illustration loads
          (2026-08-30: that was the real cause of the remaining scene 03/05
          black frames, not timeline gaps). */}
      <Img
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

// ─── Diagram SHOT model (2026-09-01 rework) ──────────────────────────────────
// A "shot" is ONE illustration on screen for one continuous span, with ONE eased
// camera path. Consecutive shots that use the same image are authored as a single
// shot (no internal cut) — this kills the "remount jump" where the picture
// appeared to teleport between two Sequences of the same image. A cut only
// happens when the image actually changes, and DiagramScene crossfades those.
interface DiagramLabelPoint {
  feature: string;
  x_pct: number;
  y_pct: number;
  confidence: "high" | "low" | "not_found";
}
interface Waypoint {
  atS: number; // seconds from this shot's start
  scale: number;
  fx: number;
  fy: number;
  holdS?: number; // hold here this long before easing to the next waypoint (a dwell)
}
interface DiagramShot {
  img: string;
  durS: number; // nominal on-screen span (crossfade overlap is added on top)
  waypoints: Waypoint[];
  labels?: DiagramLabelPoint[];
  displayNames?: Record<string, string>;
  labelOffsetsS?: Record<string, number>;
  labelHoldS?: number;
  descriptions?: Record<string, string>;
  lineColor?: string;
  labelColor?: string;
  accentColor?: string;
  labelScale?: number;
}

function buildPath(wps: Waypoint[]): CamKeyframe[] {
  const kf: CamKeyframe[] = [];
  for (const w of wps) {
    kf.push({ t: w.atS, scale: w.scale, fx: w.fx, fy: w.fy });
    if (w.holdS && w.holdS > 0) kf.push({ t: w.atS + w.holdS, scale: w.scale, fx: w.fx, fy: w.fy });
  }
  return kf;
}

const DIAGRAM_XFADE_S = 0.5;

// Lay shots end-to-end in frame-exact space. Each shot's Sequence extends
// DIAGRAM_XFADE_S past its nominal end and fades out there; the next shot starts
// exactly on the nominal boundary and fades in — so image changes cross-dissolve
// while nominal boundaries stay frame-exact and the scene total stays locked.
function DiagramScene({ shots, sceneEndS }: { shots: DiagramShot[]; sceneEndS: number }) {
  const sceneEndF = s(sceneEndS);
  const xf = s(DIAGRAM_XFADE_S);
  let cursorF = 0;
  const starts = shots.map((sh) => {
    const startF = cursorF;
    cursorF += s(sh.durS);
    return startF;
  });
  // absorb any rounding remainder into the last shot so it reaches scene end
  return (
    <>
      {shots.map((sh, i) => {
        const startF = starts[i];
        const nominalEndF = i === shots.length - 1 ? sceneEndF : starts[i + 1];
        const isFirst = i === 0;
        const isLast = i === shots.length - 1;
        // extend every non-final shot xf past its nominal end so it stays fully
        // opaque underneath the next shot's fade-in (true crossfade).
        const seqDurF = (isLast ? sceneEndF : nominalEndF + xf) - startF;
        return (
          <Sequence key={`${sh.img}-${startF}`} from={startF} durationInFrames={seqDurF} layout="none">
            <DiagramShotBody shot={sh} fadeInF={isFirst ? 0 : xf} />
          </Sequence>
        );
      })}
    </>
  );
}

function DiagramShotBody({
  shot,
  fadeInF,
}: {
  shot: DiagramShot;
  fadeInF: number;
}) {
  const frame = useCurrentFrame();
  // Crossfade = the INCOMING shot fades in on top; the outgoing shot stays fully
  // opaque underneath (its Sequence just extends past its nominal end). Fading
  // both would let the #0B0F1A background bleed through and darken the dissolve.
  const opIn = fadeInF > 0 ? interpolate(frame, [0, fadeInF], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) : 1;
  return (
    <AbsoluteFill style={{ opacity: opIn }}>
      <DiagramCamera src={shot.img} keyframes={buildPath(shot.waypoints)} />
      {shot.labels && shot.labels.length > 0 && (
        <DiagramLabels
          labels={shot.labels}
          labelStaggerS={1.5}
          displayNames={shot.displayNames ?? {}}
          labelOffsetsS={shot.labelOffsetsS}
          labelHoldS={shot.labelHoldS}
          descriptions={shot.descriptions}
          lineColor={shot.lineColor}
          labelColor={shot.labelColor}
          accentColor={shot.accentColor}
          scale={shot.labelScale ?? 1}
        />
      )}
    </AbsoluteFill>
  );
}

// ─── legacy single diagram segment (still used for scene 06's isolated beats) ─
interface DiagramSegment {
  fromS: number;
  durS: number;
  src: string;
  keyframes: CamKeyframe[];
  labels?: DiagramLabelPoint[];
  displayNames?: Record<string, string>;
  labelOffsetsS?: Record<string, number>;
  labelHoldS?: number;
  labelScale?: number;
  lineColor?: string;
  labelColor?: string;
}
function DiagramSegInner(seg: DiagramSegment) {
  return (
    <AbsoluteFill>
      <DiagramCamera src={seg.src} keyframes={seg.keyframes} />
      {seg.labels && (
        <DiagramLabels
          labels={seg.labels}
          labelStaggerS={1.5}
          displayNames={seg.displayNames ?? {}}
          labelOffsetsS={seg.labelOffsetsS}
          labelHoldS={seg.labelHoldS}
          lineColor={seg.lineColor}
          labelColor={seg.labelColor}
          scale={seg.labelScale ?? 1.15}
        />
      )}
    </AbsoluteFill>
  );
}
function DiagramSeg(seg: DiagramSegment) {
  return (
    <Sequence key={`${seg.src}-${seg.fromS}`} from={s(seg.fromS)} durationInFrames={s(seg.durS)} layout="none">
      <DiagramSegInner {...seg} />
    </Sequence>
  );
}

// ─── ChainScene — lay a scene's video / diagram / node segments end-to-end with
// a ~0.5s cross-dissolve at EVERY cut (Glass Frog Note 1 — Tony wants the
// scene_02-style dissolve on all cuts, not just scene boundaries + diagram image
// changes). Each non-final segment's Sequence extends CHAIN_XF_F past its nominal
// end and FREEZES its last real frame there (a video must never play past its
// floor(real) length — that's the loop-flash bug); the next segment starts on the
// nominal boundary and fades in on top. Nominal boundaries stay frame-exact; the
// scene total stays locked. Freeze-under + live-over is the same crossfade shape
// as scene_02 / VideoSegFilled (Tony-approved) — never two *live* videos at once. ─
const CHAIN_XF_F = 15;
type ChainSeg =
  | { kind: "video"; file: string; durF: number }
  | { kind: "node"; node: React.ReactNode; durF: number };

function ChainScene({ segs, tailFreeze = false }: { segs: ChainSeg[]; tailFreeze?: boolean }) {
  let cursor = 0;
  const starts = segs.map((sg) => { const s0 = cursor; cursor += sg.durF; return s0; });
  const total = cursor;
  return (
    <>
      {segs.map((sg, i) => {
        const startF = starts[i];
        const isLast = i === segs.length - 1;
        const nominalEndF = isLast ? total : starts[i + 1];
        const extend = !isLast || tailFreeze;
        const seqDurF = (extend ? nominalEndF + CHAIN_XF_F : nominalEndF) - startF;
        return (
          <Sequence key={i} from={startF} durationInFrames={seqDurF} layout="none">
            <ChainSegBody seg={sg} fadeInF={i === 0 ? 0 : CHAIN_XF_F} realDurF={nominalEndF - startF} />
          </Sequence>
        );
      })}
    </>
  );
}
function ChainSegBody({ seg, fadeInF, realDurF }: { seg: ChainSeg; fadeInF: number; realDurF: number }) {
  const frame = useCurrentFrame();
  const opIn = fadeInF > 0
    ? interpolate(frame, [0, fadeInF], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })
    : 1;
  const frozen = frame >= realDurF;
  if (seg.kind === "node") {
    return <AbsoluteFill style={{ opacity: opIn }}>{seg.node}</AbsoluteFill>;
  }
  return (
    <AbsoluteFill style={{ opacity: opIn }}>
      <Freeze active={frozen} frame={Math.max(0, realDurF - 1)}>
        <OffthreadVideo
          src={staticFile(`${ASSET_ROOT}/Video_Clips/${seg.file}`)}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
          volume={0}
        />
      </Freeze>
    </AbsoluteFill>
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

// ─── Scene-6 tail shots (06F → 06G → 06H) ────────────────────────────────────
// 06F and 06H are "vanish" beats Seedance 1.5 can't animate (no transparency
// dissolve): the clip plays, then cross-dissolves to its generated end-frame
// still (frog gone into the leaf). Anti-tear rules for the 2026-09-03 horizontal-
// band artifact Tony caught at the 06F→06G boundary:
//  1. Each shot's OffthreadVideo is fully faded out AND UNMOUNTED at least ~12
//     frames before that clip's real footage ends — the decoder is never asked
//     for a near-boundary frame.
//  2. Never two live OffthreadVideos at once. Held tails use a pre-extracted
//     still PNG, not <Freeze><OffthreadVideo/></Freeze>.
//  3. Every tail boundary is a real ~1.3s cross-dissolve (incoming fades in on
//     top; outgoing holds its last still underneath at full opacity).

// VanishShot — video plays `videoPlayF` frames, dissolves to `endFrame` over
// `dissolveF`, then the still holds (subtle drift) to the end of this Sequence.
function VanishShot({
  file, endFrame, videoPlayF, dissolveF, fadeInF = 0,
}: { file: string; endFrame: string; videoPlayF: number; dissolveF: number; fadeInF?: number }) {
  const frame = useCurrentFrame();
  const shotOpacity = fadeInF > 0
    ? interpolate(frame, [0, fadeInF], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })
    : 1;
  const videoGoneF = videoPlayF + dissolveF;
  const vidOpacity = interpolate(frame, [videoPlayF, videoGoneF], [1, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.ease),
  });
  const kb = interpolate(frame, [videoPlayF, videoGoneF + 90], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const stillScale = 1 + 0.035 * kb;
  return (
    <AbsoluteFill style={{ opacity: shotOpacity }}>
      <AbsoluteFill style={{ transform: `scale(${stillScale})`, transformOrigin: "50% 50%" }}>
        <Img src={staticFile(`${ASSET_ROOT}/${endFrame}`)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      </AbsoluteFill>
      {frame < videoGoneF && (
        <AbsoluteFill style={{ opacity: vidOpacity }}>
          <OffthreadVideo
            src={staticFile(`${ASSET_ROOT}/Video_Clips/${file}`)}
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
            volume={0}
          />
        </AbsoluteFill>
      )}
    </AbsoluteFill>
  );
}

// HeldVideoShot — video plays `videoPlayF` frames then cross-dissolves to a
// pre-extracted hold still that Ken-Burns'es on to fill the rest of the Sequence,
// so a short clip still gets real screen time (Tony: "06G is too fast").
function HeldVideoShot({
  file, holdStill, videoPlayF, fadeInF = 0,
}: { file: string; holdStill: string; videoPlayF: number; fadeInF?: number }) {
  const frame = useCurrentFrame();
  const shotOpacity = fadeInF > 0
    ? interpolate(frame, [0, fadeInF], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })
    : 1;
  const XF = 18;
  const vidOpacity = interpolate(frame, [videoPlayF - XF, videoPlayF], [1, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.ease),
  });
  const kb = interpolate(frame, [videoPlayF - XF, videoPlayF + 200], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const stillScale = 1.02 + 0.05 * kb;
  return (
    <AbsoluteFill style={{ opacity: shotOpacity }}>
      <AbsoluteFill style={{ transform: `scale(${stillScale})`, transformOrigin: "52% 46%" }}>
        <Img src={staticFile(`${ASSET_ROOT}/${holdStill}`)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      </AbsoluteFill>
      {frame < videoPlayF && (
        <AbsoluteFill style={{ opacity: vidOpacity }}>
          <OffthreadVideo
            src={staticFile(`${ASSET_ROOT}/Video_Clips/${file}`)}
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
            volume={0}
          />
        </AbsoluteFill>
      )}
    </AbsoluteFill>
  );
}

// ─── VideoSegFilled — the "never loop, never regenerate" fallback ──────────────
// A clip whose beat (targetS) is longer than the real generated footage (realS)
// plays for its real length, then holds its final frame — via Remotion's <Freeze>,
// no pre-extracted still needed — for the remaining `targetS - realS` seconds.
// The held frame is NOT static: a slow Ken Burns push + drift (KenBurns below)
// runs from the dissolve point onward so the shortfall reads as an intentional
// settle with the camera still breathing, never a dead freeze. The zoom always
// stays large enough to cover the pan, so no black edge is ever revealed.
// When realS >= targetS this is just a plain trimmed VideoSeg. Assembly-side
// half of the clip_durations.py padding rule: the supervisor pads + trims so
// this rarely fires; when it does the pipeline never loops the source
// (OffthreadVideo loop-back = the 0003 flash-cut bug) and never regenerates.
function VideoSegFilled(seg: {
  fromS: number;
  targetS: number;
  realS: number;
  file: string;
  dissolveS?: number;
}) {
  const dissolveS = seg.dissolveS ?? 0.6;
  const playS = Math.min(seg.realS, seg.targetS);
  const needFillS = Math.max(0, seg.targetS - seg.realS);
  const realFrames = s(playS);

  if (needFillS <= 0) {
    return VideoSeg({ fromS: seg.fromS, durS: seg.targetS, file: seg.file });
  }

  const src = staticFile(`${ASSET_ROOT}/Video_Clips/${seg.file}`);
  const fadeStartFrame = Math.max(0, realFrames - s(dissolveS));
  const endFrame = s(seg.targetS);
  return (
    <Sequence
      key={`filled-${seg.file}-${seg.fromS}`}
      from={s(seg.fromS)}
      durationInFrames={endFrame}
      layout="none"
    >
      <KenBurns startFrame={fadeStartFrame} endFrame={endFrame} holdSpanS={dissolveS + needFillS}>
        {/* frozen last frame underneath, revealed as the live clip fades out */}
        <AbsoluteFill>
          <Freeze frame={Math.max(0, realFrames - 1)}>
            <OffthreadVideo src={src} style={{ width: "100%", height: "100%", objectFit: "cover" }} volume={0} />
          </Freeze>
        </AbsoluteFill>
        <FadeOutTail totalFrames={endFrame} holdStartFrame={realFrames} dissolveFrames={s(dissolveS)}>
          <OffthreadVideo src={src} style={{ width: "100%", height: "100%", objectFit: "cover" }} volume={0} />
        </FadeOutTail>
      </KenBurns>
    </Sequence>
  );
}

// Slow zoom + drift applied equally to every child, so the frozen frame and the
// fading-out live clip move as one (no "gear change" at the handoff). Motion
// ramps in from `startFrame` (the dissolve point) — the live clip before that is
// untouched. The pan is clamped to what the current zoom can cover, so the frame
// edge is never exposed (no black).
function KenBurns({
  children,
  startFrame,
  endFrame,
  holdSpanS,
  zoomPerSecond = 0.045,
  maxZoom = 0.09,
}: {
  children: React.ReactNode;
  startFrame: number;
  endFrame: number;
  holdSpanS: number;
  zoomPerSecond?: number;
  maxZoom?: number;
}) {
  const frame = useCurrentFrame();
  const t = interpolate(frame, [startFrame, endFrame], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.ease),
  });
  const zoom = Math.min(maxZoom, zoomPerSecond * holdSpanS); // total added scale
  const scale = 1 + zoom * t;
  // Fraction of the frame the zoom overhangs on each side; keep the pan safely
  // inside it so no edge is ever revealed.
  const coverMargin = (scale - 1) / (2 * scale);
  const pan = coverMargin * 0.7; // fraction of width/height, at full t
  const tx = -pan * t * 100;          // drift right…
  const ty = -pan * 0.6 * t * 100;    // …and slightly down
  return (
    <AbsoluteFill
      style={{
        transform: `translate(${tx}%, ${ty}%) scale(${scale})`,
        transformOrigin: "50% 50%",
      }}
    >
      {children}
    </AbsoluteFill>
  );
}

function FadeOutTail({
  children,
  totalFrames,
  holdStartFrame,
  dissolveFrames,
}: {
  children: React.ReactNode;
  totalFrames: number;
  holdStartFrame: number;
  dissolveFrames: number;
}) {
  const frame = useCurrentFrame();
  const fadeStart = Math.max(0, holdStartFrame - dissolveFrames);
  const opacity = interpolate(frame, [fadeStart, holdStartFrame], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.ease),
  });
  if (frame >= holdStartFrame || frame >= totalFrames) return null;
  return <AbsoluteFill style={{ opacity }}>{children}</AbsoluteFill>;
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
// Real regional basemap (Natural Earth II shaded relief, public domain — see
// Images/scene_04_range_map/SOURCE.md, no attribution required) styled to the
// channel palette, with the glass-frog range path drawn on top tracing the ACTUAL
// geography: southern Mexico → Pacific-side Central America → Panama → Colombian
// Andes → down the Andes → western Amazon basin (Glass Frog notes 9 + 10).
// Waypoints are in 1920×1080 px, computed from lon/lat against the basemap crop
// (lon [-112,-38], lat [-13,28.6]).
const RANGE_MAP_BASEMAP = `${ASSET_ROOT}/Images/scene_04_range_map/basemap.png`;
const RANGE_PATH_D =
  "M441,319 Q506,336 571,353 Q623,376 675,400 Q720,445 765,491 " +
  "Q811,526 856,561 Q882,626 908,691 Q902,782 895,872 " +
  "Q941,924 986,976 Q1051,983 1116,989 Q1187,970 1258,950";

function RangeMapAnimation() {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const mapOpacity = interpolate(frame, [0, fps * 0.7], [0, 1], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.ease),
  });
  // slow push toward the Amazon end so the reveal feels like it's arriving there
  const kb = interpolate(frame, [0, fps * 5.2], [0, 1], { extrapolateRight: "clamp" });
  const scale = 1 + 0.05 * kb;
  const tx = -1.6 * kb;
  const ty = -1.1 * kb;

  const draw = interpolate(frame, [fps * 1.1, fps * 3.9], [0, 1], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.ease),
  });
  const dotIn = interpolate(frame, [fps * 3.7, fps * 4.2], [0, 1], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });
  const pulse = 0.55 + 0.45 * Math.sin(frame / 5);
  const capOpacity = interpolate(frame, [fps * 0.9, fps * 1.6, fps * 4.7, fps * 5.2], [0, 1, 1, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });

  // Place-name labels (SVG px, same 1920×1080 space as the path — they pan with
  // the Ken Burns). Positions from lon/lat against the basemap crop. Staggered in.
  const PLACE_LABELS: { text: string; x: number; y: number; anchor: "start" | "middle" | "end"; size: number; atS: number; rotate?: number }[] = [
    { text: "MEXICO", x: 300, y: 205, anchor: "middle", size: 34, atS: 0.5 },
    { text: "ANDES", x: 815, y: 660, anchor: "middle", size: 24, atS: 2.4, rotate: -70 },
    { text: "AMAZON BASIN", x: 1360, y: 690, anchor: "middle", size: 34, atS: 3.4 },
  ];

  return (
    <AbsoluteFill style={{ backgroundColor: "#0B0F1A" }}>
      <AbsoluteFill style={{ opacity: mapOpacity, transform: `translate(${tx}%, ${ty}%) scale(${scale})` }}>
        <Img src={staticFile(RANGE_MAP_BASEMAP)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        <svg
          viewBox="0 0 1920 1080"
          preserveAspectRatio="xMidYMid slice"
          style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }}
        >
          <path
            d={RANGE_PATH_D} fill="none" stroke="#8AFA47" strokeWidth={7}
            strokeLinecap="round" strokeLinejoin="round" pathLength={1}
            strokeDasharray={1} strokeDashoffset={1 - draw}
            style={{ filter: "drop-shadow(0 0 9px rgba(138,250,71,0.85)) drop-shadow(0 0 3px rgba(0,0,0,0.6))" }}
          />
          {dotIn > 0 && (
            <>
              <circle cx={1258} cy={950} r={9 + 14 * pulse} fill="none"
                stroke="#8AFA47" strokeWidth={2} opacity={dotIn * (1 - pulse * 0.6)} />
              <circle cx={1258} cy={950} r={7} fill="#8AFA47" opacity={dotIn}
                style={{ filter: "drop-shadow(0 0 8px #8AFA47)" }} />
            </>
          )}
          {PLACE_LABELS.map((lb) => {
            const op = interpolate(
              frame,
              [fps * lb.atS, fps * (lb.atS + 0.5)],
              [0, 1],
              { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
            );
            if (op <= 0) return null;
            return (
              <text
                key={lb.text}
                x={lb.x}
                y={lb.y}
                textAnchor={lb.anchor}
                transform={lb.rotate ? `rotate(${lb.rotate} ${lb.x} ${lb.y})` : undefined}
                opacity={op}
                fill="#FFFFFF"
                stroke="rgba(0,0,0,0.85)"
                strokeWidth={4}
                paintOrder="stroke"
                style={{
                  fontFamily: "'Montserrat', Arial, sans-serif",
                  fontWeight: 800,
                  fontSize: lb.size,
                  letterSpacing: "0.16em",
                }}
              >
                {lb.text}
              </text>
            );
          })}
        </svg>
      </AbsoluteFill>

      <div
        style={{
          position: "absolute", left: 80, bottom: 84, opacity: capOpacity,
          fontFamily: "'Montserrat', Arial, sans-serif",
        }}
      >
        <div style={{
          fontWeight: 800, color: "#FFFFFF", fontSize: 30, letterSpacing: "0.14em",
          textShadow: "0 2px 10px rgba(0,0,0,0.9)",
        }}>
          GLASS FROG RANGE
        </div>
        <div style={{
          marginTop: 6, fontWeight: 600, color: "#8AFA47", fontSize: 18, letterSpacing: "0.08em",
          textShadow: "0 2px 8px rgba(0,0,0,0.9)",
        }}>
          Southern Mexico → the Amazon basin
        </div>
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
// Real glass-frog photo (GPT-Image-2, Tony-approved prompt 2026-09-03) — cut here
// off the diagram for the "actively camouflaging its own insides" line (~43.5s),
// slow Ken Burns push. Variety beat (R2-2). Sachatamia albomaculata, Costa Rican
// stream — organs visible through the translucent belly, which is the point.
const FROG_PHOTO_03 = `${ASSET_ROOT}/Images/scene_03/glass_frog_photo/illustration.png`;

// 2026-09-01 rework: same-image runs merged into single continuous shots (no
// "remount jump"); one eased camera path per shot with dwell holds while each
// label is up (camera holds still under labels, note 4); DiagramScene
// cross-dissolves the real image changes (note 1).
const S03_SHOTS: DiagramShot[] = [
  {
    // organ cutaway — was 4 separate segs (0 / 4.79 / 6.88 / 9.52)
    img: ORGAN_CUTAWAY,
    durS: 15.49,
    labels: [
      { feature: "heart", x_pct: 50.2, y_pct: 39.5, confidence: "high" },
      { feature: "liver", x_pct: 50.1, y_pct: 47.3, confidence: "high" },
      { feature: "lungs", x_pct: 43.4, y_pct: 41.0, confidence: "high" },
      { feature: "intestines", x_pct: 50.1, y_pct: 62.0, confidence: "high" },
    ],
    displayNames: S03_DISP,
    labelOffsetsS: { heart: 2.0, liver: 5.8, lungs: 6.3, intestines: 9.6 },
    labelHoldS: 3.0,
    labelScale: 1.15,
    waypoints: [
      { atS: 0, scale: 1.0, fx: 50, fy: 50 },
      { atS: 1.8, scale: 1.32, fx: 50.2, fy: 39.5, holdS: 3.4 }, // heart
      { atS: 5.6, scale: 1.32, fx: 47.0, fy: 44.0, holdS: 3.6 }, // liver + lungs
      { atS: 9.4, scale: 1.32, fx: 50.1, fy: 60.0, holdS: 3.0 }, // intestines
      { atS: 13.6, scale: 1.06, fx: 50, fy: 50 }, // pull back to wide
    ],
  },
  {
    img: SPECIES_MONTAGE,
    durS: 9.69,
    waypoints: [
      { atS: 0, scale: 1.12, fx: 18, fy: 50 },
      { atS: 9.69, scale: 1.12, fx: 82, fy: 50 },
    ],
  },
  {
    img: ORGAN_CUTAWAY,
    durS: 8.02,
    waypoints: [
      { atS: 0, scale: 1.0, fx: 50.1, fy: 47.3 },
      { atS: 8.02, scale: 1.5, fx: 50.1, fy: 47.3 },
    ],
  },
  {
    // mirrored pouch — was 3 separate segs (33.2 / 41.94 / 47.86). Shortened to
    // 9.8s (ends ~43.0s scene-rel) so it cross-dissolves to the real frog photo
    // right as the VO reaches "actively camouflaging its own insides" (R2-2).
    img: MIRRORED_POUCH_03,
    durS: 9.8,
    labels: [
      { feature: "mirrored_pouch", x_pct: 59.2, y_pct: 50.1, confidence: "high" },
      { feature: "guanine_crystal_surface", x_pct: 51.1, y_pct: 47.9, confidence: "high" },
    ],
    displayNames: S03_DISP,
    labelOffsetsS: { mirrored_pouch: 0.8, guanine_crystal_surface: 4.8 },
    labelHoldS: 3.4,
    labelScale: 1.15,
    waypoints: [
      { atS: 0, scale: 1.0, fx: 57, fy: 50 },
      { atS: 1.0, scale: 1.28, fx: 59.2, fy: 50.1, holdS: 3.6 }, // mirrored_pouch
      { atS: 5.0, scale: 1.34, fx: 51.1, fy: 47.9, holdS: 3.4 }, // guanine crystal surface
      { atS: 9.8, scale: 1.1, fx: 52, fy: 49 }, // gentle settle into the cross-dissolve
    ],
  },
  {
    // real glass-frog photo — "actively camouflaging its own insides" → scene end.
    // No labels; slow push toward the frog (negative space is left-of-frame).
    img: FROG_PHOTO_03,
    durS: 7.898,
    waypoints: [
      { atS: 0, scale: 1.03, fx: 50, fy: 50 },
      { atS: 7.898, scale: 1.1, fx: 60, fy: 48 },
    ],
  },
];

function Scene03Diagram() {
  return <DiagramScene shots={S03_SHOTS} sceneEndS={AUDIO.scene_03} />;
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

const S05_SHOTS: DiagramShot[] = [
  {
    img: SIDE_BY_SIDE,
    durS: 5.77,
    waypoints: [
      { atS: 0, scale: 1.0, fx: 50, fy: 50 },
      { atS: 5.77, scale: 1.14, fx: 50, fy: 50 },
    ],
  },
  {
    // blood cell concentration — was 2 segs (5.77 / 18.45)
    img: BLOOD_CELL,
    durS: 20.1,
    labels: [
      { feature: "red_blood_cells_awake", x_pct: 25.1, y_pct: 50.1, confidence: "high" },
      { feature: "red_blood_cells_asleep", x_pct: 75.3, y_pct: 50.5, confidence: "high" },
    ],
    displayNames: S05_DISP,
    labelOffsetsS: { red_blood_cells_awake: 1.0, red_blood_cells_asleep: 9.0 },
    labelHoldS: 3.4,
    labelScale: 1.15,
    waypoints: [
      { atS: 0, scale: 1.18, fx: 26, fy: 50 },
      { atS: 1.0, scale: 1.22, fx: 25.1, fy: 50.1, holdS: 3.6 }, // awake
      { atS: 6.0, scale: 1.24, fx: 50, fy: 50 },
      { atS: 9.0, scale: 1.28, fx: 75.3, fy: 50.5, holdS: 3.6 }, // asleep
      { atS: 14.0, scale: 1.5, fx: 75.3, fy: 50.5, holdS: 2.6 },
      { atS: 20.1, scale: 1.6, fx: 75.3, fy: 50.5 },
    ],
  },
  {
    // mirrored pouch camouflage — was 2 segs (25.87 / 29.25)
    img: MIRRORED_POUCH_CAM,
    durS: 12.2,
    labels: [
      { feature: "liver", x_pct: 51.5, y_pct: 42.5, confidence: "high" },
      { feature: "mirrored_surface", x_pct: 40.0, y_pct: 28.0, confidence: "high" },
      { feature: "red_blood_cells", x_pct: 43.1, y_pct: 53.2, confidence: "high" },
    ],
    displayNames: S05_DISP,
    labelOffsetsS: { liver: 2.17, mirrored_surface: 5.38, red_blood_cells: 9.38 },
    labelHoldS: 2.8,
    labelScale: 1.15,
    waypoints: [
      { atS: 0, scale: 1.0, fx: 51.5, fy: 42.5 },
      { atS: 1.8, scale: 1.22, fx: 51.5, fy: 42.5, holdS: 3.0 }, // liver
      { atS: 5.0, scale: 1.34, fx: 40.0, fy: 28.0, holdS: 3.0 }, // mirrored_surface
      { atS: 8.8, scale: 1.4, fx: 43.1, fy: 53.2, holdS: 2.8 }, // red_blood_cells
      { atS: 12.2, scale: 1.4, fx: 43.1, fy: 53.2 },
    ],
  },
  {
    img: SIDE_BY_SIDE,
    durS: 6.49,
    waypoints: [
      { atS: 0, scale: 1.1, fx: 22, fy: 50 },
      { atS: 6.49, scale: 1.1, fx: 78, fy: 50 },
    ],
  },
  {
    // vessel cross-section — was 2 segs (44.56 / 52.15)
    img: VESSEL_CROSS,
    durS: 13.28,
    labels: [
      { feature: "red_blood_cells", x_pct: 47.9, y_pct: 53.6, confidence: "high" },
      { feature: "vessel_wall", x_pct: 39.5, y_pct: 28.5, confidence: "high" },
    ],
    displayNames: S05_DISP,
    labelOffsetsS: { red_blood_cells: 1.0, vessel_wall: 5.2 },
    labelHoldS: 3.4,
    labelScale: 1.15,
    waypoints: [
      { atS: 0, scale: 1.0, fx: 50, fy: 50 },
      { atS: 1.0, scale: 1.24, fx: 47.9, fy: 53.6, holdS: 3.6 }, // red_blood_cells
      { atS: 5.2, scale: 1.3, fx: 39.5, fy: 28.5, holdS: 3.6 }, // vessel_wall
      { atS: 9.8, scale: 1.05, fx: 50, fy: 50 },
      { atS: 13.28, scale: 1.07, fx: 50, fy: 50 },
    ],
  },
  {
    img: PHOTOACOUSTIC,
    durS: 15.164,
    waypoints: [
      { atS: 0, scale: 1.0, fx: 50, fy: 50 },
      { atS: 7.0, scale: 1.06, fx: 50, fy: 50 },
      { atS: 15.164, scale: 1.3, fx: 50, fy: 45 },
    ],
  },
];

function Scene05Diagram() {
  return <DiagramScene shots={S05_SHOTS} sceneEndS={AUDIO.scene_05} />;
}

// ─── SCENE 06 mixed content, sequenced per Clip_Plan.json's letter order ───
const CIRCULATORY_INFOGRAPHIC = `${ASSET_ROOT}/Images/scene_06B_circulatory_infographic/illustration.png`;
const LAB_INSERT_06C = `${ASSET_ROOT}/Images/scene_06C_lab_insert/illustration.png`;
const S06B_DISP = { clot_formation: "Clot Formation", platelets: "Platelets", normal_blood_flow: "Normal Blood Flow" };

function Scene06Content() {
  return (
    <>
      {/* 2026-08-30 systemic fix (RESUME_NOTES "Systemic finding"): every VideoSeg below plays
          at floor(real ffprobe duration) in whole frames, never Clip_Plan.json's planned value,
          so OffthreadVideo can't run past real content and loop back to frame 0 (the Note #1
          flash-cut mechanism). Real lengths: 06A/06D/06G 6.083s, 06E/06F 8.083s, 06H 5.083s.
          The two synthetic diagram segs (06B 189f, 06C 142f) absorb all slack so scene_06 stays
          locked to AUDIO.scene_06 (1513 frames). Layout in frames:
          06A 0→182 | 06B 182→371 | 06C 371→513 | 06D 513→695 | 06E 695→937 | 06F 937→1179 | 06G 1179→1361 | 06H 1361→1513 */}
      {/* 06A → 06B → 06C → 06D → 06E — every cut a ~0.5s cross-dissolve
          (ChainScene, Note 1). 06E freezes its last frame for the 0.5s dissolve
          into the 06F tail below. Sum = 937 frames. */}
      <ChainScene tailFreeze segs={[
        { kind: "video", file: "scene_06/Scene_06A_looped.mp4", durF: 182 },
        { kind: "node", durF: 189, node: (
          <DiagramSegInner
            fromS={0} durS={0} src={CIRCULATORY_INFOGRAPHIC}
            keyframes={[
              { t: 0, scale: 1.18, fx: 36.0, fy: 47.0 },
              { t: 0.4, scale: 1.22, fx: 36.0, fy: 47.0 },
              { t: 3.4, scale: 1.22, fx: 36.0, fy: 47.0 },
              { t: 4.1, scale: 1.24, fx: 75.6, fy: 59.8 },
              { t: 6.3, scale: 1.28, fx: 75.6, fy: 59.8 },
            ]}
            labels={[
              { feature: "clot_formation", x_pct: 36.9, y_pct: 49.3, confidence: "high" },
              { feature: "platelets", x_pct: 35.0, y_pct: 44.1, confidence: "high" },
              { feature: "normal_blood_flow", x_pct: 75.6, y_pct: 59.8, confidence: "high" },
            ]}
            displayNames={S06B_DISP}
            labelOffsetsS={{ clot_formation: 0.4, platelets: 1.1, normal_blood_flow: 4.2 }}
            labelHoldS={2.6}
            labelScale={1.15}
            lineColor="rgba(255,255,255,0.95)" labelColor="#FFFFFF"
          />
        ) },
        { kind: "node", durF: 142, node: (
          <DiagramSegInner
            fromS={0} durS={0} src={LAB_INSERT_06C}
            keyframes={[
              { t: 0, scale: 1.0, fx: 50, fy: 50 },
              { t: 5.0, scale: 1.25, fx: 50, fy: 45 },
            ]}
          />
        ) },
        { kind: "video", file: "scene_06/Scene_06D_looped.mp4", durF: 182 },
        { kind: "video", file: "scene_06/Scene_06E_looped.mp4", durF: 242 },
      ]} />

      {/* 06F → 06G → 06H tail (2026-09-03 rework). Every boundary is a ~1.3s
          cross-dissolve; 06F/06H vanish into their end-frame stills; 06G is held +
          Ken-Burns'd past its 6.07s real length so it gets ~8.8s on screen
          (Tony: "06G is too fast, you only see about a second"). No two live
          OffthreadVideos ever overlap → kills the horizontal-band tear.
          Frames: 06F 937→1095(seq 1140) | 06G 1095→1360(seq 1400) | 06H 1360→1513 */}
      <Sequence from={s(F(937))} durationInFrames={s(F(1140)) - s(F(937))} layout="none">
        <VanishShot file="scene_06/Scene_06F_looped.mp4"
          endFrame="Images/Start_End_Frames/Scene_06F_End.png"
          videoPlayF={95} dissolveF={55} fadeInF={15} />
      </Sequence>
      <Sequence from={s(F(1095))} durationInFrames={s(F(1400)) - s(F(1095))} layout="none">
        <HeldVideoShot file="scene_06/Scene_06G_looped.mp4"
          holdStill="Images/scene_06/hold_frames/Scene_06G_hold.png"
          videoPlayF={165} fadeInF={45} />
      </Sequence>
      <Sequence from={s(F(1360))} durationInFrames={s(F(1513)) - s(F(1360))} layout="none">
        <VanishShot file="scene_06/Scene_06H_looped.mp4"
          endFrame="Images/Start_End_Frames/Scene_06H_End.png"
          videoPlayF={90} dissolveF={45} fadeInF={40} />
      </Sequence>
    </>
  );
}

// ─── Main Composition ───────────────────────────────────────────────────────
// Narration is one continuous hard-cut track; the visual layer per scene
// cross-dissolves into the next (SceneVisual). Every scene's inner content is
// authored relative to that scene's start (frame 0 = scene start).
export const GlassFrogDoc: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: "#0B0F1A" }}>
    <NarrationTrack />

    {/* SCENE 01 — Glitch Hook */}
    <SceneVisual scene="scene_01" isFirst>
      <VideoClip file="scene_01/Scene_01A_looped.mp4" />
    </SceneVisual>

    {/* SCENE 02 — Setup — Species Name Card. 02A plays real 7.083s, eases into a
        Ken-Burns freeze-hold to 8.083s, 02B crossfades in over the freeze. 02B
        windowed to the exact last frame of the scene. */}
    <SceneVisual scene="scene_02">
      {VideoSegFilled({ fromS: 0.0, targetS: 8.083, realS: 7.083, file: "scene_02/Scene_02A_looped.mp4", dissolveS: 0.4 })}
      <Sequence from={s(7.583)} durationInFrames={s(AUDIO.scene_02) - s(7.583)} layout="none">
        <VideoClip file="scene_02/Scene_02B_looped.mp4" fadeInS={0.5} />
      </Sequence>
      <SceneOverlays overlays={OV.scene_02} />
    </SceneVisual>

    {/* SCENE 03 — Tease #1 — diagram sub-pipeline (merged shots + eased camera) */}
    <SceneVisual scene="scene_03">
      <Scene03Diagram />
      <SceneOverlays overlays={OV.scene_03} />
    </SceneVisual>

    {/* SCENE 04 — Context Loop — Range Map + b-roll. Every cut is a ~0.5s
        cross-dissolve (ChainScene, Note 1). Durations = floor(real ffprobe)
        whole frames; RangeMap absorbs the slack. Sum = 1066 = s(AUDIO.scene_04). */}
    <SceneVisual scene="scene_04">
      <ChainScene segs={[
        { kind: "node", node: <RangeMapAnimation />, durF: 156 },
        { kind: "video", file: "scene_04/Scene_04B_looped.mp4", durF: 182 },
        { kind: "video", file: "scene_04/Scene_04C_looped.mp4", durF: 182 },
        { kind: "video", file: "scene_04/Scene_04D_looped.mp4", durF: 182 },
        { kind: "video", file: "scene_04/Scene_04E_looped.mp4", durF: 212 },
        { kind: "video", file: "scene_04/Scene_04F_looped.mp4", durF: 152 },
      ]} />
      <LocationCard text="Cloud Forests, Central & South America" startS={6.5} durS={3} />
    </SceneVisual>

    {/* SCENE 05 — Tease #2 — longest diagram beat */}
    <SceneVisual scene="scene_05">
      <Scene05Diagram />
      <SceneOverlays overlays={OV.scene_05} />
      <AnomalyMeter value={9} startS={44.8} durS={6} />
    </SceneVisual>

    {/* SCENE 06 — Reward — mixed live footage + diagram */}
    <SceneVisual scene="scene_06">
      <Scene06Content />
      <SceneOverlays overlays={OV.scene_06} />
    </SceneVisual>

    {/* SCENE 07 — Hook Forward */}
    <SceneVisual scene="scene_07" isLast>
      <VideoClip file="scene_07/Scene_07A_looped.mp4" />
    </SceneVisual>
  </AbsoluteFill>
);
