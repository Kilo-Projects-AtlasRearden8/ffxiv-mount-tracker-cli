# STATUS

## What was built

A local-first Python CLI for Final Fantasy XIV players to log collected mounts.
Each mount record stores the mount name, acquisition source, rarity tier, and
acquisition date. Data persists to a local JSON file, and the full collection
can be exported to CSV.

## Files

- `pyproject.toml` — project metadata, packaging, and pytest configuration
- `ffxiv_mount_tracker/__init__.py` — package marker
- `ffxiv_mount_tracker/__main__.py` — `python -m ffxiv_mount_tracker` entry point
- `ffxiv_mount_tracker/models.py` — `Mount` dataclass and `Rarity` enum
- `ffxiv_mount_tracker/storage.py` — `MountStore` backed by local JSON
- `ffxiv_mount_tracker/export.py` — CSV export
- `ffxiv_mount_tracker/cli.py` — argparse CLI: add/list/remove/export
- `tests/test_mounts.py` — set logic and storage behavior tests
- `LICENSE` — MIT, copyright Asdale Dynamics, LLC (2026)
- `README.md` — usage and credits for Asdale Dynamics, LLC
- `STATUS.md` — this file

## How to run it

Install (editable):

```bash
python3 -m pip install -e .
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

- `python3 -m pytest` — all tests pass
- `ffxiv-mount-tracker` console script installs and runs (add/list/remove/export)
- `python3 -m ffxiv_mount_tracker` runs as a module
- CSV export produces valid output readable back into the store
- No secrets, API keys, or personal data present in files
- No `.github/workflows` files present

## Known gaps

- No input validation beyond blank name/source and date/rarity formats
- No "edit" command beyond `upsert` (internal); use remove + add to change a record
- No mount image / icon handling (fan project, no game assets)
- No sync or cloud backup; storage is local only
- Rarity is a closed enum (Common, Uncommon, Rare, Legendary)
