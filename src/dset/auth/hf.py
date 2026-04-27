"""HuggingFace Hub source — delegates to the `datasets` library."""
from pathlib import Path


def fetch(repo: str, target: Path, config_name: str | None = None) -> Path:
    try:
        from datasets import load_dataset  # noqa: F401
    except ImportError as e:
        raise ImportError(
            "HuggingFace source requires `datasets`. Install with: pip install dset[hf]"
        ) from e
    # We don't materialize anything here; HF caches into its own dir.
    # Just touch the target so install() considers it complete.
    target.mkdir(parents=True, exist_ok=True)
    return target
