#!/usr/bin/env node
import { spawn, spawnSync } from 'node:child_process';
import { mkdir, mkdtemp, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function args() {
  const cfg = {
    baseUrl: 'http://127.0.0.1:4173',
    out: '.qa/visual-probe.json',
    routes: ['/', '/generated', '/lab'],
    chrome: process.env.CHROME_BIN || ''
  };
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
    this.ws = ws;
    this.id = 0;
    this.pending = new Map();
    ws.addEventListener('message', (event) => {
      const message = JSON.parse(String(event.data));
      if (!message.id || !this.pending.has(message.id)) return;
      const pending = this.pending.get(message.id);
      this.pending.delete(message.id);
      if (message.error) pending.reject(new Error(message.error.message));
      else pending.resolve(message.result || {});
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
}

async function connect(getStderr, proc) {
  let wsUrl = '';
  for (let i = 0; i < 200; i++) {
    const match = getStderr().match(/DevTools listening on (ws:\/\/[^\s]+)/);
    if (match) {
      wsUrl = match[1];
      break;
    }
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

const PROBE = String.raw`(() => {
  const visible = (el) => {
    const s = getComputedStyle(el), r = el.getBoundingClientRect();
    return s.display !== 'none' && s.visibility !== 'hidden' && Number(s.opacity || 1) > 0 && r.width > 0 && r.height > 0;
  };
  const parseRgb = (value) => {
    const m = String(value || '').match(/rgba?\(([^)]+)\)/i);
    if (!m) return null;
    const p = m[1].split(',').map((x) => Number.parseFloat(x.trim()));
    if (p.length < 3 || p.slice(0, 3).some((x) => !Number.isFinite(x))) return null;
    return { r: p[0], g: p[1], b: p[2], a: Number.isFinite(p[3]) ? p[3] : 1 };
  };
  const luminance = ({ r, g, b }) => {
    const channel = (v) => {
      const x = v / 255;
      return x <= .03928 ? x / 12.92 : ((x + .055) / 1.055) ** 2.4;
    };
    return .2126 * channel(r) + .7152 * channel(g) + .0722 * channel(b);
  };
  const contrast = (a, b) => {
    const l1 = luminance(a), l2 = luminance(b);
    return (Math.max(l1, l2) + .05) / (Math.min(l1, l2) + .05);
  };
  const backgroundFor = (el) => {
    let node = el;
    while (node && node !== document.documentElement) {
      const bg = parseRgb(getComputedStyle(node).backgroundColor);
      if (bg && bg.a > .02) return bg;
      node = node.parentElement;
    }
    return parseRgb(getComputedStyle(document.documentElement).backgroundColor) || { r: 255, g: 255, b: 255, a: 1 };
  };
  const selector = (el) => {
    if (el.id) return '#' + CSS.escape(el.id);
    const classes = [...el.classList].slice(0, 2).map((c) => '.' + CSS.escape(c)).join('');
    return el.tagName.toLowerCase() + classes;
  };

  const copy = [...document.querySelectorAll('main p, main li')]
    .filter((el) => {
      const value = (el.textContent || '').trim();
      const classes = String(el.className || '');
      return visible(el) && value.length >= 80 && !el.closest('footer, nav, aside') && !/(eyebrow|kicker|label|meta|caption|step-num)/i.test(classes);
    })
    .slice(0, 160)
    .map((el) => {
      const r = el.getBoundingClientRect(), s = getComputedStyle(el);
      const font = Number.parseFloat(s.fontSize) || 16;
      const line = Number.parseFloat(s.lineHeight) || font * 1.2;
      return {
        selector: selector(el),
        chars: (el.textContent || '').trim().length,
        width: Math.round(r.width),
        fontPx: Number(font.toFixed(2)),
        lineHeightRatio: Number((line / font).toFixed(2)),
        measureEm: Number((r.width / font).toFixed(1))
      };
    });
  const measures = copy.map((x) => x.measureEm).filter(Number.isFinite).sort((a, b) => a - b);
  const median = measures.length ? measures[Math.floor(measures.length / 2)] : 0;
  const minFont = copy.length ? Math.min(...copy.map((x) => x.fontPx)) : 0;
  const minLeading = copy.length ? Math.min(...copy.map((x) => x.lineHeightRatio)) : 0;

  const headings = [...document.querySelectorAll('main h1, main h2, main h3, main h4, main h5, main h6')]
    .filter(visible)
    .map((el) => ({ level: Number(el.tagName.slice(1)), text: (el.textContent || '').trim().slice(0, 90), selector: selector(el), top: Math.round(el.getBoundingClientRect().top + scrollY) }));
  const headingJumps = [];
  for (let i = 1; i < headings.length; i++) {
    const delta = headings[i].level - headings[i - 1].level;
    if (delta > 1) headingJumps.push({ from: headings[i - 1].level, to: headings[i].level, text: headings[i].text });
  }

  const controls = [...document.querySelectorAll('main button, main input, main select, main textarea, main [role="button"], main [role="link"], main a[href]')]
    .filter((el) => {
      if (!visible(el)) return false;
      if (el.matches('a[href]') && el.closest('p, li') && getComputedStyle(el).display === 'inline') return false;
      return true;
    })
    .map((el) => {
      const r = el.getBoundingClientRect();
      return { selector: selector(el), width: Math.round(r.width), height: Math.round(r.height), text: (el.textContent || el.getAttribute('aria-label') || '').trim().slice(0, 70) };
    });
  const smallTargets = controls.filter((x) => x.width < 44 || x.height < 44).slice(0, 20);

  const clipCandidates = [...document.querySelectorAll('main p, main li, main h1, main h2, main h3, main button, main summary, main th, main td')]
    .filter(visible)
    .filter((el) => {
      const s = getComputedStyle(el);
      const horizontal = el.scrollWidth > el.clientWidth + 2 && !['visible', 'clip'].includes(s.overflowX);
      const vertical = el.scrollHeight > el.clientHeight + 2 && !['visible', 'clip'].includes(s.overflowY);
      return horizontal || vertical;
    })
    .slice(0, 20)
    .map((el) => ({ selector: selector(el), text: (el.textContent || '').trim().slice(0, 80) }));

  const contrastNodes = [...document.querySelectorAll('main p, main li, main h1, main h2, main h3, main button, main a[href], main summary')]
    .filter((el) => visible(el) && (el.textContent || '').trim())
    .slice(0, 180)
    .map((el) => {
      const s = getComputedStyle(el);
      const fg = parseRgb(s.color), bg = backgroundFor(el);
      if (!fg || !bg) return null;
      const ratio = contrast(fg, bg);
      const font = Number.parseFloat(s.fontSize) || 16;
      const bold = Number.parseInt(s.fontWeight, 10) >= 700;
      const large = font >= 24 || (bold && font >= 18.66);
      const required = large ? 3 : 4.5;
      return { selector: selector(el), ratio: Number(ratio.toFixed(2)), required, text: (el.textContent || '').trim().slice(0, 70) };
    })
    .filter(Boolean);
  const lowContrast = contrastNodes.filter((x) => x.ratio < x.required).sort((a, b) => a.ratio - b.ratio).slice(0, 20);
  const severeContrast = contrastNodes.filter((x) => x.ratio < 3).sort((a, b) => a.ratio - b.ratio).slice(0, 20);

  const visuals = [...document.querySelectorAll('main svg, main canvas, main figure, main img')]
    .filter(visible)
    .map((el) => {
      const r = el.getBoundingClientRect();
      return { selector: selector(el), width: Math.round(r.width), height: Math.round(r.height), aspect: Number((r.width / Math.max(1, r.height)).toFixed(2)), top: Math.round(r.top + scrollY) };
    });
  const stickyCount = [...document.querySelectorAll('main *')].filter((el) => visible(el) && ['sticky', 'fixed'].includes(getComputedStyle(el).position)).length;
  const bodyText = (document.querySelector('main')?.innerText || '').trim().length;
  const documentHeight = Math.max(document.documentElement.scrollHeight, document.body?.scrollHeight || 0);
  const h1 = document.querySelector('main h1');

  return {
    viewport: { width: innerWidth, height: innerHeight },
    documentHeight,
    copy: {
      blockCount: copy.length,
      maxMeasureEm: measures.length ? Math.max(...measures) : 0,
      medianMeasureEm: Number(median.toFixed ? median.toFixed(1) : median),
      minFontPx: minFont,
      minLineHeightRatio: minLeading,
      samples: copy.sort((a, b) => b.measureEm - a.measureEm).slice(0, 8)
    },
    headings: { sequence: headings, jumps: headingJumps },
    controls: { count: controls.length, smallTargetCount: smallTargets.length, smallTargets },
    clipping: { count: clipCandidates.length, samples: clipCandidates },
    contrast: { lowCount: lowContrast.length, severeCount: severeContrast.length, lowSamples: lowContrast, severeSamples: severeContrast },
    visuals: { count: visuals.length, items: visuals, wideMobileCount: innerWidth <= 480 ? visuals.filter((x) => x.aspect > 2.4 && x.width > innerWidth * .8).length : 0 },
    composition: {
      h1Bottom: h1 ? Math.round(h1.getBoundingClientRect().bottom) : null,
      firstVisualTop: visuals.length ? visuals[0].top : null,
      stickyCount,
      textCharsPerViewport: Number((bodyText / Math.max(1, documentHeight / innerHeight)).toFixed(1))
    }
  };
})()`;

async function evalValue(cdp, sessionId, expression) {
  const result = await cdp.call('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true }, sessionId);
  if (result.exceptionDetails) throw new Error(result.exceptionDetails.text || 'Runtime.evaluate failed');
  return result.result?.value;
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
  for (let attempt = 1; attempt <= 8; attempt++) {
    try {
      await rm(profile, { recursive: true, force: true });
      return;
    } catch (error) {
      if (!['ENOTEMPTY', 'EBUSY', 'EPERM'].includes(error?.code) || attempt === 8) {
        console.warn(`WARN: unable to remove temporary visual-probe profile: ${error?.message || error}`);
        return;
      }
      await sleep(100 * attempt);
    }
  }
}

async function main() {
  const cfg = args();
  const output = path.resolve(cfg.out);
  await mkdir(path.dirname(output), { recursive: true });
  const chrome = chromePath(cfg.chrome);
  const profile = await mkdtemp(path.join(tmpdir(), 'pudding-visual-'));
  const proc = spawn(chrome, ['--headless=new', '--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage', '--no-first-run', '--remote-debugging-port=0', `--user-data-dir=${profile}`, 'about:blank'], { stdio: ['ignore', 'ignore', 'pipe'] });
  let stderr = '';
  proc.stderr.on('data', (chunk) => { stderr += chunk.toString(); });
  let cdp;
  try {
    cdp = await connect(() => stderr, proc);
    const { targetId } = await cdp.call('Target.createTarget', { url: 'about:blank' });
    const { sessionId } = await cdp.call('Target.attachToTarget', { targetId, flatten: true });
    await cdp.call('Page.enable', {}, sessionId);
    await cdp.call('Runtime.enable', {}, sessionId);
    const viewports = [
      { name: 'desktop', width: 1440, height: 900, mobile: false },
      { name: 'mobile', width: 390, height: 844, mobile: true }
    ];
    const results = [];
    for (const route of cfg.routes) {
      for (const viewport of viewports) {
        await cdp.call('Emulation.setDeviceMetricsOverride', { width: viewport.width, height: viewport.height, deviceScaleFactor: 1, mobile: viewport.mobile, screenWidth: viewport.width, screenHeight: viewport.height }, sessionId);
        await cdp.call('Emulation.setEmulatedMedia', { media: 'screen', features: [{ name: 'prefers-reduced-motion', value: 'reduce' }] }, sessionId);
        const url = new URL(route, cfg.baseUrl.endsWith('/') ? cfg.baseUrl : `${cfg.baseUrl}/`).href;
        await cdp.call('Page.navigate', { url }, sessionId);
        await sleep(700);
        await evalValue(cdp, sessionId, 'window.scrollTo(0, 0); true');
        await sleep(100);
        const metrics = await evalValue(cdp, sessionId, PROBE);
        const routeSlug = route === '/' ? 'home' : route.replace(/^\/+|\/+$/g, '').replace(/[^a-z0-9]+/gi, '-');
        const topPath = path.join(path.dirname(output), `visual-${routeSlug}-${viewport.name}-top.png`);
        const topShot = await cdp.call('Page.captureScreenshot', { format: 'png', fromSurface: true }, sessionId);
        await writeFile(topPath, Buffer.from(topShot.data, 'base64'));
        await evalValue(cdp, sessionId, 'window.scrollTo(0, document.documentElement.scrollHeight * .55); true');
        await sleep(250);
        const midPath = path.join(path.dirname(output), `visual-${routeSlug}-${viewport.name}-mid.png`);
        const midShot = await cdp.call('Page.captureScreenshot', { format: 'png', fromSurface: true }, sessionId);
        await writeFile(midPath, Buffer.from(midShot.data, 'base64'));
        const screenshots = [
          { position: 'top', path: path.relative(process.cwd(), topPath).split(path.sep).join('/') },
          { position: 'mid', path: path.relative(process.cwd(), midPath).split(path.sep).join('/') }
        ];
        results.push({ route, viewport: viewport.name, screenshots, metrics });
        console.log(`PROBE ${route} ${viewport.name} — ${metrics.copy.blockCount} long-form copy blocks, ${metrics.visuals.count} visuals`);
      }
    }
    const report = { generatedAt: new Date().toISOString(), baseUrl: cfg.baseUrl, total: results.length, results };
    await writeFile(output, JSON.stringify(report, null, 2) + '\n');
    console.log(`Wrote visual probe: ${output}`);
  } finally {
    try { cdp?.ws.close(); } catch {}
    if (proc.exitCode == null && proc.signalCode == null) proc.kill('SIGTERM');
    if (!(await waitForExit(proc))) {
      try { proc.kill('SIGKILL'); } catch {}
      await waitForExit(proc, 1500);
    }
    await removeProfile(profile);
  }
}

main().catch((error) => {
  console.error(error.stack || error);
  process.exit(1);
});
