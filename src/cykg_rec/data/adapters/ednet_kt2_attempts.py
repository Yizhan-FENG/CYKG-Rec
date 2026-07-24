"""Privacy-preserving KT2 response-to-attempt transformation."""

from __future__ import annotations

import csv
import hashlib
import io
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator


USER_FILE = re.compile(r"KT2/u(\d+)\.csv$")


def learner_hash(raw_id: str) -> str:
    return hashlib.sha256(f"ednet-kt2-public:{raw_id}".encode("utf-8")).hexdigest()[:32]


def question_metadata(contents_zip: Path) -> dict[str, dict[str, str]]:
    with zipfile.ZipFile(contents_zip) as archive, archive.open("contents/questions.csv") as binary:
        return {row["question_id"]: row for row in csv.DictReader(io.TextIOWrapper(binary, encoding="utf-8"))}


def iter_attempts(kt2_zip: Path, contents_zip: Path, max_students: int) -> Iterator[dict[str, object]]:
    metadata = question_metadata(contents_zip)
    seen_students = 0
    with zipfile.ZipFile(kt2_zip) as archive:
        for member in archive.infolist():
            match = USER_FILE.search(member.filename)
            if match is None:
                continue
            if seen_students >= max_students:
                break
            with archive.open(member) as binary:
                rows = csv.DictReader(io.TextIOWrapper(binary, encoding="utf-8"))
                for order, row in enumerate(rows):
                    question_id = row.get("item_id", "")
                    if row.get("action_type") != "respond" or question_id not in metadata:
                        continue
                    question = metadata[question_id]
                    answer = row.get("user_answer") or ""
                    timestamp = int(row["timestamp"])
                    tags = [f"ednet_tag:{tag}" for tag in (question.get("tags") or "").split(";") if tag]
                    yield {
                        "dataset_id": "ednet_kt2_public",
                        "dataset_scope": "real_public",
                        "learner_id_hash": learner_hash(match.group(1)),
                        "event_time": datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc).isoformat(),
                        "event_order": order,
                        "event_type": "respond",
                        "item_id": question_id,
                        "question_id": question_id,
                        "knowledge_point_ids": tags,
                        "correct": int(answer == question["correct_answer"]),
                        "response_option": answer or None,
                        "source_context": row.get("source") or None,
                        "evidence_confidence": 1.0,
                    }
            seen_students += 1
