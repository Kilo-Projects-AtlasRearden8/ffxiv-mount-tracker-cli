# FFXIV Mount Tracker CLI

A friendly Python command-line tool for Final Fantasy XIV players to log the
mounts they've collected. For each mount, you record its name, where you got
it (source), how rare it is (rarity), and the date you picked it up. Your
collection is saved to a small JSON file on your own computer, and you can
export it to a CSV spreadsheet whenever you like.

This is a fan project. No Square Enix game assets are included or distributed.

## About Asdale Dynamics, LLC

Built by [Asdale Dynamics, LLC](https://dylanasdale.github.io) — an Indiana
company formed in October 2026 — founded by Dylan Asdale, a registered nurse
turned AI author. Dylan wrote *The Massive AI Manual* and runs the hub site
dylanasdale.github.io, where he explains AI "like a friend would": plain
English, step by step, never condescending.

Asdale Dynamics focuses on beginner-friendly AI education, books and guides,
and practical open-source tools the LLC can publish or sell. This CLI follows
that same spirit: clear, warm, tested, local-first, and free of secrets or
personal data.

## Is this for me?

Yes, if you:

- Play FFXIV and want a simple place to track your mount collection
- Prefer keeping your data on your own computer (not in someone's cloud)
- Want something you can run without creating accounts or API keys

No programming experience required. If you can copy and paste a command, you
can use this tool.

## Features

- **Add** a mount with name, source, rarity, and acquisition date
- **List** your whole collection in a tidy table
- **Filter** by source (like "Gold Saucer") or rarity (like "Rare"), or both at once
- **Update** a mount's details if something changes
- **Remove** a mount you no longer want tracked
- **Export** your collection to a CSV file you can open in Excel, Google Sheets,
  or Numbers
- **Duplicate detection** — adding the same mount twice is blocked (matches are
  case-insensitive)
- **Local-first** — everything lives in a JSON file on your machine. No network
  calls, no API keys, no game assets.

## Installation

Open your terminal in this project folder and run:

```bash
python3 -m pip install -e .
```

You may see a message about "externally managed environments." If so, add
`--break-system-packages` to the command:

```bash
python3 -m pip install -e . --break-system-packages
```

That installs the `ffxiv-mount-tracker` command so you can run it from anywhere.

## Usage

### Add a mount

```bash
ffxiv-mount-tracker add "Azure Drake" "The Final Coil of Bahamut" Rare 2024-01-15
```

The pieces, in order:

1. Mount name — `"Azure Drake"`
2. Source — where you got it — `"The Final Coil of Bahamut"`
3. Rarity — `Common`, `Uncommon`, `Rare`, or `Legendary`
4. Acquisition date — `YYYY-MM-DD` — `2024-01-15`

### List your mounts

```bash
ffxiv-mount-tracker list
```

Filter by source:

```bash
ffxiv-mount-tracker list --source "Gold Saucer"
```

Filter by rarity:

```bash
ffxiv-mount-tracker list --rarity Rare
```

Filter by both at once:

```bash
ffxiv-mount-tracker list --source "Gold Saucer" --rarity Common
```

### Update a mount

Got a detail wrong? Update just the fields you want to change:

```bash
ffxiv-mount-tracker update "Azure Drake" --rarity Common
```

You can update `--source`, `--rarity`, and `--acquisition-date` (YYYY-MM-DD).

### Remove a mount

```bash
ffxiv-mount-tracker remove "Azure Drake"
```

### Export to CSV

```bash
ffxiv-mount-tracker export my_mounts.csv
```

This writes every tracked mount to `my_mounts.csv`, which you can open in any
spreadsheet app.

### Run without installing

You can also run the tool straight from the project folder:

```bash
python3 -m ffxiv_mount_tracker list
```

## Where your data lives

By default, your mounts are stored here:

```
~/.local/share/ffxiv-mount-tracker/mounts.json
```

You can put the file somewhere else with the `--data` option, or by setting
the `FFXIV_MOUNT_TRACKER_DATA` environment variable.

## Development

Run the test suite from the project folder:

```bash
python3 -m pytest
```

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC. See [LICENSE](LICENSE).
