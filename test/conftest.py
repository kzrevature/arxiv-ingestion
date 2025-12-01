import pytest

from db.connection_manager import ConnectionManager


# reset ConnectionManager singleton between tests
@pytest.fixture(autouse=True)
def reset_singleton():
    ConnectionManager._connection = None
    yield
    if ConnectionManager._connection is not None:
        ConnectionManager._connection.close()
        ConnectionManager._connection = None
