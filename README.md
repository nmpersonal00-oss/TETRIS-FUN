# Glow Stack — iPhone Full-Screen Fit v6

A standalone neon Tetris-style block game, designed for GitHub Pages. This version addresses the extra blank area BELOW the controls when launched from the iPhone Home Screen. Gameplay and score-saving keys are unchanged.

## Upload

1. Download and extract the ZIP.
2. In your existing **TETRIS-FUN** GitHub repository, upload the included **index.html**, **README.md** and **.nojekyll** to the repository root, replacing the older files.
3. Commit, then open the GitHub Pages site once deployment is finished.
4. On iPhone, fully close the Home Screen game and reopen it. If its layout has not changed, visit the GitHub Pages URL in Safari and reload, then relaunch the Home Screen app. You do not need to clear website data or delete your high scores.

## What changed

- In installed iPhone Home Screen mode, page height is based on the device screen height instead of Safari's often-shorter CSS dynamic viewport.
- In Safari browser tabs, the layout still respects the visible browsing viewport and the browser toolbar.
- The app stays pinned to the TOP of the viewport; no vertical auto-centering.
- The 10-column x 20-row board preserves its proper aspect ratio and the action buttons reserve space for Home indicator safe areas.
- Existing pause, hold, line-clearing effects, scoring, endless levels, and saved progress were not changed.

## Important

The game saves your score and progress in the local browser storage for its website. Updating the same GitHub Pages address preserves that storage; changing the domain or clearing website storage does not. Real device appearance still depends on the exact iOS WebKit version and Home Screen configuration.
