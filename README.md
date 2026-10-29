# FFXIV Mount Tracker CLI

A Python command-line tool for Final Fantasy XIV players to log their collected
mounts, recording each mount's name, source, rarity, and acquisition date.
Data is stored locally as JSON, and collections can be exported to CSV.

This is a fan project. No Square Enix game assets are included or distributed.

## About Asdale Dynamics, LLC

Built by [Asdale Dynamics, LLC](https://dylanasdale.github.io) — Indiana,
formed October 2026 — founded by Dylan Asdale, a registered nurse turned AI
author. Asdale Dynamics focuses on beginner-friendly AI education, books and
guides (including *The Massive AI Manual*), and practical open-source tools that
the LLC can publish or sell. This CLI follows the LLC's style: clear, warm,
polished, tested, local-first, and free of secrets or personal data.

## Features

- Add, list, remove, and export mount records
- Track mount name, source, rarity, and acquisition date
- Local JSON storage (default: `~/.local/share/ffxiv-mount-tracker/mounts.json`,
  or set `FFXIV_MOUNT_TRACKER_DATA`)
- CSV export of your full collection
- Duplicate detection by mount name (case-insensitive)
- Filter listings by source or rarity
- No network calls, no API keys, no game assets

## Installation

From this repository folder:

```bash
python3 -m pip install -e .
```

This installs the `ffxiv-mount-tracker` console script.

## Usage

```bash
# Add a mount
ffxiv-mount-tracker add "Azure Drake" "The Final Coil of Bahamut" Rare 2024-01-15

# List all mounts
ffxiv-mount-tracker list

# List mounts from a specific source
ffxiv-mount-tracker list --source "Gold Saucer"

# List mounts by rarity
ffxiv-mount-tracker list --rarity Rare

# Remove a mount
ffxiv-mount-tracker remove "Azure Drake"

# Export collection to CSV
ffxiv-mount-tracker export my_mounts.csv
```

You can also run the package directly:

```bash
python3 -m ffxiv_mount_tracker list
```

Rarity values: `Common`, `Uncommon`, `Rare`, `Legendary`. Dates use
`YYYY-MM-DD` format.

## Development

Run the test suite:

```bash
python3 -m pytest
```

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC. See [LICENSE](LICENSE).
