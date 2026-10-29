# Glow Stack — iPhone Home Screen layout repair (v8)

This build fixes **the actual installed Home Screen app**. The game itself and its saved-game format are unchanged.

## What changed (layout only)

- Replaced `apple-mobile-web-app-status-bar-style=black-translucent` with `black`. iOS now reserves the status bar instead of trying to draw the game under it. Apple's WebKit developers have deprecated `black-translucent` for Home Screen apps; it has caused reported viewport-height errors.
- Removed the JavaScript calculation that stretched the game to `screen.height` (the source of clipped Restart Level and Level 1 buttons).
- Removed fixed-root sizing; the CSS grid uses the **usable viewport** and allocates the two control rows *before* sizing the board.
- Kept the safe-area padding for the bottom Home indicator, with a minimum margin if iOS reports an inset of zero.
- Kept game mechanics, touch behavior, scoring, animations, saved scores, and pause/restart controls exactly as before.

## Upload to GitHub Pages

1. Extract the ZIP. In your existing `nmpersonal00-oss/TETRIS-FUN` repository, upload `index.html`, `README.md`, and `.nojekyll` to the repository root, replacing existing files.
2. Commit and let Pages redeploy. Force-close Glow Stack from the iPhone app switcher and open the Home Screen icon again.
3. **Do not delete the installed icon or clear its website data to refresh the game**: locally stored game scores can be lost. If the app keeps showing the previous layout, first check the deployed site using Safari as a separate step, then return to the installed app. Reinstall only after backing up any game data you need.

### Why this specific change?

Apple documents that `black` status-bar style displays content **below** the status bar, while `black-translucent` paints content beneath it. WebKit has documented an installed PWA bug where the viewport is shortened by the status-bar height, causing an unreachable bottom strip. Increasing the web page height to match physical `screen.height` pushes the controls outside the app's actual viewport. The fix is to stop using the physical height and let the OS reserve the status bar.

### Testing limitation

Desktop browser tests reproduce layout dimensions and control interaction but **cannot emulate the iPhone's Home Screen WebKit shell precisely**. Please check this version on your iPhones after deploying. The old files remain available in GitHub history for a fast rollback.
