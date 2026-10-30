# Accessibility features

Every system accessibility feature the platform offers gets its own checklist items. Turn it on, walk the main screens (all screens for screen readers and text size), check the expected behaviour below, then turn it off again so later items start from the default. Restore every setting you changed at the end of the run and say so in the report. On the user's own device, change system settings only if approved in the upfront round.

## What to check per feature

| Feature | Check |
|---|---|
| Screen reader (VoiceOver, TalkBack, Narrator) | Every control is reachable by swiping/Tab, has a meaningful label (no "button", file names or icon names), states are announced (selected, on/off), order follows the screen, custom gestures and actions have an accessible alternative (custom actions, rotor), images are labelled or hidden, alerts and toasts are announced. |
| Largest text size / Dynamic Type / font scale | No truncation that hides meaning, no overlap, layouts reflow or scroll, buttons stay tappable. |
| Bold text | Text still fits, custom fonts respect it. |
| Increase contrast / high contrast | Text and icons stay readable, borders and separators appear, nothing disappears. |
| Reduce motion | Large or parallax animations are replaced by fades; nothing that conveys state is lost. |
| Reduce transparency | Blurred/glass backgrounds become solid and text stays readable. |
| Smart invert / colour inversion / colour filters | Images and media are not inverted; status is not conveyed by colour alone. |
| Button shapes, On/Off labels | Controls stay recognisable. |
| Voice Control / Voice Access | Every control has a name that can be spoken ("Tap Add"); numbered overlay covers all controls. |
| Switch Control / Switch Access, Full Keyboard Access | Every control is reachable and operable without touch; focus is visible. |
| Hover/zoom (Zoom, Magnifier) | Focused content follows the zoomed area; no fixed-position UI covers content. |

## How to switch them on

- **iOS Simulator:** `xcrun simctl ui booted content_size accessibility-extra-extra-extra-large` (reset: `large`), `xcrun simctl ui booted increase_contrast enabled|disabled`. Others (Bold Text, Reduce Motion, Reduce Transparency, Button Shapes, Smart Invert, Full Keyboard Access) through the Settings app in the Simulator → Accessibility. VoiceOver does not run in the Simulator: use Xcode's **Accessibility Inspector** (audit + element labels) there, and a real iPhone for an actual VoiceOver pass.
- **Real iPhone:** Settings → Accessibility; the Accessibility Shortcut (triple-click side button) toggles VoiceOver quickly. Switching features on their own phone is a user-driven step: agree on it in the upfront round and do it as one block.
- **Android:** `adb shell settings put system font_scale 2.0`, `adb shell settings put secure high_text_contrast_enabled 1`, `adb shell settings put secure accessibility_display_inversion_enabled 1`, reduce motion via `adb shell settings put global animator_duration_scale 0` (and `transition_animation_scale`, `window_animation_scale`), TalkBack via `adb shell settings put secure enabled_accessibility_services com.google.android.marvin.talkback/com.google.android.marvin.talkback.TalkBackService` and `accessibility_enabled 1` (emulator image needs TalkBack installed). Accessibility Scanner gives an automated audit.
- **macOS:** System Settings → Accessibility (VoiceOver with Cmd+F5, Increase Contrast, Reduce Motion, Reduce Transparency, text size). These are system-wide: change them only if approved in the upfront round, and switch them back.
- **Windows:** Settings → Accessibility (Narrator with Win+Ctrl+Enter, Contrast themes, text size, Animation effects). System-wide: only if approved up front.
- **Web/extensions:** built-in browser `resize_window` with `colorScheme`, browser zoom 200 %, `read_page` for names and roles, keyboard-only pass; emulate `prefers-reduced-motion` and `prefers-contrast` with `javascript_tool` only for inspection (e.g. checking which CSS media queries exist), or through the OS settings with permission.
