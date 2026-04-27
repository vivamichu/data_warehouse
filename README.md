# dset

> One line to load any ML dataset, anywhere. No more "register, click EULA, unzip, write a Dataset class" 17 times a year.

[![CI](https://github.com/vivamichu/data_warehouse/actions/workflows/ci.yml/badge.svg)](https://github.com/vivamichu/data_warehouse/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

```python
from dset import load

ds = load("oxford-pets")              # segmentation, ~800 MB, fetched + cached
img, mask = ds[0]

ds = load("isic-2019", accept_license=True)   # registration-gated medical
img, label = ds[0]

ds = load("mnist", streaming=True)    # HF Hub, no download
```

`dset` is a **package manager for ML datasets**. It doesn't host data — it
*resolves* dataset names to wherever the data actually lives (HuggingFace, Kaggle,
academic mirrors, S3, your own servers), handles auth and licensing, normalizes
the on-disk format, and caches everything locally so you only download once.

Think `pip` for datasets, or `Homebrew` formulas for ML data.

---

## Why this exists

Every ML practitioner has done this dance:

1. Find dataset → download zip → unzip → realize the format is weird
2. Write a custom `Dataset` class to load it
3. Forget which laptop has the cached copy
4. Re-download 5 GB next week
5. Repeat for every project

HuggingFace `datasets` solved this for ~80% of NLP, but the long tail of
computer-vision and domain-specific datasets (ISIC, BraTS, Cityscapes, KITTI,
ChestX-ray14, ...) is still a manual mess.

`dset` is the package manager that didn't exist for that long tail.

## Install

```bash
pip install -e .              # from a clone
# pip install dset            # (PyPI release coming)

# Optional extras
pip install dset[hf]          # HuggingFace source
pip install dset[kaggle]      # Kaggle source
pip install dset[torch]       # PyTorch DataLoader integration
```

## Usage

```python
from dset import load

# Classification
ds = load("hymenoptera")
img, label = ds[0]                         # PIL.Image, int

# Segmentation — same call shape, different return
ds = load("oxford-pets")
img, mask = ds[0]                          # PIL.Image, np.ndarray

# Drop into PyTorch
from torch.utils.data import DataLoader
loader = DataLoader(ds, batch_size=16, num_workers=4, shuffle=True)

# Streaming (no download — pulls samples on demand)
ds = load("mnist", streaming=True)
```

### CLI

```bash
dset list                       # all available datasets
dset info oxford-pets           # show manifest details
dset install oxford-pets        # fetch + extract (cached at ~/.cache/dset)
dset install isic-2019 --accept-license
dset where oxford-pets          # print local cache path
dset cache-info                 # disk usage per dataset
dset clean oxford-pets          # remove from cache
```

## How it works

A YAML **manifest** describes each dataset: where to fetch it, what auth it
needs, how to lay it out on disk, and which **adapter** turns the on-disk files
into `(image, target)` samples.

```yaml
# src/dset/manifests/oxford-pets.yaml
name: oxford-pets
task: segmentation
license: CC-BY-SA-4.0
source:
  type: http
  files:
    - url: https://www.robots.ox.ac.uk/~vgg/data/pets/data/images.tar.gz
    - url: https://www.robots.ox.ac.uk/~vgg/data/pets/data/annotations.tar.gz
post_fetch: [{extract: "*.tar.gz"}]
adapter:
  name: mask_segmentation
  config:
    images_dir: images/
    masks_dir: annotations/trimaps/
```

**Adding a new dataset = writing one YAML file.** Adding a new on-disk format
= one Python class. That's the whole architecture.

## What ships today

| Source types | Adapters | CLI | Tests |
|---|---|---|---|
| HTTP, HuggingFace, Kaggle | `mask_segmentation`, `csv_classification`, `folder_classification`, `coco_segmentation`, `hf_passthrough` | list, info, install, where, clean, cache-info | 25 passing |

| Bundled manifests |
|---|
| oxford-pets, hymenoptera, isic-2019, mnist, carvana, coco-2017-val |

## Roadmap

**v0.1 (next)**
- [ ] PyPI release
- [ ] Google Drive source (with virus-scan interstitial handling)
- [ ] `dset gc` for LRU eviction by total cache size
- [ ] 25 more bundled manifests across CV
- [ ] Optional content-addressed dedup (sha256 cache keys)

**v0.2**
- [ ] WebDataset / MosaicML Streaming source for sharded data
- [ ] Detection adapter (YOLO + COCO bbox formats)
- [ ] Per-team / per-org manifest registries

**v1.0**
- [ ] LAN peer cache (mDNS-discovered shared cache across machines)
- [ ] On-prem appliance for air-gapped GPUs

## 🤝 We need contributors

This project only matters if it covers the dataset *you* care about. Adding
one is **5 minutes and one YAML file** — see [CONTRIBUTING.md](CONTRIBUTING.md).

The most useful first contributions:

- **Add a manifest** for a dataset that isn't here yet — see the
  [new dataset issue template](.github/ISSUE_TEMPLATE/new_dataset_request.md)
- **Add a source type** (Google Drive, Zenodo, S3 requester-pays, ...)
- **Add an adapter** for an unsupported on-disk format
- **Find a broken link** in an existing manifest and fix it

Open a discussion or issue if you're not sure where to start.

## License

[MIT](LICENSE). Dataset licenses are the dataset's own — `dset` only resolves
and caches; it does not relicense anything.
