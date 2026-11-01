# MTGSim Mobile — Card Review PWA

A standalone, mobile-first progressive web app for reviewing cards one at a time.
Pick filters (sets, rarity, color identity, mana value, type, name/rules text, format,
your user tags, tier list + tiers, price, ownership, one printing per name), pick an
order (collector #, name, mana value, price, rarity, color, set, tier — plus a
secondary sort and direction), then swipe through the matching cards.

Completely separate from `frontend/` — its own dependencies, no shared packages.

## Commands

```bash
npm install
npm run dev              # http://localhost:5175 (proxies /api to :8001)
npm run build            # typecheck + production build with service worker
npm run preview          # serve the build
npm run storybook        # component stories on :6007
npm test                 # ranking logic tests (node --test)
```

Start the backend first: `uv run mtgsim-api` from the repo root. Point the dev proxy
elsewhere with `API_URL=http://host:port npm run dev`.

## Ranking mode

Separate from review: tap **Rank** on the filter screen, name a ranking, and it is
created from the current filters (one printing per card name, up to 600 cards).

- Each round shows up to 4 cards; tap them best to worst and save. Tap ⤢ on a card
  to open it full-size, swipe left/right through the round's other cards, tap to close. A round is stored as
  every pair it implies (4 cards → 6 "A beats B" comparisons, `POST /api/rankings/{id}/rounds`).
- Next round, in priority order: a **conflict** (the shortest cycle such as A>B>C>A — re-rank
  it to resolve, since the latest result for a pair wins), then **unranked cards** drawn at
  random, then cards whose **relative order is still undetermined** (adjacent cards in the
  current order with no chain of comparisons between them).
- When every adjacent pair is decided the ranking is complete. **Results** shows the
  current order any time, flagging cards in a conflict and ties not yet decided.
- Logic lives in `src/ranking.ts` with tests in `src/ranking.test.ts` (`npm test`).

## Running as a service (launchd)

In production the FastAPI backend serves this app's build (`mobile/dist`) at the site
root, with client-side routes falling back to `index.html`; `/api/*` and `/docs` keep
their usual handlers. One LaunchAgent (`deploy/launchd/com.mtgsim.api.plist`) runs it:
started at login, restarted if it crashes, log in `~/Library/Logs/mtgsim/api.log`.

```bash
just services-install     # build mobile/, install + start the agent
just mobile-deploy        # after frontend changes: rebuild (served immediately)
just services-restart     # after backend changes
just services-status      # running? pid?
just services-logs        # tail the log
just services-uninstall   # stop + remove, and turn off the tailscale serve route
```

The API listens on `127.0.0.1:18001` only (not reachable from the LAN, and `:8001` stays
free for development). `services-install` runs `tailscale serve --bg --https=443
http://127.0.0.1:18001`, which publishes it over HTTPS at
https://dylans-macbook-pro-2.tail4ca9d8.ts.net/ (tailnet only) and persists across restarts. The service runs whatever
is checked out in this working tree. (`vite preview` was tried first but crashed on
dropped client connections.)

## Install on a phone

Open the dev server over Tailscale (e.g. `http://<mac>.tail4ca9d8.ts.net:5175`),
then Share → **Add to Home Screen** (iOS) or **Install app** (Android).
Service workers need a secure context, so offline caching only kicks in on
`localhost` or HTTPS (e.g. `tailscale serve`); the app works without it.

## How it works

- Filters are stored as the literal query params of `GET /api/cards`
  (`src/filters.ts`), so the form state, the review URL, and the API request are the
  same object. The review URL (`/review?sets=TRK&rarity=common&colors=W&sort=number&i=0`)
  is bookmarkable and survives reloads; `i` is the position.
- The review screen loads 100-card pages on demand, prefetches the next page near
  the end of the current one, and preloads the next 3 card images.
- Swipe left/right, use Prev/Next, arrow keys, or drag the position slider.
- **Grading:** pick (or create) a list under "Grade into" on the filter screen. The
  review screen then shows 17Lands-style grades (A+ … F); tapping one saves it and
  advances to the next card, ✕ clears it. Grades are stored as tier-list entries
  (`PUT/DELETE /api/tier-lists/{id}/entries`, keyed by card name), so they show up
  everywhere tier lists do and can be used as a filter/sort ("Tier list" section).
  "Ungraded only" (`not_in_tier_list=<id>`) hides cards already in the grade list, so
  each grade drops the card and the next ungraded one takes its place.
- Card images from Scryfall are cached by the service worker (cache-first, 30 days).
