import os
from importlib import resources
from pathlib import Path

import yaml


def _user_manifest_dirs() -> list[Path]:
    dirs = []
    if env := os.environ.get("DSET_MANIFEST_DIR"):
        dirs.append(Path(env))
    user = Path.home() / ".config" / "dset" / "manifests"
    if user.exists():
        dirs.append(user)
    return dirs


def _bundled_manifests():
    base = resources.files("dset") / "manifests"
    for p in base.iterdir():
        if p.name.endswith(".yaml"):
            yield p.name[:-5], p.read_text()


def list_datasets() -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for d in _user_manifest_dirs():
        for p in sorted(d.glob("*.yaml")):
            if p.stem not in seen:
                seen.add(p.stem)
                out.append(p.stem)
    for name, _ in _bundled_manifests():
        if name not in seen:
            seen.add(name)
            out.append(name)
    return sorted(out)


def get_manifest(name: str) -> dict:
    for d in _user_manifest_dirs():
        p = d / f"{name}.yaml"
        if p.exists():
            return yaml.safe_load(p.read_text())
    for n, text in _bundled_manifests():
        if n == name:
            return yaml.safe_load(text)
    raise ValueError(
        f"No manifest found for '{name}'. Available: {list_datasets()}"
    )
