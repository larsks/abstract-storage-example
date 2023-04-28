# Example storage interface abstraction

This repository contains an example storage abstraction. Code using this package can use a variety of stores for data by selecting an appropriate backend:

- In-memory
- Filesystem
- Database

For example, if I have code that reads a file, produces some sort of analysis, and writes that to the backing store, I could write something like:

```python
class Summarizer:
    def __init__(self, store):
        self.store = store

    def summarize(self):
        data = self.store.fetch('datafile.txt')
        summary = {}
        for row in data:
            # Populate `summary` somehow based on the data
            ...

        self.store.store('summary.json', json.dumps(summary))
```

If I want to store files in the filesystem, I might use it like this:

```
from storage import FilesystemStore

store = FilesystemStore('/tmp/store')
sum = Summarizer(store)
sum.summarize()
```

But if I need to use a database, I would need to make only minimal changes:

```
from storage import DatabaseStore

store = DatabaseStore('postgres://pguser:password@localhost/storedb')
sum = Summarizer(store)
sum.summarize()
```

In either case, the Summarizer class doesn't know anything about how the storage is realized; it just interacts with the `store` variable via the appropriate methods.

## Notes on the database store

The database backend uses [sqlalchemy](https://www.sqlalchemy.org/). Because we're using an ORM, we don't need to write SQL by hand. We can instantiate tables, perform queries, etc, using Python syntax and methods. Furthermore, this means the backend will work with a variety of database backends with no code changes; the tests included in this repository run against sqlite, Postgres, and MariaDB.

## Tests

The tests included in this repository thoroughly exercise the code. By default, the tests run against `MemoryStore`, `FilesystemStore` backends and the `DatabaseStore` using an in-memory sqlite database. Running `pytest` with the `--postgres` option will spin up a Postgres container and run the tests against that, and the `--mariadb` option will spin up a MariaDB container and run the  tests there.
