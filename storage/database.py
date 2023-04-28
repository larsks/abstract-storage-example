import warnings

from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy import select
from sqlalchemy import ForeignKey
from sqlalchemy import LargeBinary
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session
import sqlalchemy.exc

from .base import BaseStore
from .exc import StorageError, StorageFileNotFoundError, StorageFileExistsError


warnings.filterwarnings(category=sqlalchemy.exc.SAWarning, action="ignore")


class Base(DeclarativeBase):
    pass


class File(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(primary_key=True, auto_increment=True)
    path: Mapped[str] = mapped_column(String(4096), unique=True)
    content: Mapped[bytes] = mapped_column(LargeBinary)

    def __repr__(self) -> str:
        return f"File(path={self.path})"


class DatabaseStore(BaseStore):
    def __init__(self, dburl: str):
        self._dburl = dburl
        self._engine = create_engine(dburl)
        Base.metadata.create_all(self._engine)

    def fetch(self, path: str) -> bytes:
        try:
            with Session(self._engine) as session:
                res = session.query(File).filter(File.path == path)
                return res[0].content
        except IndexError:
            raise StorageFileNotFoundError(path)

    def store(self, path: str, content: bytes):
        if self.exists(path):
            raise StorageFileExistsError(path)

        return self.replace(path, content)

    def replace(self, path: str, content: bytes):
        try:
            with Session(self._engine) as session:
                res = session.query(File).filter(File.path == path)
                if existing := res.first():
                    session.delete(existing)
                    session.flush()

                new_file = File(
                    path=path,
                    content=content,
                )

                session.add(new_file)
                session.commit()
        except sqlalchemy.exc.IntegrityError:
            raise StorageFileExistsError(path)

    def exists(self, path: str) -> bool:
        with Session(self._engine) as session:
            res = session.query(File).filter(File.path == path)
            return res.first() is not None

    def delete(self, path: str):
        with Session(self._engine) as session:
            res = session.query(File).filter(File.path == path)
            if existing := res.first():
                session.delete(existing)
                session.commit()
            else:
                raise StorageFileNotFoundError(path)
