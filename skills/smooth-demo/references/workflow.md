# Screen Recording Workflow

## 1. Define The Story

Write the demo in one sentence:

```text
Show how a user starts from X, performs Y, and reaches visible outcome Z.
```

Keep landing-page demos narrow. For multiple stories, follow the requested format: separate clips if requested, or chapters within one video. For executive or narrated videos, also follow `executive-narration.md`.

## 2. Prepare The App

- Confirm the app is running.
- Confirm the target route loads.
- Confirm the seeded org and records are present.
- Close noisy panels, dev tools, notifications, and irrelevant tabs.
- Set viewport size intentionally:
  - Desktop landing videos: 1440x900 or 1728x1080.
  - Mobile videos: 390x844.
- If the app has theme support, choose the theme that best matches the landing page.

## 3. Write A Shot List

Use this structure:

```markdown
| Time | Shot | Action | Visible result |
|------|------|--------|----------------|
| 0-5s | Context | Open dashboard | User sees current workload |
| 5-15s | Input | Click New Request and fill fields | Request details are complete |
| 15-30s | Outcome | Submit / approve / schedule | Final status is visible |
```

Use exact selectors or visual targets when possible.

Before the full recording, pass the Motion quality gate in `SKILL.md`; the early styled test must demonstrate gradual scrolling as well as cursor and camera motion.

## 4. Record

Preferred execution pattern:

1. Start recording the current tab/window.
2. Wait one beat on the starting screen.
3. Execute the shot list with Browser, Playwright, Chrome, or Computer Use.
4. Pause on the final success state.
5. Stop recording.

If using macOS screen recording manually, use QuickTime or Screenshot recording and drive the browser with Codex. If using a CLI recorder, record only the browser region/window when possible.

## 5. Interaction Guidance

- Use seeded, realistic data.
- Move deliberately: wait 300-800 ms after important clicks.
- Avoid typing long paragraphs in real time unless typing itself is the feature.
- Prefer filters, tabs, selections, and submit actions with clear visual outcomes.
- If the app uses async data, wait for loaded states before recording the next action.
- If an action mutates seeded data, note whether the seed should be reset afterward.

## 6. Style the captured footage

Follow `cinematic-motion.md` for every new smooth demo, including basic and narrated walkthroughs. Record timed move/click/focus markers during capture, plan the timeline, then run `scripts/render-motion.py` for a preview and final export. Add timed explanatory `subtitles` cues in the dedicated below-app band by default. Confirm wallpaper margins, a moving eased cursor, zoom in/out, and readable captions outside the app before proceeding. Generate voiceover only on explicit request and disclose API key requirements and usage charges before calling OpenAI. If using another recorder, preserve equivalent timed target metadata; video pixels alone do not supply a cursor path. For narration, style each chapter first and assemble those styled clips; retime cursor/camera events along with footage if chapter timing changes.

## 7. Verification

Review the recording for:

- Correct route and account context.
- No private data.
- No accidental or unexplained empty states; intentional empty results are explained. No broken states.
- No dev overlays or console errors.
- Readable text at target video size.
- Final export includes the selected OS wallpaper at wide framing, a single smoothly moving cursor aligned with clicks, and eased zoom in/out.
- Cursor/actions are understandable.
- Final frame shows the promised outcome.

If verification fails, adjust the route, seed data, viewport, or action timing and retake.
