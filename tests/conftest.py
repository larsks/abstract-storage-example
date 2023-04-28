import pytest
import random
import string
import time

import docker
from sqlalchemy import create_engine
from sqlalchemy import text
import sqlalchemy.exc

from storage import BaseStore
from storage import MemoryStore
from storage import FilesystemStore
from storage import DatabaseStore


def pytest_addoption(parser):
    parser.addoption(
        "--postgres", action="store_true", help="Run tests against postgres"
    )
    parser.addoption("--mariadb", action="store_true", help="Run tests against mariadb")


def pytest_generate_tests(metafunc):
    if "store_type" in metafunc.fixturenames:
        if metafunc.config.getoption("postgres"):
            metafunc.parametrize("store_type", ["postgres"])
        elif metafunc.config.getoption("mariadb"):
            metafunc.parametrize("store_type", ["mariadb"])
        else:
            metafunc.parametrize("store_type", ["memory", "filesystem", "sqlite"])


@pytest.fixture
def random_string():
    return "".join(random.choices(string.ascii_letters + string.digits, k=15))


@pytest.fixture(scope="session")
def mariadb_port():
    """random port for publishing mariadb service on the host to avoid
    conflicts with an existing mariadb service"""
    return random.randint(10000, 20000)


@pytest.fixture(scope="session")
def postgres_port():
    """random port for publishing postgres service on the host to avoid
    conflicts with an existing postgres service"""
    return random.randint(30000, 40000)


@pytest.fixture
def store(
    store_type,
    request,
    tmp_path,
    random_string_session,
    postgres_port,
    mariadb_port,
):
    if store_type == "memory":
        yield MemoryStore()
    elif store_type == "filesystem":
        root = tmp_path / "__store__"
        root.mkdir()
        yield FilesystemStore(root)
    elif store_type == "sqlite":
        yield DatabaseStore("sqlite://")
    elif store_type == "postgres":
        request.getfixturevalue("postgres_container")
        dburl = f"postgresql://storage_tests:{random_string_session}@127.0.0.1:{postgres_port}/testdb"
        wait_for_db(dburl)
        yield DatabaseStore(dburl)
    elif store_type == "mariadb":
        request.getfixturevalue("mariadb_container")
        dburl = f"mysql+mysqlconnector://storage_tests:{random_string_session}@127.0.0.1:{mariadb_port}/testdb"
        wait_for_db(dburl)
        yield DatabaseStore(dburl)


def wait_for_db(url, timeout=60):
    engine = create_engine(url)
    t_start = time.time()
    while True:
        try:
            with engine.connect() as connection:
                res = connection.execute(text("select 1"))
                if res.first() is not None:
                    break
        except sqlalchemy.exc.SQLAlchemyError:
            if time.time() - t_start > timeout:
                raise TimeoutError()
            time.sleep(1)


@pytest.fixture(scope="session")
def random_string_session():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=15))


@pytest.fixture(scope="session")
def postgres_container(random_string_session, postgres_port):
    client = docker.from_env()
    env = {
        "POSTGRES_PASSWORD": random_string_session,
        "POSTGRES_USER": "storage_tests",
        "POSTGRES_DB": "testdb",
    }
    ports = {
        "5432": f"{postgres_port}",
    }
    container = client.containers.run(
        "docker.io/postgres:14", environment=env, ports=ports, detach=True
    )
    yield container
    container.remove(force=True)


@pytest.fixture(scope="session")
def mariadb_container(random_string_session, mariadb_port):
    client = docker.from_env()
    env = {
        "MARIADB_ROOT_PASSWORD": random_string_session,
        "MARIADB_PASSWORD": random_string_session,
        "MARIADB_USER": "storage_tests",
        "MARIADB_DATABASE": "testdb",
    }
    ports = {
        "3306": f"{mariadb_port}",
    }
    container = client.containers.run(
        "docker.io/mariadb:10", environment=env, ports=ports, detach=True
    )
    yield container
    container.remove(force=True)
