import pytest

from storage.exc import (
    StorageFileNotFoundError,
    StorageFileExistsError,
)


def test_fetch_missing_file_raises_filenotfound(store):
    with pytest.raises(StorageFileNotFoundError):
        store.fetch("does-not-exist")


def test_store_file_can_be_fetched(store, random_string):
    expected = b"this is a test"

    store.store(random_string, expected)
    res = store.fetch(random_string)

    assert res == expected


def test_cannot_store_duplicate_file(store, random_string):
    expected = b"this is a test"

    store.store(random_string, expected)
    with pytest.raises(StorageFileExistsError):
        store.store(random_string, expected)


def test_can_replace_duplicate_file(store, random_string):
    store.store(random_string, b"original content")
    store.replace(random_string, b"replaced content")

    have = store.fetch(random_string)
    assert have == b"replaced content"


def test_file_is_not_found_after_delete(store, random_string):
    expected = b"this is a test"

    store.store(random_string, expected)
    store.delete(random_string)

    with pytest.raises(StorageFileNotFoundError):
        store.fetch(random_string)


def test_file_exists_after_store(store, random_string):
    expected = b"this is a test"

    assert not store.exists(random_string)
    store.store(random_string, expected)
    assert store.exists(random_string)
    assert store.fetch(random_string) == expected


def test_delete_missing_file_raises_filenotfound(store, random_string):
    with pytest.raises(StorageFileNotFoundError):
        store.delete(random_string)
