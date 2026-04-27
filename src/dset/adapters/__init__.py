from dset.adapters.coco_segmentation import COCOSegmentation
from dset.adapters.csv_classification import CSVClassification
from dset.adapters.folder_classification import FolderClassification
from dset.adapters.hf_passthrough import HFPassthrough
from dset.adapters.mask_segmentation import MaskSegmentation

ADAPTERS = {
    "mask_segmentation": MaskSegmentation,
    "csv_classification": CSVClassification,
    "folder_classification": FolderClassification,
    "coco_segmentation": COCOSegmentation,
    "hf_passthrough": HFPassthrough,
}


def get_adapter(name: str):
    if name not in ADAPTERS:
        raise ValueError(
            f"Unknown adapter '{name}'. Available: {sorted(ADAPTERS)}"
        )
    return ADAPTERS[name]
