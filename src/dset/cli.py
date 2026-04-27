import argparse
import shutil
import sys
from pathlib import Path

from dset.cache import cache_root, extracted_dir
from dset.fetch import install
from dset.registry import get_manifest, list_datasets


def _human_bytes(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def _dir_size(p: Path) -> int:
    if not p.exists():
        return 0
    return sum(f.stat().st_size for f in p.rglob("*") if f.is_file())


def main() -> None:
    p = argparse.ArgumentParser(prog="dset")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="List available datasets")

    p_info = sub.add_parser("info", help="Show manifest details")
    p_info.add_argument("name")

    p_inst = sub.add_parser("install", help="Fetch + extract a dataset")
    p_inst.add_argument("name")
    p_inst.add_argument("--accept-license", action="store_true")

    p_where = sub.add_parser("where", help="Show local cache path for a dataset")
    p_where.add_argument("name")

    p_clean = sub.add_parser("clean", help="Remove a dataset from local cache")
    p_clean.add_argument("name")
    p_clean.add_argument("--yes", action="store_true", help="Skip confirmation")

    sub.add_parser("cache-info", help="Show on-disk cache size per dataset")

    args = p.parse_args()

    if args.cmd == "list":
        for n in list_datasets():
            print(n)

    elif args.cmd == "info":
        m = get_manifest(args.name)
        print(f"name:    {m['name']}")
        print(f"version: {m.get('version', '?')}")
        print(f"task:    {m.get('task')}")
        print(f"license: {m.get('license', '?')}")
        print(f"source:  {m['source']['type']}")
        if (m["source"].get("auth") or {}).get("kind"):
            print(f"auth:    {m['source']['auth']['kind']}")
        print(f"adapter: {m['adapter']['name']}")

    elif args.cmd == "install":
        path = install(args.name, accept_license=args.accept_license)
        print(f"\nInstalled to: {path}")

    elif args.cmd == "where":
        m = get_manifest(args.name)
        print(extracted_dir(m["name"], str(m.get("version", "unknown"))))

    elif args.cmd == "clean":
        m = get_manifest(args.name)
        target = extracted_dir(m["name"], str(m.get("version", "unknown")))
        if not target.exists():
            print(f"Nothing to clean for '{args.name}'.")
            return
        size = _human_bytes(_dir_size(target))
        if not args.yes:
            ans = input(f"Remove {target} ({size})? [y/N]: ").strip().lower()
            if ans != "y":
                print("Aborted.")
                return
        shutil.rmtree(target)
        print(f"Removed {target}")

    elif args.cmd == "cache-info":
        root = cache_root()
        extracted = root / "extracted"
        blobs = root / "blobs"
        print(f"Cache root: {root}")
        if extracted.exists():
            entries = sorted(extracted.iterdir())
            for d in entries:
                print(f"  {d.name:<40} {_human_bytes(_dir_size(d))}")
        print(f"  {'(blobs)':<40} {_human_bytes(_dir_size(blobs))}")
        print(f"  {'TOTAL':<40} {_human_bytes(_dir_size(root))}")


if __name__ == "__main__":
    sys.exit(main())
