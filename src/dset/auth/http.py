import hashlib
from pathlib import Path

import requests
from tqdm import tqdm


def download(url: str, dest: Path, sha256: str | None = None) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and (sha256 is None or _sha256(dest) == sha256):
        return dest

    tmp = dest.with_suffix(dest.suffix + ".part")
    with requests.get(url, stream=True, timeout=60, allow_redirects=True) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        with open(tmp, "wb") as f, tqdm(
            total=total, unit="B", unit_scale=True, desc=dest.name
        ) as bar:
            for chunk in r.iter_content(chunk_size=1 << 20):
                if not chunk:
                    continue
                f.write(chunk)
                bar.update(len(chunk))

    if sha256 and _sha256(tmp) != sha256:
        tmp.unlink()
        raise ValueError(f"sha256 mismatch for {url}")
    tmp.rename(dest)
    return dest


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()
