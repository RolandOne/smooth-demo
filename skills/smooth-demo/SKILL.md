---
name: smooth-demo
description: Create product demo videos from the actual app UI using browser or app-window recording and fictional data, including Screen Studio-style smooth cursor and zoom effects. Use for short workflow clips or long executive approval walkthroughs with a table of contents, chapter cards, OpenAI TTS voice samples or selected-voice narration, synchronized captions, and playback verification. Also use to revise narration on existing demo footage.
---

# Smooth Demo

## Purpose

Create demo videos from the actual product UI using seeded data and controlled browser/app interaction. Do not recreate product components in a landing page unless the user explicitly requests a mockup.

Default approach:

1. Use the real app route and seeded demo organization.
2. Script the story as a sequence of visible user actions.
3. Record the browser tab/window.
4. Drive the UI with Computer Use or browser automation.
5. Render the captured UI with wallpaper framing, smooth cursor motion, click pulses, and eased zoom in/out using `scripts/render-motion.py`.
6. Review the final styled export, then add narration/captions when requested.

Read `references/workflow.md` before planning or recording a demo. Read `references/deploymu-stories.md` when working in DeployMu.

For executive/client approval videos, multiple chapters in one video, TTS narration, voice auditions, or replacing narration on existing footage, also read `references/executive-narration.md` before acting. Its chapter and audio workflow extends the short-demo workflow; honor the requested deliverable rather than splitting a requested long video into separate demos.

For every new demo, read [references/cinematic-motion.md](references/cinematic-motion.md). Use the bundled capture helper with viewport checks and interruption recovery, action-based timeline planner, and configurable renderer with draft previews and curved cursor motion; keep the actual UI footage and verify the final action succeeded. Wallpaper defaults follow the render host: Lake Tahoe Day on macOS, Windows 11 Bloom on Windows; custom backgrounds remain available.

Default to a silent video with timed explanatory subtitles in a dedicated band below the app canvas. Describe the visible action/result; keep text outside the app area even during zooms. Supply `subtitles` cues to the motion renderer. Do not generate speech by default.

Generate OpenAI voiceover only when explicitly requested. Before any speech API call, tell the user: "This voiceover uses the OpenAI API, requires an OpenAI API key, and incurs API usage charges separate from your ChatGPT/Codex subscription." Use Marin unless another voice is selected. Honor existing budget/authorization; do not add repeated confirmation gates. If the key or API is unavailable, report that and continue with subtitles; never silently substitute a system voice.

## Default visual contract

Invoking `$smooth-demo` requests the styled video by default; the user does not need to repeat "smooth cursor" or "macOS background". This applies to basic walkthroughs, long videos, and narrated demos too. Only an explicit request for raw footage or a different visual style overrides it. Narration-only revisions preserve the existing visuals unless a visual change is requested.

- Render real UI footage through `scripts/render-motion.py` (or a verified equivalent that delivers all these effects). Raw capture, a slideshow, chapter bars, or direct FFmpeg narration assembly alone is not the finished smooth demo.
- Show wallpaper margins around the app at wide framing: Lake Tahoe Day for macOS, Windows 11 Bloom for Windows. Resolve the user's target OS before rendering and write `backgroundPreset: "macos"` or `"windows"` explicitly when the render host differs (for example Linux/WSL/cloud). Retain an explicit custom background choice.
- Capture timed cursor targets during real interactions; render an eased, curved pointer that reaches the actual click locations. A stationary default cursor or missing action markers does not satisfy the requirement. Capture without a baked-in native cursor to avoid duplicates.
- Include eased zoom in to meaningful controls/results and zoom out for context/navigation. Keep fields readable and avoid zooming every click.
- Render a short representative preview early and inspect a wide frame, moving pointer, click, and zoom transition. At delivery verify these effects in the final video after narration/caption assembly. If a tool cannot provide them, try the documented fallback; report an incomplete styled export rather than silently dropping effects.

## Motion quality gate

For every new recording, apply the [motion checklist](references/cinematic-motion.md#motion-quality-checklist) before the full take and again after the final export. The early test must include a tab change, a long scroll, a click, and a zoom, reviewed in motion at normal playback speed.

If any scroll jumps, cursor teleports, click misses its target, or camera transition snaps, the demo is not finished. Correct the capture or edit and review it again before delivery. Screenshots and successful decoding alone do not establish smoothness. If the available tools cannot meet this gate, describe the concrete limitation and label the recording as an incomplete draft.

## When To Use

Use this skill for requests like:

- "Record a demo of this flow."
- "Make a landing page video using the real app."
- "Have Codex click through the seeded demo and record it."
- "Create a sales demo video / planning demo video."
- "Use the current tab and screen recording instead of recreating components."

## Core Rules

- Prefer the real app UI over rebuilt demo components.
- Use seeded data; do not use private production data.
- Default to 30–90 seconds for a landing-page clip. For an executive overview, default to a cohesive 3–6 minute story unless the user specifies otherwise.
- Use stable routes, filters, dates, and seed records so the recording is repeatable.
- Hide or avoid distracting browser chrome, dev overlays, logs, and personal information.
- Verify the recording visually before reporting success.
- Treat recording, paid audio generation, and external delivery as separate scopes. Do not send a video to a client, publish it, or deploy app changes without authorization.

For multi-browser-tab, overlapping-window, before/after, or multi-viewport demos, or when evaluating this skill, read [references/scenario-review.md](references/scenario-review.md). Choose its visible-tabs, partial-overlap, or near-complete-overlap layout to fit the story; honor any layout the user specifies. Requested browser tabs and window stacking must be visible in the export, not replaced by cuts between page-only captures. Apply only the scenarios relevant to the requested demo.

## Deliverables

For planning tasks, produce:

- Story objective.
- Target route and seeded org/context.
- Shot list with exact user actions.
- Recording setup.
- Acceptance checklist.

For execution tasks, produce:

- Recorded video path.
- Script/shot list used.
- Verification notes.
- Any retakes or gaps.

## Tool Preference

- Use Browser or Playwright for deterministic navigation, clicks, forms, and screenshots.
- Use Computer Use when the task depends on the visible current tab, OS screen recorder, browser chrome, or non-DOM UI.
- Use Chrome when logged-in profile state or existing authenticated tabs are required.
- If a recording tool is unavailable, produce the shot list and exact operator instructions rather than faking a component demo.

## Quality Bar

- The video must look like the actual app.
- Actions should be slow enough to follow but not sluggish.
- Every shot should communicate one product outcome.
- No broken loading states, unexplained empty states, console overlays, or visual glitches. Legitimate empty states may be shown when they serve the story and are explained.
- Final frame should land on a useful success/result state.
