# Screen sizes, resolutions and form factors

Layout bugs hide at the edges, so every audit covers at least the **smallest**, a **typical** and the **largest** size the app supports, plus every form factor it declares (tablet, foldable, desktop window). Check what the app supports first (iOS `UIDeviceFamily` / `TARGETED_DEVICE_FAMILY` and `UISupportedInterfaceOrientations`, Android `screenOrientation`, `resizeableActivity` and tablet layouts in `res/layout-sw600dp`, web breakpoints in CSS/Tailwind config, desktop `minWidth`/`minHeight` in the window config). An unsupported size is not a bug; record it as `not supported` in the checklist.

Run the **full** walkthrough on the typical size. On the other sizes, revisit every screen (not every item) and check layout only: truncation, overlap, clipped or unreachable controls, wasted space, images scaled badly, sheets and dialogs fitting, keyboard covering inputs. Name screenshots with the size, e.g. `S02-ipad-landscape.png`.

## Per platform

| Platform | Smallest | Typical | Largest / other form factors |
|---|---|---|---|
| iOS | iPhone SE (4.7", 375 pt wide) | current standard iPhone | Pro Max / Plus; iPad (portrait, landscape, Split View ⅓ and ½, Stage Manager window) if supported; landscape on iPhone if supported |
| Android | small phone (~360 dp wide, e.g. a 5" AVD) | Pixel standard | Pixel Pro / large phone; tablet AVD (sw600dp and sw840dp); foldable AVD folded and unfolded; split screen; landscape; density buckets mdpi vs xxxhdpi for icon and image sharpness |
| Web | 320 px (small phone) | 390 px phone, 768 px tablet, 1280–1440 px laptop | 1920 px and ultra-wide 2560 px; portrait and landscape tablet; 200 % zoom; every CSS breakpoint ±1 px |
| Browser extension | popup at its minimum size | popup default, side panel default width | side panel widened; content-script UI on narrow and wide pages |
| Desktop | the window's minimum size | default window size on a 1366×768 and a 1920×1080 screen | maximised / full screen on 4K; display scaling 100 %, 125 %, 150 %, 200 % (Windows) and Retina vs non-Retina (macOS); moving the window between monitors with different scaling |

## How to switch

- **iOS Simulator:** boot several devices (`xcrun simctl list devices available`, `xcrun simctl boot <udid>`) and `launch` the app on each; `rotate` for landscape. iPad multitasking via the Simulator's window controls or by dragging from the top of the screen.
- **Android:** create AVDs per size (`avdmanager create avd -n tablet -k "<system image>" -d pixel_tablet`; foldables `pixel_fold`), or resize one device: `adb shell wm size 1080x2400` / `adb shell wm density 420`, reset with `wm size reset` and `wm density reset`.
- **Web:** built-in browser `resize_window` with presets (mobile, tablet, desktop) or exact `width`/`height`; Claude in Chrome `resize_window`; Playwright device descriptors if the project has Playwright.
- **Desktop:** resize the window with computer-use or `osascript` (macOS); change display scaling only with the user's permission (it is a system setting) — alternatively ask the user to switch it, or test on a second monitor they provide.
