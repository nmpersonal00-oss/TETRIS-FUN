# Glow Stack — iPhone safe-area visibility (v9)

This is a **layout-only** update for the iPhone version of Glow Stack. The Tetris game logic, side previews, on-screen button positions, touch gestures, and local save keys remain unchanged.

## Layout adjustments

- The Level / Score / Best row now respects `env(safe-area-inset-top)`, so it stays below the Dynamic Island and clock when a Home Screen app renders under the iPhone status bar.
- Removed the standalone-only CSS rule that overrode the top safe-area padding with just `8px`. An icon installed while an older `black-translucent` status bar was in effect can keep those launch settings even after the site changes.
- Reduced the *minimum* bottom padding from 16px to 8px to avoid adding an unnecessary strip, while still honoring `env(safe-area-inset-bottom)` for the Home indicator.
- Kept the grid and board-fitting logic that reserve space for the six game controls and three action buttons.

## Updating the iPhone game

1. Merge the pull request into `main` and allow GitHub Pages to deploy it.
2. Open the hosted game in Safari and reload to check the new layout.
3. Fully close the installed Home Screen app from the app switcher and open it again to check its layout.
4. **Don't clear Safari website data or delete the installed app just to refresh.** Doing so may erase locally stored progress and best scores. Old Home Screen icons can retain install-time status-bar settings; if only the installed icon remains misaligned, back up any scores you need before considering a fresh Home Screen installation.

## What the web page cannot fix

Some iOS versions show a black/empty band at the physical bottom of standalone Home Screen apps, *outside the viewport exposed to web pages*. The game cannot draw or place buttons in an area iOS doesn't expose. This patch removes excess bottom padding from the page, but cannot guarantee removal of an iOS-managed strip. See [WebKit bug 313800](https://bugs.webkit.org/show_bug.cgi?id=313800).

## Testing

The CSS can be inspected and checked in desktop/mobile emulation, but iPhone Home Screen status-bar behavior must be checked on the actual device; Safari tabs can behave differently from installed icons.
