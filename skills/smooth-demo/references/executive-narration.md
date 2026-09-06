# Narrated executive demo workflow

For new `$smooth-demo` videos, narration extends the default cinematic workflow; it does not replace it. Read `cinematic-motion.md`, style real UI chapters through `scripts/render-motion.py`, then assemble the styled chapters with audio, cards, and captions. Preserve wallpaper, smooth cursor, zoom transitions, and 60 fps during final assembly. Retiming footage requires retiming its cursor/camera events too. A direct raw-frame-to-narration export is incomplete unless the user explicitly requested an unstyled video. Narration-only revisions of an existing video preserve its visuals.


Use this workflow for one polished, chaptered product video, or for revising the voice of an existing demo. A video request is not permission to mutate production records, expose private data, deploy changes, or send the result externally.

## Opt-in audio and default subtitles

Use OpenAI speech generation only when the user explicitly requests voiceover/audio narration. Otherwise produce a silent video with concise timed explanations below the app canvas using the motion renderer's `subtitles` cues. Keep that band outside the camera crop so it never covers controls, including while zoomed.

Before the first speech API call, explicitly disclose that OpenAI voiceover requires an API key and incurs API usage charges separate from ChatGPT/Codex subscription fees. An explicit voiceover request authorizes the requested generation scope; respect any budget constraint and do not repeatedly ask for approval already given. Default to Marin. Missing credentials or service availability must not trigger an unrequested paid or system-voice fallback.

## 1. Establish the deliverable

- Recover the audience, approved flows, duration, voice choice, footage, scripts, and brand assets from the current task and local artifacts. Ask only for missing choices that materially change the result.
- For a president or executive audience, organize around business outcomes: visibility, ownership, approvals, execution, and results. Do not enumerate every tutorial unless requested.
- Default to one 3–6 minute video: brief opening, readable table of contents, selected workflow chapters, and a concise closing. Follow explicit scope such as “E01 only.”
- Before each new flow, show a short chapter card with the chapter list and the upcoming chapter highlighted. Keep these transitions brief and readable; do not repeatedly narrate the entire contents.
- If the user requests only samples, an estimate, a script, or a diagram, produce only that deliverable. Do not start the full video or incur unrelated generation costs.
- If replacing narration, inspect and reuse existing usable footage. A voice change does not require recapturing the app.

Maintain a shot list with: chapter, business outcome, route/persona, exact visible action, expected result, narration, capture file, and verification status. Distinguish an action actually performed from inspection of a seeded before/after state. Never narrate an unperformed lifecycle as a demonstrated end-to-end flow.

## 2. Prepare safe capture

- Verify the app, environment, account, role, and all visible records before recording. A localhost URL does not prove the data is fictional: queues, dashboards, reports, and imported records can still reveal real clients or employees.
- Prefer the isolated training sandbox or an authorized seeded environment. Use fictional records and scoped aggregates. Do not alter production or seed/reset a database merely to make the shot attractive.
- For ordinary page walkthroughs, capture the page viewport. When visible browser tabs or overlapping windows are requested, follow `scenario-review.md` and include the necessary browser chrome and window arrangement. Verify a short crop test first, including menus or dialogs needed by the flow, to avoid capturing another display, credentials, notifications, or unrelated windows.
- Choose a consistent viewport, theme, zoom, and aspect ratio; preserve readable text. Do not stretch the UI to force a different aspect ratio. Use real brand assets for editorial title cards, not fabricated product screens.
- Prefer native 24/30 fps video capture for smooth motion. Exporting 6 fps footage at 30 fps duplicates frames; it does not improve captured motion. If only screenshot sequences are available, disclose the fallback, preserve timing, and do not describe it as smooth native video.
- Capture deliberate clicks, short pauses after visible results, and useful final states. Await actual loaded UI rather than relying exclusively on fixed delays. Retake mistakes, exposed information, and distracting loading failures.

## 3. Plan narration and voice selection

- Write concise narration against verified app behavior and visible evidence. Avoid unsupported claims about automation, security, immutable audit trails, conflict prevention, or deployment readiness.
- For new videos, generate narration before locking the final edit; footage can then accommodate natural speech. Keep capture actions and voice beats matched to the shot list.
- Default to OpenAI Marin (`voice: "marin"`) whenever voiceover is requested and no other voice is explicitly selected. Honor an explicit alternative. Do not ask for a voice choice or generate auditions by default. This default selects the voice; it does not add narration to a silent-video request.
- If Marin generation is unavailable because of credentials, tooling, or service errors, report that blocker and continue independent visual/script work. Do not silently substitute macOS `say`/Samantha, a Windows system voice, or another provider/voice.
- Only when the user requests voice comparisons, use the same short 10–20 second introduction, direction, and comparable loudness for the requested voices. Present playable samples and honor the resulting choice.
- When making OpenAI API calls or quoting current pricing/model/voice support, use the available OpenAI documentation skill and verify official documentation. Do not hardcode current prices or assume an older voice/model list remains valid.
- Give a cost estimate when requested or when required to resolve a material budget choice. Distinguish an estimate from actual billed usage. Do not impose repeated approval gates after the user has authorized generation within a clear scope.
- Read the key internally from the user-designated environment or ignored secret file. Never print it, put it in command-line arguments, use a public/client environment variable, copy it into this skill, or include it in artifacts. Redact API error output and never dump credential-bearing request headers.

## 4. Generate reusable chapter audio

- Generate one clip per chapter, using consistent voice and speaking direction. Keep narration text, model, voice, and nonsecret generation settings alongside the output.
- Cache each successful clip using a hash of its text, model, voice, and generation instructions/settings. Reuse unchanged audio; regenerate only changed or failed chapters. Check existing artifacts before any paid retry.
- Use bounded retries for transient failures within the authorized scope/budget. Stop and report persistent errors; do not run an uncontrolled paid retry loop.
- Preserve the natural delivery of the chosen sample. Do not apply a fixed slowdown to every voice or force new narration into obsolete chapter timings.
- Prefer adjusting meaningful UI holds and shot timing to fit speech. Use mild pitch-preserving retiming only when necessary and listen to the result. Avoid long frozen screens or rushed narration.

## 5. Assemble the final video

Use available local media tooling, such as FFmpeg, after checking installed capabilities. Reuse project-specific scripts only after inspecting their paths, secrets handling, timing assumptions, and output-overwrite behavior; do not blindly copy a previous project's hardcoded assembly script.

1. Arrange the verified footage in the requested page or browser-window layout, with clean editorial opening/chapter/closing cards.
2. Match each narration beat to the action or result being shown; keep the active chapter identifiable.
3. Normalize speech consistently and check peaks. If background music is requested, use authorized/licensed material and keep it below speech; otherwise omit it.
4. Build captions against the actual final narration, using alignment/transcription when available and correcting brand names, role names, and acronyms. Old captions do not become valid merely because replacement audio has similar duration.
5. Recalculate chapter timestamps from the final edit. Export a broadly playable MP4, a caption file, and readable chapter timestamps; embed chapters/captions when supported and useful.
6. Add an unobtrusive disclosure that narration is AI-generated to the delivery notes or closing card. Do not imply a human speaker recorded it.

Preserve source footage/audio and avoid overwriting an approved final without a recoverable copy. When a timeline changes, rebuild captions and chapter metadata rather than leaving stale timestamps.

## 6. Verify before delivery

Automated checks are necessary but do not substitute for watching and listening:

- Inspect codec, dimensions, frame rate, stream durations, and file integrity. Decode the output to catch corrupt frames or audio errors. Check actual audio/video endpoints, not only container duration, which subtitle or chapter metadata can inflate.
- Check resampling, normalization, trimming, and padding for clipped final words or missing chapter tails. Ensure captions and chapter boundaries fit the actual media endpoints.
- Watch opening, each transition, every demonstrated action/result, and closing. Listen to the narration at the same points, especially acronyms, names, seams, and the final sentence. Review caption timing against audible speech.
- Verify crop, readability, motion, cursor behavior, privacy, fictional data, claim accuracy, and absence of broken/loading/dev states. Confirm the file plays in an available player.
- State exactly what was checked. A waveform, screenshot, successful encode, or decode-only check is not evidence that the full video was watched or narration listened to. If playback tools are unavailable, report that gap and provide precise human-review steps.

Deliver the video, captions, chapter list, and script/shot list with local links or previews. Note any remaining limitations and ask for review of the concrete draft. Do not send to executives, upload publicly, or change the app unless separately authorized.
