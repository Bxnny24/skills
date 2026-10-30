# iOS (Simulator and real iPhone)

## Tools

- **Simulator:** the iOS Simulator tool (`mcp__Claude_Code_iOS_Simulator__control`, plus its `build` tool when present). Call `attach` first so the user can watch, then build and `launch`. Inputs: `tap` (with `duration` > 0.5 for long press), `swipe`, `touch_path` (drag, long-press-then-drag, pull to refresh), `touch2_path` (pinch/rotate), `text`, `press_key`, `button` (HOME, LOCK), `open_url` (deep links), `set_appearance` (light/dark), `rotate`, `set_keyboard`, `screenshot`. Coordinates are device points from the latest screenshot.
- Without that tool: `xcrun simctl` (`boot`, `install`, `launch`, `openurl`, `io booted screenshot`, `ui booted appearance dark`, `privacy booted grant|revoke|reset`, `status_bar override`, `push` for notifications, `spawn booted log stream`).
- **Real iPhone:** build with `xcodebuild -destination 'platform=iOS,id=<udid>'`, install and launch with `xcrun devicectl device install app` / `device process launch`. Screenshots come from the user or a device tool; most simulator input tools cannot tap on a physical device (agent-device can, if installed). Use the device only for what the Simulator cannot show: real camera, Face ID, push, background sync, haptics, performance.

## Choosing the simulator

Use the simulator or device the project names (instructions, launch config, memory notes, CI workflow). Otherwise pick a booted one, else the newest iPhone runtime from `xcrun simctl list devices available`, and check it meets the app's deployment target. For the size passes (small, large, iPad if supported) follow [screen-sizes.md](screen-sizes.md). Record the exact device and iOS version in the checklist header.

## Not on a Mac (Windows, Linux, cloud sandbox)

Simulator and Xcode exist only on macOS: on Windows or Linux an iOS app can't be built or simulated. Tell the user right away and offer the fallbacks in [environments.md](environments.md) — a session on their Mac, or a user-driven pass on a real iPhone with a TestFlight build, are usually the best ones.

## Code pass – what to grep (SwiftUI / UIKit)

- Screens and navigation: `NavigationStack`, `NavigationLink`, `.navigationDestination`, `TabView`, `.tabItem`, `.sheet`, `.fullScreenCover`, `.popover`, `.inspector`, `UIViewController` subclasses.
- Controls: `Button(`, `.onTapGesture`, `Toggle`, `Picker`, `Stepper`, `Slider`, `DatePicker`, `Menu`, `Link`, `ShareLink`, `PhotosPicker`, `.fileImporter`, `.fileExporter`.
- Gestures: `.contextMenu`, `.onLongPressGesture`, `LongPressGesture`, `DragGesture`, `.swipeActions`, `.refreshable`, `.onDelete`, `.onMove`, `.draggable`, `.dropDestination`, `MagnificationGesture`.
- Feedback: `.alert`, `.confirmationDialog`, toasts/banners, `ProgressView`, `ContentUnavailableView` (empty states).
- Text input: `TextField`, `SecureField`, `TextEditor`, `.searchable`, `.focused`, `.submitLabel`, `.onSubmit`.
- Entry points outside the app: `onOpenURL`, `Info.plist` `CFBundleURLTypes` (URL schemes), universal links, `AppIntent` / App Shortcuts, widgets, share extension, Control Center controls, notifications (`UNUserNotificationCenter`), Spotlight, Handoff. How to exercise them (and which need a team-signed build on a device) is in [system-entry-points.md](system-entry-points.md).
- Permissions: `NS*UsageDescription` keys in `Info.plist`, `requestAuthorization`, local network, camera, photos, notifications, pasteboard access.
- Settings bundle (`Settings.bundle`) – appears in the system Settings app.

## Interactions people forget on iOS

- Long press on rows, images, links, and the app icon (Home Screen quick actions).
- Swipe back from the left edge (start exactly at the edge) vs. dragging content near the edge (start > 4 pt away).
- Pull to refresh; scroll to the very end of long lists; scroll-to-top by tapping the status bar.
- Dismissing sheets by dragging down — does unsaved input survive or get a warning?
- Keyboard: return key action, dismissal, the field staying visible above the keyboard, paste from clipboard (the paste-permission prompt appears only when the app reads the pasteboard).
- Dynamic Type: set the largest accessibility size (`simctl ui booted content_size accessibility-extra-extra-extra-large`) and recheck every screen.
- Dark mode, rotation (if supported), iPad/split view (if supported), reduced motion.
- Backgrounding and returning (`button HOME`, relaunch), killing and relaunching (state restoration).
- Permission prompts: first-time allow, deny, then the "denied" state and its recovery path. Reset with `simctl privacy booted reset all <bundle-id>`.
- Offline / unreachable peer or server: the Simulator uses the Mac's network; stop the local server or peer instead of toggling the Mac's Wi-Fi.

## Proof

Screenshots from the Simulator tool show only the screen. If the project wants the whole device with its frame, follow that project's rule (e.g. a device-frame screenshot of the Simulator window).
