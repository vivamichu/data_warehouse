"""Wraps a HuggingFace dataset as a dset adapter, matching the (image, label) shape."""
from dset.adapters.base import DatasetAdapter


class HFPassthrough(DatasetAdapter):
    task = "classification"  # default; manifest can override via config["task"]

    def __init__(self, root, split, config):
        super().__init__(root, split, config)
        try:
            from datasets import load_dataset
        except ImportError as e:
            raise ImportError(
                "HF adapter requires `datasets`. Install with: pip install dset[hf]"
            ) from e

        repo = config["repo"]
        config_name = config.get("config_name")
        streaming = config.get("streaming", False)

        ds = load_dataset(
            repo, name=config_name, split=split, streaming=streaming
        )
        self._ds = ds
        self.task = config.get("task", "classification")
        self._image_key = config.get("image_key", "image")
        self._label_key = config.get("label_key", "label")
        self._streaming = streaming

        if not streaming:
            self._len = len(ds)

    def __len__(self):
        if self._streaming:
            raise TypeError("Streaming HF datasets have no fixed length; iterate instead.")
        return self._len

    def __getitem__(self, i):
        if self._streaming:
            raise TypeError("Streaming HF datasets are iterable, not indexable.")
        sample = self._ds[i]
        return sample[self._image_key], sample[self._label_key]

    def __iter__(self):
        for sample in self._ds:
            yield sample[self._image_key], sample[self._label_key]
