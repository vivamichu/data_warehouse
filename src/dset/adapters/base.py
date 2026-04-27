from pathlib import Path


class DatasetAdapter:
    task: str = ""

    def __init__(self, root: Path, split: str, config: dict):
        self.root = Path(root)
        self.split = split
        self.config = config

    def __len__(self) -> int:
        raise NotImplementedError

    def __getitem__(self, i):
        raise NotImplementedError
