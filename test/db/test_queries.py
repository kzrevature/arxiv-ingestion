from unittest.mock import MagicMock

from db.queries import create_article_table, drop_article_table


def test_drop_article_table():
    expected_sql = "DROP TABLE IF EXISTS Article;"

    conn_mock = MagicMock()
    conn_mock.run = MagicMock()

    drop_article_table(conn_mock)

    conn_mock.run.assert_called_once_with(expected_sql)


def test_create_article_table():
    expected_sql_startswith = "CREATE TABLE Article"

    conn_mock = MagicMock()
    conn_mock.run = MagicMock()

    create_article_table(conn_mock)

    args, _ = conn_mock.run.call_args
    assert args[0].startswith(expected_sql_startswith)
