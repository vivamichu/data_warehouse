import csv

from PIL import Image

from dset.adapters.base import DatasetAdapter


class CSVClassification(DatasetAdapter):
    task = "classification"

    def __init__(self, root, split, config):
        super().__init__(root, split, config)
        images_dir = self.root / config["images_dir"]
        labels_csv = self.root / config["labels_csv"]
        id_col = config["id_column"]
        label_cols = config["label_columns"]
        image_ext = config.get("image_ext", ".jpg")

        self.classes = label_cols
        self.samples = []
        with open(labels_csv) as f:
            reader = csv.DictReader(f)
            for row in reader:
                img_path = images_dir / f"{row[id_col]}{image_ext}"
                if not img_path.exists():
                    continue
                label = next(
                    (i for i, c in enumerate(label_cols) if float(row[c]) == 1.0),
                    -1,
                )
                if label >= 0:
                    self.samples.append((img_path, label))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, i):
        img_path, label = self.samples[i]
        return Image.open(img_path).convert("RGB"), label
