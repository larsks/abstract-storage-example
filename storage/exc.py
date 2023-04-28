class StorageError(Exception):
    pass


class StorageFileNotFoundError(StorageError):
    pass


class StorageFileExistsError(StorageError):
    pass


class StorageInvalidPathError(StorageError):
    pass
