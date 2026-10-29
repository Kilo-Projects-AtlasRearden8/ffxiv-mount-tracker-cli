"""Command-line interface for the FFXIV mount tracker."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from datetime import date, datetime
from typing import Optional

from ffxiv_mount_tracker.export import export_csv
from ffxiv_mount_tracker.models import Mount, Rarity
from ffxiv_mount_tracker.storage import DEFAULT_DATA_FILE, MountStore


def _parse_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"invalid date '{value}': expected YYYY-MM-DD"
        ) from exc


def _parse_rarity(value: str) -> Rarity:
    try:
        return Rarity(value.strip().capitalize())
    except ValueError as exc:
        valid = ", ".join(r.value for r in Rarity)
        raise argparse.ArgumentTypeError(
            f"invalid rarity '{value}': must be one of {valid}"
        ) from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ffxiv-mount-tracker",
        description="Log collected FFXIV mounts with source, rarity, and acquisition date.",
    )
    parser.add_argument(
        "--data",
        default=DEFAULT_DATA_FILE,
        help="Path to the JSON storage file (default: %(default)s). "
        "Can also be set via FFXIV_MOUNT_TRACKER_DATA env var.",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # add
    add = sub.add_parser("add", help="Add a mount record.")
    add.add_argument("name", help="Mount name.")
    add.add_argument("source", help="How the mount was acquired.")
    add.add_argument("rarity", type=_parse_rarity, help="Rarity tier.")
    add.add_argument("acquisition_date", type=_parse_date, help="Acquisition date (YYYY-MM-DD).")
    add.set_defaults(func=_cmd_add)

    # list
    list_cmd = sub.add_parser("list", help="List tracked mounts.")
    list_cmd.add_argument(
        "--source", help="Filter mounts by source (case-insensitive)."
    )
    list_cmd.add_argument(
        "--rarity", type=_parse_rarity, help="Filter mounts by rarity."
    )
    list_cmd.set_defaults(func=_cmd_list)

    # update
    update = sub.add_parser("update", help="Update a mount record's fields.")
    update.add_argument("name", help="Mount name to update.")
    update.add_argument("--source", help="New source (how the mount was acquired).")
    update.add_argument("--rarity", type=_parse_rarity, help="New rarity tier.")
    update.add_argument(
        "--acquisition-date", type=_parse_date, dest="acquisition_date",
        help="New acquisition date (YYYY-MM-DD).",
    )
    update.set_defaults(func=_cmd_update)

    # remove
    remove = sub.add_parser("remove", help="Remove a mount record.")
    remove.add_argument("name", help="Mount name to remove.")
    remove.set_defaults(func=_cmd_remove)

    # export
    export_cmd = sub.add_parser("export", help="Export mounts to CSV.")
    export_cmd.add_argument("output", help="Path to the output CSV file.")
    export_cmd.set_defaults(func=_cmd_export)

    return parser


def _cmd_add(args: argparse.Namespace, store: MountStore) -> int:
    mount = Mount(
        name=args.name,
        source=args.source,
        rarity=args.rarity,
        acquisition_date=args.acquisition_date,
    )
    try:
        store.add(mount)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"added mount: {mount.name} ({mount.rarity.value})")
    return 0


def _cmd_update(args: argparse.Namespace, store: MountStore) -> int:
    mount = store.get(args.name)
    if mount is None:
        print(f"error: mount not tracked: {args.name}", file=sys.stderr)
        return 1

    updated = Mount(
        name=mount.name,
        source=args.source if args.source is not None else mount.source,
        rarity=args.rarity if args.rarity is not None else mount.rarity,
        acquisition_date=(
            args.acquisition_date if args.acquisition_date is not None
            else mount.acquisition_date
        ),
    )
    store.upsert(updated)
    print(f"updated mount: {updated.name}")
    return 0


def _cmd_list(args: argparse.Namespace, store: MountStore) -> int:
    mounts = store.all()
    if args.source:
        mounts = store.filter_by_source(args.source, mounts)
    if args.rarity:
        mounts = store.filter_by_rarity(args.rarity, mounts)

    if not mounts:
        print("no mounts tracked.")
        return 0

    header = f"{'Name':<28} {'Source':<30} {'Rarity':<10} {'Acquired':<12}"
    print(header)
    print("-" * len(header))
    for mount in mounts:
        print(
            f"{mount.name:<28} {mount.source:<30} "
            f"{mount.rarity.value:<10} {mount.acquisition_date_iso:<12}"
        )
    return 0


def _cmd_remove(args: argparse.Namespace, store: MountStore) -> int:
    try:
        removed = store.remove(args.name)
    except KeyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"removed mount: {removed.name}")
    return 0


def _cmd_export(args: argparse.Namespace, store: MountStore) -> int:
    mounts = store.all()
    export_csv(mounts, args.output)
    print(f"exported {len(mounts)} mount(s) to {args.output}")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    store = MountStore(args.data)
    return args.func(args, store)


if __name__ == "__main__":
    raise SystemExit(main())
