# Visual check for every screenshot

Run this check on every screenshot you take, not only when something looks off — clipping is easy to miss at a glance. Zoom into edges, corners and dense areas (`zoom` action of the screenshot tools, or crop) instead of judging the whole screen at thumbnail size. Repeat it in every size, text size, language and theme the audit covers, because most of these bugs only appear there.

## Text
- Cut off at the edge of its container, or clipped vertically (descenders like g/y, accents on capitals, second line half visible).
- Ellipsis ("…") that hides the information the user needs (names that differ only at the end, prices, dates); a tooltip or detail view to read the full text.
- Text overflowing its container, overlapping other text or icons, running under buttons or badges.
- Wrapping badly: single word on the last line, hyphenation breaking words wrongly, button labels on two lines.
- Wrong font, weight or size compared with similar elements; placeholder or developer text (`Lorem`, `TODO`, keys like `settings.title`).

## Images, icons and media
- Missing or broken image (empty box, broken-image icon, endless placeholder/skeleton).
- Stretched or squashed (wrong aspect ratio), cropped so the subject is cut off, blurry or pixelated (low resolution on Retina/xxxhdpi, upscaled thumbnails).
- Icons misaligned with their label, inconsistent sizes, wrong tint in dark mode, invisible on the background.
- Video/animation thumbnails, avatars and app icons with wrong masks or corners.

## Containers and layout
- Content clipped by a parent: cards, cells, sheets, popovers, dialogs, menus cut off at the screen or window edge, shadows and rounded corners chopped off.
- Elements overlapping (z-order wrong), floating buttons covering the last list item or a text field.
- Content under system UI: notch / Dynamic Island, status bar, home indicator, Android navigation bar, keyboard, macOS menu bar, Windows taskbar. Safe areas respected in portrait **and** landscape.
- Unwanted scrolling: horizontal scroll on a page that should fit, a scroll view that can't reach its last item, nested scroll fighting.
- Misalignment and inconsistent spacing between similar elements; empty gaps where hidden content left its space; layout jumping when data loads.
- Controls pushed off-screen or below the fold with no way to scroll there; touch targets smaller than 44 pt / 48 dp or overlapping each other.

## Colour and theme
- Text or icons with too little contrast (especially in dark mode, on images, on disabled states).
- Hard-coded colours that don't switch with the theme (white boxes in dark mode, black text on dark backgrounds).
- Focus rings, selection highlights and pressed states visible.

## Tool support to catch it
- **Web / web views:** inspect with `javascript_tool` (inspection only): elements where `scrollWidth > clientWidth` or `scrollHeight > clientHeight` with `overflow: hidden` (clipped text), `document.documentElement.scrollWidth > innerWidth` (horizontal overflow), `img` with `naturalWidth === 0` (broken) or a natural size smaller than the rendered size × `devicePixelRatio` (blurry), elements whose bounding box lies outside their clipping parent.
- **iOS:** Xcode Accessibility Inspector audit (clipped text, contrast, small targets); the view debugger for overlapping views in a debug build.
- **Android:** `uiautomator dump` bounds that extend beyond the parent or the screen; Accessibility Scanner (contrast, target size, clipped text); Layout Inspector in a debug build.
- **Desktop:** zoomed screenshots at every scaling level; the web-view checks above for Tauri/Electron.
