import pytest

from storage import FilesystemStore
from storage.exc import (
    StorageError,
    StorageInvalidPathError,
)


def test_cannot_create_filesystem_store_in_missing_directory(tmp_path, random_string):
    with pytest.raises(StorageError):
        FilesystemStore(tmp_path / random_string)


@pytest.mark.parametrize(
    "path",
    (
        "../foo",
        "foo/bar/../../../baz",
    ),
)
def test_cannot_escape_filesystem_store(tmp_path, path):
    store = FilesystemStore(tmp_path)
    with pytest.raises(StorageInvalidPathError):
        store.store(path, b"example content")
