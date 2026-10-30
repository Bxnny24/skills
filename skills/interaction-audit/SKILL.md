---
name: interaction-audit
description: Walk through a whole app and exercise every interaction it offers, one by one, with screenshot proof and a checklist file. Inventories every screen, control and gesture from the code and the running app, drives each one with the right tool for the platform (iOS Simulator or real iPhone, Android emulator, web, browser extension, desktop app on macOS or Windows), and records every crash, dead control, broken animation or wrong text with repro steps. Use this whenever the user wants to "go through the whole app", "tap everything", "test every button/interaction", do a full UI walkthrough or interaction audit, smoke test or exploratory pass before a release, check that nothing is broken after a big change, or says "/interaction-audit" with a platform such as mobile, ios, android, web, extension or desktop — even if they don't say "test".
---

# Interaction audit

The goal is **coverage**, not a quick bug hunt: by the end, every interaction the app offers on the chosen platform has been exercised at least once, and there is proof. A short list of bugs is a by-product. If something could not be exercised, the checklist says so and why — an honest "not reached" beats a silent gap.

Argument: the platform or area to cover (`mobile`, `ios`, `android`, `web`, `extension`, `desktop`, or a screen/feature name). If missing, infer it from the project and the user's words; ask only when two platforms are equally plausible.

## Ground rules

- **Safe by default.** Never perform destructive or outward-facing actions without asking first in chat: purchases or subscriptions, sending real messages/emails/posts, deleting real user data, unpairing or signing out of real accounts, resetting settings, granting system permissions on the user's own device, changing account settings. Open the confirmation dialog, screenshot it, then **cancel** and mark the item `asked` or `skipped (destructive)`. Prefer test data and simulators; create throwaway test content yourself and delete only what you created.
- **Real behaviour over code.** The code tells you *what exists*; only the running app tells you *whether it works*. Never mark an item done from reading code.
- **One thing at a time.** Stateful UI (focus, sheets, text fields, navigation stack) gets polluted by parallel actions. Drive serially; return to a known state after each item.
- **Write as you go.** Update the checklist and findings after every item, not at the end — a long run may be interrupted or summarized.

## Workflow

### 1. Prepare

1. Read the project's own instructions and any `run`/launch skill or `.claude/launch.json` to learn how to build and start the app.
2. **Check what this environment can actually run** before planning anything. The same request means different things on a Mac, on Windows, in a cloud sandbox:
   - Host OS (`uname -s` / `$env:OS`) and what is installed: `xcrun simctl list devices` and `xcrun devicectl list devices` (iOS, macOS only), `adb devices` and `emulator -list-avds` (Android), the project's dev command.
   - Which driving tools this session has (loaded or deferred): iOS Simulator tool, built-in browser, Claude in Chrome, computer-use, `agent-device`, Playwright/Maestro in the project.
   - What the project targets and pins: deployment target, a simulator or device named in its instructions, launch configs, memory notes.
   Write a short capability table at the top of `checklist.md` (platform → device/simulator → driving tool → available yes/no). [references/environments.md](references/environments.md) has the matrix of which target runs on which host (iOS only on macOS, Windows apps only on Windows, Android emulators need virtualisation, …). If the requested platform cannot run here, do not improvise: say so, offer the fallbacks listed there, and let the user choose. Platforms that *can* run here (e.g. the web part of the same app) may proceed meanwhile.
3. Pick the platform reference and read it now:
   - iOS (Simulator or real iPhone): [references/ios.md](references/ios.md)
   - Android: [references/android.md](references/android.md)
   - Web app or browser extension: [references/web-and-extension.md](references/web-and-extension.md)
   - Desktop app (Tauri, Electron, native; macOS or Windows): [references/desktop.md](references/desktop.md)
4. Create the run folder outside the product repositories (scratchpad or a private notes folder): `interaction-audit-<platform>-<YYYY-MM-DD>/` with `checklist.md`, `findings.md` and `screenshots/`. Copy the templates from [references/checklist-template.md](references/checklist-template.md).
5. Build and launch the app; take a baseline screenshot.

### 2. Inventory — from code *and* from the running app

Build the full list before driving anything. Do both passes, because each misses things the other sees:

- **Code pass.** Grep the UI layer for every entry point: screens/routes/views, buttons and tappable views, menus and context menus, gestures (tap, long press/hold, swipe actions, drag and drop, pinch, pull to refresh), sheets/popovers/alerts/toasts, text fields and pickers, toggles in settings, keyboard shortcuts and menu-bar items, deep links/URL schemes, notifications, widgets/share extensions/shortcuts, permission requests, onboarding/first-run flows, empty/loading/error states, feature flags. Platform references list the patterns to search for.
- **App pass.** Visit every reachable screen and list what you actually see (accessibility tree or `read_page` where available, screenshots otherwise). Add anything the code pass missed and note code entries you could not find on screen.

Then add the **cross-cutting variations** that apply to the platform: light/dark mode, the system accessibility features (screen reader, large text, bold text, increase contrast, reduce motion, reduce transparency, voice and switch control, full keyboard access — see [references/accessibility.md](references/accessibility.md); each one the platform offers is a checklist item, not an optional extra), rotation or window resize, offline / server or peer unreachable, empty state (fresh install, no data), lots of data (long lists, long text), interrupted flows (background the app, cancel half way), keyboard-only navigation, localisation if the app ships more than one language.

Group the checklist by screen. Each item is one interaction with its expected result. Expect dozens to hundreds of items for a real app — that is the point.

### 3. Exercise — item by item

For every checklist item:

1. Bring the app to the item's starting state.
2. Perform the interaction with the platform's tool.
3. Screenshot the result (and the intermediate state for animations or multi-step flows) into `screenshots/` with a name matching the item ID, e.g. `S03-07-long-press-menu.png`.
4. Compare with the expected result: right screen, right text, animation completes, no freeze, no console/log errors, state persists after leaving and returning.
5. Mark the item: `ok`, `problem` (link the finding), `blocked` (say what blocks it), `skipped (destructive)`, `asked`, or `not reachable`.

When something is wrong, write the finding immediately in `findings.md` (template in the checklist reference) with severity, exact repro steps from a known start state, expected vs actual, screenshot paths and relevant log lines. Then continue — don't stop to fix unless the user asked you to; a blocker that hides the rest of the app is the exception (report it and ask).

Watch for these problem classes in particular: crash or hang, dead control (nothing happens), wrong or untranslated text, truncated/overlapping layout, broken or janky animation, state lost after navigation, missing feedback (no spinner, no confirmation), inconsistent behaviour between similar controls, accessibility gaps (unlabeled buttons, too small targets, unreadable in dark mode or large text).

### 4. Report

Finish with:

- Coverage numbers: total items, ok, problem, blocked, skipped, not reachable — per screen.
- The findings, most severe first.
- What was **not** covered and why, plus the residual risk.
- Paths to `checklist.md`, `findings.md` and the screenshots folder; send the most telling screenshots with a file tool if one is available.

If the project tracks tests or issues somewhere (a status page, an issue tracker), follow its rules for where findings go — but ask before filing anything publicly.

## Optional helper: agent-device

If `agent-device` (Callstack, npm) is already installed, it can replace coordinate tapping on iOS, Android, macOS and web: `snapshot -i` lists every interactive element with stable refs, `press`/`fill`/`scroll` act on them, and `record start/stop` captures videos. It also drives taps on a **real iPhone**, which most other tools cannot. Do not install it without asking the user; everything in this skill works without it.
