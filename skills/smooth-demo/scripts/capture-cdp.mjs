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

export function createRecorder(cdp, directory) {
  let running = false, task, cursor, started, failure, requested, stopped, active = false;
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
          throw new Error(`Viewport mismatch: requested ${width}x${height}, layout ${actual.width}x${actual.height}, pixels ${pixels.width}x${pixels.height}. Set the browser viewport before recording.`);
        cursor = (await cdp.readEvents({ methods: ['Page.screencastFrame'] })).cursor;
        // Timing starts after preflight so setup latency is not footage.
        started = Date.now();
        await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 95, maxWidth: width, maxHeight: height, everyNthFrame: 1 });
        active = true; running = true;
        await persist('recording');
        task = (async () => {
          try {
            while (running) {
              const batch = await cdp.readEvents({ afterSequence: cursor, methods: ['Page.screencastFrame'], timeoutMs: 500, limit: 100 });
              cursor = batch.cursor;
              if (batch.truncated) throw new Error('Capture buffer truncated; partial take saved');
              for (const event of batch.events) {
                const p = event.params;
                try {
                  const data = Buffer.from(p.data, 'base64');
                  if (!sameSize(imageSize(data), requested)) throw new Error('Screencast dimensions changed; partial take saved');
                  const file = `frame-${String(frames.length).padStart(6, '0')}.jpg`;
                  const frame = { file, time: elapsed() };
                  await fs.writeFile(path.join(directory, file), data);
                  frames.push(frame);
                  await persist('recording');
                } finally { await cdp.send('Page.screencastFrameAck', { sessionId: p.sessionId }); }
              }
            }
          } catch (e) { failure = e; running = false; await persist('interrupted'); }
        })();
      } catch (e) {
        failure = e; running = false;
        if (active) { try { await cdp.send('Page.stopScreencast'); } catch {} active = false; }
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
      try { await task; } catch (e) { failure ??= e; }
      if (error) failure ??= error instanceof Error ? error : new Error(String(error));
      if (active) {
        try { await cdp.send('Page.stopScreencast'); } catch (e) { failure ??= e; }
        active = false;
      }
      if (!frames.length) failure ??= new Error('No screen frames captured');
      stopped = await persist(failure ? 'interrupted' : 'complete');
      if (failure) throw new Error(`${failure.message}. Recovery: ${path.join(directory, 'capture.json')}`);
      return stopped;
    },
  };
}

// Keep this entire call in one CUA REPL invocation. Pass recorder explicitly.
export async function recordChapter(cdp, directory, options, actions) {
  const recorder = createRecorder(cdp, directory);
  await recorder.start(options);
  let actionError;
  try { await actions(recorder); } catch (e) { actionError = e; }
  return recorder.stop({ error: actionError });
}
