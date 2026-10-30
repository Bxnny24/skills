# Entry points outside the app's own UI

Shortcuts, widgets, share sheets, tiles and system search run app code in situations the normal UI never sees: the app is killed or in the background, the device is locked, there is no window, a time limit applies, and the system — not the app — draws the UI. That is where they break, so each entry point gets its own checklist items in **every app state**.

## The state matrix for every entry point

Run each entry point with the app **killed**, **in the background** and **in the foreground**, and where it matters with the device **locked**, **offline** and **signed out / unlicensed**. Check:

- It does what it says and returns the right result (text, file, URL, error) to the caller.
- It opens the app only when it should, on the right screen, and without losing what the user was doing.
- It fails with a clear message (not a silent nothing or a generic "something went wrong") when it can't work: no network, no peer, no permission, locked device, expired licence.
- It finishes within the platform's time limit (background App Intents get roughly 30 s) and doesn't leave half-done work behind; whatever it queued is processed later.
- Its parameters work with typical, empty and very large inputs and with every supported type (text, image, file, URL).
- The main app reflects the change afterwards (new item visible, counts updated) without a restart.

## iOS / iPadOS / macOS

| Entry point | Find it | Exercise it |
|---|---|---|
| App Shortcuts and App Intents (Shortcuts app, Siri, Spotlight, Action button, Apple Intelligence) | `AppIntent`, `AppShortcutsProvider`, `AppEntity`, `@Parameter`, `supportedModes` / `openAppWhenRun` | Shortcuts app: find the app's actions, build a shortcut that chains them with system actions (e.g. *Get Clipboard* → app action → *Show Result*), run it from the Shortcuts app, from a Home Screen icon, from Spotlight; Siri with each `AppShortcut` phrase (device only); Action button (iPhone 15 Pro and later, device only) |
| Personal automations | the same intents | Shortcuts → Automation (time of day, opening an app, NFC, Focus): run once manually and once triggered |
| Widgets, interactive widgets, Lock Screen widgets, StandBy | `Widget`, `TimelineProvider`, `AppIntentConfiguration`, `Button(intent:)` | add every size, configure, tap, use the interactive buttons, check timeline refresh, dark/tinted/clear Home Screen styles |
| Control Center, Lock Screen and Action-button controls | `ControlWidget` | add the control, toggle/run it with the app killed |
| Live Activities and Dynamic Island | `ActivityKit` | start, update, end; compact, minimal and expanded presentations; Lock Screen |
| Share extension and action extension | extension targets, `NSExtensionActivationRule` | share every supported type from Photos, Files, Safari, Notes; cancel; large files; app not launched since install |
| Spotlight and Siri Suggestions | `CSSearchableItem`, `NSUserActivity`, `IndexedEntity` | search for app content, open a result |
| Home Screen quick actions | `UIApplicationShortcutItems`, `shortcutItem` | long press the app icon, every item, cold and warm start |
| Focus filters | `SetFocusFilterIntent` | set up a filter, switch Focus, check the app adapts |
| URL schemes and universal links | `onOpenURL`, `CFBundleURLTypes`, associated domains | `simctl openurl`, links from Notes/Messages/Safari, invalid and malicious parameters |
| macOS only | Services menu, menu-bar extras, Finder extensions, Quick Look | run each from Finder / another app |

**Simulator limits:** an ad-hoc or unsigned Simulator build can list App Shortcuts but the system may refuse to run them (`linkd` reports a missing team ID) — those items need a team-signed build on a real device. Siri, the Action button, Back Tap, NFC automations and real push-driven Live Activities also need a device. Mark them `blocked (needs device)` instead of skipping silently.

**Background traps worth a dedicated item:** the system pasteboard can't be read while the app is in the background (pass clipboard content in as a parameter instead, e.g. from the *Get Clipboard* action); files with complete data protection can't be written while the device is locked; long-lived connections that the app keeps only in the foreground are not available to an intent unless it opens its own.

## Android

| Entry point | Find it | Exercise it |
|---|---|---|
| Launcher shortcuts (static, dynamic, pinned) | `res/xml/shortcuts.xml`, `ShortcutManager` | long press the icon, pin to Home Screen, run with the app killed |
| Quick Settings tiles | `TileService` | add the tile, tap, long press (opens settings) |
| Widgets | `AppWidgetProvider`, Glance | add, resize, configure, tap, update intervals |
| Share targets and direct share | `intent-filter` `SEND`/`SEND_MULTIPLE`, `ChooserTarget` / sharing shortcuts | share every supported type from Photos, Files, Chrome |
| Assistant / App Actions, Routines | `shortcuts.xml` capabilities | via the Assistant on a device or the App Actions test tool |
| Notifications with actions, bubbles | `NotificationCompat.Action`, `BubbleMetadata` | every action with the app killed, inline reply |
| Deep links and App Links | `intent-filter` with `VIEW` | `adb shell am start -a android.intent.action.VIEW -d '<url>'`, verified vs. unverified links |

## Windows

Jump lists (right click on the taskbar icon), Start-menu tiles/pins, the Share target contract, protocol handlers (`myapp://`), file-type associations and "Open with", context-menu entries in Explorer, tray menu, toast notification actions, startup tasks. Exercise each with the app closed, minimised to tray and open.

## Web and browser extensions

PWA manifest `shortcuts` (long press the installed icon / right click in the dock), share target (`share_target`), protocol and file handlers, push notifications and their actions, extension `commands` (keyboard shortcuts, check `chrome://extensions/shortcuts`), context-menu entries, omnibox keyword, side panel opened from the toolbar.
