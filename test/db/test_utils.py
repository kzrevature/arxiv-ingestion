from unittest.mock import patch

from db.utils import create_connection


@patch("pg8000.native.Connection.__init__")
def test_create_connection(conn_constructor_mock):
    user = "postgres"
    password = "password123"
    url = "url567"

    conn_constructor_mock.return_value = None
    with patch.dict("os.environ", {"ARXIN_DB_PASS": password, "ARXIN_DB_URL": url}):

        create_connection()
        conn_constructor_mock.assert_called_once_with(user, password=password, host=url)
