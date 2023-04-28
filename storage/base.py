from abc import ABC
from abc import abstractmethod


class BaseStore(ABC):
    @abstractmethod
    def fetch(self, path: str) -> bytes:
        """Fetch content from the store.

        :param str path: Path to the content
        :return: Content as bytes
        """

    @abstractmethod
    def store(self, path: str, content: bytes):
        """Write content to the store. Raise StorageFileExistsError if
        the file already exists.

        :param str path: Path to the content
        :param bytes content: The file content as bytes
        """

    @abstractmethod
    def replace(self, path: str, content: bytes):
        """Write content to the store. Replace existing content.

        :param str path: Path to the content
        :param bytes content: The file content as bytes
        """

    @abstractmethod
    def delete(self, path: str):
        """Delete a file from the store.

        :param str path: Path to file to delete
        """

    @abstractmethod
    def exists(self, path: str) -> bool:
        """Test if a file exists.

        :param str path: Path to the file
        :returns: True if the file exists, False otherwise
        """
