# Narrated executive demo workflow

For new smooth-demo videos, narration extends the default cinematic workflow; it does not replace it. Read `cinematic-motion.md`, style real UI chapters through `scripts/render-motion.py`, then assemble the styled chapters with audio, cards, and captions. Preserve wallpaper, smooth cursor, zoom transitions, and 60 fps during final assembly. Retiming footage requires retiming its cursor/camera events too. A direct raw-frame-to-narration export is incomplete unless the user explicitly requested an unstyled video. Narration-only revisions of an existing video preserve its visuals.


Use this workflow for one polished, chaptered product video, or for revising the voice of an existing demo. A video request is not permission to mutate production records, expose private data, deploy changes, or send the result externally.

## Opt-in audio and default subtitles

Generate speech only when the user explicitly requests voiceover/audio narration, and only with the free local Kokoro model described below. Otherwise produce a silent video with concise timed explanations below the app canvas using the motion renderer's `subtitles` cues. Keep that band outside the camera crop so it never covers controls, including while zoomed.

Kokoro runs on-device and needs no API key, so there is no cost disclosure. Disclose only the one-time download (about 1.4 GB) before installing it. An explicit voiceover request authorizes generating the requested clips. Missing tooling or unsupported hardware must not trigger an unrequested paid, cloud, or system-voice fallback. This skill has no paid-TTS option: never call the OpenAI speech API or any other paid or cloud TTS service.

### Kokoro setup (once per machine, Apple Silicon only)

The model is `mlx-community/Kokoro-82M-bf16` on Hugging Face (Apache-2.0, 82M parameters, 327 MB file), run through the `mlx-audio` library. First check whether `~/.local/share/uv/tools/mlx-audio/bin/python` exists. If not, ask before downloading, then run `scripts/setup-kokoro.sh` (about 1.1 GB tool environment plus a 341 MB model; needs `uv`; uv also caches wheels, which `uv cache clean` reclaims).

Do not use the mlx-audio README's `--prerelease=allow` install: it pulls a pre-release spaCy/thinc that crashes with "numpy.dtype size changed". The setup script installs `misaki[en]` with stable `spacy<4`, `thinc<9`, and the `en-core-web-sm` wheel, because the uv tool environment has no pip for misaki to fetch the spaCy model at run time. Run this skill's Python scripts with the tool's interpreter (`~/.local/share/uv/tools/mlx-audio/bin/python`), which has numpy and scipy; the system Python usually does not.

mlx-audio requires an Apple Silicon Mac. On Windows, Linux, or Intel Macs the same Kokoro weights can run through `kokoro-onnx` or `hexgrad/kokoro` on CPU; that route is not wired into this skill, so say so and offer subtitles instead of improvising.

## 1. Establish the deliverable

- Recover the audience, approved flows, duration, voice choice, footage, scripts, and brand assets from the current task and local artifacts. Ask only for missing choices that materially change the result.
- For a president or executive audience, organize around business outcomes: visibility, ownership, approvals, execution, and results. Do not enumerate every tutorial unless requested.
- Default to one 3–6 minute video: brief opening, readable table of contents, selected workflow chapters, and a concise closing. Follow explicit scope such as “E01 only.”
- Before each new flow, show a short chapter card with the chapter list and the upcoming chapter highlighted. Keep these transitions brief and readable; do not repeatedly narrate the entire contents.
- If the user requests only samples, an estimate, a script, or a diagram, produce only that deliverable. Do not start the full video or generate unrelated audio.
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
- Default to Kokoro `af_heart` (American English, graded A on the model card) whenever voiceover is requested and no other voice is explicitly selected. Other solid choices are `af_bella` (A-) and British `bf_emma` (B-, `--lang b`). The male voices (`am_michael`, `am_fenrir`, `am_puck`) grade lower (C+). Honor an explicit alternative. Do not ask for a voice choice or generate auditions by default. This default selects the voice; it does not add narration to a silent-video request.
- If Kokoro is unavailable (not installed, model not cached, unsupported hardware), report that blocker and continue independent visual/script work. Do not silently substitute macOS `say`/Samantha, a Windows system voice, or any paid or cloud provider.
- Only when the user requests voice comparisons, use the same short 10–20 second introduction and comparable loudness for the requested voices (run `scripts/kokoro-narrate.py` once per voice). Present playable samples and honor the resulting choice.
- Take voice names, grades, and license from the Hugging Face model card (`hexgrad/Kokoro-82M`, VOICES.md) and the mlx-audio README. Do not assume an older voice list is still current.
- Pronunciation: pass a `--respell` JSON for code words, acronyms, and codes (`API` becomes `ay pee eye`, because a plain "A P I" can be read as the article "uh"; `401` becomes `four oh one`). camelCase identifiers are split into words automatically. `narration.json` records the spoken text of each clip; listen to the first clip that contains each respelling.

## 4. Generate reusable chapter audio

- Write the narration as a JSON list of `{id, text}` and generate it with `scripts/kokoro-narrate.py script.json --out narration/` using the tool interpreter. Use one clip per chapter (or per caption cue when the captions are the script), with one voice and speed throughout. The script writes `<id>.wav` (24 kHz mono, silence trimmed) and `narration.json` with the text, spoken text, model, voice, speed, and duration.
- Clips are cached by a hash of the spoken text, model, voice, speed, and language. Rerunning regenerates only changed clips, so editing one line leaves every other clip identical.
- Generation is local, so there is no retry budget. If a clip fails, shorten very long segments or remove unusual symbols and rerun.
- Preserve the natural delivery. Kokoro's pace varies by sentence (roughly 12–19 characters per second); do not apply a fixed slowdown or force new narration into obsolete chapter timings.
- Prefer adjusting meaningful UI holds and shot timing to fit speech: set each chapter or caption duration to the larger of its minimum animation time and the clip length plus about 0.45 s, place each clip at its start, rebuild the timeline from those durations, and re-render. Use mild pitch-preserving retiming only when necessary and listen to the result. Avoid long frozen screens or rushed narration.

## 5. Assemble the final video

Use available local media tooling, such as FFmpeg, after checking installed capabilities. Reuse project-specific scripts only after inspecting their paths, secrets handling, timing assumptions, and output-overwrite behavior; do not blindly copy a previous project's hardcoded assembly script.

1. Arrange the verified footage in the requested page or browser-window layout, with clean editorial opening/chapter/closing cards.
2. Match each narration beat to the action or result being shown; keep the active chapter identifiable.
3. Normalize speech consistently and check peaks. Raw Kokoro is quiet (about -26 LUFS) and plain gain clips; this chain gave -17 LUFS with a -4 dBFS peak: `acompressor=threshold=-28dB:ratio=2.5:attack=8:release=120:makeup=3,loudnorm=I=-17:TP=-1.5:LRA=7`, then 48 kHz stereo AAC. If background music is requested, use authorized/licensed material and keep it below speech; otherwise omit it.
4. Build captions against the actual final narration, using alignment/transcription when available and correcting brand names, role names, and acronyms. Old captions do not become valid merely because replacement audio has similar duration.
5. Recalculate chapter timestamps from the final edit. Export a broadly playable MP4, a caption file, and readable chapter timestamps; embed chapters/captions when supported and useful.
6. Add an unobtrusive disclosure that narration is AI-generated to the delivery notes or closing card. Do not imply a human speaker recorded it.

Preserve source footage/audio and avoid overwriting an approved final without a recoverable copy. When a timeline changes, rebuild captions and chapter metadata rather than leaving stale timestamps.

## 6. Verify before delivery

Automated checks are necessary but do not substitute for watching and listening:

- Inspect codec, dimensions, frame rate, stream durations, and file integrity. Decode the output to catch corrupt frames or audio errors. Check actual audio/video endpoints, not only container duration, which subtitle or chapter metadata can inflate.
- Check resampling, normalization, trimming, and padding for clipped final words or missing chapter tails. Ensure captions and chapter boundaries fit the actual media endpoints.
- Watch opening, each transition, every demonstrated action/result, and closing. Listen to the narration at the same points, especially acronyms, names, seams, and the final sentence. Review caption timing against audible speech.
- No speech-to-text tool is installed by default. If you did not listen to the narration, say so and list the respelled words and numbers for the user to check by ear.
- Verify crop, readability, motion, cursor behavior, privacy, fictional data, claim accuracy, and absence of broken/loading/dev states. Confirm the file plays in an available player.
- State exactly what was checked. A waveform, screenshot, successful encode, or decode-only check is not evidence that the full video was watched or narration listened to. If playback tools are unavailable, report that gap and provide precise human-review steps.

Deliver the video, captions, chapter list, and script/shot list with local links or previews. Note any remaining limitations and ask for review of the concrete draft. Do not send to executives, upload publicly, or change the app unless separately authorized.
