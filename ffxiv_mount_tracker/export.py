"""CSV export for mount records."""

from __future__ import annotations

import csv
from collections.abc import Iterable
from pathlib import Path

from ffxiv_mount_tracker.models import MOUNT_FIELD_ORDER, Mount


def export_csv(mounts: Iterable[Mount], path: str | Path) -> None:
    """Write mount records to a CSV file at path."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MOUNT_FIELD_ORDER)
        writer.writeheader()
        for mount in mounts:
            writer.writerow(mount.to_dict())
