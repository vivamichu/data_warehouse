import hashlib

import pytest

from dset.auth.http import download


def test_download_writes_file(http_server, tmp_path):
    base_url, served = http_server
    (served / "hello.bin").write_bytes(b"hello world")
    dest = tmp_path / "out.bin"
    download(f"{base_url}/hello.bin", dest)
    assert dest.read_bytes() == b"hello world"


def test_download_skips_when_already_present(http_server, tmp_path):
    base_url, served = http_server
    (served / "x.bin").write_bytes(b"NEW")
    dest = tmp_path / "out.bin"
    dest.write_bytes(b"EXISTING")
    download(f"{base_url}/x.bin", dest)
    assert dest.read_bytes() == b"EXISTING"


def test_download_sha256_verify_passes(http_server, tmp_path):
    base_url, served = http_server
    payload = b"verified content"
    (served / "v.bin").write_bytes(payload)
    sha = hashlib.sha256(payload).hexdigest()

    dest = tmp_path / "v.bin"
    download(f"{base_url}/v.bin", dest, sha256=sha)
    assert dest.read_bytes() == payload


def test_download_sha256_mismatch_raises(http_server, tmp_path):
    base_url, served = http_server
    (served / "bad.bin").write_bytes(b"actual content")
    dest = tmp_path / "bad.bin"
    with pytest.raises(ValueError, match="sha256"):
        download(f"{base_url}/bad.bin", dest, sha256="0" * 64)
    assert not dest.exists()
