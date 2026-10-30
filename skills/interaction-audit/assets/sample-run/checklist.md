# Sample app – desktop (browser build)

Device/OS: Chrome 141, 1440×900 · State: Pro licence, 12 sample clips · Versions covered: newest
Legend: Prio A critical · B core flow · C other screens · D polish

## S01 Library
| ID | Interaction | Expected | Result | Proof |
|---|---|---|---|---|
| S01-01 | B Click "New clip" | Editor opens with empty clip | ok | screenshots/S01-01-add.svg |
| S02-04 | B Ctrl-click a second clip | Both clips selected | problem → F-001 | screenshots/S02-04-ctrl-click.svg |
| S02-05 | C Right-click a clip | Context menu with Copy, Pin, Delete | ok | |

## S03 Popup
| ID | Interaction | Expected | Result | Proof |
|---|---|---|---|---|
| S03-01 | C Open a clip for editing | Footer shows "14 clips" | problem → F-002 | screenshots/S03-01-counter.svg |
| S03-02 | B Global shortcut Ctrl+Shift+V in another app | Popup opens over that app | blocked (only in the real app) | |

## S05 Settings
| ID | Interaction | Expected | Result | Proof |
|---|---|---|---|---|
| S05-02 | A Click "Reset all shortcuts" | Asks first or offers undo | problem → F-003 | screenshots/S05-02-reset.svg |
| S07-03 | D Open language picker | Languages in their own names | problem → F-004 | screenshots/S07-03-language.svg |
| S07-04 | C Paste into another program | Clip arrives in Notepad | not reachable (browser build has no system paste) | |
