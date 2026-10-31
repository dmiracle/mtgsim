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
```

Start the backend first: `uv run mtgsim-api` from the repo root. Point the dev proxy
elsewhere with `API_URL=http://host:port npm run dev`.

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
