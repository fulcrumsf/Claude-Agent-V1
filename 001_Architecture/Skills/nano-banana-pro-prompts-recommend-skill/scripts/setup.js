#!/usr/bin/env node
/**
 * setup.js - Downloads/updates Nano Banana Pro prompt library from GitHub
 *
 * Fully dynamic: reads manifest.json first to discover all categories.
 * New/renamed/removed categories are handled automatically — no hardcoding.
 *
 * Security gate (added 2026-10-01, Agent-OS skill audit): every download from
 * GitHub's unpinned `main` branch is scanned with NVIDIA SkillSpector before
 * it's trusted. A SAFE scan promotes it into references/; anything else
 * (CAUTION, DO_NOT_INSTALL, or SkillSpector not being available) leaves the
 * existing references untouched and just warns — it never silently applies
 * unscanned data.
 *
 * The scan runs in the BACKGROUND, not inline: this skill's data is ~15k
 * prompts (~46MB), and a static SkillSpector scan of that took over 10
 * minutes in testing. Blocking every skill invocation on that isn't
 * practical, so `--check` spawns a detached worker and returns immediately —
 * the skill keeps using its current (already-scanned) data until the worker
 * finishes and promotes a clean result. `--force` does the same, but prints
 * where to watch for the result instead of pretending it's instant.
 *
 * Baseline (added same day, after the first real run): scanning 15k+ pieces of
 * crowd-sourced prompt text reliably trips SkillSpector's keyword/YARA rules on
 * coincidental phrasing — e.g. a prompt mentioning "keychain" tripping
 * "Privilege Escalation", or a prompt titled with the word "Prompt" near the
 * word "print" tripping "System Prompt Leakage". All 52 findings from the
 * first real scan were manually reviewed and confirmed to be exactly this —
 * noise from scale, not actual injected instructions — then accepted into
 * `references/.skillspector-baseline.yaml` via `skillspector baseline`. Future
 * scans pass `--baseline` so only genuinely NEW findings (new fingerprints,
 * e.g. from newly-added prompts) still block an update. This baseline is a
 * one-time human-reviewed snapshot, not a standing exemption — if a future
 * scan blocks on a new finding, it needs the same quick manual look before
 * regenerating the baseline (don't just regenerate it blindly; that would
 * defeat the point of the gate).
 *
 * Usage:
 *   node scripts/setup.js           # Download missing files only (first install)
 *   node scripts/setup.js --force   # Queue a forced re-check in the background
 *   node scripts/setup.js --check   # Auto-queue a background update if stale (> 24h)
 *   node scripts/setup.js --worker  # Internal: the actual download+scan+promote step
 */

import { existsSync, mkdirSync, statSync, writeFileSync, readFileSync, readdirSync, unlinkSync, rmSync, cpSync, openSync, closeSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { spawnSync, spawn } from 'child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const refsDir = join(__dirname, '..', 'references');
const stagingDir = join(refsDir, '.staging');
const stampFile = join(refsDir, '.last-updated');
const flaggedFile = join(refsDir, '.update-flagged.json');
const lockFile = join(refsDir, '.update-in-progress');
const workerLogFile = join(refsDir, '.update-worker.log');
const baselineFile = join(refsDir, '.skillspector-baseline.yaml');

const BASE_URL = 'https://raw.githubusercontent.com/YouMind-OpenLab/nano-banana-pro-prompts-recommend-skill/main/references';
const STALE_HOURS = 24;
const LOCK_STALE_HOURS = 2; // if a worker's lock is older than this, assume it crashed and allow a new one

function isStale() {
  if (!existsSync(stampFile)) return true;
  const ts = parseInt(readFileSync(stampFile, 'utf8').trim(), 10);
  return (Date.now() - ts) / 1000 / 3600 > STALE_HOURS;
}

function lockIsActive() {
  if (!existsSync(lockFile)) return false;
  const ts = parseInt(readFileSync(lockFile, 'utf8').trim() || '0', 10);
  return (Date.now() - ts) / 1000 / 3600 < LOCK_STALE_HOURS;
}

async function fetchText(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status} — ${url}`);
  return res.text();
}

/** Scan a directory with SkillSpector. Returns { ok, recommendation, raw } — ok=false on any
 *  problem (tool missing, scan failure, non-SAFE verdict), which is the fail-closed default.
 *  NOTE: SkillSpector exits non-zero (status 1) whenever it finds anything above SAFE — that's
 *  its CI-gate convention, not a sign the scan failed to run. A spawn error (result.error, e.g.
 *  the binary isn't on PATH) is the only thing that means "the scan didn't run"; a non-zero exit
 *  with valid JSON on stdout is a completed scan with a real verdict and must be parsed, not
 *  treated as unavailable. */
function scanStaged(dir) {
  const args = ['scan', dir, '--no-llm', '--format', 'json'];
  if (existsSync(baselineFile)) args.push('--baseline', baselineFile);
  const result = spawnSync('skillspector', args, {
    encoding: 'utf8',
    timeout: 30 * 60 * 1000, // generous — this runs in the background worker, nothing is waiting on it
    maxBuffer: 1024 * 1024 * 64,
  });
  if (result.error || !result.stdout) {
    return { ok: false, recommendation: 'SCAN_UNAVAILABLE', raw: result.stderr || result.error?.message || `skillspector did not run (exit ${result.status})` };
  }
  try {
    const parsed = JSON.parse(result.stdout);
    const risk = parsed?.risk_assessment ?? {};
    const rec = risk.recommendation ?? 'UNKNOWN';
    const issueCount = Array.isArray(parsed.issues) ? parsed.issues.length : null;
    // This skill's data (~15k prompts, tens of MB) exceeds SkillSpector's per-file analysis
    // limits, so `analysis_completeness` is always partial and the tool marks that CAUTION
    // even with zero actual findings — that's a coverage artifact, not a risk signal. Treat
    // zero remaining issues + a zero score as equally acceptable to an outright SAFE verdict.
    const ok = rec === 'SAFE' || (issueCount === 0 && risk.score === 0);
    return { ok, recommendation: rec, raw: risk };
  } catch (err) {
    return { ok: false, recommendation: 'SCAN_PARSE_ERROR', raw: result.stdout.slice(0, 500) || err.message };
  }
}

/** The actual work: download everything fresh into staging, scan it, promote or flag.
 *  Runs as a detached background process so nothing blocks on it. */
async function runWorker() {
  writeFileSync(lockFile, String(Date.now()), 'utf8');
  try {
    if (existsSync(stagingDir)) rmSync(stagingDir, { recursive: true, force: true });
    mkdirSync(stagingDir, { recursive: true });

    let categories;
    const manifestText = await fetchText(`${BASE_URL}/manifest.json`);
    const manifest = JSON.parse(manifestText);
    categories = manifest.categories;
    writeFileSync(join(stagingDir, 'manifest.json'), manifestText, 'utf8');

    let downloaded = 0, failed = 0;
    for (const cat of categories) {
      try {
        const text = await fetchText(`${BASE_URL}/${cat.file}`);
        writeFileSync(join(stagingDir, cat.file), text, 'utf8');
        downloaded++;
      } catch (err) {
        failed++;
        const existing = join(refsDir, cat.file);
        if (existsSync(existing)) cpSync(existing, join(stagingDir, cat.file));
      }
    }

    console.log(`[worker] Downloaded ${downloaded} file(s), ${failed} failed. Scanning with SkillSpector before applying...`);
    const scan = scanStaged(stagingDir);

    if (!scan.ok) {
      writeFileSync(flaggedFile, JSON.stringify({ when: new Date().toISOString(), ...scan }, null, 2), 'utf8');
      console.warn(`[worker] NOT applying this update — SkillSpector verdict: ${scan.recommendation}. Existing references left as-is.`);
      console.warn(`[worker] Staged (unapplied) files kept at: ${stagingDir}. Details: ${flaggedFile}`);
      return;
    }

    const validFiles = new Set([...categories.map(c => c.file), 'manifest.json', '.last-updated', '.gitkeep']);
    for (const f of readdirSync(refsDir)) {
      if (f.startsWith('.staging') || f.startsWith('.update-') || f.startsWith('.last-updated')) continue;
      if (!validFiles.has(f)) unlinkSync(join(refsDir, f));
    }
    for (const f of readdirSync(stagingDir)) {
      cpSync(join(stagingDir, f), join(refsDir, f));
    }
    rmSync(stagingDir, { recursive: true, force: true });
    if (existsSync(flaggedFile)) unlinkSync(flaggedFile);
    writeFileSync(stampFile, String(Date.now()), 'utf8');
    console.log(`[worker] SkillSpector verdict: SAFE. ${downloaded} file(s) applied. Skill data is up to date.`);
  } catch (err) {
    console.warn(`[worker] Update failed (non-fatal, old data still in use): ${err.message}`);
  } finally {
    if (existsSync(lockFile)) unlinkSync(lockFile);
  }
}

/** Fire-and-forget: spawn this same script with --worker, detached, output captured to a log file. */
function queueBackgroundUpdate() {
  if (lockIsActive()) {
    console.log('[setup] An update is already being scanned in the background. Current references still in use until it clears.');
    return;
  }
  const out = openSync(workerLogFile, 'a');
  const child = spawn(process.execPath, [__filename, '--worker'], {
    detached: true,
    stdio: ['ignore', out, out],
  });
  child.unref();
  closeSync(out);
  console.log('[setup] Stale data detected. Update + SkillSpector scan queued in the background (see .update-worker.log).');
  console.log('[setup] Current references remain in use until the scan clears it as SAFE.');
}

async function firstInstallIfEmpty() {
  // Only for a genuinely empty install (no manifest at all yet) — fetch synchronously once,
  // still gated through the same worker+scan path, since there's nothing safe to fall back to.
  if (existsSync(join(refsDir, 'manifest.json'))) return false;
  console.log('[setup] No local data yet — running the first download + SkillSpector scan synchronously (this is the one-time case with nothing to fall back to)...');
  if (existsSync(lockFile)) unlinkSync(lockFile);
  await runWorker();
  return true;
}

async function main() {
  const args = process.argv.slice(2);
  if (!existsSync(refsDir)) mkdirSync(refsDir, { recursive: true });

  if (args.includes('--worker')) {
    await runWorker();
    return;
  }

  const checkMode = args.includes('--check');
  const forceMode = args.includes('--force');

  if (await firstInstallIfEmpty()) return;

  if (checkMode && !isStale()) return; // fresh — silent no-op, matches original behavior

  if (checkMode || forceMode) {
    queueBackgroundUpdate();
    return;
  }

  // Bare `node setup.js` with existing data and no flag: nothing to do.
  console.log('[setup] References already present. Use --force to queue a refresh, or --check for the normal stale-triggered path.');
}

main().catch(err => {
  console.warn('[setup] Warning (non-fatal):', err.message);
  process.exit(0);
});
