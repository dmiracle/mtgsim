"""Batch scan job — runs all images in a directory through multiple pipelines.

Calls the scan API endpoint for each image with both openai and tesseract
pipelines. OpenAI results are authoritative (add_to_collection=true).
All results are logged to the scan_log database with a shared batch_id.
"""

import logging
import time
from datetime import UTC, datetime
from pathlib import Path

import httpx

from mtgsim.scan_log.db import get_session, log_scan
from mtgsim.scan_log.models import ScanBatch

logger = logging.getLogger("mtgsim.scan_log.batch")

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def _mime_type(path: Path) -> str:
    return "image/png" if path.suffix.lower() == ".png" else "image/jpeg"


def run_batch(
    source_dir: str,
    api_base: str = "http://localhost:8001",
    add_to_collection: bool = True,
) -> int:
    """Run a batch scan job. Returns the batch_id.

    For each image:
    1. POST to /api/cards/scan?pipeline=openai&add_to_collection={flag}
    2. POST to /api/cards/scan?pipeline=tesseract
    3. Log both results with the same batch_id

    Args:
        source_dir: Directory containing card images.
        api_base: Base URL for the API server.
        add_to_collection: Whether to add openai-matched cards to collection.
    """
    source = Path(source_dir)
    images = sorted(p for p in source.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS)

    if not images:
        logger.warning(f"No images found in {source_dir}")
        return -1

    # Create batch record
    with get_session() as session:
        batch = ScanBatch(source_dir=str(source), total_images=len(images), status="running")
        session.add(batch)
        session.commit()
        session.refresh(batch)
        batch_id = batch.id

    logger.info(f"Batch {batch_id}: scanning {len(images)} images from {source_dir}")

    t_batch_start = time.perf_counter()
    matched_oa = 0
    matched_ts = 0
    agreed = 0
    added = 0
    processed = 0

    scan_url = f"{api_base}/api/cards/scan"

    with httpx.Client(timeout=60.0) as client:
        for _i, img_path in enumerate(images):
            processed += 1
            image_data = img_path.read_bytes()
            mime = _mime_type(img_path)
            fname = img_path.name

            logger.info(f"Batch {batch_id}: [{processed}/{len(images)}] {fname}")

            # OpenAI scan (authoritative — adds to collection)
            oa_result = _scan_via_api(client, scan_url, img_path, "openai", add_to_collection=add_to_collection)

            # Tesseract scan (comparison only)
            ts_result = _scan_via_api(client, scan_url, img_path, "tesseract", add_to_collection=False)

            # Log both to scan_log DB with batch_id
            if oa_result:
                log_scan(
                    pipeline="openai",
                    image_data=image_data,
                    mime_type=mime,
                    extracted_name=oa_result.get("extracted_name", ""),
                    raw_text="",
                    matched=oa_result.get("matched", False),
                    match_type=oa_result.get("match_type", "none"),
                    match_confidence=oa_result.get("match_confidence"),
                    matched_card_uuid=oa_result.get("card", {}).get("uuid") if oa_result.get("card") else None,
                    matched_card_name=oa_result.get("card", {}).get("name") if oa_result.get("card") else None,
                    added_to_collection=oa_result.get("added_to_collection", False),
                    added_to_deck_id=None,
                    timing=None,
                    params={"pipeline": "openai", "source_file": fname},
                    batch_id=batch_id,
                )
                if oa_result.get("matched"):
                    matched_oa += 1
                if oa_result.get("added_to_collection"):
                    added += 1

            if ts_result:
                log_scan(
                    pipeline="tesseract",
                    image_data=image_data,
                    mime_type=mime,
                    extracted_name=ts_result.get("extracted_name", ""),
                    raw_text=ts_result.get("extraction", {}).get("oracle_text", ""),
                    matched=ts_result.get("matched", False),
                    match_type=ts_result.get("match_type", "none"),
                    match_confidence=ts_result.get("match_confidence"),
                    matched_card_uuid=ts_result.get("card", {}).get("uuid") if ts_result.get("card") else None,
                    matched_card_name=ts_result.get("card", {}).get("name") if ts_result.get("card") else None,
                    added_to_collection=False,
                    added_to_deck_id=None,
                    timing=None,
                    params={"pipeline": "tesseract", "source_file": fname},
                    batch_id=batch_id,
                )
                if ts_result.get("matched"):
                    matched_ts += 1

            # Check agreement
            if oa_result and ts_result:
                oa_name = oa_result.get("extracted_name", "")
                ts_name = ts_result.get("extracted_name", "")
                if oa_name and ts_name and oa_name == ts_name:
                    agreed += 1

            # Update batch progress periodically
            if processed % 10 == 0:
                _update_batch_progress(batch_id, processed, matched_oa, matched_ts, agreed, added)

    total_time = time.perf_counter() - t_batch_start

    # Finalize batch
    summary = {
        "images": [img.name for img in images],
        "per_image_avg_s": round(total_time / len(images), 2) if images else 0,
    }

    with get_session() as session:
        batch = session.get(ScanBatch, batch_id)
        batch.status = "completed"
        batch.completed_at = datetime.now(UTC)
        batch.processed = processed
        batch.matched_openai = matched_oa
        batch.matched_tesseract = matched_ts
        batch.agreed = agreed
        batch.added_to_collection = added
        batch.total_time_s = round(total_time, 2)
        batch.summary_json = summary
        session.add(batch)
        session.commit()

    logger.info(
        f"Batch {batch_id} complete: {processed} images, "
        f"OA={matched_oa} TS={matched_ts} agreed={agreed} added={added} "
        f"in {total_time:.1f}s"
    )
    return batch_id


def _scan_via_api(
    client: httpx.Client,
    url: str,
    image_path: Path,
    pipeline: str,
    add_to_collection: bool = False,
) -> dict | None:
    """Call the scan API for a single image. Returns parsed JSON or None on error."""
    params = {"pipeline": pipeline}
    if add_to_collection:
        params["add_to_collection"] = "true"

    try:
        with open(image_path, "rb") as f:
            response = client.post(url, params=params, files={"image": (image_path.name, f, _mime_type(image_path))})

        if response.status_code == 200:
            return response.json()

        logger.warning(f"Scan failed for {image_path.name} ({pipeline}): HTTP {response.status_code}")
        return None
    except Exception:
        logger.exception(f"Scan error for {image_path.name} ({pipeline})")
        return None


def _update_batch_progress(
    batch_id: int, processed: int, matched_oa: int, matched_ts: int, agreed: int, added: int
) -> None:
    with get_session() as session:
        batch = session.get(ScanBatch, batch_id)
        if batch:
            batch.processed = processed
            batch.matched_openai = matched_oa
            batch.matched_tesseract = matched_ts
            batch.agreed = agreed
            batch.added_to_collection = added
            session.add(batch)
            session.commit()
