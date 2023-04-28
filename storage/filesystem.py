import os
from pathlib import Path

from .base import BaseStore
from .exc import (
    StorageError,
    StorageFileNotFoundError,
    StorageFileExistsError,
    StorageInvalidPathError,
)


class FilesystemStore(BaseStore):
    def __init__(self, root: str = "/"):
        self.root = Path(root)

        if not self.root.is_dir():
            raise StorageError(f"{root} is not a directory")

    def resolve(self, path: str):
        _path = Path(path)
        if _path.root == "/":
            _path = _path.relative_to("/")

        _resolved = (self.root / _path).resolve()
        if self.root not in _resolved.parents:
            raise StorageInvalidPathError(path)

        return str(_resolved)

    def fetch(self, path: str) -> bytes:
        try:
            with open(self.resolve(path), "rb") as fd:
                return fd.read()
        except FileNotFoundError:
            raise StorageFileNotFoundError(path)

    def store(self, path: str, content: bytes):
        if os.path.exists(self.resolve(path)):
            raise StorageFileExistsError(path)

        return self.replace(path, content)

    def replace(self, path: str, content: bytes):
        resolved = self.resolve(path)
        os.makedirs(os.path.dirname(resolved), exist_ok=True)
        with open(resolved, "wb") as fd:
            fd.write(content)

    def delete(self, path: str):
        try:
            os.unlink(self.resolve(path))
        except FileNotFoundError:
            raise StorageFileNotFoundError(path)

    def exists(self, path: str):
        return os.path.isfile(self.resolve(path))
