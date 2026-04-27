import pytest

from dset.registry import get_manifest, list_datasets


def test_list_includes_bundled():
    names = list_datasets()
    for expected in ("oxford-pets", "hymenoptera", "isic-2019", "mnist", "carvana"):
        assert expected in names


def test_get_manifest_oxford_pets():
    m = get_manifest("oxford-pets")
    assert m["name"] == "oxford-pets"
    assert m["task"] == "segmentation"
    assert m["adapter"]["name"] == "mask_segmentation"


def test_get_manifest_unknown_raises():
    with pytest.raises(ValueError, match="No manifest found"):
        get_manifest("definitely-not-a-real-dataset")


def test_user_manifest_dir_overrides_bundled(tmp_path, monkeypatch):
    user_dir = tmp_path / "manifests"
    user_dir.mkdir()
    (user_dir / "my-private.yaml").write_text(
        "name: my-private\nversion: '1'\ntask: classification\n"
        "source: {type: http, files: []}\nadapter: {name: csv_classification, config: {}}\n"
    )
    monkeypatch.setenv("DSET_MANIFEST_DIR", str(user_dir))
    assert "my-private" in list_datasets()
    assert get_manifest("my-private")["name"] == "my-private"
