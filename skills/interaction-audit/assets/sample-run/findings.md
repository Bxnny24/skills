# Findings

## F-001 Ctrl-click keeps only the last clip selected
- Prio: B
- Severity: high
- Category: state
- Where: Main window › Library › Clip list, item S02-04
- Start state: library with 12 clips, nothing selected
- Steps:
  1. Click a clip
  2. Hold Ctrl and click a second clip
- Expected: both clips selected, like in Explorer or Finder
- Actual: only the second clip stays selected
- Why it matters: deleting or moving several clips only works through the small checkboxes
- Group: fix
- Fix / Options (for decide): keep the selection on Ctrl-click, Shift-click selects a range
- Proof: screenshots/S02-04-ctrl-click.svg

## F-002 Clip counter cut off while editing
- Prio: C
- Category: layout
- Where: Popup › Footer › Clip counter, item S03-01
- Steps:
  1. Open the popup
  2. Open any clip for editing
- Expected: footer shows "14 clips"
- Actual: footer shows "14…"
- Why it matters: the count is unreadable exactly when you need it
- Group: fix
- Fix / Options (for decide): let the counter take the space of the hidden search hint
- Proof: screenshots/S03-01-counter.svg

## F-003 Reset all shortcuts without asking
- Prio: A
- Category: feedback
- Where: Settings › Shortcuts › Reset all shortcuts, item S05-02
- Steps:
  1. Open Settings › Shortcuts
  2. Click "Reset all shortcuts"
- Expected: a confirmation or an undo option
- Actual: all custom shortcuts are gone immediately
- Why it matters: one misclick and there is no way back
- Group: decide
- Fix / Options (for decide): a) confirmation dialog · b) undo toast for 10 s · c) leave it
- Proof: screenshots/S05-02-reset.svg

## F-004 Language picker shows "German" instead of "Deutsch"
- Prio: D
- Category: wrong text
- Where: Settings › General › Language
- Why it matters: common convention, mostly taste
- Group: leave
- Proof: screenshots/S07-03-language.svg
