# Android (emulator and real device)

## Tools

- `emulator -list-avds`, `emulator -avd <name>` (run in the background), `adb devices`.
- Build/install: the project's Gradle task (`./gradlew installDebug`) or `adb install -r <apk>`; launch with `adb shell monkey -p <package> 1` or `adb shell am start -n <package>/<activity>`.
- Inspect: `adb exec-out uiautomator dump /dev/tty` gives the view hierarchy with bounds, text, resource IDs and `clickable`/`long-clickable` flags — use it both for inventory and for exact tap coordinates.
- Input: `adb shell input tap x y`, `input swipe x1 y1 x2 y2 [ms]` (long press = swipe to the same point with 800 ms), `input text '...'`, `input keyevent KEYCODE_BACK|KEYCODE_HOME|KEYCODE_APP_SWITCH|KEYCODE_ENTER`.
- Proof: `adb exec-out screencap -p > screenshots/<id>.png`; video `adb shell screenrecord /sdcard/x.mp4` then `adb pull`.
- Logs: `adb logcat -c` before an item, `adb logcat -d *:E` after; crashes show as `FATAL EXCEPTION`.
- Variations: `adb shell cmd uimode night yes|no`, `adb shell settings put system font_scale 2.0`, `adb shell settings put system user_rotation 1` (after disabling auto-rotate), `adb shell svc wifi disable` / `svc data disable` (emulator only — never on the user's own phone without asking), `adb shell pm revoke|grant <package> <permission>`, `adb shell am start -a android.intent.action.VIEW -d '<deep link>'`.
- agent-device, Maestro or Appium may exist in the project; use them if they are already set up.

Android tooling runs on macOS, Windows and Linux. Use the AVD the project names, otherwise one booted or the newest image matching `minSdk`/`targetSdk`; note it in the checklist header. Emulators need hardware acceleration — in a cloud sandbox without it, use the fallbacks in [environments.md](environments.md): a phone over `adb pair`/`adb connect` on the same Wi-Fi, a user-driven pass, or a device farm (ask first).

## Code pass – what to grep

- Compose: `@Composable` screens, `NavHost`/`composable(`, `Button(`, `IconButton(`, `Modifier.clickable`, `combinedClickable` (long press), `pointerInput`/`detectDragGestures`, `SwipeToDismissBox`, `PullToRefreshBox`, `ModalBottomSheet`, `AlertDialog`, `DropdownMenu`, `TextField`, `Switch`, `Checkbox`, `Snackbar`.
- Views: `setOnClickListener`, `setOnLongClickListener`, `ItemTouchHelper`, `SwipeRefreshLayout`, menus in `res/menu/`, layouts in `res/layout/`.
- `AndroidManifest.xml`: activities, `intent-filter`s (deep links, share targets), permissions, services, widgets (`appwidget-provider`), Quick Settings tiles, notification channels.
- Flutter/React Native: see web/desktop references for JS patterns; Flutter `GestureDetector`, `InkWell`, `onLongPress`, `Dismissible`, `RefreshIndicator`.

## Interactions people forget on Android

- System back (button and predictive back gesture) on every screen, including inside sheets and dialogs.
- Process death: `adb shell am kill <package>` while backgrounded, then return — is state restored?
- Split screen / multi-window, foldable postures if supported.
- Share sheet in and out, notification actions, widget taps.
- Permission "Don't allow" and "Only this time", and the app's recovery path afterwards.
