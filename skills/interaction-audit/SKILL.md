---
name: interaction-audit
description: Walk through a whole app and exercise every interaction it offers, one by one, with screenshot proof and a checklist file. Inventories every screen, control and gesture from the code and the running app, drives each one with the right tool for the platform (iOS Simulator or real iPhone, Android emulator, web, browser extension, desktop app on macOS or Windows), and records every crash, dead control, broken animation or wrong text with repro steps. Use this whenever the user wants to "go through the whole app", "tap everything", "test every button/interaction", do a full UI walkthrough or interaction audit, smoke test or exploratory pass before a release, check that nothing is broken after a big change, or says "/interaction-audit" with a platform such as mobile, ios, android, web, extension or desktop — even if they don't say "test".
---

# Interaction audit

The goal is **coverage**, not a quick bug hunt: by the end, every interaction the app offers on the chosen platform has been exercised at least once, and there is proof. A short list of bugs is a by-product. If something could not be exercised, the checklist says so and why — an honest "not reached" beats a silent gap.

Argument: the platform or area to cover (`mobile`, `ios`, `android`, `web`, `extension`, `desktop`, or a screen/feature name). If missing, infer it from the project and the user's words; ask only when two platforms are equally plausible.

## Modes

- **Full** (default): the whole app on the chosen platform.
- **Changed** (`changed`, "only what this PR touches", after a branch or diff): derive the affected screens from `git diff <base>...HEAD` (UI files, routes, strings, shared components and everything that uses them), audit those fully and smoke-check the main flow of every other screen. Say in the report which screens were out of scope.
- **Release** (`release`, "before submitting to the store"): full mode plus the store and legal checks in [references/store-and-legal.md](references/store-and-legal.md) and the oldest supported OS/browser versions.
- **Scope is a contract.** Whatever the user chose (platform, build, "browser version only", "everything incl. right click") is what you audit and what you report on. Don't pad the result with other areas; list out-of-scope things you noticed in one short section at the end.
- **Resume**: if a `checklist.md` from an earlier run exists for the same platform and build, continue from its first open item instead of starting over; re-run items marked `problem` when the build changed.

## Ground rules

- **Safe by default.** Never perform destructive or outward-facing actions without asking first in chat: purchases or subscriptions, sending real messages/emails/posts, deleting real user data, unpairing or signing out of real accounts, resetting settings, granting system permissions on the user's own device, changing account settings. Open the confirmation dialog, screenshot it, then **cancel** and mark the item `asked` or `skipped (destructive)`. Prefer test data and simulators; create throwaway test content yourself and delete only what you created.
- **Real behaviour over code.** The code tells you *what exists*; only the running app tells you *whether it works*. Never mark an item done from reading code.
- **One thing at a time per instance.** Stateful UI (focus, sheets, text fields, navigation stack) gets polluted by parallel actions. Within one app instance, drive serially and return to a known state after each item. For large apps (hundreds of controls), split the work by area across subagents only if each one gets its **own** instance — its own browser tab, simulator or emulator — and its own test data, with nothing shared that one could change under another (same account, same local database). Give each agent the checklist section, the design profile and the findings template; the main session merges the results and **re-checks every finding itself** before reporting it.
- **Don't take over the user's machine.** Computer-use moves the real mouse and keyboard. If the user may be working on the same computer, ask before driving native windows with it; offer the browser or web-view build, a simulator, or a VM instead, and collect what truly needs the native app as a user-driven list.
- **Write as you go.** Update the checklist and findings after every item, not at the end — a long run may be interrupted or summarized.

## Workflow

### 1. Prepare

1. Read the project's own instructions and any `run`/launch skill or `.claude/launch.json` to learn how to build and start the app. Note any **UX rules** they state (e.g. "disabled controls always get a tooltip with the reason", "paid features are shown disabled, never hidden", "destructive actions ask first") — they are part of the rubric, and breaking them is a finding.
2. **Agree on scope before starting**, in one short round of questions if the request doesn't already answer them:
   - What to audit: whole app, an area, or what a branch/PR changed — and which interaction kinds (e.g. "everything including right-click menus").
   - Which build: `main`, a branch, or several unmerged fixes together. To test unmerged work together, merge it into a **local test branch** (e.g. `test/audit-<date>`), never push it, and delete it at the end; resolve conflicts there, not on the real branches.
   - How to drive it: native app, browser/web-view build, simulator, real device — and whether you may take over mouse and keyboard (see ground rules).
   - Which test data: seed/fixture data, a mocked backend, debug parameters for plans and states.
3. **Check what this environment can actually run** before planning anything. The same request means different things on a Mac, on Windows, in a cloud sandbox:
   - Host OS (`uname -s` / `$env:OS`) and what is installed: `xcrun simctl list devices` and `xcrun devicectl list devices` (iOS, macOS only), `adb devices` and `emulator -list-avds` (Android), the project's dev command.
   - Which driving tools this session has (loaded or deferred): iOS Simulator tool, built-in browser, Claude in Chrome, computer-use, `agent-device`, Playwright/Maestro in the project.
   - What the project targets and pins: deployment target, a simulator or device named in its instructions, launch configs, memory notes.
   - The oldest and newest OS / browser versions the app supports, and which of them are installed here (see the version table in [references/environments.md](references/environments.md)).
   Write a short capability table at the top of `checklist.md` (platform → device/simulator → driving tool → available yes/no). [references/environments.md](references/environments.md) has the matrix of which target runs on which host (iOS only on macOS, Windows apps only on Windows, Android emulators need virtualisation, …). If the requested platform cannot run here, do not improvise: say so, offer the fallbacks listed there, and let the user choose. Platforms that *can* run here (e.g. the web part of the same app) may proceed meanwhile.
4. Pick the platform reference and read it now:
   - iOS (Simulator or real iPhone): [references/ios.md](references/ios.md)
   - Android: [references/android.md](references/android.md)
   - Web app or browser extension: [references/web-and-extension.md](references/web-and-extension.md)
   - Desktop app (Tauri, Electron, native; macOS or Windows): [references/desktop.md](references/desktop.md)
5. Create the run folder outside the product repositories (scratchpad or a private notes folder): `interaction-audit-<platform>-<YYYY-MM-DD>/` with `checklist.md`, `findings.md` and `screenshots/`. Copy the templates from [references/checklist-template.md](references/checklist-template.md).
6. Build and launch the app; take a baseline screenshot.
7. **Find the design language** and write the design profile (system language such as HIG/Liquid Glass, Material 3 or Fluent; the app's own tokens for spacing, radii, type, colour, materials, icons and motion; which design skill was used to build it). Load the matching design skill as the rubric if one is available. See [references/design-language.md](references/design-language.md). Without a profile, spacing and animation findings are just taste.

### 2. Inventory — from code *and* from the running app

Build the full list before driving anything. Do both passes, because each misses things the other sees:

- **Code pass.** Grep the UI layer for every entry point: screens/routes/views, buttons and tappable views, menus and context menus, gestures (tap, long press/hold, swipe actions, drag and drop, pinch, pull to refresh), sheets/popovers/alerts/toasts, text fields and pickers, toggles in settings, keyboard shortcuts and menu-bar items, deep links/URL schemes, notifications, entry points outside the app's UI (Shortcuts / App Intents, Siri, widgets, controls and tiles, share extensions, quick actions, jump lists — see [references/system-entry-points.md](references/system-entry-points.md)), permission requests, onboarding/first-run flows, empty/loading/error states, feature flags. Platform references list the patterns to search for.
- **App pass.** Visit every reachable screen and list what you actually see (accessibility tree or `read_page` where available, screenshots otherwise). Add anything the code pass missed and note code entries you could not find on screen.
- **Catalog pass.** Go through [references/interaction-catalog.md](references/interaction-catalog.md) section by section (gestures, mouse and pointer incl. double/triple/middle/modifier clicks, keyboard, text editing, language and region, lifecycle and updates, network and multi-device sync, performance, system integration and hardware, privacy, robustness) and add every entry that applies to a control or screen you found. This is what turns "I tapped every button" into real coverage.

Then add the **cross-cutting variations** that apply to the platform: light/dark mode, the system accessibility features (screen reader, large text, bold text, increase contrast, reduce motion, reduce transparency, voice and switch control, full keyboard access — see [references/accessibility.md](references/accessibility.md); each one the platform offers is a checklist item, not an optional extra), screen sizes and form factors (smallest, typical and largest supported size, tablet, foldable, split view, desktop window sizes and display scaling — see [references/screen-sizes.md](references/screen-sizes.md)), rotation, offline / server or peer unreachable, empty state (fresh install, no data), lots of data (long lists, long text), interrupted flows (background the app, cancel half way), keyboard-only navigation, localisation if the app ships more than one language.

Also list the **states the app can be in** — plans and licences (free, trial, paid, expired, offline licence), account states, roles, feature flags and remote config — as a state matrix, and plan which screens to revisit in which state: [references/states-and-flags.md](references/states-and-flags.md). Use test accounts, sandbox purchases and local overrides only.

Group the checklist by screen. Each item is one interaction with its expected result. Expect dozens to hundreds of items for a real app — that is the point.

**Order by risk**, so an interrupted run has still covered what matters most: first the core flows (the reason the app exists), then anything touching money (purchases, licences, paywalls), then anything that can lose or leak data (delete, sync, sign-out, export, permissions), then the rest of the screens, then the cross-cutting variations and states. Mark each item's priority (`P1`–`P3`) in the checklist and work top-down.

### 3. Exercise — item by item

For every checklist item:

1. Bring the app to the item's starting state.
2. Perform the interaction with the platform's tool.
3. Screenshot the result (and the intermediate state for animations or multi-step flows) into `screenshots/` with a name matching the item ID, e.g. `S03-07-long-press-menu.png`. For animations, transitions, jank or anything timing-related, record a short video instead (`xcrun simctl io booted recordVideo`, `adb shell screenrecord`, the browser's or OS's screen recording, `agent-device record`), because a still frame can't prove an animation is broken.
4. Compare with the expected result: right screen, right text, animation completes, no freeze, no console/log errors, state persists after leaving and returning. Then run the visual check from [references/visual-check.md](references/visual-check.md) on the screenshot: clipped or cut-off text, broken, stretched or blurry images, containers cut off or overlapping, content under the notch, keyboard or system bars. Zoom into edges instead of judging the whole screen at a glance. Compare spacing, type, colours, shapes, icons and motion against the design profile.
5. Mark the item: `ok`, `problem` (link the finding), `blocked` (say what blocks it), `skipped (destructive)`, `asked`, or `not reachable`.

After a crash or hang, collect the evidence before relaunching: the crash report (Simulator/macOS: `~/Library/Logs/DiagnosticReports/`; device: Xcode Organizer or `devicectl`; Android: `adb logcat -b crash`; Windows: Event Viewer → Application; web: console and network), plus the log lines around the timestamp.

When something is wrong, write the finding immediately in `findings.md` (template in the checklist reference) with severity, exact repro steps from a known start state, expected vs actual, screenshot paths and relevant log lines. Then continue — don't stop to fix unless the user asked you to; a blocker that hides the rest of the app is the exception (report it and ask).

Watch for these problem classes in particular: crash or hang, dead control (nothing happens), wrong or untranslated text, truncated text, broken or distorted images, clipped or overlapping containers, content under system UI, broken or janky animation, state lost after navigation, missing feedback (no spinner, no confirmation), inconsistent behaviour between similar controls, deviations from the design profile (spacing off the scale, wrong type style, hard-coded colours, foreign icons, non-native or inconsistent animations), accessibility gaps (unlabeled buttons, too small targets, unreadable in dark mode or large text).

### 4. Report

The result for the user is **always tables, in this fixed order, with no prose between them** — at most one short line under a heading. Write in the user's language and in plain words they recognise from the app, not in the shorthand you or the subagents used while working; never compress findings further on the way to the user. Translate the column names. Each cell stays short (a few words up to one sentence); details live in `findings.md` and the HTML report.

1. **Overview** — one line: items checked · A fix · B decide · C leave · not checked.
2. **A – Fix** (clear bugs and rule violations), sorted by priority:

   | No. | Prio | Area | You do | Happens | Expected | Why it matters | Proposed fix | Proof |
   |---|---|---|---|---|---|---|---|---|
   | A1 | P1 | Library | Ctrl-click a second clip | only the second stays selected | both selected, like Explorer | multi-delete/move needs the tiny checkboxes | keep selection on Ctrl-click | [S04-07](screenshots/S04-07.png) |

3. **B – Decide** (may be intended or needs a product decision): same columns, but **Options** instead of *Proposed fix* (e.g. "a) confirm dialog · b) undo toast · c) leave").
4. **C – Leave** (cosmetic or arguably intended), short: `No. | Area | What | Why leave it`.
5. **Not checked** — what was out of reach and how the user can check it: `No. | What | Why not here | How you check it yourself` (global shortcuts, pasting into other apps, tray, device-only features). Test-setup-only issues (mock data, test branch) go here too, marked as such, so they aren't mistaken for app bugs.
6. **One question** to close: which option for each B, and whether A and C are fine (the user can answer with numbers, e.g. "A all, B1 a, B2 c").

"You do" names concrete steps from a start state the user recognises; "Happens" and "Expected" are observable, not technical causes. Priority: P1 core flow, money or data · P2 other screens · P3 variations and polish. "Proof" links the screenshot or video file (relative to the run folder) so the user can open it.

Then also deliver, below the tables:

- The clickable report: `python3 <skill-dir>/scripts/build_report.py <run-dir>` writes `report.html` (filter by status, search, screenshots and videos per item, findings linked). With `--previous <earlier-run-dir>` it compares every screenshot with the same file from that run and marks it unchanged, changed or new, with side-by-side and blink comparison (pixel ratio and diff image if Pillow is installed). For stable comparisons, keep device, size and data the same and freeze the status bar (`xcrun simctl status_bar booted override --time 9:41 --batteryLevel 100`, Android demo mode). Open the report or send it with a file tool.
- Paths to `checklist.md`, `findings.md` and the screenshots folder; send the most telling screenshots with a file tool if one is available.

If the project tracks tests or issues somewhere (a status page, an issue tracker), follow its rules for where findings go — but ask before filing anything publicly.

Offer, don't do unasked: fixing the design findings with the profile's tokens and the rubric skill (before/after screenshots as proof); turning the checklist's most important flows into automated UI tests in the framework the project already uses (XCUITest, Espresso/Compose tests, Maestro, Playwright), so the next audit only needs to cover what automation can't.

## Optional helper: agent-device

If `agent-device` (Callstack, npm) is already installed, it can replace coordinate tapping on iOS, Android, macOS and web: `snapshot -i` lists every interactive element with stable refs, `press`/`fill`/`scroll` act on them, and `record start/stop` captures videos. It also drives taps on a **real iPhone**, which most other tools cannot. Do not install it without asking the user; everything in this skill works without it.
