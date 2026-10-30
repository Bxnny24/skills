# Native-feel pass

An app can pass every functional check and still feel wrong: the keyboard leaves late, a sheet snaps instead of sliding, swipe-back doesn't work, a badge sits on top of its icon. Users notice these at once; stills and code reading don't. This pass makes that class of bug systematic instead of a lucky find. Run it **per screen**, after the functional items of that screen, and give every point below its own checklist item (or `not applicable – <reason>`).

## 1. Motion and timing — always against a native reference

Every one of these is recorded on video, turned into a frame strip and compared with a native app doing the same thing **on the same device or simulator**:

- keyboard show and hide (tap into a field, tap *Done*/*Cancel*/the X in a search field, scroll to dismiss, submit)
- sheet, popover, menu and dialog open and close; drag to dismiss
- search open and close (search bar activation, cancel, clear)
- push and pop (navigation forward, back button, swipe back)
- tab switch, segmented control switch
- list row insert, delete and reorder; expand and collapse
- any custom transition or loading-to-content change

A still before/after **never** counts as proof for these: the problem is in the frames between.

| Platform | Native reference to record alongside |
|---|---|
| iOS / iPadOS | Settings (search field, push/pop, toggles), Messages or Mail (keyboard, swipe actions), Files (sheets, search), Photos (zoom, drag) |
| Android | Settings (search, navigation), Files by Google, Messages; predictive back on Android 14+ |
| macOS | System Settings (search, sidebar), Finder (lists, Quick Look), Notes (popovers) |
| Windows | Settings (search, navigation), File Explorer, Notepad (dialogs) |
| Web / extension | the browser's own UI is not a reference; compare with the platform's conventions above and with `prefers-reduced-motion` honoured |

How to compare:
1. Make the motion visible: on the iOS Simulator turn on touch indicators (`defaults write com.apple.iphonesimulator ShowSingleTouches 1`, Simulator restart; a system-app setting, so approved up front), on Android *Show taps* in developer options.
2. Record the app and the reference with the same tool and frame rate (`xcrun simctl io booted recordVideo --codec h264`, `adb shell screenrecord`, screen recording on desktop).
3. Cut both to the same window (from the tap to the settled state) and make strips with the same frame count and interval (`scripts/video_frames.swift`, or `ffmpeg … tile`). Put them one above the other as the proof.
4. Count frames from the tap to the settled state, and look at the curve: does it start at once, ease like the reference, move in the same direction, end without a jump? A difference of more than ~2 frames at 60 fps (≈ 35 ms), a missing animation, a different direction or a visible jump is a finding, with both strips as proof and the frame counts in *What happens / Should be*.
5. Repeat with *Reduce Motion* on: the app should cross-fade or cut like the reference does.

## 2. Gestures the platform promises

- **iOS:** swipe back from the left edge on every pushed screen (also with a keyboard open), tap the status bar to scroll to top, pull to refresh where lists refresh, drag sheets down to dismiss (with a confirmation if there is unsaved input), long-press context menus with preview, swipe actions on rows, edge-to-edge scrolling under translucent bars.
- **Android:** system back and predictive back, edge-to-edge insets, long-press, swipe to refresh, overscroll effect.
- **macOS / Windows:** trackpad swipe back/forward where the app has history, inertial scrolling, window resize live layout, keyboard focus and Escape closing popovers.

A gesture that the platform offers everywhere and the app silently ignores is a finding.

## 3. Keyboard behaviour (touch platforms)

- The focused field stays visible above the keyboard, with the same spacing as native forms; nothing jumps after the keyboard settled.
- Scrolling or dragging the list dismisses the keyboard the way the platform does it (interactive on iOS where native lists do it).
- Return key type matches the action (*Search*, *Done*, *Next*), *Next* moves focus in order, and the keyboard leaves at the same moment as in the reference (section 1).

## 4. Haptics and sound (where reachable)

Real device only: toggles, pickers, long-press menus, pull to refresh and destructive confirmations give the same haptic as the native counterpart, and no extra ones. Not reachable in a simulator — list it as a user-driven step agreed up front.

## 5. Small elements at 100 %

Zoom into every badge, dot, counter, chevron, check mark, close button and small icon at 100 % or more (`proof_detail.swift`, the screenshot tools' `zoom`). Each must:
- not cover its own glyph or label (a count badge over the clock it belongs to is a finding),
- not be clipped by its container or the screen edge,
- sit where the platform puts it (iOS: top trailing corner of the icon, overlapping it only at the corner; Material: top end of the icon; tab-bar and toolbar badges as in the native apps),
- stay readable at the largest text size and in both themes.

## 6. Spacing and type against the platform

Compare margins, row heights, control sizes and text styles with the design profile and the platform guide (HIG, Material 3, Fluent): standard margins, minimum touch targets, system text styles instead of fixed sizes, the platform's own controls instead of look-alikes. Measure, don't eyeball: pixel distances in the full-resolution screenshot divided by the scale factor.
