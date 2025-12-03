from datetime import datetime
from typing import Generator

import pytest
from pg8000 import DatabaseError
from testcontainers.postgres import PostgresContainer

from article import Article
from db.connection import Pg8000Connection
from db.queries import (
    PG_TIME_FMT,
    create_article_table,
    drop_article_table,
    insert_article,
    select_article,
)


@pytest.fixture(scope="module")
def pg_container():
    with PostgresContainer("postgres:16.10") as pg:
        yield pg


@pytest.fixture
def conn(pg_container) -> Generator[Pg8000Connection]:
    with Pg8000Connection(
        port=pg_container.get_exposed_port(5432),
        user=pg_container.username,
        password=pg_container.password,
        url=pg_container.get_container_host_ip(),
    ) as conn:
        # reset entire pg schema
        conn.run("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
        yield conn


def test_drop_article_table(conn):
    conn.run("CREATE TABLE Article();")

    drop_article_table(conn)

    # Article table is dropped so this should error
    with pytest.raises(DatabaseError):
        conn.run("SELECT * FROM Article;")


def test_drop_article_table_noop_when_missing(conn):
    # even though Article table doesn't exist yet
    # this shouldn't error
    drop_article_table(conn)


def test_create_article_table(conn):
    expected_res = []

    create_article_table(conn)

    actual_res = conn.run("SELECT * FROM Article;")
    assert expected_res == actual_res


def test_create_article_table_fails_if_already_exists(conn):
    conn.run("CREATE TABLE Article();")

    with pytest.raises(DatabaseError):
        create_article_table(conn)


def test_insert_article(conn):
    id_ = "id_123"
    title = "title_123"
    created_at = datetime(2025, 8, 8)
    updated_at = datetime(2025, 9, 9)
    test_article = Article(id_, title, created_at, updated_at)

    expected = [[id_, title, created_at, updated_at]]

    create_article_table(conn)
    insert_article(conn, test_article)

    actual = conn.run("SELECT id, title, created_at, updated_at FROM Article;")

    assert actual == expected


def test_insert_article_fails_on_duplicate_id(conn):
    id_common = "id_123"
    title_1 = "title_999"
    title_2 = "title_888"
    created_at_1 = datetime(2024, 6, 6)
    created_at_2 = datetime(2024, 7, 7)
    updated_at_1 = datetime(2025, 8, 8)
    updated_at_2 = datetime(2025, 9, 9)
    article_1 = Article(id_common, title_1, created_at_1, updated_at_1)
    article_2 = Article(id_common, title_2, created_at_2, updated_at_2)

    create_article_table(conn)
    insert_article(conn, article_1)

    with pytest.raises(DatabaseError):
        insert_article(conn, article_2)


def test_select_article(conn):
    id_ = "math/123"
    title = "Math and Math and Math"
    created_at = datetime(2007, 6, 6)
    updated_at = datetime(2007, 7, 7)

    create_article_table(conn)
    conn.run(
        "INSERT INTO Article (id, title, created_at, updated_at) "
        f"VALUES ('{id_}', '{title}', '{created_at.strftime(PG_TIME_FMT)}', '{updated_at.strftime(PG_TIME_FMT)}');"
    )
    actual = select_article(conn, id_)

    assert actual.id == id_
    assert actual.title == title
    assert actual.created_at == created_at
    assert actual.updated_at == updated_at


def test_select_article_returns_none_on_nohit(conn):
    create_article_table(conn)
    result = select_article(conn, "nonexistent_id")
    assert result is None
