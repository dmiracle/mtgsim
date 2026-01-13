"""Download and extraction utilities for MTGJSON files."""

import logging
import lzma
import shutil
import tarfile
from pathlib import Path

import requests

logger = logging.getLogger(__name__)


def download(url: str, dest: Path) -> bool:
    """Download a file from URL to destination path."""
    logger.info(f"Downloading {dest.name}...")
    try:
        with requests.get(url, stream=True, timeout=300) as r:
            r.raise_for_status()
            dest.parent.mkdir(parents=True, exist_ok=True)
            with open(dest, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return True
    except requests.RequestException as e:
        logger.error(f"Download failed: {e}")
        return False


def extract_xz(source: Path, dest: Path) -> bool:
    """Extract a .xz compressed file."""
    try:
        with lzma.open(source) as f_in:
            with open(dest, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        return True
    except (lzma.LZMAError, OSError) as e:
        logger.error(f"Extraction failed: {e}")
        return False


def extract_tar_xz(source: Path, dest_dir: Path) -> bool:
    """Extract a .tar.xz archive to a directory."""
    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
        with tarfile.open(source, "r:xz") as tar:
            tar.extractall(path=dest_dir)
        return True
    except (tarfile.TarError, OSError) as e:
        logger.error(f"Extraction failed: {e}")
        return False


def download_and_extract_xz(url: str, dest: Path, force: bool = False) -> bool:
    """Download a .xz file and extract it.

    Skips download if dest already exists (unless force=True).
    """
    if dest.exists() and not force:
        logger.info(f"{dest.name} exists, skipping")
        return True

    xz_path = dest.with_suffix(dest.suffix + ".xz")
    if not download(url, xz_path):
        return False

    if not extract_xz(xz_path, dest):
        return False

    xz_path.unlink(missing_ok=True)
    return True


def download_and_extract_tar_xz(url: str, dest_dir: Path, force: bool = False) -> bool:
    """Download a .tar.xz file and extract it.

    Skips download if dest_dir already exists (unless force=True).
    """
    if dest_dir.exists() and not force:
        logger.info(f"{dest_dir.name} exists, skipping")
        return True

    tar_path = dest_dir.parent / f"{dest_dir.name}.tar.xz"
    if not download(url, tar_path):
        return False

    if not extract_tar_xz(tar_path, dest_dir.parent):
        return False

    tar_path.unlink(missing_ok=True)
    return True
