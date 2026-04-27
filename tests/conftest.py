import csv
import http.server
import json
import socketserver
import threading

import pytest
from PIL import Image


@pytest.fixture
def tmp_cache(tmp_path, monkeypatch):
    cache = tmp_path / "cache"
    monkeypatch.setenv("DSET_CACHE", str(cache))
    return cache


@pytest.fixture
def synthetic_image_folder(tmp_path):
    """ImageFolder-style: <root>/<split>/<class>/*.jpg"""
    root = tmp_path / "folder_data"
    for split in ("train", "val"):
        for cls_idx, cls in enumerate(("cat", "dog")):
            d = root / split / cls
            d.mkdir(parents=True)
            for i in range(3):
                Image.new("RGB", (32, 32), (cls_idx * 100, i * 30, 0)).save(
                    d / f"{i}.jpg"
                )
    return root


@pytest.fixture
def synthetic_mask_pairs(tmp_path):
    images = tmp_path / "images"
    masks = tmp_path / "masks"
    images.mkdir()
    masks.mkdir()
    for i in range(3):
        Image.new("RGB", (32, 32), (i * 50, 0, 0)).save(images / f"sample{i}.jpg")
        Image.new("L", (32, 32), i + 1).save(masks / f"sample{i}.png")
    return tmp_path


@pytest.fixture
def synthetic_csv_classification(tmp_path):
    images = tmp_path / "images"
    images.mkdir()
    label_cols = ["MEL", "NV", "BCC"]
    rows = []
    for i in range(4):
        Image.new("RGB", (32, 32), (i * 60, 0, 0)).save(images / f"img{i}.jpg")
        row = {"image": f"img{i}", **{c: 0 for c in label_cols}}
        row[label_cols[i % len(label_cols)]] = 1
        rows.append(row)
    csv_path = tmp_path / "labels.csv"
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["image"] + label_cols)
        w.writeheader()
        w.writerows(rows)
    return tmp_path


@pytest.fixture
def synthetic_coco(tmp_path):
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    Image.new("RGB", (64, 64), (255, 0, 0)).save(images_dir / "a.jpg")
    Image.new("RGB", (64, 64), (0, 255, 0)).save(images_dir / "b.jpg")
    coco = {
        "images": [
            {"id": 1, "file_name": "a.jpg", "width": 64, "height": 64},
            {"id": 2, "file_name": "b.jpg", "width": 64, "height": 64},
        ],
        "annotations": [
            {
                "id": 1, "image_id": 1, "category_id": 1, "iscrowd": 0,
                "segmentation": [[10, 10, 50, 10, 50, 50, 10, 50]],
            },
            {
                "id": 2, "image_id": 2, "category_id": 2, "iscrowd": 0,
                "segmentation": [[20, 20, 60, 20, 60, 60, 20, 60]],
            },
            {
                # RLE annotation — should be skipped
                "id": 3, "image_id": 1, "category_id": 3, "iscrowd": 1,
                "segmentation": {"size": [64, 64], "counts": "abc"},
            },
        ],
        "categories": [
            {"id": 1, "name": "cat"},
            {"id": 2, "name": "dog"},
            {"id": 3, "name": "crowd"},
        ],
    }
    (tmp_path / "anns.json").write_text(json.dumps(coco))
    return tmp_path


@pytest.fixture
def http_server(tmp_path):
    """Serves tmp_path/served on a random local port. Yields (base_url, served_dir)."""
    served = tmp_path / "served"
    served.mkdir()

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(served), **kwargs)

        def log_message(self, *args, **kwargs):
            pass  # silence stderr in tests

    httpd = socketserver.TCPServer(("127.0.0.1", 0), Handler)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}", served
    finally:
        httpd.shutdown()
        httpd.server_close()
