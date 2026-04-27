import json

import numpy as np
from PIL import Image, ImageDraw

from dset.adapters.base import DatasetAdapter


class COCOSegmentation(DatasetAdapter):
    """Semantic segmentation from COCO-format polygon annotations.

    Each pixel of the returned mask holds the COCO category_id (0 = background).
    RLE-encoded annotations are skipped — install pycocotools and write a separate
    adapter if you need them.
    """

    task = "segmentation"

    def __init__(self, root, split, config):
        super().__init__(root, split, config)
        images_dir = self.root / config["images_dir"]
        anns_path = self.root / config["annotations_file"]

        with open(anns_path) as f:
            coco = json.load(f)

        self._images_dir = images_dir
        self._image_info = {img["id"]: img for img in coco["images"]}
        self.categories = {c["id"]: c["name"] for c in coco["categories"]}

        category_filter = set(config.get("category_ids") or [])
        anns_by_image: dict[int, list] = {}
        for ann in coco["annotations"]:
            if isinstance(ann.get("segmentation"), dict):
                continue  # RLE
            if category_filter and ann["category_id"] not in category_filter:
                continue
            anns_by_image.setdefault(ann["image_id"], []).append(ann)

        self._anns_by_image = anns_by_image
        self._image_ids = sorted(anns_by_image.keys())

    def __len__(self):
        return len(self._image_ids)

    def __getitem__(self, i):
        image_id = self._image_ids[i]
        info = self._image_info[image_id]
        img = Image.open(self._images_dir / info["file_name"]).convert("RGB")

        mask = Image.new("L", (info["width"], info["height"]), 0)
        draw = ImageDraw.Draw(mask)
        for ann in self._anns_by_image[image_id]:
            cat_id = ann["category_id"]
            for poly in ann["segmentation"]:
                xy = list(zip(poly[0::2], poly[1::2]))
                if len(xy) >= 3:
                    draw.polygon(xy, fill=cat_id)

        return img, np.array(mask)
