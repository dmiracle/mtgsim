"""17Lands personal data client.

Authenticates with the 17Lands website and downloads the user's personal
event history, draft picks, and game data.

IMPORTANT: This client is deliberately slow and respectful:
- 5 second delay between requests by default
- Session cookie auth (no token scraping)
- Incremental sync (only fetches new events)
"""

import json
import logging
import time

import httpx
from sqlmodel import select

from mtgdb.config import SEVENTEENLANDS_DIR, ensure_dirs
from mtgdb.models import User17LEvent
from mtgdb.session import get_session

logger = logging.getLogger(__name__)

BASE_URL = "https://www.17lands.com"
REQUEST_DELAY = 5.0  # seconds between requests
USER_AGENT = "mtgsim/1.0 (personal data sync; respectful client)"

# Local file to store session cookies (not committed to git)
COOKIE_FILE = SEVENTEENLANDS_DIR / ".session_cookies.json"


class SeventeenLandsClient:
    """Client for 17Lands personal data API."""

    def __init__(self, delay: float = REQUEST_DELAY):
        self.delay = delay
        self._client = httpx.Client(
            base_url=BASE_URL,
            follow_redirects=True,
            timeout=30,
            headers={"User-Agent": USER_AGENT},
        )
        self._last_request_at = 0.0
        self._load_cookies()

    def _load_cookies(self):
        """Load saved session cookies if they exist."""
        if COOKIE_FILE.exists():
            try:
                data = json.loads(COOKIE_FILE.read_text())
                for name, value in data.items():
                    self._client.cookies.set(name, value)
                logger.debug("Loaded saved session cookies")
            except (json.JSONDecodeError, KeyError):
                logger.debug("Could not load saved cookies")

    def _save_cookies(self):
        """Persist session cookies to disk."""
        ensure_dirs()
        cookies = dict(self._client.cookies.items())
        COOKIE_FILE.write_text(json.dumps(cookies))

    def _throttle(self):
        """Wait between requests to be respectful."""
        elapsed = time.time() - self._last_request_at
        if elapsed < self.delay:
            wait = self.delay - elapsed
            logger.debug(f"Throttling: waiting {wait:.1f}s")
            time.sleep(wait)
        self._last_request_at = time.time()

    def _get(self, path: str, params: dict | None = None) -> dict:
        """Make a throttled GET request."""
        self._throttle()
        logger.debug(f"GET {path} params={params}")
        resp = self._client.get(path, params=params)
        resp.raise_for_status()
        return resp.json()

    def login(self, email: str, password: str) -> bool:
        """Authenticate with 17Lands. Returns True on success."""
        logger.info("Logging in to 17Lands...")
        self._throttle()
        resp = self._client.post(
            "/login",
            json={"email": email, "password": password, "remember_me": True},
        )
        if resp.status_code == 200:
            self._save_cookies()
            logger.info("Login successful")
            return True
        logger.error(f"Login failed: {resp.status_code} {resp.text}")
        return False

    def is_authenticated(self) -> bool:
        """Check if current session is valid."""
        try:
            self._throttle()
            resp = self._client.get("/api/readonly")
            return resp.status_code == 200 and not resp.json()
        except Exception:
            return False

    def get_account(self) -> dict:
        """Get account info including sharing token."""
        return self._get("/api/account")

    def get_event_history(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        expansion: str | None = None,
        event_format: str | None = None,
    ) -> dict:
        """Fetch personal event history list.

        Returns dict with events list and pagination token.
        """
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if expansion:
            params["expansion"] = expansion
        if event_format:
            params["format"] = event_format

        return self._get("/user/data", params=params)

    def get_event_details(self, draft_id: str) -> dict:
        """Fetch detailed event data (picks, deck, games)."""
        return self._get("/data/event_details", params={"draft_id": draft_id})

    def get_event_preview(self, draft_id: str) -> dict:
        """Fetch event preview (deck composition, pool)."""
        return self._get("/data/event_preview", params={"draft_id": draft_id})

    def get_draft_picks(self, draft_id: str) -> dict:
        """Fetch draft picks for an event."""
        return self._get("/api/draft_picks", params={"draft_id": draft_id})

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def sync_personal_events(
    email: str,
    password: str,
    start_date: str | None = None,
    end_date: str | None = None,
    expansion: str | None = None,
    event_format: str | None = None,
    fetch_details: bool = True,
    delay: float = REQUEST_DELAY,
) -> int:
    """Sync personal 17Lands event data to the database.

    Fetches event history, then for each new event fetches details.
    Only syncs events not already in the database (incremental).

    Returns count of new events synced.
    """
    ensure_dirs()

    with SeventeenLandsClient(delay=delay) as client:
        # Try existing session first
        if not client.is_authenticated():
            if not client.login(email, password):
                raise RuntimeError("Failed to authenticate with 17Lands")

        # Fetch event history
        logger.info("Fetching event history...")
        history = client.get_event_history(
            start_date=start_date,
            end_date=end_date,
            expansion=expansion,
            event_format=event_format,
        )

        events = history.get("events", [])
        logger.info(f"Found {len(events)} events in history")

        if not events:
            return 0

        # Check which events are already synced
        with get_session() as session:
            existing_ids = set(session.exec(select(User17LEvent.draft_id)).all())

        new_events = [e for e in events if e.get("draft_id") not in existing_ids]
        logger.info(f"{len(new_events)} new events to sync ({len(existing_ids)} already synced)")

        synced = 0
        for i, event in enumerate(new_events):
            draft_id = event.get("draft_id")
            if not draft_id:
                continue

            logger.info(f"Syncing event {i + 1}/{len(new_events)}: {draft_id}")

            event_details = {}
            draft_details = {}
            deck_details = {}

            if fetch_details:
                try:
                    details = client.get_event_details(draft_id)
                    event_details = details.get("details", {})
                except Exception as e:
                    logger.warning(f"Could not fetch details for {draft_id}: {e}")

                try:
                    preview = client.get_event_preview(draft_id)
                    deck_details = preview
                except Exception as e:
                    logger.warning(f"Could not fetch preview for {draft_id}: {e}")

                try:
                    picks = client.get_draft_picks(draft_id)
                    draft_details = picks
                except Exception as e:
                    logger.warning(f"Could not fetch picks for {draft_id}: {e}")

            record = User17LEvent(
                draft_id=draft_id,
                expansion=event.get("expansion"),
                event_type=event.get("event_type"),
                start_time=event.get("start_time"),
                end_time=event.get("end_time"),
                entry_fee=event.get("entry_fee"),
                wins=event.get("wins"),
                losses=event.get("losses"),
                rank=event.get("rank"),
                deck_colors=event.get("deck_colors"),
                deck_index=event.get("deck_index"),
                event_data=event,
                draft_data=draft_details,
                deck_data=deck_details,
                game_data=event_details,
            )

            with get_session() as session:
                session.add(record)
                session.commit()

            synced += 1
            logger.info(
                f"  Saved: {event.get('expansion', '?')} {event.get('event_type', '?')} "
                f"({event.get('wins', '?')}-{event.get('losses', '?')})"
            )

    logger.info(f"Sync complete: {synced} new events")
    return synced
