"""Local JSON storage for mount records."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

from ffxiv_mount_tracker.models import Mount

DEFAULT_DATA_FILE = os.environ.get(
    "FFXIV_MOUNT_TRACKER_DATA",
    str(Path.home() / ".local" / "share" / "ffxiv-mount-tracker" / "mounts.json"),
)


class MountStore:
    """Persistent store of Mount records backed by a JSON file."""

    def __init__(self, path: str | Path = DEFAULT_DATA_FILE) -> None:
        self.path = Path(path)

    def _load_all(self) -> Dict[str, Mount]:
        """Read every mount from disk keyed by normalized name."""
        if not self.path.exists():
            return {}
        try:
            with self.path.open("r", encoding="utf-8") as handle:
                raw = json.load(handle)
        except (json.JSONDecodeError, OSError):
            return {}
        mounts: Dict[str, Mount] = {}
        if isinstance(raw, dict):
            for key, value in raw.items():
                try:
                    mount = Mount.from_dict(value)
                except (KeyError, TypeError, ValueError):
                    continue
                mounts[mount.normalized_name] = mount
        return mounts

    def _save_all(self, mounts: Dict[str, Mount]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        serializable = {
            mount.normalized_name: mount.to_dict() for mount in mounts.values()
        }
        tmp_path = self.path.with_suffix(self.path.suffix + ".tmp")
        with tmp_path.open("w", encoding="utf-8") as handle:
            json.dump(serializable, handle, indent=2, sort_keys=True)
        tmp_path.replace(self.path)

    def all(self) -> List[Mount]:
        """Return every mount, sorted by acquisition date then name."""
        return sorted(
            self._load_all().values(),
            key=lambda mount: (mount.acquisition_date, mount.normalized_name),
        )

    def get(self, name: str) -> Optional[Mount]:
        """Return the mount matching name, case-insensitively, or None."""
        return self._load_all().get(name.strip().lower())

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

    def remove(self, name: str) -> Mount:
        """Remove and return the mount matching name, case-insensitively.

        Raises KeyError if no mount matches.
        """
        mounts = self._load_all()
        key = name.strip().lower()
        if key not in mounts:
            raise KeyError(f"mount not tracked: {name}")
        removed = mounts.pop(key)
        self._save_all(mounts)
        return removed

    def filter_by_source(self, source: str) -> List[Mount]:
        """Return mounts whose source matches, case-insensitively."""
        target = source.strip().lower()
        return [m for m in self.all() if m.normalized_source == target]

    def filter_by_rarity(self, rarity) -> List[Mount]:
        """Return mounts whose rarity matches."""
        return [m for m in self.all() if m.rarity == rarity]

    def names(self) -> List[str]:
        """Return sorted normalized names of all tracked mounts."""
        return sorted(mount.name for mount in self.all())
