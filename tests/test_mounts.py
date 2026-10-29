"""Tests for mount set logic and storage behavior."""

from __future__ import annotations

from datetime import date

import pytest

from ffxiv_mount_tracker.models import Mount, Rarity
from ffxiv_mount_tracker.storage import MountStore


def _mount(
    name: str,
    source: str,
    rarity: Rarity = Rarity.COMMON,
    day: int = 1,
) -> Mount:
    return Mount(
        name=name,
        source=source,
        rarity=rarity,
        acquisition_date=date(2024, 1, day),
    )


# ---- Mount model / set identity ----

def test_mount_identity_case_insensitive() -> None:
    a = _mount("Azure Drake", "Quest")
    b = _mount("azure drake", "Quest")
    assert a.normalized_name == b.normalized_name
    assert a != b  # dataclass equality uses raw fields


def test_mount_normalized_source_groups() -> None:
    m1 = _mount("Aetherial Ram", "The Final Coil of Bahamut")
    m2 = _mount("Bahamut's Horn", "the final coil of bahamut")
    assert m1.normalized_source == m2.normalized_source


# ---- Store set logic: add, dedup, upsert, remove ----

def test_store_add_and_list(tmp_path) -> None:
    store = MountStore(tmp_path / "mounts.json")
    m1 = _mount("Azure Drake", "Quest", Rarity.RARE, 5)
    m2 = _mount("Cloud Manta", "Gold Saucer", Rarity.COMMON, 10)
    store.add(m1)
    store.add(m2)
    names = [m.name for m in store.all()]
    assert names == ["Azure Drake", "Cloud Manta"]


def test_store_add_duplicate_raises(tmp_path) -> None:
    store = MountStore(tmp_path / "mounts.json")
    store.add(_mount("Azure Drake", "Quest"))
    with pytest.raises(ValueError):
        store.add(_mount("azure drake", "Quest"))


def test_store_upsert_replaces(tmp_path) -> None:
    store = MountStore(tmp_path / "mounts.json")
    store.add(_mount("Azure Drake", "Quest", Rarity.RARE, 1))
    store.upsert(_mount("Azure Drake", "FATE", Rarity.LEGENDARY, 2))
    mounts = store.all()
    assert len(mounts) == 1
    assert mounts[0].source == "FATE"
    assert mounts[0].rarity == Rarity.LEGENDARY


def test_store_remove_existing(tmp_path) -> None:
    store = MountStore(tmp_path / "mounts.json")
    store.add(_mount("Azure Drake", "Quest"))
    removed = store.remove("azure drake")
    assert removed.name == "Azure Drake"
    assert store.get("Azure Drake") is None


def test_store_remove_missing_raises(tmp_path) -> None:
    store = MountStore(tmp_path / "mounts.json")
    with pytest.raises(KeyError):
        store.remove("Nonexistent")


def test_get_and_remove_are_whitespace_insensitive(tmp_path) -> None:
    store = MountStore(tmp_path / "mounts.json")
    store.add(_mount("Azure Drake", "Quest"))
    assert store.get("  azure   drake  ") is not None
    removed = store.remove("AZURE DRAKE")
    assert removed.name == "Azure Drake"
    assert store.get("Azure Drake") is None


def test_store_update_changes_fields(tmp_path) -> None:
    store = MountStore(tmp_path / "mounts.json")
    store.add(_mount("Azure Drake", "Quest", Rarity.RARE, 1))
    store.update(
        "Azure Drake", source="FATE", rarity=Rarity.LEGENDARY,
        acquisition_date=date(2024, 2, 2),
    )
    mount = store.get("Azure Drake")
    assert mount is not None
    assert mount.name == "Azure Drake"
    assert mount.source == "FATE"
    assert mount.rarity == Rarity.LEGENDARY
    assert mount.acquisition_date == date(2024, 2, 2)


def test_store_update_partial_fields_keeps_others(tmp_path) -> None:
    store = MountStore(tmp_path / "mounts.json")
    store.add(_mount("Azure Drake", "Quest", Rarity.RARE, 1))
    store.update("Azure Drake", rarity=Rarity.COMMON)
    mount = store.get("Azure Drake")
    assert mount is not None
    assert mount.source == "Quest"
    assert mount.rarity == Rarity.COMMON
    assert mount.acquisition_date == date(2024, 1, 1)


def test_store_update_missing_returns_none(tmp_path) -> None:
    store = MountStore(tmp_path / "mounts.json")
    assert store.update("Ghost", source="Nowhere") is None


# ---- Store set logic: filtering (source / rarity) ----

def test_filter_by_source(tmp_path) -> None:
    store = MountStore(tmp_path / "mounts.json")
    store.add(_mount("Azure Drake", "The Final Coil of Bahamut"))
    store.add(_mount("Bahamut's Horn", "the final coil of bahamut"))
    store.add(_mount("Cloud Manta", "Gold Saucer"))
    results = store.filter_by_source("The Final Coil of Bahamut")
    assert {m.name for m in results} == {"Azure Drake", "Bahamut's Horn"}


def test_filter_by_rarity(tmp_path) -> None:
    store = MountStore(tmp_path / "mounts.json")
    store.add(_mount("Azure Drake", "Quest", Rarity.RARE))
    store.add(_mount("Cloud Manta", "Gold Saucer", Rarity.COMMON))
    store.add(_mount("Minion Bat", "Achievement", Rarity.RARE))
    rare = store.filter_by_rarity(Rarity.RARE)
    assert {m.name for m in rare} == {"Azure Drake", "Minion Bat"}


def test_combined_source_and_rarity_filter(tmp_path) -> None:
    store = MountStore(tmp_path / "mounts.json")
    store.add(_mount("Azure Drake", "The Final Coil of Bahamut", Rarity.RARE))
    store.add(_mount("Bahamut's Horn", "the final coil of bahamut", Rarity.LEGENDARY))
    store.add(_mount("Cloud Manta", "Gold Saucer", Rarity.RARE))
    results = store.filter_by_source(
        "The Final Coil of Bahamut",
        store.filter_by_rarity(Rarity.RARE),
    )
    assert {m.name for m in results} == {"Azure Drake"}


# ---- Store set logic: set-style operations on names ----

def test_names_subset_and_difference(tmp_path) -> None:
    store_a = MountStore(tmp_path / "a.json")
    store_b = MountStore(tmp_path / "b.json")
    store_a.add(_mount("Azure Drake", "Quest"))
    store_a.add(_mount("Cloud Manta", "Gold Saucer"))
    store_a.add(_mount("Minion Bat", "Achievement"))
    store_b.add(_mount("Azure Drake", "Quest"))
    store_b.add(_mount("Minion Bat", "Achievement"))

    names_a = set(store_a.names())
    names_b = set(store_b.names())

    # Intersection: mounts tracked by both stores.
    assert names_a & names_b == {"Azure Drake", "Minion Bat"}
    # Difference: mounts in A but not B.
    assert names_a - names_b == {"Cloud Manta"}
    # B is a subset of A.
    assert names_b <= names_a
    assert not (names_a <= names_b)


def test_all_sorted_by_date_then_name(tmp_path) -> None:
    store = MountStore(tmp_path / "mounts.json")
    store.add(_mount("Zebra Mount", "Quest", day=5))
    store.add(_mount("Alpha Mount", "Quest", day=1))
    store.add(_mount("Beta Mount", "Quest", day=1))
    ordered = [m.name for m in store.all()]
    assert ordered == ["Alpha Mount", "Beta Mount", "Zebra Mount"]


# ---- Round-trip persistence ----

def test_persistence_round_trip(tmp_path) -> None:
    path = tmp_path / "mounts.json"
    store = MountStore(path)
    store.add(_mount("Azure Drake", "Quest", Rarity.RARE, 15))
    reloaded = MountStore(path)
    assert reloaded.get("Azure Drake") is not None
    assert reloaded.get("Azure Drake").rarity == Rarity.RARE
    assert reloaded.get("Azure Drake").acquisition_date == date(2024, 1, 15)


def test_missing_file_treated_as_empty(tmp_path) -> None:
    store = MountStore(tmp_path / "does_not_exist.json")
    assert store.all() == []
    assert store.get("Anything") is None
