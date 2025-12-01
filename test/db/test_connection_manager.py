from unittest.mock import patch

import pytest

from db.connection_manager import ConnectionManager


@pytest.fixture(scope="function")
def init_mock():
    with patch("db.connection_manager.Connection") as mock:
        yield mock


def test_connection_manager_instantiates_only_once(init_mock):
    ConnectionManager.get_connection()
    ConnectionManager.get_connection()
    ConnectionManager.get_connection()
    init_mock.assert_called_once()


def test_connection_manager_instantiates_with_configured_parameters(init_mock):
    config_kwargs = {
        "host": "myhost123",
        "port": 7654,
        "potato": "fries",
    }

    ConnectionManager.configure(**config_kwargs)
    ConnectionManager.get_connection()

    init_mock.assert_called_once_with(**config_kwargs)
