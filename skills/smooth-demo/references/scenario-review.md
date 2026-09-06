# Scenario review

Use short 30–60 second clips to evaluate a new recording capability before a full demo. Define the promised outcome, target route, viewports, and pass/fail evidence first. Use the existing motion checklist; do not run this entire suite for an ordinary demo.

## Browser tabs

Prompt: “Show the event dashboard, open its public event page in another browser tab, scroll through it, then return to the dashboard.”

Distinguish browser tabs from tabs inside an app. For a multi-tab demo, show the browser tab strip and the switch between its tabs. Identify and verify each source tab by its observed URL and title. Recheck capture dimensions after selecting or opening each tab; viewport settings may not propagate to newly opened tabs. A tab-scoped recorder does not automatically follow the selected tab or include its chrome. Use browser-window capture for the visible-tab layout. Page-only clips with labeled cuts are a different composition and do not fulfill a request to show two browser tabs. Verify that returning to the original tab preserves its state; prevent stale-source frames and duplicate cursors at joins.

## Browser-window layouts

Select the layout by the story's purpose, preserving the user's choice. A demo may use different layouts in different chapters; do not force every layout into every demo.

| Layout | Use when | Example |
|---|---|---|
| 1. Two visible browser tabs | Moving between related pages while each uses the full window. | Organizer dashboard → public event page → dashboard. |
| 2. Partially overlapping windows | Showing the relationship between two views while keeping some of both visible. | Organizer setting → attendee preview; desktop and mobile together. |
| 3. Almost fully overlapping windows | Switching between views at consistent size and position so differences are easy to notice. | Before/after redesign; two user roles; two versions of the same page. |

### 1. Two visible browser tabs

Use one browser window with two distinct, readable tabs above the address bar. Keep both tab labels and the active-tab indication visible during switching. Move the pointer to the actual tab before clicking and hold the destination page once settled. Return wide before the switch; zooms must not hide the tab strip at the moment it explains the navigation. This is the usual layout for a multi-page walkthrough.

### 2. Partially overlapping windows

Use two separate browser windows, offset diagonally, with enough of the back window exposed to recognize its context. As a starting point, cover roughly one third to one half of the back window. Retain distinct window borders, chrome, and shadows. Show focus changing by bringing the selected window forward, with pointer movement aligned to the real focus action. Keep the control or result being discussed unobscured. For desktop/mobile, preserve each viewport's aspect ratio and label mobile emulation accurately. If both views must be read simultaneously, prefer side-by-side placement over overlap.

### 3. Almost fully overlapping windows

Use two similarly sized windows with a small diagonal offset: roughly 90% overlap, leaving the rear title/tab bar and a narrow side edge visible. Keep both windows recognizable as separate windows. Switch which window is in front while preserving scale, viewport, and framing. For before/after comparisons, match the route, content, and scroll position so the intended change is easy to see. Avoid adding camera motion during the focus switch. Hold each view long enough to compare it.

### Capture and review requirements

- Prefer actual browser-window or desktop-region capture for these layouts. Capture the tab strip, window edges, and focus changes required by the story; the general preference to hide distracting chrome does not apply to chrome that explains this interaction.
- If compositing is explicitly requested, use real UI footage, preserve the requested window arrangement, and disclose that the window motion is composed. Do not imply that synthetic chrome or cuts are captured browser interactions. If the available recorder cannot capture the requested arrangement, report that limitation rather than silently substituting page-only footage.
- Before a full take, review a short styled preview that includes the requested tab switch or focus change. Confirm which window is active, legible tab labels, correct stacking/occlusion, cursor alignment, and steady framing. Recheck these features in the final export.
- For Raceonic-style stories, use visible tabs for the main walkthrough, partial overlap for organizer-to-attendee demonstrations, and near-complete overlap for before/after comparisons. These examples guide selection; they do not restrict the layouts to this app.

## Desktop and mobile

Prompt: “Show the same public event page at 1440×900 and 390×844, with navigation and gradual scrolling in each, in one video with labeled sections.”

Capture separate takes at each size; preflight actual frame dimensions again after resizing. Wait for a settled screenshot as well as layout metrics: the first screenshot after resize may still contain the old layout. Keep viewport overrides temporary and reset afterward. Preserve aspect ratio when composing differently sized sources; never stretch a portrait capture to fill a landscape canvas. Re-measure pointer targets and adapt zoom and caption wrapping to the output size. Label browser viewport emulation accurately; do not imply physical-device or touch verification. Treat a landscape comparison and a dedicated 9:16 export as separate deliverables. For comparisons, use matching content and section positions.

## Additional prompts

| Scenario | Prompt | Evidence |
|---|---|---|
| Forms | In a sandbox, submit an incomplete registration, show validation, correct it, and stop before payment. | Readable errors, paced typing, hidden secrets, visible final state. |
| Nested scrolling | Open a menu, inspect a scrollable modal, close it, then scroll the page. | Correct scroll container, no clipped overlay, measured click targets. |
| Filters | Search demo registrations, apply a filter, show an empty result, and clear it. | Settled results and an explained empty state. |
| Roles | In a sandbox, create a draft as an organizer and show its attendee preview in a separate session. | Separate authentication contexts, labeled roles, verified outcome. |
| Recovery | Record three chapters, interrupt after chapter two, resume, and deliver one video. | No missing or duplicate action, consistent framing, recovered status verified. |
| Revision | Replace captions on an existing demo while preserving its footage and motion. | Visual timing preserved; captions synchronized and outside the app. |

## Review record

Save the exact prompt, environment, source tabs/viewports, shot list, and output paths. Record pass/fail/blocked for each promised behavior, with timestamps or observed evidence and any retakes. Review source movement separately from the styled export to isolate capture versus composition defects. Watch each scroll and transition at normal speed; then check delivered-file playback, seeking, dimensions, captions, and full decoding. Repeat the same prompt and capture conditions after a related skill change. Distinguish a tool limitation or product defect from a skill failure, and report untested scenarios explicitly.
