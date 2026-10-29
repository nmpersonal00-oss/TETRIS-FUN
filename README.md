# Glow Stack — iPhone Full-Screen Sizing Fix (v5)

A standalone falling-block game with a dark-blue neon theme, built for mobile Safari and Home Screen play. No dependencies, compilation, or cloud account required.

## Latest v5 adjustment

- Fixed the excessive empty black area at the bottom of some iPhone 15 and 16 Pro Max Home Screen versions. The older app incorrectly chose the shortest of multiple viewport height measurements. v5 uses the actual CSS dynamic screen height (`100dvh`) and retains explicit iPhone safe-area padding, so the board scales into the available space while the buttons remain visible.
- Gameplay, existing scores, controls, hold, infinite levels and animated line clearing are preserved unchanged. Your saved game continues on the same website.

## Improvements

- Rebuilt the screen layout as a four-row responsive grid so the top Level / Score / Best bar, playing field, six movement buttons, and bottom Pause / Restart Level / Level 1 buttons fit within the *usable* phone viewport.
- Allows for iPhone safe areas, status bar, browser viewport resizing, and the Home indicator. Tested in desktop Chromium with iPhone 15 and 16 Pro Max viewport simulations and additional safe-area spacing. Physical Safari testing is recommended.
- Prevents unwanted text selection, tapping highlights, Safari callouts, and game-area double-tap zoom.
- **Restart Level** now works immediately, clears the board, restores the score at the beginning of the current level, and resumes playing. **Level 1** immediately starts a fresh game from zero. Neither erases the personal best.
- **Pause / Resume** works before, during, and after line-clear animations.
- **Line clears** now have a deliberate 760-millisecond sequence: full rows brighten, colored sparks appear, then the remaining blocks descend smoothly. The next playable piece is already prepared and appears after the animation. Ordinary hard drops (without a clear) spawn the next piece immediately.
- Simple scoring: **40 / 100 / 300 / 1200** points for 1 / 2 / 3 / 4 cleared rows. No level multiplier. Soft drops do not add points.
- Gravity starts gently and speeds up gradually through level 20. Levels continue indefinitely beyond 20, with a lower bound on the gravity interval.
- Touch: tap the board to rotate; drag left/right to slide; drag down to lower; swipe up to rotate; flick down quickly to lock instantly. Six large on-screen controls provide the same functions, plus Hold.
- Next two pieces and Hold are always displayed. Hold swaps once per falling piece.
- Best score and game state save locally on the device; existing Glow Stack saves remain compatible.

## Update your existing GitHub Pages game

1. Download and **unzip** `Glow-Stack-iPhone-Full-Screen-v5.zip`.
2. Open your **Glow Stack** GitHub repository, *not* your separate health app repository.
3. Upload `index.html`, `README.md`, and `.nojekyll` into the **repository root**, replacing the older files. Commit the change. **Do not upload the ZIP itself** to GitHub Pages.
4. The existing Pages site updates after the new GitHub Pages deployment finishes. Reopen the game URL on each iPhone. If your Home Screen shortcut still shows the old layout, try the URL in Safari and reload; the shortcut may retain a cached copy.

## Keyboard

Left / Right: slide · Up or X: rotate · Z: rotate other direction · Down: soft drop · Space: hard drop · C or Shift: Hold · P or Esc: pause.

## Storage

Scores and progress are saved in browser local storage, not a cloud account. Clearing Safari site data or using a different browser or website address can remove local progress. The game does not change your existing health app or Supabase data.
