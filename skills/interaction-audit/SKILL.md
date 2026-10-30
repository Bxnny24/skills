---
name: interaction-audit
description: Walk through a whole app and exercise every interaction it offers, one by one, with screenshot proof and a checklist file. Inventories every screen, control and gesture from the code and the running app, drives each one with the right tool for the platform (iOS Simulator or real iPhone, Android emulator, web, browser extension, desktop app on macOS or Windows), and records every crash, dead control, broken animation or wrong text with repro steps. Use this whenever the user wants to "go through the whole app", "tap everything", "test every button/interaction", do a full UI walkthrough or interaction audit, smoke test or exploratory pass before a release, check that nothing is broken after a big change, or says "/interaction-audit" with a platform such as mobile, ios, android, web, extension or desktop — even if they don't say "test".
---

# Interaction audit

The goal is **coverage**, not a quick bug hunt: by the end, every interaction the app offers on the chosen platform has been exercised at least once, and there is proof. A short list of bugs is a by-product. If something could not be exercised, the checklist says so and why — an honest "not reached" beats a silent gap.

Argument: the platform or area to cover (`mobile`, `ios`, `android`, `web`, `extension`, `desktop`, or a screen/feature name). If missing, infer it from the project and the user's words; put it in the upfront questions only when two platforms are equally plausible.

## Modes

- **Full** (default): the whole app on the chosen platform.
- **Changed** (`changed`, "only what this PR touches", after a branch or diff): derive the affected screens from `git diff <base>...HEAD` (UI files, routes, strings, shared components and everything that uses them), audit those fully and smoke-check the main flow of every other screen. Say in the report which screens were out of scope.
- **Release** (`release`, "before submitting to the store"): full mode plus the store and legal checks in [references/store-and-legal.md](references/store-and-legal.md) and the oldest supported OS/browser versions.
- **Scope is a contract.** Whatever the user chose (platform, build, "browser version only", "everything incl. right click") is what you audit and what you report on. Don't pad the result with other areas; list out-of-scope things you noticed in one short section at the end.
- **Resume**: if a `checklist.md` from an earlier run exists for the same platform and build, continue from its first open item instead of starting over; re-run items marked `problem` when the build changed.

## Ground rules

- **Ask everything once, up front.** Every question, approval and choice the user has to make goes into a single round at the start (Prepare, step 4). After they answer, run to the end without interrupting them: no follow-up questions, no "may I?", no waiting. Whatever comes up later that the answers don't cover, decide on the safe side yourself (cancel, skip, use the fallback), mark the item `not approved` with what approval would unlock it, and keep going; those items land in *Not checked*, so the user can approve them all at once afterwards and you re-run only those. The closing question of the report is the only other question.
- **Safe by default.** Never perform destructive or outward-facing actions the user didn't approve in the upfront round: purchases or subscriptions, sending real messages/emails/posts, deleting real user data, unpairing or signing out of real accounts, resetting settings, granting system permissions on the user's own device, changing account settings. Open the confirmation dialog, screenshot it, then **cancel** and mark the item `not approved` or `skipped (destructive)`. Prefer test data and simulators; create throwaway test content yourself and delete only what you created.
- **Real behaviour over code.** The code tells you *what exists*; only the running app tells you *whether it works*. Never mark an item done from reading code.
- **One thing at a time per instance.** Stateful UI (focus, sheets, text fields, navigation stack) gets polluted by parallel actions. Within one app instance, drive serially and return to a known state after each item. For large apps (hundreds of controls), split the work by area across subagents only if each one gets its **own** instance — its own browser tab, simulator or emulator — and its own test data, with nothing shared that one could change under another (same account, same local database). Give each agent the checklist section, the design profile and the findings template; the main session merges the results and **re-checks every finding itself** before reporting it.
- **Don't take over the user's machine.** Computer-use moves the real mouse and keyboard. If the user may be working on the same computer, settle in the upfront round whether you may drive native windows with it and when (e.g. "now, I'm away" or "only the browser build"); offer the browser or web-view build, a simulator, or a VM instead, and collect what truly needs the native app as a user-driven list. Steps only the user can do (switching settings on their own phone, plugging in a device, approving a system dialog) are agreed up front and done as one block — at the start if later items depend on them, otherwise at the end — never one by one in between.
- **Write as you go.** Update the checklist and findings after every item, not at the end — a long run may be interrupted or summarized.

## Workflow

### 1. Prepare

Steps 1–3 are silent groundwork so that step 4 can ask everything at once, with concrete choices instead of vague ones. Don't ask anything before step 4.

1. Read the project's own instructions and any `run`/launch skill or `.claude/launch.json` to learn how to build and start the app. Note any **UX rules** they state (e.g. "disabled controls always get a tooltip with the reason", "paid features are shown disabled, never hidden", "destructive actions ask first") — they are part of the rubric, and breaking them is a finding.
2. **Check what this environment can actually run** before planning anything. The same request means different things on a Mac, on Windows, in a cloud sandbox:
   - Host OS (`uname -s` / `$env:OS`) and what is installed: `xcrun simctl list devices` and `xcrun devicectl list devices` (iOS, macOS only), `adb devices` and `emulator -list-avds` (Android), the project's dev command.
   - Which driving tools this session has (loaded or deferred): iOS Simulator tool, built-in browser, Claude in Chrome, computer-use, `agent-device`, Playwright/Maestro in the project. Pick per job, not one for everything: built-in browser for dev servers and the web view, Claude in Chrome for extensions and real Chrome, computer-use for native windows ([references/environments.md](references/environments.md#which-browser-tool)). Note what is missing but would help, for the *Helpers* question.
   - What the project targets and pins: deployment target, a simulator or device named in its instructions, launch configs, memory notes.
   - The oldest and newest OS / browser versions the app supports, and which of them are installed here (see the version table in [references/environments.md](references/environments.md)).
   - **Device access up front.** Some driving tools ask the user once per device or simulator (the iOS Simulator tool does). Request access to every device the size and version passes will need (e.g. the oldest-iOS simulator, the iPad) now, while the user is still at the keyboard; a prompt that comes up later while they are away leaves that whole pass `blocked`.
   Write a short capability table at the top of `checklist.md` (platform → device/simulator → driving tool → available yes/no). [references/environments.md](references/environments.md) has the matrix of which target runs on which host (iOS only on macOS, Windows apps only on Windows, Android emulators need virtualisation, …). If the requested platform cannot run here, do not improvise: put the fallbacks listed there into the upfront questions and let the user choose.
3. **Scan for what will need a decision.** A quick grep of the code (routes, menus, purchase and delete calls, settings the app reads) is enough here; the full inventory comes later. Note every place that would otherwise make you stop mid-run:
   - destructive or outward-facing actions: purchases and subscriptions, delete/reset/sign-out/unpair, sending messages, emails or posts, forms that submit data, uploads, account changes;
   - system-wide changes: dark mode, accessibility features, display scaling, language/region, permissions on the user's own device;
   - downloads and installs: OS runtimes, simulators, browsers, `agent-device`, Pillow;
   - anything bound to accounts or money: cloud devices, BrowserStack, sandbox purchases, production access;
   - steps only the user can do: their real phone, a second device, a hardware key, a system dialog that needs their password;
   - where findings may go: the project's issue tracker or status page.
4. **Ask everything in one round** (one message, or one question tool call with several questions), with your recommendation first in each, and skip whatever the request already answers:
   - **Scope:** whole app, an area, or what a branch/PR changed — and which interaction kinds (e.g. "everything including right-click menus").
   - **Build:** `main`, a branch, or several unmerged fixes together. To test unmerged work together, merge it into a **local test branch** (e.g. `test/audit-<date>`), never push it, and delete it at the end; resolve conflicts there, not on the real branches.
   - **Driving:** native app, browser/web-view build, simulator, real device; whether and when you may take over mouse and keyboard; which fallback if the platform can't run here.
   - **Browsers** (web apps, extensions, web views): which ones and how deep. Offer what the project supports (`browserslist`, the stores in the extension manifest) and what is installed and connected here. Recommend a full pass in one Chromium browser, a short main-flow pass in the other Chromium browsers (Edge, Brave, Opera, Arc), and a full pass in Firefox and Safari when the app supports them, since those use other engines ([references/environments.md](references/environments.md#several-browsers)).
   - **Test data and states:** seed/fixture data, a mocked backend, debug parameters for plans, roles and flags.
   - **Approvals,** as one list built from step 3, each with a default the user can accept with one word: e.g. "delete/reset only on test data I created: yes", "sandbox purchases: open the sheet, then cancel", "switch macOS to dark mode and back: yes", "download the iOS 17 runtime (≈ 7 GB): no", "file findings in the tracker: no, report only". What isn't approved is skipped and reported, never asked again mid-run.
   - **User-driven steps:** what you need from them, and whether they do it now or as one block at the end.
   - **Result:** **1** `report.html` in the browser (recommended), **2** `summary.md` as a file card in the chat, or **3** tables in the chat with the proof images as separate cards (see *Deliver*); and whether they'll read it at this computer or remotely (remote: may the report be published as a private artifact?).
   - **Helpers:** anything missing that would cover more or make the run smoother — Claude in Chrome for an extension, computer-use for native windows, an Android emulator on Windows, an iOS runtime, a VM, `agent-device`, Pillow — each with what it unlocks and what it costs ([references/environments.md](references/environments.md#helpers-worth-suggesting)). Suggest, don't install unasked.
   - **Blockers:** if something hides the rest of the app (crash on launch, login wall), keep going around it and report it, or stop right away. Default: keep going.
   Without an answer to a point, take the recommended or safest option and say which in one line.
5. **Get the tool permissions out of the way** while the user is still there: run one harmless call of every tool the run will use (a screenshot through the simulator, browser or computer-use tool, opening the run folder, the first build command), so the app's own permission prompts and site approvals appear now instead of halfway through. If the session asks for every shell command, say so once and point to the allow-rule setting rather than letting the run stall on prompts.
6. Pick the platform reference and read it now:
   - iOS (Simulator or real iPhone): [references/ios.md](references/ios.md)
   - Android: [references/android.md](references/android.md)
   - Web app or browser extension: [references/web-and-extension.md](references/web-and-extension.md)
   - Desktop app (Tauri, Electron, native; macOS or Windows): [references/desktop.md](references/desktop.md)
7. Create the run folder outside the product repositories (scratchpad or a private notes folder): `interaction-audit-<platform>-<YYYY-MM-DD>/` with `checklist.md`, `findings.md` and `screenshots/`. Copy the templates from [references/checklist-template.md](references/checklist-template.md).
8. Build and launch the app; take a baseline screenshot. If a debug-only overlay (test-build banner, debug HUD, environment ribbon) covers content, record it once as a finding marked *debug builds only*, then hide or disable it for the rest of the run so it doesn't spoil every screenshot.
9. **Find the design language** and write the design profile (system language such as HIG/Liquid Glass, Material 3 or Fluent; the app's own tokens for spacing, radii, type, colour, materials, icons and motion; which design skill was used to build it). Load the matching design skill as the rubric if one is available. See [references/design-language.md](references/design-language.md). Without a profile, spacing and animation findings are just taste.

### 2. Inventory — from code *and* from the running app

Build the full list before driving anything. Do both passes, because each misses things the other sees:

- **Code pass.** Grep the UI layer for every entry point: screens/routes/views, buttons and tappable views, menus and context menus, gestures (tap, long press/hold, swipe actions, drag and drop, pinch, pull to refresh), sheets/popovers/alerts/toasts, text fields and pickers, toggles in settings, keyboard shortcuts and menu-bar items, deep links/URL schemes, notifications, entry points outside the app's UI (Shortcuts / App Intents, Siri, widgets, controls and tiles, share extensions, quick actions, jump lists — see [references/system-entry-points.md](references/system-entry-points.md)), permission requests, onboarding/first-run flows, empty/loading/error states, feature flags. Platform references list the patterns to search for.
- **App pass.** Visit every reachable screen and list what you actually see (accessibility tree or `read_page` where available, screenshots otherwise). Add anything the code pass missed and note code entries you could not find on screen.
- **Catalog pass.** Go through [references/interaction-catalog.md](references/interaction-catalog.md) section by section (gestures, mouse and pointer incl. double/triple/middle/modifier clicks, keyboard, text editing, language and region, lifecycle and updates, network and multi-device sync, performance, system integration and hardware, privacy, robustness) and add every entry that applies to a control or screen you found. This is what turns "I tapped every button" into real coverage.

Then add the **cross-cutting variations** that apply to the platform: light/dark mode, the system accessibility features (screen reader, large text, bold text, increase contrast, reduce motion, reduce transparency, voice and switch control, full keyboard access — see [references/accessibility.md](references/accessibility.md); each one the platform offers is a checklist item, not an optional extra), screen sizes and form factors (smallest, typical and largest supported size, tablet, foldable, split view, desktop window sizes and display scaling — see [references/screen-sizes.md](references/screen-sizes.md)), rotation, offline / server or peer unreachable, empty state (fresh install, no data), lots of data (long lists, long text), interrupted flows (background the app, cancel half way), keyboard-only navigation, localisation if the app ships more than one language.

Also list the **states the app can be in** — plans and licences (free, trial, paid, expired, offline licence), account states, roles, feature flags and remote config — as a state matrix, and plan which screens to revisit in which state: [references/states-and-flags.md](references/states-and-flags.md). Use test accounts, sandbox purchases and local overrides only.

Group the checklist by screen. Each item is one interaction with its expected result. Expect dozens to hundreds of items for a real app — that is the point.

**Size the run before starting.** Count the items and estimate the time (a few minutes per item, more for videos and peer setups). If it won't fit into one sitting, say so and agree with the user how to split it: by area into several runs that continue the same `checklist.md`, or a smaller scope. `not reached (time)` is not a result; an item ends up unreached only with a reason the user accepted, and the next run starts from those items.

**Order by risk**, so an interrupted run has still covered what matters most: first the core flows (the reason the app exists), then anything touching money (purchases, licences, paywalls), then anything that can lose or leak data (delete, sync, sign-out, export, permissions), then the rest of the screens, then the cross-cutting variations and states. Mark each item's priority in the checklist and work top-down. Priority uses letters: **A** critical (crash, data loss, money, security) · **B** core flow broken · **C** other screens · **D** polish and variations.

### 3. Exercise — item by item

For every checklist item:

1. Bring the app to the item's starting state.
2. Perform the interaction with the platform's tool.
3. Screenshot the result (and the intermediate state for animations or multi-step flows) into `screenshots/` with a name matching the item ID, e.g. `S03-07-long-press-menu.png`. For animations, transitions, jank or anything timing-related, record a short video instead (`xcrun simctl io booted recordVideo`, `adb shell screenrecord`, the browser's or OS's screen recording, `agent-device record`), because a still frame can't prove an animation is broken. Then turn the stretch that matters into a **frame strip** (`swift scripts/video_frames.swift <video> <out.png> <from-s> <to-s> <count> [full|top|bottom]` on macOS, or `ffmpeg -ss <from> -t <len> -i <video> -vf "fps=4,scale=240:-1,tile=8x1" -frames:v 1 <out.png>`) and use it as the proof image next to the video: overlapping rows, jumps and missing transitions are visible at a glance, and images show in every report format and chat while videos often don't.
4. Compare with the expected result: right screen, right text, animation completes, no freeze, no console/log errors, state persists after leaving and returning. Then run the visual check from [references/visual-check.md](references/visual-check.md) on the screenshot: clipped or cut-off text, broken, stretched or blurry images, containers cut off or overlapping, content under the notch, keyboard or system bars. Zoom into edges instead of judging the whole screen at a glance. Compare spacing, type, colours, shapes, icons and motion against the design profile.
5. Mark the item: `ok`, `problem` (link the finding), `blocked` (say what blocks it), `skipped (destructive)`, `not approved` (say what approval would unlock it), or `not reachable`.

After a crash or hang, collect the evidence before relaunching: the crash report (Simulator/macOS: `~/Library/Logs/DiagnosticReports/`; device: Xcode Organizer or `devicectl`; Android: `adb logcat -b crash`; Windows: Event Viewer → Application; web: console and network), plus the log lines around the timestamp.

When something is wrong, write the finding immediately in `findings.md` (template in the checklist reference) with severity, exact repro steps from a known start state, expected vs actual, screenshot paths and relevant log lines. Then continue — don't stop to fix unless the user asked you to. A blocker that hides the rest of the app follows the blocker answer from the upfront round.

Watch for these problem classes in particular: crash or hang, dead control (nothing happens), wrong or untranslated text, truncated text, broken or distorted images, clipped or overlapping containers, content under system UI, broken or janky animation, state lost after navigation, live data that stops arriving after leaving the app and coming back (system Settings, share sheet, background) while the status still looks fine, missing feedback (no spinner, no confirmation), inconsistent behaviour between similar controls, deviations from the design profile (spacing off the scale, wrong type style, hard-coded colours, foreign icons, non-native or inconsistent animations), accessibility gaps (unlabeled buttons, too small targets, unreadable in dark mode or large text).

### 4. Report

The result for the user is **always tables, in this fixed order, with no prose between them**, in the format the user chose (see *Deliver* below) — at most one short line under a heading. Write in the user's language and in plain words they recognise from the app, not in the shorthand you or the subagents used while working; never compress findings further on the way to the user. Translate the column names into short everyday words (in German: Nr · Prio · Wo · Was du tust · Was passiert · Richtig wäre · Warum es stört · Lösung / Optionen · Beweis; Lassen: Warum lassen; Nicht geprüft: Warum nicht · So prüfst du es; group headings Beheben · Entscheiden · Lassen · Nicht geprüft). Each cell stays short (a few words up to one sentence); details live in `findings.md` and the HTML report.

Groups are headings, never letters, because priority already uses letters. Findings get **one running number across all tables** (1, 2, 3 …, continuing into *Not checked*), so the user can answer with numbers alone.

1. **Overview** — one line: items checked · to fix · to decide · to leave · not checked.
2. **Fix** (clear bugs and rule violations), sorted by priority:

   | No. | Prio | Where | What you do | What happens | Should be | Why it matters | Fix | Proof |
   |---|---|---|---|---|---|---|---|---|
   | 1 | B | Main window › Library › Clip list | Ctrl-click a second clip | only the second stays selected | both selected, like Explorer | multi-delete/move needs the tiny checkboxes | keep selection on Ctrl-click | [S04-07](screenshots/S04-07.png) |

3. **Decide** (may be intended or needs a product decision): same columns, but **Options** instead of *Fix* (e.g. "a) confirm dialog · b) undo toast · c) leave").
4. **Leave** (cosmetic or arguably intended), short: `No. | Where | What | Why leave it`.
5. **Not checked** — what was out of reach and how the user can check it: `No. | What | Why not | How you check it` (global shortcuts, pasting into other apps, tray, device-only features). Test-setup-only issues (mock data, test branch) go here too, marked as such, so they aren't mistaken for app bugs.
6. **One question** to close: which option for each *Decide* finding, and whether *Fix* and *Leave* are fine (the user can answer with numbers, e.g. "1–4 yes, 5 a, 6 c").

"Where" is the full path to the spot, using the names the user sees in the app, from window or screen down to the control: `Settings › Shortcuts › Reset all shortcuts`, `Popup › Search field`, `Library › Context menu › Move to collection`. The user must be able to find it without asking. "What you do" names concrete steps from a start state the user recognises; "What happens" and "Should be" are observable, not technical causes. Priority: A critical (crash, data loss, money, security) · B core flow broken · C other screens · D polish. "Proof" shows the screenshot itself (`<img src="screenshots/…" width="160">`, which renders in Markdown tables) or links the video.

**Deliver:**

Run `python3 <skill-dir>/scripts/build_report.py <run-dir> --lang <en|de>` (add `--previous <earlier-run-dir>` to compare screenshots with an earlier run). It writes `summary.md` and `report.html`. Never hand-write or redesign the HTML: `report.html` is [assets/report-template.html](assets/report-template.html) filled with the run's data, so every report looks the same and design improvements happen once, in the template (preview it with `build_report.py assets/sample-run`). Read `summary.md` and polish wording, order and the "How you check it" column in `findings.md` / `checklist.md`, then run the script again. Keep the run folder somewhere the app can open (a session folder or the scratchpad), or previews won't load. Then deliver in the chosen format:

1. **`report.html` (recommended):** the tables with image and video previews in the proof column (click to enlarge), priority filter and search, a detail card per finding, then every checklist item with status filter; with `--previous`, every screenshot is marked unchanged, changed or new, with side-by-side and blink comparison (pixel ratio and diff image if Pillow is installed). **Open it right away in the built-in browser** (e.g. `navigate` / `preview_start` with the `file://` URL of `report.html`). If the pane can only show a static snapshot (files outside the project folder) or no built-in browser exists, open it in the default browser instead (`open` on macOS, `start` on Windows) and say so. If the user reads it remotely (remote control, phone), local files won't open there: publish it as a private artifact if they approved that up front (it uploads their app's screenshots), otherwise send `summary.md` with the file tool.
2. **`summary.md`:** **open it right away** in the app's file view (e.g. `show_pane` with the file) and also send it with the file tool so it renders as a card in the chat; the proof column shows the images.
3. **Tables in the chat:** paste the tables into the chat with file names in the proof column, then send the proof files of all *Fix* and *Decide* findings with the file tool, in table order, caption = finding number.

In every format, the chat text itself is only the overview line, the closing question and one line pointing to the other files (`checklist.md`, `findings.md`, screenshots folder, and `report.html` if it wasn't the chosen format). For stable screenshot comparisons across runs, keep device, size and data the same and freeze the status bar (`xcrun simctl status_bar booted override --time 9:41 --batteryLevel 100`, Android demo mode).

If the project tracks tests or issues somewhere (a status page, an issue tracker), follow its rules for where findings go, within what the user approved up front; file nothing publicly without that approval.

After the closing question, offer (don't do unasked): fixing the design findings with the profile's tokens and the rubric skill (before/after screenshots as proof); turning the checklist's most important flows into automated UI tests in the framework the project already uses (XCUITest, Espresso/Compose tests, Maestro, Playwright), so the next audit only needs to cover what automation can't.

## Optional helper: agent-device

If `agent-device` (Callstack, npm) is already installed, it can replace coordinate tapping on iOS, Android, macOS and web: `snapshot -i` lists every interactive element with stable refs, `press`/`fill`/`scroll` act on them, and `record start/stop` captures videos. It also drives taps on a **real iPhone**, which most other tools cannot. Install it only if the user approved it in the upfront round; everything in this skill works without it.
