import numpy as np
from PIL import Image

from dset.adapters.coco_segmentation import COCOSegmentation
from dset.adapters.csv_classification import CSVClassification
from dset.adapters.folder_classification import FolderClassification
from dset.adapters.mask_segmentation import MaskSegmentation


def test_folder_classification_loads_classes_and_samples(synthetic_image_folder):
    ds = FolderClassification(
        root=synthetic_image_folder,
        split="train",
        config={},
    )
    assert ds.classes == ["cat", "dog"]
    assert ds.class_to_idx == {"cat": 0, "dog": 1}
    assert len(ds) == 6  # 2 classes × 3 imgs

    img, label = ds[0]
    assert isinstance(img, Image.Image)
    assert label == 0  # first sample is cat


def test_folder_classification_split_map(synthetic_image_folder):
    ds = FolderClassification(
        root=synthetic_image_folder,
        split="validation",
        config={"split_map": {"validation": "val"}},
    )
    assert len(ds) == 6


def test_mask_segmentation_pairs(synthetic_mask_pairs):
    ds = MaskSegmentation(
        root=synthetic_mask_pairs,
        split="train",
        config={
            "images_dir": "images",
            "masks_dir": "masks",
            "image_ext": ".jpg",
            "mask_ext": ".png",
        },
    )
    assert len(ds) == 3
    img, mask = ds[0]
    assert isinstance(img, Image.Image)
    assert isinstance(mask, np.ndarray)
    assert mask.shape == (32, 32)


def test_csv_classification(synthetic_csv_classification):
    ds = CSVClassification(
        root=synthetic_csv_classification,
        split="train",
        config={
            "images_dir": "images",
            "labels_csv": "labels.csv",
            "id_column": "image",
            "label_columns": ["MEL", "NV", "BCC"],
            "image_ext": ".jpg",
        },
    )
    assert len(ds) == 4
    assert ds.classes == ["MEL", "NV", "BCC"]
    img, label = ds[0]
    assert isinstance(img, Image.Image)
    assert label == 0  # img0 → MEL
    assert ds[1][1] == 1  # img1 → NV
    assert ds[2][1] == 2  # img2 → BCC
    assert ds[3][1] == 0  # img3 → MEL again


def test_coco_segmentation_rasterizes_polygons(synthetic_coco):
    ds = COCOSegmentation(
        root=synthetic_coco,
        split="train",
        config={
            "images_dir": "images",
            "annotations_file": "anns.json",
        },
    )
    assert len(ds) == 2  # RLE annotation skipped, but its image still has polygon ann

    # Image 1: polygon square at (10,10)-(50,50), category_id=1
    img, mask = ds[0]
    assert isinstance(img, Image.Image)
    assert mask.shape == (64, 64)
    assert mask[30, 30] == 1   # inside square
    assert mask[5, 5] == 0     # outside

    # Image 2: polygon square at (20,20)-(60,60), category_id=2
    _, mask2 = ds[1]
    assert mask2[40, 40] == 2
    assert mask2[5, 5] == 0


def test_coco_segmentation_category_filter(synthetic_coco):
    ds = COCOSegmentation(
        root=synthetic_coco,
        split="train",
        config={
            "images_dir": "images",
            "annotations_file": "anns.json",
            "category_ids": [1],  # only cats
        },
    )
    assert len(ds) == 1
