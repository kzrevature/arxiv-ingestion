from datetime import datetime
from typing import Generator

import pytest
from pg8000 import DatabaseError
from testcontainers.postgres import PostgresContainer

from article import Article
from db.connection import Pg8000Connection
from db.queries import (
    PG_TIME_FMT,
    create_article_category_table,
    create_article_table,
    create_category_table,
    drop_article_table,
    insert_article,
    insert_article_category,
    insert_categories,
    select_article,
    select_most_recent_updated_at,
    update_article,
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


def test_select_most_recent_updated_at(conn):
    id_1 = "sample_id_1"
    title_1 = "Sample Title 1"
    created_at_1 = datetime(2000, 1, 1)
    updated_at_1 = datetime(2000, 1, 1)
    arti_1 = Article(id_1, title_1, created_at_1, updated_at_1)
    id_2 = "sample_id_2"
    title_2 = "Sample Title 2"
    created_at_2 = datetime(2000, 1, 1)
    updated_at_2 = datetime(2000, 1, 17)
    arti_2 = Article(id_2, title_2, created_at_2, updated_at_2)
    id_3 = "sample_id_3"
    title_3 = "Sample Title 3"
    created_at_3 = datetime(2000, 1, 17)
    updated_at_3 = datetime(2000, 1, 29)  # newest updated_at date
    arti_3 = Article(id_3, title_3, created_at_3, updated_at_3)
    id_4 = "sample_id_4"
    title_4 = "Sample Title 4"
    created_at_4 = datetime(2000, 1, 23)
    updated_at_4 = datetime(2000, 1, 23)
    arti_4 = Article(id_4, title_4, created_at_4, updated_at_4)

    expected = datetime(2000, 1, 29)  # newest updated_at date

    create_article_table(conn)
    insert_article(conn, arti_1)
    insert_article(conn, arti_2)
    insert_article(conn, arti_3)
    insert_article(conn, arti_4)

    actual = select_most_recent_updated_at(conn)

    assert actual == expected


def test_select_most_recent_updated_at_returns_none_if_table_is_empty(conn):
    create_article_table(conn)

    res = select_most_recent_updated_at(conn)
    assert res is None


def test_update_article_all_fields(conn):
    id_ = "nah_ID_win"
    title = "Cool Title"
    created_at = datetime(2000, 1, 1)
    updated_at = datetime(2000, 1, 1)

    new_title = "Warm Title"
    new_created_at = datetime(2002, 1, 1)
    new_updated_at = datetime(2002, 1, 1)

    create_article_table(conn)
    insert_article(conn, Article(id_, title, created_at, updated_at))
    update_article(
        conn,
        id_,
        title=new_title,
        created_at=new_created_at,
        updated_at=new_updated_at,
    )
    updated_article = select_article(conn, id_)

    assert updated_article.id == id_
    assert updated_article.title == new_title
    assert updated_article.created_at == new_created_at
    assert updated_article.updated_at == new_updated_at


def test_update_article_no_fields(conn):
    id_ = "nah_ID_lose"
    title = "Lame Title"
    created_at = datetime(1999, 1, 1)
    updated_at = datetime(1999, 1, 1)

    create_article_table(conn)
    insert_article(conn, Article(id_, title, created_at, updated_at))
    update_article(conn, id_)
    updated_article = select_article(conn, id_)

    assert updated_article.id == id_
    assert updated_article.title == title
    assert updated_article.created_at == created_at
    assert updated_article.updated_at == updated_at


def test_update_article_fails_on_nohit(conn):
    create_article_table(conn)
    with pytest.raises(ValueError):
        update_article(conn, "id404", title="Fascinating")


def test_create_category_table(conn):
    expected = []

    create_category_table(conn)

    actual = conn.run("SELECT * FROM Category;")
    assert expected == actual


def test_create_category_table_noops_if_exists(conn):
    create_category_table(conn)

    # does not raise an exception
    create_category_table(conn)


def test_insert_categories(conn):
    cat_1 = {"id": 5, "code": "math", "name": "Math"}
    cat_2 = {"id": 6, "code": "math.c", "name": "Cooler Math"}

    expected = [
        [cat_1["id"], cat_1["code"], cat_1["name"]],
        [cat_2["id"], cat_2["code"], cat_2["name"]],
    ]

    create_category_table(conn)
    insert_categories(conn, [cat_1, cat_2])

    actual = conn.run("SELECT * FROM Category;")

    assert actual == expected


def test_insert_categories_errors_with_duplicate_id(conn):
    cat_1 = {"id": 5, "code": "eng", "name": "Math"}
    cat_2 = {"id": 5, "code": "mat", "name": "English"}

    create_category_table(conn)
    with pytest.raises(DatabaseError):
        insert_categories(conn, [cat_1, cat_2])


def test_insert_categories_errors_with_duplicate_code(conn):
    cat_1 = {"id": 5, "code": "lang/1", "name": "Spanish"}
    cat_2 = {"id": 6, "code": "lang/1", "name": "French"}

    create_category_table(conn)
    with pytest.raises(DatabaseError):
        insert_categories(conn, [cat_1, cat_2])


def test_create_article_category_table(conn):
    expected = []

    create_article_table(conn)
    create_category_table(conn)
    create_article_category_table(conn)

    actual = conn.run("SELECT * FROM Article_Category;")
    assert expected == actual


def test_create_article_category_table_noops_if_exists(conn):
    create_article_table(conn)
    create_category_table(conn)

    create_article_category_table(conn)

    # does not raise an exception
    create_article_category_table(conn)


def test_insert_article_category(conn):
    article_id = "abc"
    article_title = "A B C"
    category_id = 555
    category_name = "Alphabet"
    article = Article(article_id, article_title, datetime(1, 1, 1), datetime(1, 1, 1))

    create_article_table(conn)
    create_category_table(conn)
    create_article_category_table(conn)

    insert_categories(conn, [{"id": category_id, "code": "alp", "name": category_name}])
    insert_article(conn, article)

    expected_join = [[article_title, category_name]]

    insert_article_category(conn, article_id, category_id)

    actual_join = conn.run(
        "SELECT a.title, c.name "
        "FROM Article a "
        "JOIN Article_Category ac ON a.id = ac.article_id "
        "JOIN Category c ON c.id = ac.category_id;"
    )

    assert actual_join == expected_join


def test_insert_article_category_fails_if_article_does_not_exist(conn):
    category_id = 555

    create_article_table(conn)
    create_category_table(conn)
    create_article_category_table(conn)

    insert_categories(conn, [{"id": category_id, "code": "a", "name": "ABC"}])

    with pytest.raises(DatabaseError):
        insert_article_category(conn, "not_an_id", category_id)


def test_insert_article_category_fails_if_category_does_not_exist(conn):
    article_id = 555
    article = Article(article_id, "abc", datetime(7, 7, 7), datetime(7, 7, 7))

    create_article_table(conn)
    create_category_table(conn)
    create_article_category_table(conn)

    insert_article(conn, article)

    with pytest.raises(DatabaseError):
        insert_article_category(conn, article_id, 4040404)
