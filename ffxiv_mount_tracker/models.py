"""Data models for mounts tracked in the FFXIV mount tracker."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any


class Rarity(str, Enum):
    """Rarity tiers a mount can have in the tracker."""

    COMMON = "Common"
    UNCOMMON = "Uncommon"
    RARE = "Rare"
    LEGENDARY = "Legendary"


@dataclass(frozen=True)
class Mount:
    """A single collected mount record."""

    name: str
    source: str
    rarity: Rarity
    acquisition_date: date

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("mount name must not be blank")
        if not self.source.strip():
            raise ValueError("mount source must not be blank")

    @property
    def normalized_name(self) -> str:
        """Lowercased, whitespace-collapsed name for identity/compare operations."""
        return " ".join(self.name.split()).strip().lower()

    @property
    def normalized_source(self) -> str:
        """Lowercased source for grouping/compare operations."""
        return " ".join(self.source.split()).strip().lower()

    @property
    def acquisition_date_iso(self) -> str:
        """ISO-8601 string representation of the acquisition date."""
        return self.acquisition_date.isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "source": self.source,
            "rarity": self.rarity.value,
            "acquisition_date": self.acquisition_date_iso,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Mount:
        return cls(
            name=str(data["name"]),
            source=str(data["source"]),
            rarity=Rarity(str(data["rarity"])),
            acquisition_date=datetime.strptime(
                str(data["acquisition_date"]), "%Y-%m-%d"
            ).date(),
        )


MOUNT_FIELD_ORDER = ["name", "source", "rarity", "acquisition_date"]
