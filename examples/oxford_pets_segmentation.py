"""Minimal end-to-end: fetch Oxford-IIIT Pets, iterate it as a PyTorch DataLoader."""
import numpy as np
from torch.utils.data import DataLoader

from dset import load


def collate(batch):
    imgs = [np.array(img.resize((256, 256))) for img, _ in batch]
    masks = [np.array(  # quick resize via PIL would be better; nearest-neighbor crop here
        m[: 256, : 256]
    ) for _, m in batch]
    return np.stack(imgs), np.stack(masks)


def main() -> None:
    ds = load("oxford-pets")
    print(f"Loaded {len(ds)} samples from oxford-pets")

    img, mask = ds[0]
    print(f"Sample 0: image={img.size}, mask shape={mask.shape}, mask dtype={mask.dtype}")
    print(f"Mask classes present: {sorted(set(mask.flatten().tolist()))}")

    loader = DataLoader(ds, batch_size=4, num_workers=0, collate_fn=collate)
    for imgs, masks in loader:
        print(f"Batch: imgs={imgs.shape}, masks={masks.shape}")
        break


if __name__ == "__main__":
    main()
