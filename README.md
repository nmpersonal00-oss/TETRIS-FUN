# Glow Stack

A standalone falling-block puzzle game with a dark, neon-blue design.

## Features

- Level, Score, and Best displays
- Preview of the next two pieces and a Hold/Swap control
- Keyboard and touch controls
- Pause, Restart Level, and Reset to Level 1
- Gentle speed increases through level 20 and unlimited levels
- Lock delay to adjust pieces briefly after landing
- Local browser saving for the current game and best score

## Publish on GitHub Pages

1. Create a **new** GitHub repository for this game (for example, `glow-stack`). Do **not** replace the `index.html` in your existing health app repository.
2. Extract the ZIP file before uploading. Upload `index.html`, `README.md`, and `.nojekyll` to the root of the new repository, then commit the files.
3. Go to **Settings → Pages**, select **Deploy from a branch**, then choose **main** and **/(root)**. Save.
4. GitHub Pages will provide your game URL (typically `https://YOUR-USERNAME.github.io/glow-stack/`).

You can also open `index.html` directly on a computer to play. No build steps or external libraries are required.

**Note:** Game progress is saved locally in the browser using localStorage, not in a cloud account. Use the same browser and site URL to retain saved progress.
