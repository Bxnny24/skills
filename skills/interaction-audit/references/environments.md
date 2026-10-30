# Which platform runs on which host

Every target needs a matching host to be exercised for real. Cross-platform frameworks (Tauri, Electron, Flutter, React Native, Compose Multiplatform) don't change that: each target build still runs only where its OS or simulator runs.

## Matrix

| Target | macOS host | Windows host | Linux host | Cloud sandbox (no GUI, often no KVM) |
|---|---|---|---|---|
| iOS / iPadOS app | Simulator + real iPhone (Xcode) | no | no | no |
| Android app | Emulator (arm64 images on Apple silicon) + real device | Emulator (needs WHPX/Hyper-V or AEHD) + real device | Emulator (needs KVM) + real device | usually no emulator; real device over network or device farm |
| macOS desktop app | yes | no | no | no |
| Windows desktop app | only in a Windows VM (Parallels/UTM; Windows on ARM emulates x64) | yes | only in a VM | no |
| Linux desktop app | VM or container with a display | WSL2 with WSLg, or VM | yes | headless with Xvfb, screenshots only |
| Web app | yes, incl. Safari | yes (no real Safari; Playwright WebKit approximates it) | yes (no real Safari) | headless browser only |
| Chrome/Edge/Firefox extension | yes | yes | yes | headless only, popup hard to reach |
| Safari extension | yes (Xcode) | no | no | no |

Check the actual machine, not just the OS: virtualisation enabled, emulator images installed, enough RAM, the session's tools present. Record the result in the capability table at the top of `checklist.md`.

## OS versions and browsers

Run the full audit on the newest OS / browser the app supports, then a layout-and-main-flows pass on the **oldest** supported version, because API fallbacks, missing system features and different system UI break there first. Read the minimum from the project (`IPHONEOS_DEPLOYMENT_TARGET`, `minSdk`/`targetSdk`, `LSMinimumSystemVersion`, Windows target in the installer/manifest, `browserslist`, the extension manifest's `minimum_chrome_version` / `browser_specific_settings`).

| Target | Newest | Oldest supported | Also |
|---|---|---|---|
| iOS / iPadOS | latest iOS runtime | runtime matching the deployment target (`xcodes runtimes` or Xcode → Settings → Components to install; only if approved up front) | beta OS if the user is preparing for it |
| Android | latest API level image | `minSdk` image | one mid version where behaviour changed (e.g. notification permission, predictive back) |
| macOS app | current macOS | minimum version — usually only in a VM or on a second Mac, otherwise `blocked (needs macOS <x>)` | |
| Windows app | Windows 11 current | Windows 10 if supported (VM) | |
| Web app | latest Chrome, Edge, Firefox, Safari | oldest versions in `browserslist` (Playwright browser channels, BrowserStack — only if approved up front) | mobile Safari on iOS Simulator, Chrome on Android emulator |
| Browser extension | every store it ships to: Chrome, Edge, Firefox, Safari | `minimum_chrome_version` | Manifest V3 service-worker restarts, browser-specific APIs (`browser.*` vs `chrome.*`) |

Installing extra runtimes, browsers or VMs costs disk space and time: list what's missing in the upfront questions, with sizes, and download only what the user approves. Record which versions were covered in the checklist header; anything not covered goes into the report's residual risk.

## When the target can't run here

Put these into the upfront questions in this order and let the user choose; never pick a paid or account-bound option yourself.

1. **A session on the right machine.** Start or continue the work on a machine with the matching OS (an SSH host, a session started there, a remote desktop the user opens). Best option: the full skill runs unchanged.
2. **A VM or second machine the user provides** (Windows VM on the Mac, a Mac reached from Windows, an Android phone on the same Wi-Fi with `adb pair`/`adb connect`). Drive it with computer-use or the platform's CLI if this session can reach it.
3. **User-driven on a real device.** The user performs each step on the installed app (TestFlight, Play internal testing, an installer) while you go through the checklist one item at a time, read their screenshots and record results. Mark these items `ok (user-driven)`.
4. **Cloud devices or machines** — macOS/Windows CI runners (automated scripts only, no interactive UI), BrowserStack, Sauce Labs, AWS Device Farm, Firebase Test Lab, remote devices via `agent-device`. These need the user's account and may cost money: only if approved up front, never sign up or pay.
5. **Cover what runs here and leave the rest open.** Shared core tests, the web view or another platform build of the same feature, and a code-only inventory so the checklist is ready. Remaining items stay `blocked (needs <host>)` — never mark them done from code.
