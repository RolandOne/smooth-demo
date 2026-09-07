import fs from 'node:fs/promises';
import { appendFileSync } from 'node:fs';
import path from 'node:path';

export function imageSize(buffer) {
  if (buffer.subarray(0, 8).equals(Buffer.from([137,80,78,71,13,10,26,10])))
    return { width: buffer.readUInt32BE(16), height: buffer.readUInt32BE(20) };
  if (buffer[0] === 255 && buffer[1] === 216) {
    let i = 2;
    while (i + 8 < buffer.length) {
      if (buffer[i++] !== 255) continue;
      while (buffer[i] === 255) i++;
      const marker = buffer[i++];
      if (marker === 217 || marker === 218) break;
      if (marker === 1 || (marker >= 208 && marker <= 215)) continue;
      const length = buffer.readUInt16BE(i);
      if ([192,193,194,195,197,198,199,201,202,203,205,206,207].includes(marker))
        return { height: buffer.readUInt16BE(i + 3), width: buffer.readUInt16BE(i + 5) };
      if (length < 2) break;
      i += length;
    }
  }
  throw new Error('Unsupported or incomplete captured image');
}

// `cdp` is either a push-style session exposing send/on/off (a Playwright
// CDPSession from page.context().newCDPSession(page)) or a polling-style
// session exposing send/readEvents (the Codex desktop browser). Push frames
// are serialised through one promise chain; polled frames drain in a pump
// task. Interaction code runs concurrently in both modes.
export function createRecorder(cdp, directory) {
  const push = typeof cdp.on === 'function' && typeof cdp.off === 'function';
  if (!push && typeof cdp.readEvents !== 'function')
    throw new Error('cdp must expose on/off (Playwright CDPSession) or readEvents (Codex browser)');
  let running = false, started, failure, requested, stopped, active = false, task, cursor;
  let chain = Promise.resolve();
  const frames = [], events = [];
  const elapsed = () => started ? (Date.now() - started) / 1000 : 0;
  const sameSize = (a, b) => a.width === b.width && a.height === b.height;
  const snapshot = (status) => ({ version: 2, status, viewport: requested, frames, events,
    duration: elapsed(), ...(failure ? { error: failure.message } : {}) });
  async function persist(status) {
    const manifest = snapshot(status);
    await fs.writeFile(path.join(directory, 'capture.json.tmp'), JSON.stringify(manifest, null, 2));
    await fs.rename(path.join(directory, 'capture.json.tmp'), path.join(directory, 'capture.json'));
    return manifest;
  }
  async function stopScreencast() {
    if (!active) return;
    active = false;
    if (push) cdp.off('Page.screencastFrame', onFrame);
    try { await cdp.send('Page.stopScreencast'); } catch (e) { failure ??= e; }
  }
  async function handleFrame(p) {
    if (!running) return;
    try {
      const data = Buffer.from(p.data, 'base64');
      if (!sameSize(imageSize(data), requested)) throw new Error('Screencast dimensions changed; partial take saved');
      const file = `frame-${String(frames.length).padStart(6, '0')}.jpg`;
      const frame = { file, time: elapsed() };
      await fs.writeFile(path.join(directory, file), data);
      frames.push(frame);
      await persist('recording');
    } finally {
      // Chrome withholds the next frame until the previous one is acknowledged.
      await cdp.send('Page.screencastFrameAck', { sessionId: p.sessionId });
    }
  }
  function onFrame(p) {
    chain = chain.then(() => handleFrame(p)).catch(async (e) => {
      // Record the fault even if stop() already flipped `running`, so a
      // session dropped mid-take is never reported as a complete capture.
      failure ??= e;
      if (!running) return;
      running = false;
      await stopScreencast();
      await persist('interrupted');
    });
  }
  async function pump() {
    try {
      while (running) {
        const batch = await cdp.readEvents({ afterSequence: cursor, methods: ['Page.screencastFrame'], timeoutMs: 500, limit: 100 });
        cursor = batch.cursor;
        if (batch.truncated) throw new Error('Capture buffer truncated; partial take saved');
        for (const event of batch.events) await handleFrame(event.params);
      }
    } catch (e) { failure = e; running = false; await persist('interrupted'); }
  }
  return {
    async start({ width = 1440, height = 900 } = {}) {
      if (started) throw new Error('Use a new recorder for each take');
      await fs.mkdir(directory, { recursive: true });
      try { await fs.access(path.join(directory, 'capture.json')); throw new Error('Capture directory already contains a take'); }
      catch (e) { if (e.code !== 'ENOENT') throw e; }
      requested = { width, height }; started = Date.now();
      try {
        const metrics = await cdp.send('Page.getLayoutMetrics');
        const viewport = metrics.cssVisualViewport ?? metrics.cssLayoutViewport;
        const actual = { width: Math.round(viewport.clientWidth), height: Math.round(viewport.clientHeight) };
        const shot = await cdp.send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
        const pixels = imageSize(Buffer.from(shot.data, 'base64'));
        if (!sameSize(requested, actual) || !sameSize(requested, pixels))
          throw new Error(`Viewport mismatch: requested ${width}x${height}, layout ${actual.width}x${actual.height}, pixels ${pixels.width}x${pixels.height}. Set the browser viewport (page.setViewportSize or the host viewport capability) before recording.`);
        if (!push) cursor = (await cdp.readEvents({ methods: ['Page.screencastFrame'] })).cursor;
        // Timing starts after preflight so setup latency is not footage.
        started = Date.now();
        if (push) cdp.on('Page.screencastFrame', onFrame);
        active = true; running = true;
        await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 95, maxWidth: width, maxHeight: height, everyNthFrame: 1 });
        await persist('recording');
        if (!push) task = pump();
      } catch (e) {
        failure = e; running = false;
        await stopScreencast();
        await persist('failed'); throw e;
      }
    },
    mark(name, details = {}) {
      if (!running) throw new Error(failure?.message ?? 'Recorder is not running');
      const event = { ...details, name, time: elapsed() }; events.push(event);
      // Durable action journal survives abrupt tool/process interruption.
      appendFileSync(path.join(directory, 'events.jsonl'), JSON.stringify(event) + '\n');
      return event;
    },
    async stop({ error } = {}) {
      if (stopped) return stopped;
      running = false;
      if (task) { try { await task; } catch (e) { failure ??= e; } }
      await stopScreencast();
      await chain;
      if (error) failure ??= error instanceof Error ? error : new Error(String(error));
      if (!frames.length) failure ??= new Error('No screen frames captured');
      stopped = await persist(failure ? 'interrupted' : 'complete');
      if (failure) throw new Error(`${failure.message}. Recovery: ${path.join(directory, 'capture.json')}`);
      return stopped;
    },
  };
}

// `target` is a Playwright Page (a CDP session is opened for it), a Playwright
// CDPSession, or a Codex browser cdp object. Pass the recorder to `actions`
// explicitly; capture stops even when an action throws. Keep start, interact
// and stop in one process or one CUA REPL invocation: the session dies with it.
export async function recordChapter(target, directory, options, actions) {
  const cdp = typeof target.context === 'function' ? await target.context().newCDPSession(target) : target;
  const recorder = createRecorder(cdp, directory);
  await recorder.start(options);
  let actionError;
  try { await actions(recorder); } catch (e) { actionError = e; }
  return recorder.stop({ error: actionError });
}
