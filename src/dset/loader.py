from pathlib import Path

from dset.adapters import get_adapter
from dset.fetch import install
from dset.registry import get_manifest


def load(
    name: str,
    split: str = "train",
    accept_license: bool = False,
    streaming: bool = False,
):
    m = get_manifest(name)
    spec = m["adapter"]
    config = dict(spec.get("config") or {})

    if streaming:
        if m["source"]["type"] != "huggingface":
            raise NotImplementedError(
                f"streaming=True is only implemented for huggingface sources. "
                f"'{name}' uses '{m['source']['type']}'."
            )
        config["streaming"] = True
        cls = get_adapter(spec["name"])
        return cls(root=Path("."), split=split, config=config)

    root = install(name, accept_license=accept_license)
    cls = get_adapter(spec["name"])
    return cls(root=root, split=split, config=config)
