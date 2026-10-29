"""Local JSON storage for mount records."""

from __future__ import annotations

import json
import os
from collections.abc import Iterable
from datetime import date
from pathlib import Path
from typing import Optional

from ffxiv_mount_tracker.models import Mount

DEFAULT_DATA_FILE = os.environ.get(
    "FFXIV_MOUNT_TRACKER_DATA",
    str(Path.home() / ".local" / "share" / "ffxiv-mount-tracker" / "mounts.json"),
)


class MountStore:
    """Persistent store of Mount records backed by a JSON file."""

    def __init__(self, path: str | Path = DEFAULT_DATA_FILE) -> None:
        self.path = Path(path)

    def _normalize_key(self, name: str) -> str:
        """Lowercase and collapse whitespace so lookups are case/whitespace-insensitive."""
        return " ".join(name.split()).strip().lower()

    def _load_all(self) -> dict[str, Mount]:
        """Read every mount from disk keyed by normalized name."""
        if not self.path.exists():
            return {}
        try:
            with self.path.open("r", encoding="utf-8") as handle:
                raw = json.load(handle)
        except (json.JSONDecodeError, OSError):
            return {}
        mounts: dict[str, Mount] = {}
        if isinstance(raw, dict):
            for key, value in raw.items():
                try:
                    mount = Mount.from_dict(value)
                except (KeyError, TypeError, ValueError):
                    continue
                mounts[mount.normalized_name] = mount
        return mounts

    def _save_all(self, mounts: dict[str, Mount]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        serializable = {
            mount.normalized_name: mount.to_dict() for mount in mounts.values()
        }
        tmp_path = self.path.with_suffix(self.path.suffix + ".tmp")
        with tmp_path.open("w", encoding="utf-8") as handle:
            json.dump(serializable, handle, indent=2, sort_keys=True)
        tmp_path.replace(self.path)

    def all(self) -> list[Mount]:
        """Return every mount, sorted by acquisition date then name."""
        return sorted(
            self._load_all().values(),
            key=lambda mount: (mount.acquisition_date, mount.normalized_name),
        )

    def get(self, name: str) -> Optional[Mount]:
        """Return the mount matching name, case- and whitespace-insensitively, or None."""
        return self._load_all().get(self._normalize_key(name))

    def add(self, mount: Mount) -> None:
        """Add or replace a mount record. Raises ValueError on duplicate."""
        mounts = self._load_all()
        key = mount.normalized_name
        if key in mounts:
            raise ValueError(f"mount already tracked: {mount.name}")
        mounts[key] = mount
        self._save_all(mounts)

    def upsert(self, mount: Mount) -> None:
        """Add or replace a mount record without raising on duplicate."""
        mounts = self._load_all()
        mounts[mount.normalized_name] = mount
        self._save_all(mounts)

    def update(
        self,
        name: str,
        source: Optional[str] = None,
        rarity=None,
        acquisition_date: Optional[date] = None,
    ) -> Optional[Mount]:
        """Update an existing mount's fields in place. Returns None if not tracked."""
        mount = self.get(name)
        if mount is None:
            return None
        updated = Mount(
            name=mount.name,
            source=source if source is not None else mount.source,
            rarity=rarity if rarity is not None else mount.rarity,
            acquisition_date=(
                acquisition_date if acquisition_date is not None
                else mount.acquisition_date
            ),
        )
        self.upsert(updated)
        return updated

    def remove(self, name: str) -> Mount:
        """Remove and return the mount matching name, case- and whitespace-insensitively.

        Raises KeyError if no mount matches.
        """
        mounts = self._load_all()
        key = self._normalize_key(name)
        if key not in mounts:
            raise KeyError(f"mount not tracked: {name}")
        removed = mounts.pop(key)
        self._save_all(mounts)
        return removed

    def filter_by_source(
        self, source: str, mounts: Optional[Iterable[Mount]] = None
    ) -> list[Mount]:
        """Return mounts whose source matches, case-insensitively."""
        target = source.strip().lower()
        pool = mounts if mounts is not None else self.all()
        return [m for m in pool if m.normalized_source == target]

    def filter_by_rarity(
        self, rarity, mounts: Optional[Iterable[Mount]] = None
    ) -> list[Mount]:
        """Return mounts whose rarity matches."""
        pool = mounts if mounts is not None else self.all()
        return [m for m in pool if m.rarity == rarity]

    def names(self) -> list[str]:
        """Return sorted mount names of all tracked mounts."""
        return sorted(mount.name for mount in self.all())
