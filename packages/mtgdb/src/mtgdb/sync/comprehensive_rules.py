"""Download and parse MTG Comprehensive Rules for keyword definitions."""

import logging
import re
from datetime import UTC, datetime
from pathlib import Path

import httpx
from sqlmodel import Session, select

from mtgdb.config import COMPREHENSIVE_RULES_URL, REFERENCE_DIR, ensure_dirs
from mtgdb.models import MJKeywordDefinition
from mtgdb.session import get_engine
from mtgdb.sync.tables import SyncResult

logger = logging.getLogger(__name__)

RULES_DIR = REFERENCE_DIR / "rules"
RULES_FILE = RULES_DIR / "MagicCompRules.txt"


def download_comprehensive_rules(force: bool = False) -> Path | None:
    """Download the Comprehensive Rules text file."""
    ensure_dirs()
    RULES_DIR.mkdir(parents=True, exist_ok=True)

    if RULES_FILE.exists() and not force:
        logger.info(f"{RULES_FILE.name} exists, skipping download")
        return RULES_FILE

    logger.info(f"Downloading Comprehensive Rules from {COMPREHENSIVE_RULES_URL}")
    resp = httpx.get(COMPREHENSIVE_RULES_URL, follow_redirects=True, timeout=60)
    if resp.status_code != 200:
        logger.error(f"Failed to download rules: HTTP {resp.status_code}")
        return None

    RULES_FILE.write_bytes(resp.content)
    logger.info(f"Saved rules to {RULES_FILE} ({len(resp.content)} bytes)")
    return RULES_FILE


def parse_keyword_definitions(rules_path: Path) -> dict[str, str]:
    """Parse keyword definitions from sections 701 and 702 of the rules.

    Extracts the first sub-rule (e.g., 702.2a) as the definition for each keyword.
    Also parses the glossary for concise definitions as fallback.
    """
    content = rules_path.read_text(encoding="utf-8", errors="replace")
    lines = content.split("\n")

    # Parse sections 701 (Keyword Actions) and 702 (Keyword Abilities)
    # Format: "702.N. Keyword Name" followed by "702.Na Definition text"
    header_pattern = re.compile(r"^(701|702)\.(\d+)\.\s+(.+)$")
    subrule_pattern = re.compile(r"^(701|702)\.(\d+)a\s+(.+)$")

    definitions: dict[str, str] = {}
    current_keyword: str | None = None
    current_section: str | None = None
    current_num: str | None = None

    for line in lines:
        line = line.strip()

        header_match = header_pattern.match(line)
        if header_match:
            current_section = header_match.group(1)
            current_num = header_match.group(2)
            current_keyword = header_match.group(3).strip()
            continue

        if current_keyword and current_section and current_num:
            subrule_match = subrule_pattern.match(line)
            if subrule_match:
                section = subrule_match.group(1)
                num = subrule_match.group(2)
                if section == current_section and num == current_num:
                    definitions[current_keyword] = subrule_match.group(3).strip()
                    current_keyword = None
                    current_section = None
                    current_num = None

    # Also parse the glossary for keywords not found in 701/702
    glossary_defs = _parse_glossary(lines)
    for keyword, definition in glossary_defs.items():
        if keyword not in definitions:
            definitions[keyword] = definition

    logger.info(f"Parsed {len(definitions)} keyword definitions from comprehensive rules")
    return definitions


def _parse_glossary(lines: list[str]) -> dict[str, str]:
    """Parse the glossary section for concise keyword definitions.

    Glossary format:
        Keyword Name
        One or more lines of definition text. See rule NNN.

    Entries are separated by blank lines.
    """
    glossary: dict[str, str] = {}

    # Find the glossary section (starts after "Glossary" header)
    glossary_start = None
    for i, line in enumerate(lines):
        if line.strip() == "Glossary":
            glossary_start = i + 1
            break

    if glossary_start is None:
        return glossary

    # Parse entries: term line, then definition lines, separated by blank lines
    i = glossary_start
    while i < len(lines):
        line = lines[i].strip()
        if line == "" or line == "Credits":
            i += 1
            if line == "Credits":
                break
            continue

        # This should be a term line
        term = line
        i += 1

        # Collect definition lines until blank line
        def_lines = []
        while i < len(lines) and lines[i].strip() != "":
            def_lines.append(lines[i].strip())
            i += 1

        if def_lines:
            glossary[term] = " ".join(def_lines)

    return glossary


def sync_definitions_from_rules(force: bool = False) -> SyncResult:
    """Download comprehensive rules and sync keyword definitions to DB.

    Priority: comprehensive_rules > manual > generated.
    Only overwrites entries with source="generated".
    """
    rules_path = download_comprehensive_rules(force)
    if not rules_path:
        return SyncResult("Keyword Definitions (Rules)", 0, 0)

    parsed = parse_keyword_definitions(rules_path)
    if not parsed:
        logger.warning("No definitions parsed from rules")
        return SyncResult("Keyword Definitions (Rules)", 0, 0)

    now = datetime.now(UTC)
    engine = get_engine()
    updated = 0

    with Session(engine) as session:
        existing = {d.keyword: d for d in session.exec(select(MJKeywordDefinition)).all()}
        before = len(existing)

        for keyword, definition in parsed.items():
            if keyword in existing:
                row = existing[keyword]
                # Only overwrite generated entries
                if row.source == "generated":
                    row.definition = definition
                    row.source = "comprehensive_rules"
                    row.last_verified_at = now
                    session.add(row)
                    updated += 1
                elif row.source == "comprehensive_rules":
                    # Re-verify existing rules entries
                    row.definition = definition
                    row.last_verified_at = now
                    session.add(row)
                    updated += 1
            else:
                session.add(
                    MJKeywordDefinition(
                        keyword=keyword,
                        definition=definition,
                        source="comprehensive_rules",
                        last_verified_at=now,
                    )
                )
                updated += 1

        session.commit()
        after = session.exec(select(MJKeywordDefinition)).all()

    result = SyncResult("Keyword Definitions (Rules)", before, len(after))
    logger.info(f"{result.summary()} ({updated} updated from comprehensive rules)")
    return result
