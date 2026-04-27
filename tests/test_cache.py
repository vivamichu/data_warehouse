from dset.cache import blobs_dir, cache_root, extracted_dir, licenses_file


def test_cache_root_respects_env(tmp_cache):
    assert cache_root() == tmp_cache
    assert tmp_cache.is_dir()


def test_blobs_dir_is_under_cache(tmp_cache):
    assert blobs_dir().parent == tmp_cache


def test_extracted_dir_versioned(tmp_cache):
    d = extracted_dir("foo", "1.2")
    assert d == tmp_cache / "extracted" / "foo@1.2"
    assert d.is_dir()


def test_licenses_file_path(tmp_cache):
    assert licenses_file() == tmp_cache / "accepted-licenses.json"
