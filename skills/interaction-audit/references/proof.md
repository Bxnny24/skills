# Proof the user can read

A proof is only useful if the user sees the problem in it without reading the text next to it, at the size the report or chat shows it. Small, blurry or whole-screen-only screenshots don't meet that bar.

## Capture at real resolution

Save proof files with a tool that writes the actual pixels. A screenshot that only exists in the conversation (the browser or computer-use tool's own screenshot, which is scaled down for the model) is for your eyes, not proof for the user.

| Platform | Proof file at full resolution |
|---|---|
| iOS Simulator | `xcrun simctl io booted screenshot screenshots/<id>.png` (device pixels, e.g. 1206×2622) |
| Real iPhone | the user's own screenshot (side button + volume up), or Xcode → Devices and Simulators → Take Screenshot |
| Android | `adb exec-out screencap -p > screenshots/<id>.png` |
| macOS window | `screencapture -x -o -l<window-id> screenshots/<id>.png` (Retina, no shadow) |
| Windows | `Win+Shift+S` by the user, or a PowerShell `CopyFromScreen` of the window bounds |
| Web / web view | Playwright `page.screenshot({ path, scale: "device" })` with `deviceScaleFactor: 2`, or headless Chrome `--force-device-scale-factor=2 --screenshot`; the element alone with `locator.screenshot()` |

Keep the window or viewport at a normal size (no 3000-px-wide desktop shots of a small dialog), crop to the app window, and keep the system text size at default unless the item is about text size.

## Two images per finding

1. **Detail first:** the problem area cut out, scaled up so its text is readable at 100 % and the spot framed in red. On macOS without extra installs:
   `swift <skill-dir>/scripts/proof_detail.swift screenshots/S04-07.png screenshots/S04-07-detail.png <x> <y> <w> <h>`
   (pixel coordinates of the problem in the screenshot; optional margin and minimum width, default 40 and 900). Elsewhere use Pillow (`Image.crop`, `resize` with `NEAREST`, `ImageDraw.rectangle`) if it was approved up front, or crop to the element with the web tool.
2. **Context second:** the whole screen or window, so the user knows where it is.

List them in that order in the proof column (`screenshots/S04-07-detail.png, screenshots/S04-07.png`): the first image is the thumbnail in the report. Checklist items that passed need only the context screenshot.

For animations and timing: a short video (at least 720p, a few seconds, only the app window), plus a frame strip as a still (`swift <skill-dir>/scripts/video_frames.swift …`) so the problem is visible without playing the video.

## Check before you report

Open every proof of a *Fix* or *Decide* finding (read the image file itself) and ask: is the problem obvious at this size, without the caption? Is the text in it readable? Is it the right state (not a loading screen, not covered by a debug overlay or a tooltip)? If not, recapture or crop again. `build_report.py` warns about images that are missing or too small; fix every warning before delivering.
