from unittest.mock import Mock, patch

from services.reset_db import reset_db


@patch("services.reset_db.create_article_table")
@patch("services.reset_db.drop_article_table")
def test_reset_db(drop_table_mock, create_table_mock):
    conn = Mock()

    reset_db(conn)

    drop_table_mock.assert_called_once_with(conn)
    create_table_mock.assert_called_once_with(conn)
