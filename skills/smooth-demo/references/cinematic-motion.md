# Cinematic cursor and camera motion

Use this mode for Screen Studio-style demos: real UI footage with a wallpaper canvas, padded window, smooth cursor, click pulses, and zoom/pan transitions. The effects are post-production; preserve the actual app UI and outcomes. The bundled renderer uses scripted targets, not automatic click inference.

## Motion quality checklist

- **Scrolling:** Record gradual, continuous scrolling with eased starts and stops, using small frequent increments or a supported native smooth gesture. Never use page-sized jumps, instant scroll-to-top resets, or locator auto-scroll as finished footage. Target roughly 250–450 pixels per second, adjusting for readability. Post-production cursor and camera effects do not smooth captured page movement.
- **Capture quality:** Target at least 30 captured frames per second during movement. Check frame cadence specifically during scrolling; static holds need no new frames. A 60 fps export cannot repair choppy source footage. If capture drops or stalls, reduce capture overhead, shorten takes, or change the supported recording method, then retest.
- **Cursor accuracy:** Bring the pointer to the target before clicking. Re-measure targets after vertical or horizontal scrolling; keep markers aligned with actual click times and coordinates. Prevent duplicate native and rendered cursors.
- **Separate movements:** Finish scrolling before clicking or zooming. Keep the camera steady during page movement; avoid simultaneous scroll, camera pan, and zoom unless explicitly choreographed and reviewed.
- **Camera restraint:** Zoom only to improve readability. Ease transitions over 1–1.5 seconds, hold the useful result, and return wide before navigation. Keep controls and captions readable without abrupt crops.
- **Reading time:** Hold important content for 2–4 seconds. Scroll through overlapping sections so viewers can follow newly revealed content; shorten empty sections rather than rushing dense content.
- **Loading transitions:** Wait for the visible UI to settle before continuing. Trim long loading pauses and retake unstable layout shifts, broken states, and accidental actions. Do not present a pre-load frame as the completed result.
- **Chapter continuity:** Match scroll position, cursor position, and camera framing across adjoining clips. Capture gradual returns or use an intentional editorial transition; never join mismatched screen states as if movement were continuous. Preserve action and caption timing through trims.
- **Early motion test:** Before recording the complete story, capture one tab change, one long scroll, one click, and one zoom. Render the styled preview and watch it at normal speed, including the beginning and end of the scroll. Proceed only when the source scroll and exported motion are both smooth.
- **Final review:** Watch every scroll and transition in motion at normal speed. Check clicks and chapter seams as well as opening and closing. Record the reviewed intervals and any retakes. Screenshots, frame-rate metadata, and a successful full decode supplement this review; they do not replace it.

## Capture

Use an existing supported tab recorder, or the bundled `scripts/capture-cdp.mjs` with the selected tab's documented CDP capability. Read the current browser capability documentation first. The helper only consumes screencast frames and acknowledges them; browser interactions still use supported UI tools.

```javascript
const { recordChapter } = await import('/absolute/skill/path/scripts/capture-cdp.mjs');
const manifest = await recordChapter(cdp, '/absolute/output/take-01',
  { width: 1440, height: 900 }, async recorder => {
    // Resolve targets from current UI and scroll into view before measuring.
    // Mark actual actions; never put passwords or field values in metadata.
    recorder.mark('move-email', { x: 720, y: 400 });
    // Move/pace, then mark immediately before the real click.
    recorder.mark('click-email', { x: 720, y: 400, cursor: 'text' });
    // Perform supported browser actions and verify the visible result here.
  });
```

Drain frames concurrently while interacting, and stop capture even on an interaction failure. In Codex CUA REPL, start, interact, and stop within the same tool invocation: pending CDP operations lose their execution context when that invocation ends. For adaptive workflows, record one short chapter per invocation and combine their manifests afterward. Never leave a capture pump running between tool calls. `capture.json` stores relative frame paths, wall-clock times, named events, and duration. Screens without pixel changes hold the preceding frame. Avoid capturing passwords in plaintext, credentials in URLs, private autocomplete, account menus, or notifications. Record with fictional data in a verified local/test environment where practical. An app simulator is a different deliverable; do not substitute it silently for the actual app.

If Google or another site challenges an isolated automation browser, use an available authorized regular browser session. Do not solve challenges without the required authorization. Do not pass a failed take off as successful footage.

The recorder automatically compares requested dimensions, browser layout metrics, and a preflight screenshot before starting, then checks every screencast frame. A mismatch stops the take and writes diagnostics. In the Codex in-app browser use the documented browser `viewport` capability when fixed recording dimensions are needed; a raw CDP emulation override can leave the screencast clipped to the old surface. Re-measure a target after scrolling it into view, before recording its click coordinates.

Join successful chapter manifests without re-encoding using `python3 scripts/join-captures.py /output/combined.json /output/chapter-01/capture.json /output/chapter-02/capture.json`. The combined manifest offsets frames and events and retains chapter boundaries. Do not include failed or rehearsal takes.

### Scroll and timing implementation

A browser `scroll` method is not evidence of smooth motion: some implementations jump instantly. Prefer a supported continuous native gesture, then verify its captured result. Size command timeouts to exceed the gesture duration (distance divided by speed) plus overhead, especially for returns to the top. Do not shorten or jump a scroll to fit a tool timeout.

If native continuous gestures are unavailable and wheel-command round trips cause stutter, an allowed page-animation API can drive an eased, requestAnimationFrame-based scroll on the observed scroll container. Keep this confined to scrolling; do not modify product styling or data. Verify source cadence and playback again; support for raw browser commands varies by backend.

When screencast frames expose capture timestamps, preserve those source timestamps rather than assigning delivery times; buffered delivery can introduce artificial timing jitter. Measure frame cadence over the moving portion, not across intentional reading holds.

## Recovery

Every saved frame checkpoints `capture.json` atomically. Action marks also append to `events.jsonl`, so a tool interruption preserves the latest actions even between frame updates. A normal stop sets `status: complete`; interruptions preserve frames and diagnostics with `status: interrupted`. Abruptly abandoned captures may retain `status: recording`. Inspect those partial takes and the action journal before retrying. Chapter joining and planning reject incomplete statuses; do not label recovered footage a successful workflow without verifying its outcome. Existing take directories are protected against accidental overwrite.

## Automatic draft timeline

Run `python3 scripts/plan-motion.py /output/combined.json /output/motion.json --label "App demo"`. The planner groups action markers by chapter, suggests zoom regions, returns to the full view before a `zoom-out` marker, and creates editable cursor paths. Navigation/submit markers stay wide. It does not inspect video pixels to discover clicks.

Use `move-NAME` before the approach, `click-NAME` at the actual click, `zoom-out` before navigation, and `focus-outcome` for a closing result. Click metadata may set `cursor: arrow|hand|text` and `focusBox: [x,y,width,height]`; otherwise simple marker-name heuristics provide a starting point. Review suggested framing and timing. All coordinates refer to captured viewport pixels.

## Timeline and render

Requires Python 3 with Pillow plus `ffmpeg` and `ffprobe` on PATH. Run:

```sh
python3 /absolute/skill/path/scripts/render-motion.py /absolute/output/motion.json --preview
# Review the separate half-size, 24 fps preview before final export.
python3 /absolute/skill/path/scripts/render-motion.py /absolute/output/motion.json
```

Minimal configuration, with all x/y coordinates in the original captured viewport's pixels:

```json
{
  "capture": "take-01/capture.json",
  "output": "demo.mp4",
  "duration": 20,
  "size": [1600, 1000],
  "fps": 60,
  "label": "App demo",
  "padding": 90,
  "camera": [
    {"time": 0, "zoom": 1, "x": 720, "y": 450},
    {"time": 2, "zoom": 1, "x": 720, "y": 450},
    {"time": 3.5, "zoom": 1.7, "x": 720, "y": 400},
    {"time": 7, "zoom": 1.7, "x": 720, "y": 400},
    {"time": 8.5, "zoom": 1, "x": 720, "y": 450}
  ],
  "cursor": [
    {"time": 0, "x": 1100, "y": 700},
    {"time": 1, "x": 1100, "y": 700},
    {"time": 3, "x": 500, "y": 400},
    {"time": 7, "x": 500, "y": 400}
  ],
  "clicks": [{"time": 3, "x": 500, "y": 400}]
}
```

Paths resolve relative to the config. As an alternative to `capture`, set `video` to a raw recording path. By default, `backgroundPreset: "auto"` uses bundled Lake Tahoe Day on macOS and Windows 11 Bloom (dark blue) on Windows, detected from the renderer host. Other systems retain the generated purple gradient. Set `backgroundPreset` to `macos`, `windows`, or `gradient` to override detection (including when rendering in Linux/WSL for a Windows demo). Optional `background` supplies a local image and takes precedence over presets. Images fill the canvas with a centered crop that preserves their aspect ratio. Both wallpapers are bundled under `assets/backgrounds/`, so renders need no network access; copy the complete skill folder to other machines. Asset provenance is in [wallpaper-sources.md](wallpaper-sources.md). Optional `redactions` contains `{ "box": [left, top, right, bottom], "fill": "#f9fafb" }` rectangles in source pixels. Use `"sample": [x, y]` instead of `fill` to sample a nearby background pixel per frame, useful for removing a development badge over changing backgrounds. These export-only overlays never alter the site. The default output is silent; for narration, render visuals first and then follow the existing narration workflow.

Keyframes have strictly increasing nonnegative times. Coordinates track viewport locations, so remeasure after scrolls and navigation. Start/end at zoom 1; allow roughly 1–1.5 seconds for zooms and hold important outcomes long enough to read. Zoom out before navigation. Cursor motion uses quintic easing along gently curved paths and a separate overlay, so recordings must not contain a baked-in native cursor. The 60 fps output smooths camera/pointer motion; it does not manufacture higher-frequency source UI changes. A final still hold is intentional, not proof of a completed action.

Set `cursorSize` (default 32 output pixels) and `cursorCurvature` (default 0.16; 0 gives straight paths) to tune the pointer. Cursor keyframes accept `kind: arrow|hand|text`. Moving pointers use the arrow and switch to the destination shape on arrival. Curves retain exact click endpoints. Preview rendering writes a separate `-preview.mp4` and leaves the final export untouched.

## Verification

Review the exported motion around clicks, scrolls, route changes, and the final outcome. Check for a double cursor, wrong click coordinates, camera jumps, clipped fields, sensitive content, or a success frame that precedes actual persistence. Validate duration, resolution, frame rate, and full FFmpeg decode. For creation workflows, verify the final created record in the test environment. Keep the capture manifest, timeline, and final MP4 together for revision.

## Default explanatory subtitles

For new demos, write concise cues from observed actions/results and include them in `motion.json`:

```json
"subtitles": [
  {"start": 0, "end": 4, "text": "Open Requests to review pending items."},
  {"start": 4, "end": 8, "text": "Select New Request to enter the details."}
]
```

The renderer reserves the bottom 14% of the output for a dark subtitle band, fits the app/camera into the remaining area, and draws centered white text after camera motion. The output dimensions stay unchanged. Text cannot overlap the app even during zoom. Cues must be ordered, non-overlapping, within the duration, and at most two wrapped lines. Write cues manually from verified behavior; the planner does not infer explanations. For an explicitly requested text-free export omit `subtitles`. Narrated videos use the same outside-app placement for captions; align cues with the final audio.
