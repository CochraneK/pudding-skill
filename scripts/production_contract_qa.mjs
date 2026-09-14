#!/usr/bin/env node
import { readFile, writeFile, mkdir, mkdtemp, rm } from 'node:fs/promises';
import { spawn, spawnSync } from 'node:child_process';
import { tmpdir } from 'node:os';
import path from 'node:path';

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function args() {
  const cfg = {
    contract: 'stories/global-mental-health/production-contract.json',
    baseUrl: 'http://127.0.0.1:4173',
    out: '.qa/production-contract-browser.json',
    chrome: process.env.CHROME_BIN || ''
  };
  for (let i = 2; i < process.argv.length; i++) {
    const key = process.argv[i];
    if (key === '--contract') cfg.contract = process.argv[++i];
    else if (key === '--base-url') cfg.baseUrl = process.argv[++i];
    else if (key === '--out') cfg.out = process.argv[++i];
    else if (key === '--chrome') cfg.chrome = process.argv[++i];
    else throw new Error(`Unknown argument: ${key}`);
  }
  return cfg;
}

function chromePath(explicit) {
  if (explicit) return explicit;
  for (const bin of ['google-chrome-stable', 'google-chrome', 'chromium', 'chromium-browser']) {
    const hit = spawnSync('bash', ['-lc', `command -v ${bin} || true`], { encoding: 'utf8' }).stdout.trim();
    if (hit) return hit;
  }
  throw new Error('Chrome/Chromium not found. Set CHROME_BIN.');
}

class CDP {
  constructor(ws) {
    this.ws = ws;
    this.id = 0;
    this.pending = new Map();
    this.listeners = new Map();
    ws.addEventListener('message', (event) => {
      const message = JSON.parse(String(event.data));
      if (message.id && this.pending.has(message.id)) {
        const pending = this.pending.get(message.id);
        this.pending.delete(message.id);
        return message.error ? pending.reject(new Error(message.error.message)) : pending.resolve(message.result || {});
      }
      const key = `${message.sessionId || ''}:${message.method || ''}`;
      for (const fn of this.listeners.get(key) || []) fn(message.params || {});
    });
  }
  call(method, params = {}, sessionId) {
    const id = ++this.id;
    const message = { id, method, params };
    if (sessionId) message.sessionId = sessionId;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.ws.send(JSON.stringify(message));
      setTimeout(() => {
        if (this.pending.delete(id)) reject(new Error(`CDP timeout: ${method}`));
      }, 15000).unref?.();
    });
  }
  on(method, fn, sessionId = '') {
    const key = `${sessionId}:${method}`;
    const list = this.listeners.get(key) || [];
    list.push(fn);
    this.listeners.set(key, list);
    return () => this.listeners.set(key, (this.listeners.get(key) || []).filter((value) => value !== fn));
  }
  once(method, sessionId = '', timeout = 20000) {
    return new Promise((resolve, reject) => {
      let off = () => {};
      const timer = setTimeout(() => { off(); reject(new Error(`Event timeout: ${method}`)); }, timeout);
      off = this.on(method, (value) => { clearTimeout(timer); off(); resolve(value); }, sessionId);
    });
  }
}

async function connect(getStderr, proc) {
  let wsUrl = '';
  for (let i = 0; i < 200; i++) {
    const match = getStderr().match(/DevTools listening on (ws:\/\/[^\s]+)/);
    if (match) { wsUrl = match[1]; break; }
    if (proc.exitCode != null) throw new Error(`Chrome exited before DevTools was ready (${proc.exitCode}).`);
    await sleep(100);
  }
  if (!wsUrl) throw new Error('Chrome DevTools endpoint unavailable.');
  const ws = new WebSocket(wsUrl);
  await new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error('DevTools WebSocket timeout')), 10000);
    ws.addEventListener('open', () => { clearTimeout(timer); resolve(); }, { once: true });
    ws.addEventListener('error', () => { clearTimeout(timer); reject(new Error('DevTools WebSocket error')); }, { once: true });
  });
  return new CDP(ws);
}

async function evalValue(cdp, sessionId, expression) {
  const result = await cdp.call('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true }, sessionId);
  if (result.exceptionDetails) throw new Error(result.exceptionDetails.text || 'Runtime.evaluate failed');
  return result.result?.value;
}

async function main() {
  const cfg = args();
  const contract = JSON.parse(await readFile(cfg.contract, 'utf8'));
  const chrome = chromePath(cfg.chrome);
  const profile = await mkdtemp(path.join(tmpdir(), 'pudding-production-'));
  const proc = spawn(chrome, [
    '--headless=new', '--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage', '--no-first-run',
    '--remote-debugging-port=0', `--user-data-dir=${profile}`, 'about:blank'
  ], { stdio: ['ignore', 'ignore', 'pipe'] });
  let stderr = '';
  proc.stderr.on('data', (chunk) => { stderr += chunk.toString(); });
  let cdp;
  try {
    cdp = await connect(() => stderr, proc);
    const { targetId } = await cdp.call('Target.createTarget', { url: 'about:blank' });
    const { sessionId } = await cdp.call('Target.attachToTarget', { targetId, flatten: true });
    for (const domain of ['Page', 'Runtime']) await cdp.call(`${domain}.enable`, {}, sessionId);
    await cdp.call('Emulation.setDeviceMetricsOverride', {
      width: 390, height: 844, deviceScaleFactor: 1, mobile: true, screenWidth: 390, screenHeight: 844
    }, sessionId);
    const url = new URL(contract.route, cfg.baseUrl.endsWith('/') ? cfg.baseUrl : `${cfg.baseUrl}/`).href;
    const loaded = cdp.once('Page.loadEventFired', sessionId);
    await cdp.call('Page.navigate', { url }, sessionId);
    await loaded;
    await sleep(500);

    const payload = JSON.stringify(contract);
    const report = await evalValue(cdp, sessionId, `(() => {
      const contract = ${payload};
      const failures = [];
      const winners = contract.decision?.winner_concept_ids || [];
      const root = document.querySelector('[data-production-winner]');
      if (!root) failures.push('missing [data-production-winner] root');
      else {
        if (!winners.includes(root.dataset.productionWinner)) failures.push('runtime winner marker does not match tournament winner');
        if (root.dataset.primaryInteraction !== contract.primary_interaction_job) failures.push('runtime primary interaction does not match contract');
        const controls = root.querySelectorAll('button,select,input,textarea,[role="button"],[role="slider"]').length;
        if (contract.primary_interaction_job === 'none' && controls) failures.push('primary none-interaction story contains controls');
      }

      const beats = [...document.querySelectorAll('[data-story-beat]')].map((el) => el.dataset.storyBeat);
      const expectedBeats = contract.required_sequence || [];
      if (JSON.stringify(beats.slice(0, expectedBeats.length)) !== JSON.stringify(expectedBeats)) {
        failures.push('required story beats are missing or out of order');
      }

      for (const claim of contract.required_claims || []) {
        const el = document.querySelector('[data-claim-id="' + CSS.escape(claim.id) + '"]');
        if (!el) { failures.push('missing runtime claim ' + claim.id); continue; }
        const text = el.innerText.replace(/\s+/g, ' ').trim();
        for (const token of claim.tokens || []) if (!text.includes(String(token))) failures.push('claim ' + claim.id + ' missing token ' + token);
      }

      for (const lesson of contract.borrowed_lessons || []) {
        if (!document.querySelector('[data-borrowed-from="' + CSS.escape(lesson.from_concept_id) + '"]')) failures.push('missing borrowed lesson marker ' + lesson.from_concept_id);
      }

      for (const depth of contract.optional_depth || []) {
        const container = document.querySelector('[data-optional-depth="' + CSS.escape(depth.from_concept_id) + '"]');
        if (!container) { failures.push('missing optional depth marker ' + depth.from_concept_id); continue; }
        const links = [...container.querySelectorAll('a[href]')].map((a) => a.getAttribute('href'));
        if (!links.some((href) => href && href.includes(depth.route.replace(/^\//, '')))) failures.push('optional depth route not exposed for ' + depth.from_concept_id);
      }

      return {
        status: failures.length ? 'FAIL' : 'PASS',
        failures,
        winner: root?.dataset.productionWinner || null,
        interaction: root?.dataset.primaryInteraction || null,
        beats,
        viewport: { width: innerWidth, height: innerHeight }
      };
    })()`);

    await mkdir(path.dirname(cfg.out), { recursive: true });
    await writeFile(cfg.out, JSON.stringify(report, null, 2) + '\n');
    console.log(`Production contract browser QA: ${report.status} · winner=${report.winner || 'none'} · interaction=${report.interaction || 'none'}`);
    for (const failure of report.failures) console.log(`- ERROR: ${failure}`);
    if (report.status !== 'PASS') process.exitCode = 1;
  } finally {
    try { cdp?.ws.close(); } catch {}
    if (proc.exitCode == null) proc.kill('SIGTERM');
    await sleep(200);
    await rm(profile, { recursive: true, force: true }).catch(() => {});
  }
}

main().catch((error) => { console.error(error.stack || error); process.exit(1); });
