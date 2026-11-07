# Glow Stack — touch-first Home Screen game

Glow Stack is a neon 10×20 falling-block puzzle. This version is a **full-screen, touch-focused redesign** inspired by the clean proportions in the supplied mobile-game reference. Its own LED/neon colors, particles, scoring, progression and existing save keys remain intact.

## Main screen

- **Level / Score / Best / Next** share one compact top strip. Tap **Level** to open the pause-and-options menu.
- The game board stretches nearly edge to edge and uses almost all remaining vertical space. Its display is slightly wider (1:1.86 rather than 1:2), but the game still contains the original 10 columns and 20 rows. There is **no bottom control strip**.
- **Hold** is still a slim, horizontally aligned button directly underneath the board, matching its width. The held tetromino is now rendered at a much larger scale inside a wide high-resolution preview canvas, without making the button taller. You can swap once per falling piece, as before.
- **Next** previews exactly one upcoming piece in the top row; the old right-side rail and second preview are removed.
- Start/Resume remains a button overlay on the game board when the game has not started or is already paused.

## How to play without buttons

- **Drag left or right** anywhere on the board to move your current piece.
- **Tap the board** or **swipe up** to rotate.
- **Drag down** to soft-drop, or **flick down quickly** to hard-drop.
- **Tap Hold** to store or swap the falling piece.
- Keyboard arrow keys, Space, C and P/Escape remain available on desktop.

## Level menu

Tap the **Level** stat. The current game pauses and the menu opens:

1. **Restart Level** — restart the current level from its saved level checkpoint.
2. **Restart at Level 1** — begin a new level-one run.
3. **Challenges** — opens a deliberately empty placeholder page (with Back and X).

Tap **X** to close the options/challenges menu and **automatically resume the game if it was playing before the menu opened**. If you were on the initial Start screen, closing the menu keeps the game ready rather than starting unexpectedly.

## Display behavior

This version **removes the old iPhone-specific 64px JavaScript guard, device detection, manual sizing calibration, synthetic viewport height and button rows**. It uses CSS `100dvh`, `viewport-fit=cover`, and **no CSS `safe-area-inset-*` padding**. The bottom uses only 3px of ordinary padding, reclaiming the previously unused strip inside the page. A fixed 49px top clearance **only in portrait standalone app mode** keeps the score bar clear of the iPhone clock; this is not an iOS safe-area variable or JavaScript viewport lock. The `manifest.webmanifest` declares a standalone app.

**Hardware limitation:** iOS controls the clock/status icons and may reserve a system area outside the webpage. A website cannot hide the iPhone's Dynamic Island or reclaim pixels that the installed web view does not expose, even if a native game can. The dark app background is designed to blend into the system area where supported. Older installed Home Screen icons may retain their original launch-mode settings.

## Testing and deploying

The Playwright test `tests/test_iphone_layout.py` exercises 11 phone geometry configurations including shortened viewports and simulated installed-app top clearance; validates the widened board ratio, bottom padding no greater than 3px, compact header, Hold bar no taller than 54px, and minimum visible held-piece size. It also tests Level pause/resume, Challenges, Hold swapping and restart buttons, and produces screenshots on GitHub Actions.

You can run locally with Python + Playwright/Chromium:

```sh
python tests/test_iphone_layout.py
```

After the new `main` build deploys on GitHub Pages, fully close and reopen the Home Screen game. The saved game keys `glow-stack-save-v3` and `glow-stack-best-v3` have **not** changed. Don't clear website data or delete an existing Home Screen icon just to refresh it: that could erase locally stored scores.

Device emulation is useful but does not replace testing in an installed Home Screen app on an actual iPhone.
