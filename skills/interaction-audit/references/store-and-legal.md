# Store and legal readiness

Store reviews reject apps for a short, predictable list of reasons, and most of them are visible in the running app. Check these whenever the audit runs before a release or the user mentions a store submission. This is not legal advice: flag gaps, don't decide what the law requires.

## In-app requirements (all stores)

- **Account deletion:** if the app lets users create an account, it lets them delete it from inside the app (Apple requires this; Google requires an in-app path and a web link). Find the path, open it, screenshot the confirmation — then cancel unless it's a test account.
- **Restore purchases:** visible wherever paid features are sold (Apple); subscriptions show price, period, renewal terms and a link to manage/cancel.
- **Sign in with Apple** offered if other third-party sign-ins are (iOS, with the documented exceptions).
- **Permission prompts:** every system prompt appears only when the feature is used (not all at launch), and its purpose text (`NS*UsageDescription`, Android rationale dialogs) explains concretely why, in every shipped language. Denying keeps the app usable.
- **Privacy:** privacy policy link reachable in the app (and in the store listing), tracking prompt (ATT) before any tracking on iOS, consent banner on the web where the site needs one, data actually collected matches the store privacy labels / data-safety form as far as the app shows it.
- **Legal pages:** imprint / legal notice where required (e.g. Germany, Austria), terms of use, open-source licences screen listing bundled libraries, support/contact link, version number visible.
- **Content:** no placeholder text or images, no "beta", "test" or debug menus in a release build, no references to other platforms ("available on Android") in an Apple build, no broken or dead links (open every external link once), age-rating-relevant content matches the rating.
- **Stability basics:** no crash on launch on the oldest supported OS, works on iPad if the binary is universal, works offline or explains it needs a connection, IPv6-only network friendly (reviewers' networks).
- **Metadata match:** the screenshots and description in the store listing show features that exist in this build.

## Browser extension stores

- Every requested permission and host permission is used and justified; no remote code; the popup/options work on the store's review browser version; privacy policy link if any user data is handled; single clear purpose.

## Desktop distribution

- Signed and notarised (macOS) / signed installer (Windows, SmartScreen), uninstall leaves no broken autostart entries, update channel works, licence/EULA shown where required.

## Recording

Put these as a `Store & legal` section in the checklist with the store each item applies to, e.g. `L-03 Restore purchases visible on paywall [App Store]`. Items that need the store console or a lawyer go to the report as `needs owner check`.
