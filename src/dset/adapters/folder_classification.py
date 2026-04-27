from PIL import Image

from dset.adapters.base import DatasetAdapter

IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}


class FolderClassification(DatasetAdapter):
    """ImageFolder-style: <root>/<split>/<class_name>/*.jpg"""

    task = "classification"

    def __init__(self, root, split, config):
        super().__init__(root, split, config)
        base = self.root / config.get("base_dir", "")
        split_dir = base / config.get("split_map", {}).get(split, split)

        if not split_dir.is_dir():
            raise FileNotFoundError(
                f"Split directory not found: {split_dir}. "
                f"Available: {[p.name for p in base.iterdir() if p.is_dir()]}"
            )

        self.classes = sorted(p.name for p in split_dir.iterdir() if p.is_dir())
        self.class_to_idx = {c: i for i, c in enumerate(self.classes)}

        self.samples = []
        for cls in self.classes:
            for img in sorted((split_dir / cls).iterdir()):
                if img.suffix.lower() in IMG_EXTS:
                    self.samples.append((img, self.class_to_idx[cls]))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, i):
        img_path, label = self.samples[i]
        return Image.open(img_path).convert("RGB"), label
