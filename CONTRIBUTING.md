# Contributing

**Thank you for being here.** This project only works if it has every dataset
worth caring about — and that's not something one person can build. The whole
shape of this project assumes a steady stream of small contributions from
people who use it.

Below: the easiest first contribution, then the slightly harder ones.

---

## ⭐ The easiest contribution: add a dataset (5 minutes, no Python)

You don't need to write any code. You write one YAML file.

**1. Pick a dataset that isn't here yet.** Check `dset list` (or
`src/dset/manifests/`) to see what's already covered.

**2. Copy an existing manifest as a template.** Match the auth pattern of
the dataset you're adding:

| Pattern | Copy from |
|---|---|
| Plain HTTP, no login | `oxford-pets.yaml` |
| Registration / EULA wall | `isic-2019.yaml` |
| Kaggle | `carvana.yaml` |
| HuggingFace Hub | `mnist.yaml` |

**3. Fill in:**
- `name` — kebab-case, unique
- `version` — your choice; bump on schema changes
- `task` — `classification` / `segmentation` / `detection`
- `license` — verbatim from the dataset's official page
- `citation` — the BibTeX-style or short form citation
- `source` — URL(s), or `kaggle:` / `huggingface:` reference
- `adapter` — pick one of: `mask_segmentation`, `csv_classification`,
  `folder_classification`, `coco_segmentation`, `hf_passthrough`

**4. Test it locally:**
```bash
dset install your-dataset-name
python -c "from dset import load; ds = load('your-dataset-name'); print(len(ds), ds[0])"
```

**5. Open a PR.** That's it. Use the "New dataset" PR template.

---

## Adding a new adapter (when no existing one fits)

Adapters live in `src/dset/adapters/`. Each one is ~30 lines. The contract:

```python
from dset.adapters.base import DatasetAdapter

class MyAdapter(DatasetAdapter):
    task = "classification"   # or "segmentation" / "detection"

    def __init__(self, root, split, config):
        super().__init__(root, split, config)
        # Build self.samples (or whatever index you need) here

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, i):
        # Return (image, target) — the shape depends on task
        return img, target
```

Then register it in `src/dset/adapters/__init__.py` and write a test in
`tests/test_adapters.py` using a synthetic-data fixture (see `conftest.py`
for examples). PRs without a test for the new adapter will be asked to add one.

---

## Adding a new source type (HTTP, Kaggle, HF, ... what's next?)

Source handlers live in `src/dset/auth/`. We're missing:

- `gdrive.py` — Google Drive (with virus-scan interstitial handling)
- `webdataset.py` / `mds.py` — sharded streaming sources
- `zenodo.py` — academic/Zenodo DOI-keyed datasets
- `s3.py` — anonymous and requester-pays S3 buckets

If you tackle one, wire it into `src/dset/fetch.py`'s dispatch.

---

## Setup

```bash
git clone <fork-url> dset
cd dset
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest                 # all 25 tests should pass
```

## Style

- No formatter required, but match the existing style (terse, no trailing
  whitespace, no docstring fluff).
- Type hints encouraged but not enforced.
- One feature per PR. Small PRs get reviewed faster.

## What we won't merge (yet)

- Hard dependencies on heavy libs (torch, jax, opencv) for core functionality
  — these belong in optional extras like `[torch]`.
- Adapters that require proprietary or paid services.
- Datasets whose license forbids redistribution *and* whose source URL we
  cannot legally link to (rare, but happens).

## Code of Conduct

By participating you agree to abide by the [Code of Conduct](CODE_OF_CONDUCT.md).

## Questions

Open a discussion or an issue. We aim to respond within a few days.
