# Glow Stack — touch-first Home Screen game

Glow Stack is a neon 10×20 falling-block puzzle. This version is a **full-screen, touch-focused redesign** inspired by the clean proportions in the supplied mobile-game reference. Its own LED/neon colors, particles, scoring, progression and existing save keys remain intact.

## Home Screen and Chromebook app icon

The owner-supplied pink/purple glowing block-and-star image is used as the app icon. It keeps the neon rounded ring and original background, with a restrained ~1.5% crop around the outside to make the ring more prominent. The website declares a 180px Apple Home Screen icon, a 32px browser favicon, and 192px and 512px web-app icons for Chromium/ChromeOS. When the artwork source changes, GitHub Actions generates and commits the platform PNGs automatically.

**Important:** The icon update does not alter authentication, your two leaderboard records, or any other Supabase app. Wait until the owner finishes the separate account-cleanup plan before intentionally deleting/reinstalling the two Home Screen apps, since deleting them can lose their anonymous login identities.

## Main screen

- **Level / Score / Best / Next** share one compact top strip. Tap **Level** to open the pause-and-options menu.
- The game board stays at the original **10×20, 1:2 canvas ratio**, so the blocks remain square. It fits the available phone height and is capped at roughly **86% of the usable width** rather than zooming in edge to edge. There is **no bottom control strip**.
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

The app uses CSS `100dvh`, `viewport-fit=cover`, and the browser-provided `env(safe-area-inset-*)` values to position the score strip, game, and Hold button within the usable screen. It **does not add a 76px top band to every installed app**. In particular, standalone Samsung/Android apps receive no iPhone-specific padding.

Some iOS Home Screen versions expose the full physical screen but omit a useful top safe-area inset. A fallback protects the clock/Dynamic Island in that specific iOS full-bleed case. If iOS has already reduced the page viewport for system chrome, that fallback is not applied, avoiding double padding and an oversized gap above the game.

The 300×600 canvas is displayed at its native 1:2 ratio, keeping each of the 10×20 cells square. Its rendered size is limited by both available width (86%) and height, and it automatically refits after orientation and viewport changes. The Hold button remains aligned to the board. Side and bottom padding respect device safe areas, including the iPhone Home indicator.

**Hardware limitation:** iOS controls the clock/status icons and can reserve space outside the webpage; the game cannot reclaim those pixels. This change does not require reinstalling the Home Screen app or clearing saved game data.

## Testing and deploying

The Playwright test `tests/test_iphone_layout.py` exercises iPhone 15/16, Pro Max, compact phones, Samsung devices, installed-app mode, landscape, shortened viewports, iOS pre-inset/full-bleed modes, and dynamic viewport resize. It validates square cells, board/hold alignment, safe-area handling, menus, gestures, and leaderboard mocks. **All Playwright pages block outbound network requests**; tests do not create production anonymous accounts or modify Supabase data. GitHub Actions uploads screenshots for visual inspection.

You can run locally with Python + Playwright/Chromium:

```sh
python tests/test_iphone_layout.py
```

After the new `main` build deploys on GitHub Pages, fully close and reopen the Home Screen game. The saved game keys `glow-stack-save-v3` and `glow-stack-best-v3` have **not** changed. Don't clear website data or delete an existing Home Screen icon just to refresh it: that could erase locally stored scores.

Device emulation is useful but does not replace testing in an installed Home Screen app on an actual iPhone.


## Live couple leaderboard (Supabase)

The leaderboard uses the existing **Wifey & Hubby** Supabase project, in its new and separate `public.glow_stack_leaderboard` table. The existing project tables are untouched. The table has Row Level Security, unique case-insensitive usernames, and a database trigger preventing a player's highest score from decreasing.

**One-time dashboard setting required:** In [Wifey & Hubby → Authentication → Sign In / Providers](https://supabase.com/dashboard/project/gtcybnvjdcmuzegxwiic/auth/providers), **enable Anonymous Sign-Ins and save the setting**. Reload the Providers page to check the switch stayed enabled, then open Leaderboard and tap Save Name again. In November 2026, live Supabase Auth logs for the project recorded `anonymous_provider_disabled` / HTTP 422, indicating the provider was disabled at the time of those attempts.

**CAPTCHA is a separate recommendation**, not a prerequisite merely for switching on anonymous logins. If you decide to enforce CAPTCHA in [Authentication → Protection](https://supabase.com/dashboard/project/gtcybnvjdcmuzegxwiic/auth/protection), this app will first need a CAPTCHA challenge and token integration (such as Cloudflare Turnstile); otherwise anonymous registration will fail with a different error. The game now distinguishes provider-disabled and CAPTCHA-required errors instead of treating all anonymous errors as a disabled provider. This lets each phone own an authenticated score record without requiring email/password signup. Neither a service-role key nor a secret API key is shipped in the frontend; it uses only the public publishable key.

### How to start

1. On each phone, open Glow Stack, tap **Level → Leaderboard**.
2. Choose a different player name (2–18 letters/numbers/spaces/underscores/hyphens) and press **Save Name**. **No email address or password is required:** Supabase creates a fresh anonymous identity **only when you tap Save Name**. After successfully saving, **the username form and Save Name button disappear** and the game shows **REGISTERED AS: YourName**. Opening Leaderboard or Challenges later reuses the saved identity instead of creating a second account. Anonymous Sign-Ins must remain enabled in Supabase.
3. Close the menu and play. As you earn points or advance levels, the app submits your **personal best score** and **current level** to Supabase. The best score never decreases, even after a new run; your current level *does* reset if you restart at Level 1.
4. Open **Leaderboard** to see first and second place ranked by best score, plus both players' levels. Open **Challenges** to compare those same levels and best scores (challenge activities are coming later). While either page is open, online data refreshes approximately every 10 seconds. Higher best scores move a player ahead automatically, with alphabetical order breaking equal scores.

The leaderboard stores the score and current level in `public.glow_stack_leaderboard` (`current_level` has a 1–1,000,000 database constraint). Scores are ranked by `best_score`, not current level. The leaderboard tracks **one player identity per installed app/browser storage profile**. For best results, each person plays on their own phone. Anonymous identities stay on that installed app: if you delete the icon, sign out, or clear storage, the anonymous identity may be unrecoverable even though its score row remains online. Adding recovery with email/password can be done later. Username edits rename only your own player record; a name already claimed by someone else cannot be reused.

The original game's local saved-game keys are unchanged. When you register a name, the app now **imports your existing local Best score** into Supabase, including scores achieved before signing up. On subsequent opens it reconciles stored and online bests in both directions using the higher value, so the Best tile and leaderboard agree. The online database trigger prevents lower scores from replacing a personal best. Current Score still displays the active run separately, and restarting at Level 1 does not reduce Best.

Online rankings cannot display while offline, but gameplay still works. Submissions queue a retry for transient offline failures. Since the game score is calculated in the public browser, this is a friendly competition rather than a tamper-proof anti-cheat leaderboard. **The game is publicly accessible:** while anonymous sign-in is enabled, a visitor who chooses a username can still create an account. The app reduces unnecessary sign-ups but does not enforce an invitation-only/two-account limit.

### Test coverage

Automated tests cover a range of iPhone and Samsung screen sizes and safe-area scenarios, menu pause/resume, Hold and restart actions, trophy page navigation, and mocked Supabase scenarios verifying password-free registration, old local Best import on first username save, a 120-point online record increasing to the previous 4,960 local record, survival of restarts, best-score ranking, current levels and Challenges. An end-to-end real anonymous-auth test on both physical phones is still recommended once Anonymous Sign-Ins is enabled.
