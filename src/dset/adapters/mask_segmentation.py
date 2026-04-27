import numpy as np
from PIL import Image

from dset.adapters.base import DatasetAdapter


class MaskSegmentation(DatasetAdapter):
    task = "segmentation"

    def __init__(self, root, split, config):
        super().__init__(root, split, config)
        images_dir = self.root / config["images_dir"]
        masks_dir = self.root / config["masks_dir"]
        image_ext = config.get("image_ext", ".jpg")
        mask_ext = config.get("mask_ext", ".png")

        self.samples = []
        for img_path in sorted(images_dir.rglob(f"*{image_ext}")):
            stem = img_path.stem
            mask_path = masks_dir / f"{stem}{mask_ext}"
            if mask_path.exists():
                self.samples.append((img_path, mask_path))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, i):
        img_path, mask_path = self.samples[i]
        img = Image.open(img_path).convert("RGB")
        mask = np.array(Image.open(mask_path))
        return img, mask
