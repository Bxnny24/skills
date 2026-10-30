# Design language: find it, then audit against it

"Looks fine" is not a standard. Before judging layout, spacing or motion, find out which design language the app follows and write it down as a **design profile**; every design finding then cites the rule or value it breaks. An app can follow several layers at once — the platform's system language plus its own design system on top — and the profile records both.

## 1. Find the design language

Look in this order and note the source of every value:

1. **The project's own design sources:** design docs (`DESIGN.md`, `docs/design*`, brand guidelines, a style guide), design tokens (`tokens.json`, Style Dictionary, CSS custom properties, Tailwind `theme`, SwiftUI/Compose theme files, asset-catalog colours, `res/values/{colors,dimens,styles}.xml`), a component library or Storybook, Figma links in the README or PRs, the project's instructions and memory notes.
2. **The design skills used to build it:** skills installed in the project (`.claude/skills/`, `.agents/skills/`, plugin skills) and in this session's skill list whose names or descriptions concern design, UI, brand or a design system. Check the git log and PR descriptions for mentions of them. A project skill that defines the app's own design system is the primary authority.
3. **The platform's system language** the app targets: Apple Human Interface Guidelines (incl. Liquid Glass on current iOS/macOS), Material Design 3 on Android, Fluent 2 on Windows, platform conventions for web (or the CSS framework in use, e.g. shadcn/ui, Tailwind defaults).
4. **The running app itself:** when nothing is written down, infer the de-facto system from the screens: the spacing values that repeat, corner radii, type sizes and weights, colour palette, materials (blur/glass, solid, elevation shadows), icon set (SF Symbols, Material Symbols, Fluent icons, custom), and motion (spring vs. ease, durations). The most common value wins; deviations from it are candidates.

## 2. Write the design profile

Put it at the top of `checklist.md` (or a `design-profile.md` beside it):

```markdown
## Design profile
- System language: <HIG + Liquid Glass | Material 3 | Fluent 2 | web framework> (source: …)
- App design system: <name / none> (source: tokens file, skill, inferred from screens)
- Rubric skill loaded: <skill name or "none available">
- Spacing scale: 4 · 8 · 12 · 16 · 24 · 32 (source)
- Corner radii: … · Type scale: … · Colours/roles: … · Materials/elevation: …
- Icons: … · Components: native vs. custom (which)
- Motion: durations, curves/springs, which transitions are native, reduced-motion behaviour
- Platform conventions the app deliberately breaks (and why, if documented)
```

## 3. Load a rubric skill instead of re-inventing one

If a design skill is available, load it and use its checklist as the rubric for this pass — it is more complete than anything restated here. Prefer, in this order: the project's own design-system skill → the skill that was used to build the UI → a platform skill (e.g. an Apple HIG reviewer for iOS/macOS, a Material or Fluent one for Android/Windows) → a general UI/UX review skill. Note in the profile which one you used. If none is available, use the platform guidelines' own documentation.

## 4. What to check on every screen

- **Spacing and layout:** paddings and gaps come from the spacing scale; alignment to a consistent grid and margins; equal spacing between equal elements; layout matches the platform (navigation bars, tab bars, sidebars, toolbars where the platform puts them).
- **Typography:** only styles from the type scale (iOS text styles, Material type roles, the app's tokens); consistent weights; hierarchy clear.
- **Colour and materials:** colours from tokens/semantic roles, no stray hard-coded values; materials used consistently (glass where the system uses glass, no glass on glass, elevation levels consistent); dark mode uses the dark variants of the same roles.
- **Shape:** corner radii from the scale, concentric corners inside rounded containers, consistent borders.
- **Components:** native controls where the language expects them; custom components look and behave like their siblings everywhere; states (pressed, disabled, focused, selected) styled consistently.
- **Iconography:** one icon set, consistent weight and size relative to text, filled vs. outline used by rule.
- **Motion:** durations and curves match the profile (e.g. iOS springs, Material easing and duration tokens); transitions are the platform's native ones unless the design system says otherwise; similar actions animate the same way; nothing animates that the language keeps static; reduced motion respected; haptics consistent with the platform.
- **Writing:** labels follow the language's tone and capitalisation rules (title case vs. sentence case), consistent terms for the same thing on every screen, no typos or grammar errors (read every visible string once per language; also grep the string files — `Localizable.xcstrings`, `strings.xml`, i18n JSON — for typos, since some strings only appear in rare states), consistent punctuation (ellipsis for actions that need more input, no trailing full stops on buttons).

How to measure: web and web views — read computed styles (`getComputedStyle`) with `javascript_tool` for inspection and compare with the tokens; native — compare zoomed screenshots at a known scale (pt/dp = px ÷ scale factor) and use the code as a hint (grep for literal numbers in `.padding(`, `dp`, `px`, hex colours, custom animation durations); motion — record a video and compare against the profile.

## 5. Findings and fixes

Design findings use category `design` and state: element, the profile rule or token it should follow (with source), what it does instead, screenshot or video. Group repeated deviations (same wrong spacing on 12 screens) into one finding with all locations.

Only change code when the user asks for fixes. Then: use the tokens and components from the profile (never invent new values), follow the rubric skill, keep the change minimal, and prove it with before/after screenshots on the same device and size.
