from .base import BaseStore
from .exc import StorageError, StorageFileNotFoundError, StorageFileExistsError


class MemoryStore(BaseStore):
    def __init__(self):
        self._store = {}

    def fetch(self, path: str) -> bytes:
        try:
            return self._store[path]
        except KeyError:
            raise StorageFileNotFoundError(path)

    def store(self, path: str, content: bytes):
        if path in self._store:
            raise StorageFileExistsError(path)

        return self.replace(path, content)

    def replace(self, path: str, content: bytes):
        self._store[path] = content

    def delete(self, path: str):
        try:
            del self._store[path]
        except KeyError:
            raise StorageFileNotFoundError(path)

    def exists(self, path: str):
        return path in self._store
