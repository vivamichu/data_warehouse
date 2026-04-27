import sys

import pytest

from dset.cli import main


def _run(monkeypatch, *argv):
    monkeypatch.setattr(sys, "argv", ["dset", *argv])
    main()


def test_cli_list(capsys, monkeypatch):
    _run(monkeypatch, "list")
    out = capsys.readouterr().out
    assert "oxford-pets" in out
    assert "hymenoptera" in out


def test_cli_info(capsys, monkeypatch):
    _run(monkeypatch, "info", "oxford-pets")
    out = capsys.readouterr().out
    assert "segmentation" in out
    assert "mask_segmentation" in out


def test_cli_info_unknown_dataset(monkeypatch):
    with pytest.raises(ValueError):
        _run(monkeypatch, "info", "no-such-dataset")


def test_cli_cache_info(tmp_cache, capsys, monkeypatch):
    _run(monkeypatch, "cache-info")
    out = capsys.readouterr().out
    assert "Cache root" in out
    assert "TOTAL" in out


def test_cli_streaming_rejected_for_non_hf_source():
    """Verifies the streaming flag raises a clear error for HTTP sources via Python API."""
    from dset import load
    with pytest.raises(NotImplementedError, match="huggingface"):
        load("oxford-pets", streaming=True)
