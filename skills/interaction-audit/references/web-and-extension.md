# Web apps and browser extensions

## Tools

- **Built-in browser** (`mcp__Claude_Browser__*`): default for local dev servers (`preview_start` with a `.claude/launch.json` name) and public sites. `read_page` (accessibility tree with refs) for inventory, `find` + `computer` (click/hover/drag/key) and `form_input` to act, `read_console_messages` and `read_network_requests` after each item, `resize_window` (mobile/tablet/desktop, `colorScheme` dark/light), `computer screenshot` for proof.
- **Claude in Chrome** (`mcp__claude-in-chrome__*`): the user's real Chrome. Needed for **browser extensions** (popup, options page, content scripts on real pages, context-menu entries, keyboard commands) because the built-in browser does not load the user's extensions. Use it only when the user agrees; never act on their logged-in accounts beyond the test.
- **Playwright**: if the project already has Playwright set up, a scripted crawl can drive repeatable parts and capture traces; the manual pass still covers what scripts don't.

## Code pass – what to grep

- Routes/pages: router config (`createBrowserRouter`, `routes`, file-based `pages/` or `app/` folders, `<Route`).
- Controls: `<button`, `onClick`, `role="button"`, `<a href`, `<form`/`onSubmit`, `<input`, `<select`, `<textarea`, `contenteditable`, `onContextMenu`, `draggable`/`onDrop`, `onKeyDown` / hotkey libraries, `dialog`, `popover`, toasts.
- States: loading/skeleton components, empty-state components, error boundaries, 404 pages.
- Extension (`manifest.json`): `action.default_popup`, `options_page`/`options_ui`, `side_panel`, `content_scripts` (+ `matches`), `commands` (keyboard shortcuts), `contextMenus.create`, `permissions`/`host_permissions`, `background` service worker messages, `externally_connectable`, native messaging hosts.

## Interactions people forget on the web

- Keyboard only: Tab order, visible focus, Enter/Space on custom buttons, Escape closes dialogs, shortcuts.
- Hover-only UI (tooltips, hover menus) — also reachable by keyboard/touch?
- Browser back/forward and reload on every route; deep links opened directly; invalid URLs.
- Viewport sizes (phone, tablet, wide), dark mode, 200 % zoom.
- Network: offline (DevTools or stopping the backend), slow responses, failed requests and their error UI.
- Forms: empty submit, too long input, special characters, paste, double submit. Do not submit forms that send data outward (contact forms, sign-ups, payments) unless approved up front.
- Extensions: popup opened on a normal page, on a restricted page (`chrome://`, store pages), with no network; content script on several sites; extension reload while a page is open; the connection to a companion app missing (app closed / not paired).
