# Interaction catalog

Walk this catalog during the inventory and turn every entry that applies to the app into checklist items. Entries that don't apply (no text input, no sync, platform has no such gesture) get one line `not applicable – <reason>` so the gap is visible. Platform references hold the commands; this file is the *what*.

## Contents
- A. Touch and gestures
- B. Mouse, trackpad and pointer
- C. Keyboard
- D. Text input and editing
- E. Language, region and content
- F. App lifecycle and data
- G. Network, sync and multiple devices
- H. Performance
- H2. Motion and native feel
- I. System integration and hardware
- J. Privacy and security
- K. Robustness (abuse the UI)

## A. Touch and gestures
- Tap, double tap, long press / hold (and hold then drag), haptic touch / peek menus.
- Swipe actions on rows (both directions, full swipe), swipe between pages/tabs, edge swipe back (start exactly at the edge), drag content near the edge (start > 4 pt away).
- Scroll: fling, scroll to the very end, scroll to top (status bar tap), nested scroll views, scroll while content loads.
- Pull to refresh, drag to dismiss sheets (with unsaved input), drag to reorder.
- Pinch to zoom, two-finger rotate, two fingers on two different controls at once.
- Drag and drop within the app, between apps (iPad/Android split screen), into the app from Files/Photos.

## B. Mouse, trackpad and pointer
- Click, double click, triple click (select line/paragraph), middle click (open in new tab/window), right click / context menu, context-menu key.
- Modifier clicks: Shift-click range select, Cmd/Ctrl-click multi select or open in background, Alt/Option-click variants.
- Hover states and tooltips (also reachable without hover?), cursor shape over controls and resizable edges.
- Mouse wheel (vertical and horizontal with Shift), trackpad two-finger scroll and swipe back/forward, pinch zoom on trackpad, inertial scrolling.
- Drag and drop with the mouse: files from Finder/Explorer into the app, out of the app to the desktop, text between apps; drop onto invalid targets.
- iPad / Android tablet with trackpad or mouse: pointer hover effects, right click, scroll. Apple Pencil / stylus if the app draws or annotates (tap, press, Scribble in text fields).

## C. Keyboard
- Every shortcut and menu accelerator, Tab / Shift-Tab order, visible focus, Enter, Space, Escape.
- Arrow keys in lists and grids, Page Up / Page Down, Home / End, Cmd/Ctrl + arrows, type-ahead selection in lists.
- Hardware keyboard on iPad / Android tablet: Cmd shortcuts overlay (hold Cmd), arrow navigation, Return to submit.
- Global shortcuts while another app has focus; shortcut conflicts with the OS or the browser.

## D. Text input and editing
- Select (double/triple click or tap, drag handles), cut, copy, paste, paste-and-match-style, select all.
- Undo / redo (Cmd/Ctrl-Z, shake to undo on iOS, three-finger swipe on iPad), and whether app-level undo exists for deletes.
- Autocorrect, autocapitalisation, smart quotes/dashes (wanted or harmful, e.g. in code or URLs), spell check, text replacement.
- Dictation, emoji keyboard, IME composition (Japanese/Chinese: is Enter during composition swallowed?), third-party keyboards, password autofill and one-time-code autofill (test accounts only).
- Edge content: empty, only spaces, leading/trailing whitespace, very long single word, 10 000 characters, line breaks, tabs, emoji with skin tones and ZWJ sequences, RTL text mixed with LTR, HTML/Markdown-looking text, `'"; <script>` style characters, pasted rich text and images.
- Field behaviour: max length, keyboard type (email, number, URL), return key label, keyboard not covering the field, focus moving to the next field, value kept after rotation/backgrounding.

## E. Language, region and content
- Every shipped language: untranslated strings, wrong plurals, text that no longer fits (German and Finnish run long), mixed languages on one screen.
- Pseudo-localisation or the longest language for layout; right-to-left layout (Arabic/Hebrew) if supported.
- Region formats: date, time (12/24 h), first weekday, decimal separator, currency, units; time zone change and daylight-saving switch; midnight and month/year rollover for anything dated; device clock set far ahead/behind.
- Relative times ("2 min ago") updating; sorting with umlauts and accents.

## F. App lifecycle and data
- First launch (onboarding, permission timing), second launch, launch from a notification / deep link / widget / shortcut when the app is killed, backgrounded and already open.
- Background and return, kill and relaunch (state restoration), system kills the app under memory pressure (Android: `am kill`; iOS: memory warning in Simulator).
- **Update from the previous released version** with real data in it: migrations, settings kept, nothing duplicated. Downgrade is usually unsupported — check it fails safely.
- Reinstall / clear data: what comes back from backup or sync, what is lost, is that communicated.
- Low storage, Low Power Mode / battery saver, Do Not Disturb / Focus, Screen Time limits, device locked while the app works.
- Interruptions: incoming call or alarm, a notification banner over the app, Control Center / notification shade pulled down mid-gesture, Siri invoked, app switcher opened mid-flow.
- Multiple windows / instances (iPad, macOS, Windows, a second browser tab): same data shown consistently, edits in one reflected in the other.
- Signed-out / expired session / revoked token states and how the app recovers.

## G. Network, sync and multiple devices
- Offline at start, going offline mid-action, coming back online (queued work replays, no duplicates), airplane mode, Wi-Fi without internet / captive portal, VPN, slow (3G profile) and flaky networks, server errors (500, timeout) and their error UI.
- Retry and cancel controls; spinners that never end; double-submit while waiting.
- Multi-device: change on device A appears on B, both edit the same item (conflict), one device offline for a long time then reconnecting, pairing/unpairing flows (test devices only), clock skew between devices.

## H. Performance
- Cold and warm launch time; time to first content.
- Scrolling long lists and big images without jank; animations at full frame rate (use a screen recording to check).
- Memory over a long session (open/close the same screen 20 times), CPU and battery while idle, background activity.
- Large data: 1 000+ items, very large files/images, slow device or older OS version if the project supports one.
- Record numbers when tools allow (Xcode Instruments / `xctrace`, Android `dumpsys gfxinfo`, browser Performance panel, `agent-device perf`) — findings need numbers or a recording, not "felt slow".

## H2. Motion and native feel
- Keyboard show and hide in every field and search (tap in, *Done*, *Cancel*, clear, scroll to dismiss, submit): timing against the native reference, field stays visible.
- Sheet, popover, menu and dialog open/close and drag to dismiss; search open/close; push/pop and swipe back; tab and segment switches; row insert/delete/reorder.
- Each one recorded and compared frame by frame with a native app on the same device; a still is never proof. Details and reference apps: [native-feel.md](native-feel.md).
- Reduce Motion on: the app cross-fades or cuts like the reference.

## I. System integration and hardware
- Share sheet in and out, open-in / file associations, Files / document picker, print, export.
- Entry points outside the app's UI — Shortcuts / App Intents, Siri, Spotlight, Action button, automations, widgets, Control Center and Quick Settings controls, Live Activities, share and action extensions, launcher and Home Screen quick actions, jump lists, PWA shortcuts, extension commands: each in killed, background, foreground and locked state, see [system-entry-points.md](system-entry-points.md).
- Handoff / continuity, AirDrop, clipboard sync across devices.
- Notifications: received in foreground, background and killed state; actions on the notification; badge counts; grouping; tapping opens the right screen.
- Hardware the app uses: camera (front/back, denied), microphone, location (precise/approximate/denied/while using), Bluetooth, NFC, biometrics (Face ID / Touch ID / fingerprint success, failure, not enrolled — Simulator: Features → Face ID), haptics, sound with silent switch on/off and headphones connected/disconnected.
- Permission changed while the app runs (revoked in Settings, then return to the app).
- In-app purchases and paywalls: only with sandbox/test accounts; restore purchases; never buy for real.

## J. Privacy and security
- Sensitive content hidden in the app switcher snapshot and in screenshots/recordings if the app promises it; clipboard access prompts and expiry of copied secrets.
- Nothing sensitive in logs, URLs, notifications on the lock screen, or error messages.
- Data really deleted when the UI says so (as far as the UI can show it); sign-out clears local data where expected.
- Links open the right place; external links leave the app clearly.

## K. Robustness (abuse the UI)
- Rapid repeated taps/clicks on the same control (duplicate actions?), tapping two controls in quick succession, tapping during transitions and while loading.
- Cancelling half way: back during save, closing a sheet mid-upload, dismissing a permission dialog, rotating mid-animation.
- Going back and forth between two screens many times; deep navigation stack then deep link elsewhere.
- Starting the same flow from two entry points at once (notification + in-app button).
