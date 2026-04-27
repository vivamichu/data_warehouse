"""Kaggle source — uses the official kaggle CLI auth at ~/.kaggle/kaggle.json."""
import json
import os
from pathlib import Path

KAGGLE_CRED = Path.home() / ".kaggle" / "kaggle.json"


def _ensure_credentials() -> tuple[str, str]:
    if not KAGGLE_CRED.exists():
        raise RuntimeError(
            f"Kaggle credentials not found at {KAGGLE_CRED}. "
            f"Create an API token at https://www.kaggle.com/settings/account "
            f"and place kaggle.json there."
        )
    cred = json.loads(KAGGLE_CRED.read_text())
    os.environ.setdefault("KAGGLE_USERNAME", cred["username"])
    os.environ.setdefault("KAGGLE_KEY", cred["key"])
    return cred["username"], cred["key"]


def fetch(spec: dict, target: Path) -> list[Path]:
    """spec keys:
      - dataset: "owner/name" for `kaggle datasets download`
      - competition: "name" for `kaggle competitions download`
      - files: optional list of specific file names
    """
    _ensure_credentials()
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
    except ImportError as e:
        raise ImportError(
            "Kaggle source requires `kaggle`. Install with: pip install dset[kaggle]"
        ) from e

    api = KaggleApi()
    api.authenticate()
    target.mkdir(parents=True, exist_ok=True)

    if "dataset" in spec:
        files = spec.get("files") or [None]
        for f in files:
            api.dataset_download_files(
                spec["dataset"], path=str(target), unzip=True, file_name=f
            )
    elif "competition" in spec:
        files = spec.get("files") or [None]
        for f in files:
            if f:
                api.competition_download_file(spec["competition"], f, path=str(target))
            else:
                api.competition_download_files(spec["competition"], path=str(target))
    else:
        raise ValueError("Kaggle source needs either 'dataset' or 'competition'.")

    return list(target.iterdir())
