"""17Lands public dataset sync: fetch index from Prismic, download CSV files."""

import logging
from datetime import UTC, datetime
from pathlib import Path

import requests
from sqlmodel import select

from mtgdb.config import PRISMIC_API_URL, SEVENTEENLANDS_DIR
from mtgdb.models import MJ17LDataset
from mtgdb.session import get_session
from mtgdb.sync.download import download

logger = logging.getLogger(__name__)


def _extract_url(rich_text_field: list[dict]) -> str | None:
    """Extract hyperlink URL from Prismic rich text field."""
    if not rich_text_field:
        return None
    for block in rich_text_field:
        for span in block.get("spans", []):
            if span.get("type") == "hyperlink":
                return span["data"]["url"]
    return None


def _extract_text(rich_text_field: list[dict]) -> str | None:
    """Extract plain text from Prismic rich text field."""
    if not rich_text_field:
        return None
    return rich_text_field[0].get("text")


def fetch_dataset_index() -> list[dict]:
    """Fetch the 17Lands public dataset index from Prismic CMS.

    Returns list of dicts with keys: expansion, format, last_updated,
    draft_data_url, game_data_url, replay_data_url.
    """
    logger.info("Fetching 17Lands dataset index from Prismic...")

    # Get master ref
    api_resp = requests.get(PRISMIC_API_URL, timeout=30)
    api_resp.raise_for_status()
    api_data = api_resp.json()
    master_ref = next(r["ref"] for r in api_data["refs"] if r["isMasterRef"])

    # Query public-data document
    query_url = (
        f'{PRISMIC_API_URL}/documents/search?ref={master_ref}&q=[[at(document.type,"public-data")]]&pageSize=100'
    )
    resp = requests.get(query_url, timeout=30)
    resp.raise_for_status()
    results = resp.json()["results"]

    if not results:
        logger.warning("No public-data document found in Prismic")
        return []

    raw_datasets = results[0]["data"]["datasets"]
    datasets = []
    for ds in raw_datasets:
        datasets.append(
            {
                "expansion": _extract_text(ds.get("expansion", [])),
                "format": _extract_text(ds.get("format", [])),
                "last_updated": _extract_text(ds.get("last_updated", [])),
                "draft_data_url": _extract_url(ds.get("draft_data", [])),
                "game_data_url": _extract_url(ds.get("game_data", [])),
                "replay_data_url": _extract_url(ds.get("replay_data", [])),
            }
        )

    logger.info(f"Found {len(datasets)} datasets in 17Lands index")
    return datasets


def sync_dataset_metadata(datasets: list[dict] | None = None) -> int:
    """Upsert 17Lands dataset metadata into the database.

    Returns count of datasets synced.
    """
    if datasets is None:
        datasets = fetch_dataset_index()

    now = datetime.now(UTC).isoformat()

    with get_session() as session:
        for ds in datasets:
            exp = ds["expansion"]
            fmt = ds["format"]
            if not exp or not fmt:
                continue

            existing = session.exec(
                select(MJ17LDataset).where((MJ17LDataset.expansion == exp) & (MJ17LDataset.format == fmt))
            ).first()

            if existing:
                existing.last_updated = ds["last_updated"]
                existing.draft_data_url = ds["draft_data_url"]
                existing.game_data_url = ds["game_data_url"]
                existing.replay_data_url = ds["replay_data_url"]
                existing.synced_at = now
                session.add(existing)
            else:
                record = MJ17LDataset(
                    expansion=exp,
                    format=fmt,
                    last_updated=ds["last_updated"],
                    draft_data_url=ds["draft_data_url"],
                    game_data_url=ds["game_data_url"],
                    replay_data_url=ds["replay_data_url"],
                    synced_at=now,
                )
                session.add(record)

        session.commit()

    logger.info(f"Synced {len(datasets)} dataset metadata records")
    return len(datasets)


def _url_to_local_path(url: str) -> Path:
    """Convert an S3 URL to a local file path under SEVENTEENLANDS_DIR."""
    # URL: https://17lands-public.s3.amazonaws.com/analysis_data/draft_data/draft_data_public.STX.PremierDraft.csv.gz
    # Path: ~/.mtgsim/reference/17lands/draft_data/draft_data_public.STX.PremierDraft.csv.gz
    parts = url.split("/analysis_data/")
    if len(parts) != 2:
        return SEVENTEENLANDS_DIR / url.split("/")[-1]
    return SEVENTEENLANDS_DIR / parts[1]


def download_dataset_files(
    expansion: str | None = None,
    format: str | None = None,
    force: bool = False,
) -> int:
    """Download 17Lands CSV files for matching datasets.

    Returns count of files downloaded.
    """
    downloaded = 0

    with get_session() as session:
        query = select(MJ17LDataset)
        if expansion:
            query = query.where(MJ17LDataset.expansion == expansion)
        if format:
            query = query.where(MJ17LDataset.format == format)

        datasets = session.exec(query).all()

        for ds in datasets:
            for data_type, url_attr, flag_attr in [
                ("draft_data", "draft_data_url", "draft_data_downloaded"),
                ("game_data", "game_data_url", "game_data_downloaded"),
                ("replay_data", "replay_data_url", "replay_data_downloaded"),
            ]:
                url = getattr(ds, url_attr)
                if not url:
                    continue

                already_downloaded = getattr(ds, flag_attr)
                if already_downloaded and not force:
                    continue

                dest = _url_to_local_path(url)
                if dest.exists() and not force:
                    setattr(ds, flag_attr, True)
                    session.add(ds)
                    continue

                logger.info(f"Downloading {ds.expansion}/{ds.format} {data_type}...")
                if download(url, dest):
                    setattr(ds, flag_attr, True)
                    session.add(ds)
                    downloaded += 1

        session.commit()

    logger.info(f"Downloaded {downloaded} files")
    return downloaded
