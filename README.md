# Glow Stack — iPhone-friendly update

A standalone, offline-capable falling-block game with a black/deep-blue neon design, a large playfield, and iPhone-friendly touch controls. No build system or external scripts are required.

## What's fixed in this version

- Automatically fits the entire game, controls, and iPhone safe areas on small and large screens.
- Prevents accidental double-tap zoom, Safari text selection, highlights, and the long-press callout during gameplay.
- Play directly on the board: **tap to rotate**, **drag horizontally to move**, **drag down to move down**, **swipe up to rotate**, or **flick down quickly for an instant drop**. Buttons are also provided.
- Instant drop now **locks the piece immediately** and spawns the next one immediately. Pieces that settle naturally have a brief (~700 ms) lock delay to allow last-second sideways movement/rotation.
- Clearing a line produces glowing sparks, a sweep/flash, and a visible score bonus. The next piece spawns without waiting for the effect to finish.
- Scores follow the original BPS single/double/triple/quad clear values: **40 / 100 / 300 / 1200**. Scores do **not** multiply by level. Manual drops do not add points.
- Gradual, forgiving gravity increases through level 20; unlimited levels afterward.
- Shows Level, Score, Best; a Hold slot; and the next two pieces.
- Pause/Resume, Restart Level, and Reset to Level 1. Best score stays saved when restarting.
- Local browser saving; automatically imports an existing Glow Stack v1/v2 save if present on the same browser and site address.

## Publish an update to your GitHub Pages site

1. **Extract** the ZIP first. Do not upload the ZIP itself as a site file.
2. In your **Glow Stack game repository** (not the health app repository), open the root/main branch and upload these three files, replacing `index.html` and `README.md` if prompted: `index.html`, `README.md`, `.nojekyll`.
3. Commit the changes. GitHub Pages normally republish automatically. If Pages is not enabled, go to **Settings → Pages → Deploy from a branch → main → /(root)**.
4. On your iPhone, reopen or refresh your existing game URL. If an older page is still cached, close the Home Screen app/Safari tab and reopen it, or use a private Safari tab to confirm the new deployment.

## Keyboard controls

Left/right arrows move; up or X rotates; Z rotates the opposite way; down soft-drops; Space instantly locks; C or Shift holds; P pauses.

## Storage and privacy

This is a separate game, not an extension of your health app. Best score and play progress are stored only in the current browser's `localStorage`, not the cloud. Clearing Safari website data can remove locally saved game progress.
