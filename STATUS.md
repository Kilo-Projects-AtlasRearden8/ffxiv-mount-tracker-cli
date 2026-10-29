# STATUS

## What was built

A local-first Python CLI for Final Fantasy XIV players to log collected mounts.
Each mount record stores the mount name, acquisition source, rarity tier, and
acquisition date. Data persists to a local JSON file, and the full collection
can be exported to a CSV spreadsheet.

## Files

- `pyproject.toml` — project metadata, packaging, and pytest configuration
- `ffxiv_mount_tracker/__init__.py` — package marker
- `ffxiv_mount_tracker/__main__.py` — `python -m ffxiv_mount_tracker` entry point
- `ffxiv_mount_tracker/models.py` — `Mount` dataclass and `Rarity` enum
- `ffxiv_mount_tracker/storage.py` — `MountStore` backed by local JSON
- `ffxiv_mount_tracker/export.py` — CSV export
- `ffxiv_mount_tracker/cli.py` — argparse CLI: add/list/update/remove/export
- `tests/test_mounts.py` — set logic and storage behavior tests
- `LICENSE` — MIT, copyright Asdale Dynamics, LLC (2026)
- `README.md` — beginner-friendly usage and credits for Asdale Dynamics, LLC
- `STATUS.md` — this file

## How to run it

Install (editable) from this project folder:

```bash
python3 -m pip install -e .
```

If you see an "externally managed environment" message:

```bash
python3 -m pip install -e . --break-system-packages
```

Add a mount:

```bash
ffxiv-mount-tracker add "Azure Drake" "The Final Coil of Bahamut" Rare 2024-01-15
```

List mounts:

```bash
ffxiv-mount-tracker list
ffxiv-mount-tracker list --source "Gold Saucer"
ffxiv-mount-tracker list --rarity Rare
ffxiv-mount-tracker list --source "Gold Saucer" --rarity Common
```

Update a mount:

```bash
ffxiv-mount-tracker update "Azure Drake" --rarity Common
```

Remove a mount:

```bash
ffxiv-mount-tracker remove "Azure Drake"
```

Export to CSV:

```bash
ffxiv-mount-tracker export my_mounts.csv
```

Or run as a module:

```bash
python3 -m ffxiv_mount_tracker list
```

Storage path defaults to `~/.local/share/ffxiv-mount-tracker/mounts.json` and can
be overridden with `--data` or the `FFXIV_MOUNT_TRACKER_DATA` environment
variable.

## Verification results

- `python3 -m pytest` — all 18 tests pass
  - Mount model / set identity (case- and whitespace-insensitive)
  - Store set logic: add, duplicate detection, upsert, remove, update
  - Filtering by source and rarity, including combined `--source + --rarity`
  - Set-style operations on mount names (intersection, difference, subset)
  - Sorting by acquisition date then name
  - Persistence round-trip and missing-file handling
- `python3 -m pip install -e .` — package installs cleanly
- `ffxiv-mount-tracker` console script runs (add/list/update/remove/export)
- `python3 -m ffxiv_mount_tracker` runs as a module
- CSV export produces valid output readable back into the store
- Combined `--source` and `--rarity` filters compose correctly (bug fixed)
- Lookups are case- and whitespace-insensitive (bug fixed)
- `python3 -m compileall ffxiv_mount_tracker tests` — compiles cleanly
- No secrets, API keys, or personal data present in files
- No `.github/workflows` files present
- LICENSE copyright line is exactly `Copyright (c) 2026 Asdale Dynamics, LLC`
- README credits Asdale Dynamics, LLC

## Known gaps

- No mount image / icon handling (fan project, no game assets)
- No sync or cloud backup; storage is local only
- Rarity is a closed enum (Common, Uncommon, Rare, Legendary)
- No "delete all" or bulk-import command
- Targets Python >= 3.9, so modern `X | None` union syntax is avoided in
  favor of `typing.Optional` for compatibility

## Fixes since initial commit

- Fixed `--source` and `--rarity` filters not composing (only the last filter
  was applied); filters now chain on the in-memory result set
- Made `get()`/`remove()` whitespace-insensitive to match `normalized_name`
  (e.g. `remove("AZURE  DRAKE")` now finds "Azure Drake")
- Fixed `names()` docstring (returned raw names, claimed normalized)
- Added `update` command and `MountStore.update()` method (was a known gap)
- Added tests for combined filters, update command, and whitespace-insensitive
  lookups (13 → 18 tests)
