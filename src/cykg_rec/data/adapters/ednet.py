"""Memory-safe adapter for EdNet KT2/KT3 zip archives."""

from __future__ import annotations

import csv
import io
import re
import zipfile
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path

from cykg_rec.data.schema import CanonicalLearningEvent

USER_FILE = re.compile(r"(?:KT2|KT3)/u(\d+)\.csv$")


def _event_type(action: str, item_id: str) -> str:
    if action == "respond":
        return "respond"
    if action == "submit":
        return "submit"
    if item_id.startswith("e"):
        return "explanation_view"
    if item_id.startswith("l"):
        return "lecture_view"
    if action == "enter":
        return "enter"
    # The canonical schema intentionally has no generic ``quit`` event. A quit
    # is represented as resource engagement context once Content metadata joins.
    return "resource_view"


def iter_ednet_events(
    archive_path: Path,
    dataset_id: str,
    max_students: int | None = None,
) -> Iterator[CanonicalLearningEvent]:
    """Yield events one student file at a time without extracting the archive."""
    processed = 0
    with zipfile.ZipFile(archive_path) as archive:
        for member in archive.infolist():
            match = USER_FILE.search(member.filename)
            if member.is_dir() or match is None:
                continue
            if max_students is not None and processed >= max_students:
                break
            learner_id = f"ednet_{match.group(1)}"
            with archive.open(member) as binary:
                reader = csv.DictReader(io.TextIOWrapper(binary, encoding="utf-8"))
                for order, row in enumerate(reader):
                    raw_item = row.get("item_id") or None
                    action = row.get("action_type") or "enter"
                    timestamp = row.get("timestamp")
                    event_time = None
                    if timestamp:
                        event_time = datetime.fromtimestamp(int(timestamp) / 1000, tz=timezone.utc)
                    question_id = raw_item if raw_item and raw_item.startswith("q") else None
                    yield CanonicalLearningEvent(
                        dataset_id=dataset_id,
                        dataset_scope="real_public",
                        learner_id_hash=learner_id,
                        event_time=event_time,
                        event_order=order,
                        event_type=_event_type(action, raw_item or ""),
                        item_id=raw_item,
                        question_id=question_id,
                        response_option=row.get("user_answer") or None,
                        source_context=row.get("source") or None,
                    )
            processed += 1
