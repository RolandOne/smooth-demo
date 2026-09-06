import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { createRecorder } from '../capture-cdp.mjs';

function png(width, height) {
  const buffer = Buffer.alloc(24);
  Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]).copy(buffer);
  buffer.writeUInt32BE(width, 16);
  buffer.writeUInt32BE(height, 20);
  return buffer.toString('base64');
}

function deferred() {
  let resolve;
  const promise = new Promise(done => { resolve = done; });
  return { promise, resolve };
}

function fake({ width = 1440, fail = false } = {}) {
  let reads = 0;
  let started = false;
  const frameAcked = deferred();
  const disconnected = deferred();
  return {
    commands: [],
    frameAcked: frameAcked.promise,
    disconnected: disconnected.promise,
    async send(method) {
      this.commands.push(method);
      if (method === 'Page.getLayoutMetrics') {
        return { cssVisualViewport: { clientWidth: 1440, clientHeight: 900 } };
      }
      if (method === 'Page.captureScreenshot') return { data: png(width, 900) };
      if (method === 'Page.startScreencast') started = true;
      if (method === 'Page.screencastFrameAck') frameAcked.resolve();
      return {};
    },
    async readEvents() {
      if (!started) return { cursor: 0, events: [] };
      reads++;
      if (reads === 1) {
        return { cursor: 1, events: [{ params: { data: png(1440, 900), sessionId: 1 } }] };
      }
      if (fail) {
        disconnected.resolve();
        throw new Error('Simulated disconnection');
      }
      await new Promise(resolve => setTimeout(resolve, 5));
      return { cursor: reads, events: [] };
    },
  };
}

async function directory(t) {
  const dir = await fs.mkdtemp(path.join(os.tmpdir(), 'demo-capture-test-'));
  t.after(() => fs.rm(dir, { recursive: true, force: true }));
  return dir;
}

const options = { timeout: 5000 };

test('rejects cropped preflight before starting screencast and saves diagnosis', options, async t => {
  const dir = await directory(t);
  const cdp = fake({ width: 1280 });
  const recorder = createRecorder(cdp, dir);
  await assert.rejects(recorder.start(), /Viewport mismatch/);
  assert(!cdp.commands.includes('Page.startScreencast'));
  assert.equal(JSON.parse(await fs.readFile(path.join(dir, 'capture.json'))).status, 'failed');
});

test('interruption preserves frames and durable action journal', options, async t => {
  const dir = await directory(t);
  const cdp = fake({ fail: true });
  const recorder = createRecorder(cdp, dir);
  await recorder.start();
  recorder.mark('click-submit', { x: 700, y: 500 });
  // Wait for the simulated fault, not an arbitrary allowance for disk I/O.
  await cdp.disconnected;
  await assert.rejects(recorder.stop(), /Simulated disconnection/);
  const manifest = JSON.parse(await fs.readFile(path.join(dir, 'capture.json')));
  assert.equal(manifest.status, 'interrupted');
  assert.equal(manifest.frames.length, 1);
  assert.match(await fs.readFile(path.join(dir, 'events.jsonl'), 'utf8'), /click-submit/);
  await fs.access(path.join(dir, manifest.frames[0].file));
});

test('complete take is resumably saved and cannot be overwritten', options, async t => {
  const dir = await directory(t);
  const cdp = fake();
  const recorder = createRecorder(cdp, dir);
  await recorder.start();
  await cdp.frameAcked;
  const manifest = await recorder.stop();
  assert.equal(manifest.status, 'complete');
  assert.equal(manifest.frames.length, 1);
  await assert.rejects(createRecorder(fake(), dir).start(), /already contains/);
});
