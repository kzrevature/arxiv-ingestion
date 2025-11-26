from unittest.mock import patch

from db.utils import create_connection


@patch("pg8000.native.Connection.__init__")
def test_create_connection(conn_constructor_mock):
    expected_user = "postgres"
    expected_pass = "passw0rd"
    expected_url = "url-asdf1234"
    expected_port = 5432

    conn_constructor_mock.return_value = None
    with patch.dict(
        "os.environ", {"ARXIN_DB_PASS": expected_pass, "ARXIN_DB_URL": expected_url}
    ):
        create_connection()
        conn_constructor_mock.assert_called_once_with(
            user=expected_user,
            password=expected_pass,
            host=expected_url,
            port=expected_port,
        )
