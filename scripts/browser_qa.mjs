#!/usr/bin/env node
import { spawn, spawnSync } from 'node:child_process';
import { mkdir, mkdtemp, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function args() {
  const cfg = { baseUrl: 'http://127.0.0.1:4173', out: '.qa', routes: ['/', '/generated', '/lab'], chrome: process.env.CHROME_BIN || '' };
  for (let i = 2; i < process.argv.length; i++) {
    const key = process.argv[i];
    if (key === '--base-url') cfg.baseUrl = process.argv[++i];
    else if (key === '--out') cfg.out = process.argv[++i];
    else if (key === '--routes') cfg.routes = process.argv[++i].split(',').filter(Boolean);
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
    this.ws = ws; this.id = 0; this.pending = new Map(); this.listeners = new Map();
    ws.addEventListener('message', (e) => {
      const m = JSON.parse(String(e.data));
      if (m.id && this.pending.has(m.id)) {
        const p = this.pending.get(m.id); this.pending.delete(m.id);
        return m.error ? p.reject(new Error(m.error.message)) : p.resolve(m.result || {});
      }
      const key = `${m.sessionId || ''}:${m.method || ''}`;
      for (const fn of this.listeners.get(key) || []) fn(m.params || {});
    });
  }
  call(method, params = {}, sessionId) {
    const id = ++this.id, msg = { id, method, params };
    if (sessionId) msg.sessionId = sessionId;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject }); this.ws.send(JSON.stringify(msg));
      setTimeout(() => { if (this.pending.delete(id)) reject(new Error(`CDP timeout: ${method}`)); }, 15000).unref?.();
    });
  }
  on(method, fn, sessionId = '') {
    const key = `${sessionId}:${method}`, list = this.listeners.get(key) || [];
    list.push(fn); this.listeners.set(key, list);
    return () => this.listeners.set(key, (this.listeners.get(key) || []).filter((x) => x !== fn));
  }
  once(method, sessionId = '', timeout = 20000) {
    return new Promise((resolve, reject) => {
      let off = () => {};
      const timer = setTimeout(() => { off(); reject(new Error(`Event timeout: ${method}`)); }, timeout);
      off = this.on(method, (value) => { clearTimeout(timer); off(); resolve(value); }, sessionId);
    });
  }
}

async function connectFromChrome(getStderr, proc) {
  let wsUrl = '';
  for (let i = 0; i < 200; i++) {
    const match = getStderr().match(/DevTools listening on (ws:\/\/[^\s]+)/);
    if (match) { wsUrl = match[1]; break; }
    if (proc.exitCode != null) throw new Error(`Chrome exited before DevTools was ready (code ${proc.exitCode}).`);
    await sleep(100);
  }
  if (!wsUrl) throw new Error('Chrome DevTools endpoint unavailable.');
  const ws = new WebSocket(wsUrl);
  await new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error('DevTools WebSocket timeout')), 10000);
    ws.addEventListener('open', () => { clearTimeout(timer); resolve(); }, { once: true });
    ws.addEventListener('error', (event) => { clearTimeout(timer); reject(event.error || new Error('DevTools WebSocket error')); }, { once: true });
  });
  return new CDP(ws);
}

const CHECK = String.raw`(() => {
  const named = (el) => el.hasAttribute('aria-labelledby') || (el.getAttribute('aria-label') || el.getAttribute('title') || el.textContent || '').trim() || (el instanceof HTMLInputElement && (el.value || el.placeholder || el.alt));
  const interactive = [...document.querySelectorAll('a[href],button,input,select,textarea,[role="button"],[role="link"]')];
  const ids = [...document.querySelectorAll('[id]')].map((el) => el.id).filter(Boolean);
  return {
    title: document.title,
    text: document.body?.innerText?.trim().length || 0,
    mains: document.querySelectorAll('main').length,
    h1s: document.querySelectorAll('h1').length,
    overflow: Math.max(document.documentElement.scrollWidth, document.body?.scrollWidth || 0) - innerWidth,
    missingAlt: document.querySelectorAll('img:not([alt])').length,
    unnamed: interactive.filter((el) => !named(el)).length,
    duplicateIds: [...new Set(ids.filter((id, i) => ids.indexOf(id) !== i))],
    reducedMotion: matchMedia('(prefers-reduced-motion: reduce)').matches,
    interactive: interactive.length
  };
})()`;

async function evalValue(cdp, sid, expression) {
  const r = await cdp.call('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true }, sid);
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.text || 'Runtime.evaluate failed');
  return r.result?.value;
}

function slug(route) { return route === '/' ? 'home' : route.replace(/^\/+|\/+$/g, '').replace(/[^a-z0-9]+/gi, '-'); }

async function caseRun(cdp, sid, cfg, route, viewport) {
  const d = { route, viewport: viewport.name, errors: [], exceptions: [], networkFailures: [] };
  const stops = [
    cdp.on('Runtime.consoleAPICalled', (p) => { if (['error', 'assert'].includes(p.type)) d.errors.push((p.args || []).map((a) => a.value ?? a.description ?? '').join(' ')); }, sid),
    cdp.on('Runtime.exceptionThrown', (p) => d.exceptions.push(p.exceptionDetails?.exception?.description || p.exceptionDetails?.text || 'exception'), sid),
    cdp.on('Network.loadingFailed', (p) => { if (!p.canceled && !String(p.errorText).includes('ERR_ABORTED')) d.networkFailures.push(`${p.type}: ${p.errorText}`); }, sid),
    cdp.on('Log.entryAdded', (p) => { if (p.entry?.level === 'error') d.errors.push(p.entry.text); }, sid)
  ];
  await cdp.call('Emulation.setDeviceMetricsOverride', { width: viewport.width, height: viewport.height, deviceScaleFactor: 1, mobile: viewport.mobile, screenWidth: viewport.width, screenHeight: viewport.height }, sid);
  await cdp.call('Emulation.setTouchEmulationEnabled', { enabled: viewport.mobile, maxTouchPoints: viewport.mobile ? 5 : 1 }, sid);
  await cdp.call('Emulation.setEmulatedMedia', { media: 'screen', features: [{ name: 'prefers-reduced-motion', value: 'reduce' }] }, sid);

  const url = new URL(route, cfg.baseUrl.endsWith('/') ? cfg.baseUrl : `${cfg.baseUrl}/`).href;
  const loaded = cdp.once('Page.loadEventFired', sid);
  await cdp.call('Page.navigate', { url }, sid); await loaded; await sleep(350);
  d.checks = await evalValue(cdp, sid, CHECK);
  if (d.checks.interactive) {
    await cdp.call('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Tab', code: 'Tab', windowsVirtualKeyCode: 9 }, sid);
    await cdp.call('Input.dispatchKeyEvent', { type: 'keyUp', key: 'Tab', code: 'Tab', windowsVirtualKeyCode: 9 }, sid);
    await sleep(60);
    d.activeAfterTab = await evalValue(cdp, sid, 'document.activeElement?.tagName || null');
  }
  await evalValue(cdp, sid, 'window.scrollTo(0, document.documentElement.scrollHeight * .55); true'); await sleep(250);
  d.afterScroll = await evalValue(cdp, sid, CHECK);
  const shot = await cdp.call('Page.captureScreenshot', { format: 'png', fromSurface: true }, sid);
  d.screenshot = path.join(cfg.out, `${slug(route)}-${viewport.name}.png`);
  await writeFile(d.screenshot, Buffer.from(shot.data, 'base64'));
  stops.forEach((off) => off());

  const f = [];
  if (!d.checks.title) f.push('missing title');
  if (!d.checks.text) f.push('empty body');
  if (d.checks.mains !== 1) f.push(`expected one main, found ${d.checks.mains}`);
  if (d.checks.h1s < 1) f.push('missing h1');
  if (d.checks.overflow > 8 || d.afterScroll.overflow > 8) f.push('horizontal overflow');
  if (d.checks.missingAlt) f.push(`${d.checks.missingAlt} image(s) missing alt`);
  if (d.checks.unnamed) f.push(`${d.checks.unnamed} unnamed interactive element(s)`);
  if (d.checks.duplicateIds.length) f.push(`duplicate ids: ${d.checks.duplicateIds.join(',')}`);
  if (!d.checks.reducedMotion) f.push('reduced-motion emulation failed');
  if (d.checks.interactive && ['BODY', 'HTML', null].includes(d.activeAfterTab)) f.push('keyboard Tab did not reach an interactive element');
  if (d.errors.length) f.push(`${d.errors.length} console error(s)`);
  if (d.exceptions.length) f.push(`${d.exceptions.length} uncaught exception(s)`);
  if (d.networkFailures.length) f.push(`${d.networkFailures.length} network failure(s)`);
  d.failures = f; d.ok = !f.length; return d;
}

async function waitForExit(proc, timeoutMs = 2500) {
  if (proc.exitCode != null || proc.signalCode != null) return true;
  return await new Promise((resolve) => {
    const timer = setTimeout(() => { cleanup(); resolve(false); }, timeoutMs);
    const onExit = () => { cleanup(); resolve(true); };
    const cleanup = () => { clearTimeout(timer); proc.off('exit', onExit); };
    proc.once('exit', onExit);
  });
}

async function removeProfile(profile) {
  const retryable = new Set(['ENOTEMPTY', 'EBUSY', 'EPERM']);
  let lastError;
  for (let attempt = 1; attempt <= 8; attempt++) {
    try {
      await rm(profile, { recursive: true, force: true });
      return;
    } catch (error) {
      lastError = error;
      if (!retryable.has(error?.code) || attempt === 8) break;
      await sleep(100 * attempt);
    }
  }
  console.warn(`WARN: unable to remove temporary Chrome profile ${profile}: ${lastError?.message || lastError}`);
}

async function shutdownChrome(cdp, proc, profile) {
  try { cdp?.ws.close(); } catch {}
  if (proc.exitCode == null && proc.signalCode == null) proc.kill('SIGTERM');
  if (!(await waitForExit(proc))) {
    try { proc.kill('SIGKILL'); } catch {}
    await waitForExit(proc, 1500);
  }
  await removeProfile(profile);
}

async function main() {
  const cfg = args(); cfg.out = path.resolve(cfg.out); await mkdir(cfg.out, { recursive: true });
  const chrome = chromePath(cfg.chrome), profile = await mkdtemp(path.join(tmpdir(), 'pudding-qa-'));
  const proc = spawn(chrome, ['--headless=new', '--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage', '--no-first-run', '--remote-debugging-port=0', `--user-data-dir=${profile}`, 'about:blank'], { stdio: ['ignore', 'ignore', 'pipe'] });
  let stderr = ''; proc.stderr.on('data', (x) => { stderr += x.toString(); });
  let cdp;
  try {
    cdp = await connectFromChrome(() => stderr, proc);
    const { targetId } = await cdp.call('Target.createTarget', { url: 'about:blank' });
    const { sessionId } = await cdp.call('Target.attachToTarget', { targetId, flatten: true });
    for (const domain of ['Page', 'Runtime', 'Log', 'Network']) await cdp.call(`${domain}.enable`, {}, sessionId);
    const viewports = [{ name: 'desktop', width: 1440, height: 900, mobile: false }, { name: 'mobile', width: 390, height: 844, mobile: true }];
    const results = [];
    for (const route of cfg.routes) for (const viewport of viewports) results.push(await caseRun(cdp, sessionId, cfg, route, viewport));
    const report = { generatedAt: new Date().toISOString(), baseUrl: cfg.baseUrl, status: results.every((r) => r.ok) ? 'PASS' : 'FAIL', passed: results.filter((r) => r.ok).length, total: results.length, results };
    await writeFile(path.join(cfg.out, 'browser-qa.json'), JSON.stringify(report, null, 2) + '\n');
    for (const r of results) {
      console.log(`${r.ok ? 'PASS' : 'FAIL'} ${r.route} ${r.viewport}${r.failures.length ? ` — ${r.failures.join('; ')}` : ''}`);
      if (!r.ok) {
        for (const value of r.errors) console.log(`  console: ${value}`);
        for (const value of r.exceptions) console.log(`  exception: ${value}`);
        for (const value of r.networkFailures) console.log(`  network: ${value}`);
      }
    }
    console.log(`${report.status}: ${report.passed}/${report.total} browser QA cases passed.`);
    if (report.status !== 'PASS') process.exitCode = 1;
  } finally {
    await shutdownChrome(cdp, proc, profile);
    if (process.exitCode && stderr) await writeFile(path.join(cfg.out, 'chrome-stderr.log'), stderr);
  }
}

main().catch((error) => { console.error(error.stack || error); process.exit(1); });
