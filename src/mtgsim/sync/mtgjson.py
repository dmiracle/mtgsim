"""MTGJSON data synchronization helpers."""

import logging
import lzma
import shutil
import tarfile
from pathlib import Path

import requests

from mtgsim.config import ensure_dirs

logger = logging.getLogger(__name__)


def download_file(url: str, dest: Path) -> bool:
    """Download a file with progress indication."""
    ensure_dirs()
    logger.info(f"Downloading {url} to {dest}")
    try:
        with requests.get(url, stream=True, timeout=300) as r:
            r.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        logger.info("Download complete")
        return True
    except requests.RequestException as e:
        logger.error(f"Download failed: {e}")
        return False


def extract_xz(source: Path, dest: Path) -> bool:
    """Extract an xz compressed file."""
    logger.info(f"Extracting {source} to {dest}")
    try:
        with lzma.open(source) as f_in:
            with open(dest, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        logger.info("Extraction complete")
        return True
    except (lzma.LZMAError, OSError) as e:
        logger.error(f"Extraction failed: {e}")
        return False


def extract_tar_xz(source: Path, dest_dir: Path) -> bool:
    """Extract a tar.xz file."""
    logger.info(f"Extracting {source} to {dest_dir}")
    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
        with tarfile.open(source, "r:xz") as tar:
            tar.extractall(path=dest_dir)
        logger.info("Extraction complete")
        return True
    except (tarfile.TarError, OSError) as e:
        logger.error(f"Extraction failed: {e}")
        return False


def should_update(dest: Path, force: bool = False) -> bool:
    """Check if a file or directory should be updated."""
    if force:
        return True
    if not dest.exists():
        return True
    return False


def download_and_extract(url: str, dest: Path, force: bool = False) -> bool:
    """Download and extract an xz file if needed."""
    ensure_dirs()
    if not should_update(dest, force):
        logger.info(f"{dest.name} exists, skipping (use --force to update)")
        return True

    xz_path = dest.with_suffix(dest.suffix + ".xz")
    if not download_file(url, xz_path):
        return False

    if not extract_xz(xz_path, dest):
        return False

    xz_path.unlink(missing_ok=True)
    return True


# Legacy function stubs for backwards compatibility
def update_references(force: bool = False):
    """Deprecated: Use sync_all() from unified module instead."""
    from .unified import sync_all

    return sync_all(force=force)


def update_decks(force: bool = False):
    """Deprecated: Use sync_decks() from unified module instead."""
    from mtgsim.config import ALL_DECK_FILES_DIR, ALL_DECK_FILES_URL, MTGJSON_DIR

    from .unified import sync_decks

    all_decks_tar = MTGJSON_DIR / "AllDeckFiles.tar.xz"
    if should_update(ALL_DECK_FILES_DIR, force):
        if download_file(ALL_DECK_FILES_URL, all_decks_tar):
            extract_tar_xz(all_decks_tar, MTGJSON_DIR)
            all_decks_tar.unlink(missing_ok=True)

    if ALL_DECK_FILES_DIR.exists():
        sync_decks(ALL_DECK_FILES_DIR)


def update_sets(set_files_dir: Path | None = None):
    """Deprecated: Use sync_sets() from unified module instead."""
    from mtgsim.config import ALL_PRINTINGS_URL, MTGJSON_DIR

    from .unified import sync_sets

    printings_db = MTGJSON_DIR / "AllPrintings.sqlite"
    download_and_extract(ALL_PRINTINGS_URL, printings_db, force=False)
    sync_sets(printings_db)


def update_keywords(force: bool = False):
    """Deprecated: Keywords are now part of card data."""
    logger.info("Keywords are now synced as part of card data")
