"""End-to-end install via a custom manifest pointing to a local HTTP server."""
import zipfile

from PIL import Image

from dset.fetch import install


def _build_zip(zip_path, image_filenames):
    with zipfile.ZipFile(zip_path, "w") as zf:
        for name in image_filenames:
            img = Image.new("RGB", (16, 16))
            img_bytes_path = zip_path.parent / name
            img_bytes_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(img_bytes_path)
            zf.write(img_bytes_path, arcname=name)
            img_bytes_path.unlink()


def test_install_http_downloads_and_extracts(http_server, tmp_cache, tmp_path, monkeypatch):
    base_url, served = http_server

    # Build a tiny zip and serve it
    zip_path = served / "tiny.zip"
    _build_zip(zip_path, ["images/0.jpg", "images/1.jpg"])

    # Write a user manifest pointing to the zip
    manifests = tmp_path / "manifests"
    manifests.mkdir()
    (manifests / "tiny.yaml").write_text(
        f"""
name: tiny
version: '1'
task: classification
license: TEST
source:
  type: http
  files:
    - url: {base_url}/tiny.zip
post_fetch:
  - extract: '*.zip'
adapter:
  name: folder_classification
  config: {{}}
"""
    )
    monkeypatch.setenv("DSET_MANIFEST_DIR", str(manifests))

    target = install("tiny")
    assert target.exists()
    assert (target / ".dset_complete").exists()
    assert (target / "images" / "0.jpg").exists()
    assert (target / "images" / "1.jpg").exists()


def test_install_is_idempotent(http_server, tmp_cache, tmp_path, monkeypatch):
    base_url, served = http_server
    zip_path = served / "tiny2.zip"
    _build_zip(zip_path, ["a.jpg"])

    manifests = tmp_path / "manifests"
    manifests.mkdir()
    (manifests / "tiny2.yaml").write_text(
        f"""
name: tiny2
version: '1'
task: classification
license: TEST
source:
  type: http
  files:
    - url: {base_url}/tiny2.zip
post_fetch:
  - extract: '*.zip'
adapter:
  name: folder_classification
  config: {{}}
"""
    )
    monkeypatch.setenv("DSET_MANIFEST_DIR", str(manifests))

    t1 = install("tiny2")
    mtime1 = (t1 / ".dset_complete").stat().st_mtime

    t2 = install("tiny2")
    mtime2 = (t2 / ".dset_complete").stat().st_mtime

    assert t1 == t2
    assert mtime1 == mtime2  # not re-touched on second call
