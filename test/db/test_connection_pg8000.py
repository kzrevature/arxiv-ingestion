from unittest.mock import patch

import pytest

from db.connection import Pg8000Connection


@pytest.fixture
def pg8000_conn_mock():
    with patch("db.connection.pg8000.Connection") as mock:
        yield mock


def test_pg8000_connection_builds_connection_with_params(
    pg8000_conn_mock,
):
    user = "my_user_123"
    password = "my_password_abc"
    url = "my_url_777"
    port = 33333

    Pg8000Connection(user=user, password=password, url=url, port=port)
    pg8000_conn_mock.assert_called_with(
        user=user,
        password=password,
        host=url,
        port=port,
    )


def test_pg8000_connection_builds_connection_with_expected_defaults(
    pg8000_conn_mock,
):
    expected_user = "postgres"
    expected_password = "passw0rd"
    expected_host = "url-asdf1234"
    expected_port = 5432

    with patch.dict(
        "os.environ",
        {
            "ARXIN_DB_PASS": expected_password,
            "ARXIN_DB_URL": expected_host,
        },
    ):
        Pg8000Connection()
        pg8000_conn_mock.assert_called_with(
            user=expected_user,
            password=expected_password,
            host=expected_host,
            port=expected_port,
        )


@patch("db.connection.pg8000.Connection.run")
def test_pg8000_connection_run_passes_kwargs_to_pg8000_run(pg8000_run_mock):
    sql = "SELECT * FROM SomeTableABC;"
    kwargs = {
        "apple": "banana",
        "romeo": "alpha",
    }

    conn = Pg8000Connection()
    conn.run(sql, **kwargs)
    pg8000_run_mock.assert_called_once_with(sql, **kwargs)


@patch("db.connection.pg8000.Connection.close")
def test_connection_close_closes_pg8000_connection(pg8000_close_mock):
    conn = Pg8000Connection()
    conn.close()
    pg8000_close_mock.assert_called_once()
