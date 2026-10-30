# Desktop apps (Tauri, Electron, native) on macOS and Windows

## Tools

- **Web-view first.** Tauri and Electron render HTML: if the project can serve the frontend in a browser (a dev server with mocked backend calls), do the bulk of the UI inventory and clicking in the built-in browser — it gives an accessibility tree, console and network. Then verify the native parts in the real app.
- **The real app:** start it with the project's dev command (`npm run tauri dev`, `npm run electron:dev`, …) in the background, then drive it with **computer-use** (load the `anthropic-skills:computer-use` skill): screenshots, clicks, typing, keyboard shortcuts, drag and drop, right clicks. Ask the user to grant screen/accessibility access if prompted; do not change system security settings yourself.
- **macOS extras:** `screencapture -x -l<windowid>` or `screencapture -x` for proof, `osascript` for menu-bar items and window resize, `defaults write -g AppleInterfaceStyle Dark` is a system setting — ask before changing it, or use the app's own theme switch.
- **Windows extras:** PowerShell for launching and window handling; screenshots through computer-use. WinAppDriver or Playwright for Electron may exist in the project.
- **Electron:** Playwright's `_electron.launch()` can drive the real app if the project already uses it.
- Logs: the dev command's terminal output (Rust/Node side) and the web-view devtools console (Tauri: right click → Inspect in dev builds).

## Host matters

A desktop app can only be exercised natively on its own OS: the macOS build on a Mac, the Windows build on Windows. If the requested OS is not the host, say so, run the web-view part here, and offer the fallbacks in [environments.md](environments.md) (a session on that machine, a Windows VM on the Mac, a user-driven pass); native items stay `blocked (needs <OS>)` until then.

## Code pass – what to grep

- Frontend: same patterns as [web-and-extension.md](web-and-extension.md).
- Tauri: `#[tauri::command]` (every backend action reachable from the UI), `invoke(` calls, `tauri.conf.json` windows, tray (`TrayIconBuilder`, `SystemTray`), menus (`Menu::`, `MenuItem`), global shortcuts (`global_shortcut`, `register(`), deep links (`deep-link` plugin, URL schemes), autostart, notifications, dialogs (`dialog` plugin), clipboard, updater, single-instance.
- Electron: `ipcMain.handle/on`, `Menu.buildFromTemplate`, `Tray`, `globalShortcut.register`, `app.setAsDefaultProtocolClient`, `dialog.show*`, `Notification`, `autoUpdater`.

## Interactions people forget on desktop

- Tray/menu-bar icon: left click, right click, every menu entry, with the main window open, hidden and minimised.
- Global shortcuts while another app has focus; conflicts with system shortcuts.
- Window: resize to minimum and very large, maximise, full screen, multiple monitors, close vs. quit (does the app keep running in the tray?), reopen from dock/taskbar.
- Drag and drop files/text into and out of the app; copy/paste with the system clipboard; right-click context menus.
- Keyboard: every menu accelerator, Tab order, Escape, Enter in dialogs, platform differences (Cmd vs. Ctrl).
- App lifecycle: first launch (no data, onboarding), second instance launch, autostart, sleep/wake, update prompt (do not install updates without asking).
- System theme switch, scaling (125 %/150 % on Windows), right-to-left or other locales if supported.
- Companion connections (browser extension, phone): connected, disconnected, reconnecting — never unpair real devices without asking.
