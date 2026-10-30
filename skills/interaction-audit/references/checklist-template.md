# Checklist and findings templates

## checklist.md

```markdown
# <App> – interaction walkthrough (<platform>, <device/OS>, <build or commit>)

Started: <date time> · Status: in progress | done
Device/OS: <device, OS version> · State: <plan/account/flags for the full pass> · Versions covered: <newest, oldest>
Legend: P1 core flow, money or data · P2 other screens · P3 variations ·
ok · problem (→ F-ID) · blocked · skipped (destructive) · asked · not reachable

## Coverage
| Screen | Items | ok | problem | blocked | skipped | not reachable |
|---|---|---|---|---|---|---|

## S01 <Screen name> (source: <file path>)
| ID | Interaction | Expected | Result | Proof |
|---|---|---|---|---|
| S01-01 | P1 Tap "Add" button | Editor sheet opens | ok | screenshots/S01-01-add.png |
| S01-02 | Long press a row | Context menu with Copy, Pin, Delete | problem → F-003 | screenshots/S01-02-hold.png |
| S01-03 | Swipe row left → Delete | Confirmation, then row removed | skipped (destructive, real data) | screenshots/S01-03-confirm.png |

## X Cross-cutting
| ID | Variation | Screens checked | Result | Proof |
|---|---|---|---|---|
| X-01 | Dark mode | all | ok | screenshots/X-01-*.png |
| X-02 | Largest text size | S01–S05 | problem → F-004 | … |
| X-03 | Offline / peer unreachable | sync, settings | … | … |
| X-04 | Smallest size (iPhone SE) | all | … | … |
| X-05 | Tablet landscape (iPad) | all | not supported | – |

## Found in code but not on screen
- <file:line> – <what> – <why not reachable>
```

## findings.md

```markdown
# Findings

## F-001 <short title>
- Severity: critical (crash, data loss, core flow blocked) | high (major feature broken) | medium (friction, workaround exists) | low (polish)
- Category: crash · dead control · wrong text · layout · animation · state · feedback · accessibility · design · performance
- Where: <screen>, item <ID>
- Start state: <e.g. fresh install, 3 clips, offline>
- Steps:
  1. …
  2. …
- Expected: …
- Actual: …
- Why it matters: <who runs into it and what it costs them>
- Group: A fix · B decide · C leave
- Proposed fix (A) / Options (B): …
- Proof: screenshots/F-001-1.png, screenshots/F-001-2.png; log lines: …
- Notes: suspected source <file:line> (only as a hint, the finding stands on observed behaviour)
```
