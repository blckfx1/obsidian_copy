from pathlib import Path
import os

class Vault:
    def __init__(self, path: str = None):
        self.path = Path(path) if path else None

    def set_path(self, path: str):
        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)
        # Create Daily Notes folder
        (self.path / "Daily Notes").mkdir(exist_ok=True)

    def is_valid(self) -> bool:
        return self.path is not None and self.path.exists()

    def get_md_files(self):
        if not self.is_valid():
            return []
        return list(self.path.rglob("*.md"))