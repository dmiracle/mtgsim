"""Download and extraction utilities for MTGJSON files."""

import logging
import lzma
import shutil
import tarfile
from pathlib import Path

import requests

from ._progress import console, download_progress, spinner_progress

logger = logging.getLogger(__name__)

CHUNK_SIZE = 64 * 1024


def download(url: str, dest: Path) -> bool:
    """Download a file from URL to destination path with a progress bar."""
    try:
        with requests.get(url, stream=True, timeout=300) as r:
            r.raise_for_status()
            total = int(r.headers.get("content-length") or 0) or None
            dest.parent.mkdir(parents=True, exist_ok=True)
            with download_progress() as progress:
                task = progress.add_task(f"Downloading {dest.name}", total=total)
                with open(dest, "wb") as f:
                    for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                        f.write(chunk)
                        progress.advance(task, len(chunk))
        size_mb = dest.stat().st_size / 1024 / 1024
        console.print(f"  [green]✓[/green] saved {dest.name} ({size_mb:,.1f} MB)")
        return True
    except requests.RequestException as e:
        logger.error(f"Download failed: {e}")
        return False


def extract_xz(source: Path, dest: Path) -> bool:
    """Extract a .xz compressed file."""
    try:
        with spinner_progress() as progress:
            progress.add_task(f"Extracting {source.name}", total=None)
            with lzma.open(source) as f_in, open(dest, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out, length=CHUNK_SIZE)
        size_mb = dest.stat().st_size / 1024 / 1024
        console.print(f"  [green]✓[/green] extracted {dest.name} ({size_mb:,.1f} MB)")
        return True
    except (lzma.LZMAError, OSError) as e:
        logger.error(f"Extraction failed: {e}")
        return False


def extract_tar_xz(source: Path, dest_dir: Path) -> bool:
    """Extract a .tar.xz archive to a directory."""
    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
        with tarfile.open(source, "r:xz") as tar:
            members = tar.getmembers()
            with download_progress() as progress:
                task = progress.add_task(
                    f"Extracting {source.name}",
                    total=sum(m.size for m in members) or None,
                )
                for member in members:
                    tar.extract(member, path=dest_dir)
                    progress.advance(task, member.size)
        console.print(f"  [green]✓[/green] extracted {len(members):,} files to {dest_dir.name}/")
        return True
    except (tarfile.TarError, OSError) as e:
        logger.error(f"Extraction failed: {e}")
        return False


def download_and_extract_xz(url: str, dest: Path, force: bool = False) -> bool:
    """Download a .xz file and extract it.

    Skips download if dest already exists (unless force=True).
    """
    if dest.exists() and not force:
        console.print(f"  [yellow]•[/yellow] {dest.name} exists, skipping (use --force to re-download)")
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
        console.print(f"  [yellow]•[/yellow] {dest_dir.name}/ exists, skipping (use --force to re-download)")
        return True

    tar_path = dest_dir.parent / f"{dest_dir.name}.tar.xz"
    if not download(url, tar_path):
        return False

    if not extract_tar_xz(tar_path, dest_dir.parent):
        return False

    tar_path.unlink(missing_ok=True)
    return True
