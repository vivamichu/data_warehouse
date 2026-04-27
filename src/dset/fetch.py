import shutil
import tarfile
import zipfile
from pathlib import Path

from dset.auth import http, registration
from dset.cache import blobs_dir, extracted_dir
from dset.registry import get_manifest


def install(name: str, accept_license: bool = False) -> Path:
    m = get_manifest(name)
    version = str(m.get("version", "unknown"))
    target = extracted_dir(name, version)
    if (target / ".dset_complete").exists():
        return target

    src = m["source"]
    auth = src.get("auth") or {}
    kind = auth.get("kind")

    if kind == "registration":
        ok = registration.prompt_and_accept(
            name,
            auth.get("eula_url", ""),
            auth.get("prompt", ""),
            auto=accept_license,
        )
        if not ok:
            raise RuntimeError(f"License for '{name}' not accepted; cannot install.")

    src_type = src["type"]
    if src_type == "http":
        _install_http(src, m, target)
    elif src_type == "huggingface":
        _install_hf(src, target)
    elif src_type == "kaggle":
        _install_kaggle(src, m, target)
    else:
        raise NotImplementedError(f"Source type '{src_type}' is not implemented.")

    (target / ".dset_complete").touch()
    return target


def _install_http(src: dict, manifest: dict, target: Path) -> None:
    downloaded: list[Path] = []
    for f in src["files"]:
        url = f["url"]
        sha = f.get("sha256")
        fname = url.rsplit("/", 1)[-1].split("?", 1)[0]
        dest = blobs_dir() / fname
        http.download(url, dest, sha256=sha)
        downloaded.append(dest)

    extracted_any = False
    for step in manifest.get("post_fetch") or []:
        if "extract" in step:
            for blob in downloaded:
                _extract_or_copy(blob, target)
            extracted_any = True

    if not extracted_any:
        for blob in downloaded:
            dst = target / blob.name
            if not dst.exists():
                shutil.copy(blob, dst)


def _install_hf(src: dict, target: Path) -> None:
    from dset.auth import hf
    hf.fetch(src["repo"], target, config_name=src.get("config_name"))


def _install_kaggle(src: dict, manifest: dict, target: Path) -> None:
    from dset.auth import kaggle
    kaggle.fetch(src, target)
    # Kaggle downloads land directly in target, often pre-extracted by the API.
    # If any zips remain, expand them.
    for step in manifest.get("post_fetch") or []:
        if "extract" in step:
            for blob in list(target.iterdir()):
                if blob.suffix.lower() in (".zip", ".tar", ".gz", ".tgz", ".bz2"):
                    _extract_or_copy(blob, target)


def _extract_or_copy(archive: Path, dest: Path) -> None:
    name = archive.name.lower()
    if name.endswith(".zip"):
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(dest)
    elif name.endswith((".tar.gz", ".tgz", ".tar.bz2", ".tbz2", ".tar")):
        with tarfile.open(archive) as tf:
            tf.extractall(dest)
    else:
        shutil.copy(archive, dest / archive.name)
