import os
from pathlib import Path


def cache_root() -> Path:
    root = Path(os.environ.get("DSET_CACHE", Path.home() / ".cache" / "dset"))
    root.mkdir(parents=True, exist_ok=True)
    return root


def blobs_dir() -> Path:
    d = cache_root() / "blobs"
    d.mkdir(parents=True, exist_ok=True)
    return d


def extracted_dir(name: str, version: str) -> Path:
    d = cache_root() / "extracted" / f"{name}@{version}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def licenses_file() -> Path:
    return cache_root() / "accepted-licenses.json"
