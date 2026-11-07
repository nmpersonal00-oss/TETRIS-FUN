# Glow Stack — touch-first Home Screen game

Glow Stack is a neon 10×20 falling-block puzzle. This version is a **full-screen, touch-focused redesign** inspired by the clean proportions in the supplied mobile-game reference. Its own LED/neon colors, particles, scoring, progression and existing save keys remain intact.

## Main screen

- **Level / Score / Best / Next** share one compact top strip. Tap **Level** to open the pause-and-options menu.
- The game board stretches nearly edge to edge and uses almost all remaining vertical space. Its display is slightly wider (1:1.86 rather than 1:2), but the game still contains the original 10 columns and 20 rows. There is **no bottom control strip**.
- **Hold** is a little taller (57–64px depending on screen size) to use the remaining bottom space, without changing the board, game text, piece animations or gameplay. The held tetromino remains brightly visible. You can swap once per falling piece.
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
3. **Leaderboard** — shared online ranking featuring a neon trophy and, for each player, **username, highest-ever score, and current level**. Scores determine first and second place.
4. **Challenges** — shows both players' current levels and best scores as a progress comparison, with future challenge activities still marked "coming soon".

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


## Live couple leaderboard (Supabase)

The leaderboard uses the existing **Wifey & Hubby** Supabase project, in its new and separate `public.glow_stack_leaderboard` table. The existing project tables are untouched. The table has Row Level Security, unique case-insensitive usernames, and a database trigger preventing a player's highest score from decreasing.

**One-time dashboard setting required:** In [Wifey & Hubby → Authentication → Sign In / Providers](https://supabase.com/dashboard/project/gtcybnvjdcmuzegxwiic/auth/providers), **enable Anonymous Sign-Ins** if it is currently off. This lets each phone own an authenticated score record without requiring email/password signup. Neither a service-role key nor a secret API key is shipped in the frontend; it uses only the public publishable key.

### How to start

1. On each phone, open Glow Stack, tap **Level → Leaderboard**.
2. Choose a different player name (2–18 letters/numbers/spaces/underscores/hyphens) and press **Save Name**. **No email address or password is required:** Supabase anonymously identifies each installed copy of the game in the background, provided Anonymous Sign-Ins is enabled.
3. Close the menu and play. As you earn points or advance levels, the app submits your **personal best score** and **current level** to Supabase. The best score never decreases, even after a new run; your current level *does* reset if you restart at Level 1.
4. Open **Leaderboard** to see first and second place ranked by best score, plus both players' levels. Open **Challenges** to compare those same levels and best scores (challenge activities are coming later). While either page is open, online data refreshes approximately every 10 seconds. Higher best scores move a player ahead automatically, with alphabetical order breaking equal scores.

The leaderboard stores the score and current level in `public.glow_stack_leaderboard` (`current_level` has a 1–1,000,000 database constraint). Scores are ranked by `best_score`, not current level. The leaderboard tracks **one player identity per installed app/browser storage profile**. For best results, each person plays on their own phone. Anonymous identities stay on that installed app: if you delete the icon, sign out, or clear storage, the anonymous identity may be unrecoverable even though its score row remains online. Adding recovery with email/password can be done later. Username edits rename only your own player record; a name already claimed by someone else cannot be reused.

The original game's local saved-game keys are unchanged and its local Best display continues to represent the previous device-local record. Online rankings are separate and cannot display while offline, but gameplay still works. Submissions queue a retry for transient offline failures. Since the game score is calculated in the public browser, this is a friendly competition rather than a tamper-proof anti-cheat leaderboard.

### Test coverage

Automated tests cover 11 phone sizes, menu pause/resume, Hold and restart actions, trophy page navigation, plus a mocked Supabase scenario verifying password-free player creation, best-score ranking, current level labels on Leaderboard, and current level comparisons in Challenges. An end-to-end real anonymous-auth test on both physical phones is still recommended once Anonymous Sign-Ins is enabled.
