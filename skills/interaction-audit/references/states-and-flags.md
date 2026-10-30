# User roles, plans, account states and feature flags

The same screen can look and behave completely differently depending on who is signed in, what they paid for and which flags are on. An audit that only ever runs as one user in one plan misses the paywall that never appears, the Pro button that is still clickable after expiry, or the screen that crashes when a flag is off.

## 1. Find every state the app knows

Grep the code and config for the switches that change the UI, and list them in the checklist header as a **state matrix**:

- **Plans and licences:** free / trial / paid tiers, trial expiring soon, expired, cancelled but still active until period end, refunded, grace period, payment failed, family/team seat, lifetime licence, licence activated on too many devices, offline licence (cached, cache expired, clock moved back), licence server unreachable.
- **Account states:** signed out, signed in, new account (no data), long-time account (lots of data), email unverified, session expired, password changed elsewhere, account deleted elsewhere, banned/locked.
- **Roles and permissions:** viewer / editor / admin / owner, shared vs. own items, child or managed (MDM) accounts.
- **Feature flags and remote config:** every flag (`isEnabled(`, `featureFlag`, `RemoteConfig`, LaunchDarkly, Statsig, Unleash, env/build flags such as `#if BETA`), A/B variants, kill switches, minimum-version / forced-update prompts, maintenance mode.
- **Build variants:** debug / beta / release, store vs. direct download, region-specific builds.

## 2. Get into each state safely

Use only test accounts, sandbox purchases and local overrides — never real customer accounts or real payments.

- Prefer the app's own debug switches (debug menu, launch arguments, environment variables, a local mock of the licence or flag service, `UserDefaults`/`SharedPreferences`/`localStorage` overrides in a dev build).
- Sandbox purchases: StoreKit configuration files / sandbox testers (iOS), license testers and test cards (Google Play), the payment provider's test mode on the web.
- Time-based states (trial ending, expiry, grace period): move the clock forward on a simulator or test device, or use the server's test hooks — and move it back afterwards.
- If a state can't be reached without production access or a real purchase, mark it `blocked (needs …)` and ask.

## 3. What to check per state

Don't repeat the full audit for every state. Run the full audit in the most common state (typically the paid or main plan), then for every other state revisit every screen whose content depends on it and check:

- The right things are visible, hidden, locked or upsold — and locked features can't be reached another way (deep link, shortcut, keyboard shortcut, widget, extension, old cached screen).
- Transitions while the app is open: trial expires, licence is revoked, a flag flips via remote config, the user upgrades or downgrades — the UI updates without a restart, nothing crashes, no data is lost or hidden permanently.
- Downgrade keeps the user's data readable (or explains clearly what happens).
- Messaging is correct: plan names, prices, dates, remaining days, renewal text, restore-purchase entry point.
- Every combination of flags that ships together: at minimum all flags at their release defaults, each flag individually flipped, and all new flags off (rollback case).

Record results in the checklist as `S04-02 [trial-expired]`, so it's clear which state an item was exercised in.
