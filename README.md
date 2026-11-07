# Glow Stack — iPhone viewport / Dynamic Island repair (v10)

The game is a single-page falling-block puzzle. This release changes **layout only**; gameplay, scoring, hold, controls, and existing `localStorage` save keys are untouched.

## What we found

- The screenshot showed the Level / Score / Best cards drawn **behind the iPhone status indicators**. The app previously depended on `env(safe-area-inset-top)`, which can incorrectly report `0px` in certain installed iPhone WebKit configurations.
- The screenshot's unusually dark band under the controls matches a separate iOS Home Screen viewport bug: `innerHeight` / `visualViewport.height` can be about one status-bar height less than `screen.height`. **No website can draw into pixels the OS excludes from the web viewport.** Do not try to stretch the game to `screen.height` — that cuts off the controls.
- Apple's documented `black-translucent` mode draws behind the status bar. The source now omits the legacy status-bar-style meta so **new installations** use a system-managed bar; old Home Screen icons may retain their original install-time chrome.

## Layout changes

1. Reserve **at least 64 CSS px at the top** for portrait installed iPhone apps, even when WebKit incorrectly reports a zero top safe-area inset. Normal Safari and landscape are not forced into that clearance. Where iOS already reserves a status-bar area, this conservative rule can produce extra top space; it prioritizes avoiding obscured scores on existing icons.
2. Drive the grid from the smallest usable page viewport measurement (`innerHeight`, `documentElement.clientHeight`, `visualViewport.height`) rather than physical `screen.height`, while respecting the bottom Home-indicator inset.
3. Re-fit the 10×20 board after rotations, page visibility changes and Visual Viewport changes. Both button rows keep their grid space; the game board shrinks when necessary.
4. Removed an inappropriate 70 px minimum board width for exceptionally small viewports.
5. Added optional **`?layout-debug=1`** diagnostic readout; normal gameplay is unchanged. In Safari Web Inspector you can also call `glowStackLayoutReport()` to read screen, viewport, safe-area and shell measurements.

## One-tap calibration for differently installed iPhones

Some iPhones already reserve top status-bar space; older installed icons can instead paint the clock over the game. When the app is installed on the Home Screen in portrait mode, the default is **Protected** (64px top guard) to keep score cards visible. If a newly installed icon instead shows too much empty space above Level / Score / Best, **double-tap the LEVEL score card** to switch to **Compact** spacing. Double-tap LEVEL again to restore **Protected**. A brief label confirms the choice. The preference is stored separately from game scores, and normal game controls do not change.

## Testing

A browser geometry regression test is provided in `tests/test_iphone_layout.py`. Run with Python + Playwright installed and a Chromium browser available:

```bash
python tests/test_iphone_layout.py
```

It covers portrait sizes for iPhone 15 (393×852), 15 Pro Max (430×932) and 16 Pro Max (440×956), plus viewport-shortened versions (height minus approximately 59–62 px), landscape and a narrow-screen case. Browser emulation **cannot reproduce iPhone Home Screen WebKit bugs exactly**. Real-device verification is still required.

## Installing / refreshing safely

1. Merge the pull request into `main` and wait for GitHub Pages to publish.
2. Open the deployed link in Safari and reload it.
3. Fully close the installed game from the app switcher, reopen it, and check the Level / Score / Best row and both control rows.
4. If the old Home Screen icon still uses an overlapping status bar or shows a system-controlled bottom band, compare with a **newly added Home Screen icon**. Do not delete the original icon or clear Safari website data first: these actions can cause loss of stored game progress or best score. An icon added earlier may preserve different status-bar configuration.

WebKit references: [bug 313800](https://bugs.webkit.org/show_bug.cgi?id=313800) (unexposed lower strip); [bug 317153](https://bugs.webkit.org/show_bug.cgi?id=317153) (status-bar installation behavior). Apple: [Supported Meta Tags](https://developer.apple.com/library/archive/documentation/AppleApplications/Reference/SafariHTMLRef/Articles/MetaTags.html).
