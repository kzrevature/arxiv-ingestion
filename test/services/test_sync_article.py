from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from article import Article
from services.sync_article import sync_article


@pytest.fixture
def insert_mock():
    with patch("services.sync_article.insert_article") as mock:
        yield mock


@pytest.fixture
def select_mock():
    with patch("services.sync_article.select_article") as mock:
        yield mock


@pytest.fixture
def update_mock():
    with patch("services.sync_article.update_article") as mock:
        yield mock


def test_sync_article_inserts_new_record(select_mock, insert_mock, update_mock):
    article = Article(
        "geo/345", "Rocks rock", datetime(2000, 1, 1), datetime(2000, 1, 1)
    )

    conn_mock = Mock()
    select_mock.return_value = None

    sync_article(conn_mock, article)

    insert_mock.assert_called_once_with(conn_mock, article)
    update_mock.assert_not_called()


def test_sync_article_updates_existing_record(select_mock, insert_mock, update_mock):
    old_record = Article(
        "55.66", "Numbers are bad", datetime(2002, 2, 2), datetime(2002, 2, 2)
    )
    new_record = Article(
        "55.66",
        "Numbers are cool actually",
        datetime(2002, 2, 2),
        datetime(2005, 5, 15),
    )

    conn_mock = Mock()
    select_mock.return_value = old_record

    sync_article(conn_mock, new_record)

    update_mock.assert_called_once_with(
        conn_mock,
        id_=old_record.id,
        title=new_record.title,
        updated_at=new_record.updated_at,
    )
    insert_mock.assert_not_called()


def test_sync_article_errors_on_altered_created_at(
    select_mock, insert_mock, update_mock
):
    old_record = Article(
        "80.8000", "Ants on the Lawn", datetime(2015, 5, 15), datetime(2022, 2, 2)
    )
    new_record = Article(
        "80.8000", "Ants on the Lawn", datetime(2016, 6, 16), datetime(2022, 2, 2)
    )

    conn_mock = Mock()
    select_mock.return_value = old_record

    with pytest.raises(ValueError):
        sync_article(conn_mock, new_record)

    insert_mock.assert_not_called
    update_mock.assert_not_called


def test_sync_article_errors_on_older_updated_at(select_mock, insert_mock, update_mock):
    old_record = Article(
        "70.7000", "Hoppers in the Grass", datetime(2022, 2, 22), datetime(2044, 4, 4)
    )
    new_record = Article(
        "70.7000", "Hoppers in the Grass", datetime(2022, 2, 22), datetime(2033, 3, 3)
    )

    conn_mock = Mock()
    select_mock.return_value = old_record

    with pytest.raises(ValueError):
        sync_article(conn_mock, new_record)

    insert_mock.assert_not_called
    update_mock.assert_not_called
