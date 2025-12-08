from datetime import datetime

from article import Article
from db.connection import Connection

PG_TIME_FMT = "%Y-%m-%d %H:%M:%S"


def drop_article_table(conn: Connection):
    """
    Drops the Article table.

    Fails silently (no-op) if the table does not exist.
    """

    query_str = "DROP TABLE IF EXISTS Article CASCADE;"
    conn.run(query_str)


def drop_category_table(conn: Connection):
    """
    Drops the Category table.

    Fails silently (no-op) if the table does not exist.
    """

    query_str = "DROP TABLE IF EXISTS Category CASCADE;"
    conn.run(query_str)


def drop_keyword_table(conn: Connection):
    """
    Drops the Keyword table.

    Fails silently (no-op) if the table does not exist.
    """

    query_str = "DROP TABLE IF EXISTS Keyword CASCADE;"
    conn.run(query_str)


# creates Article table with the columns shown below
def create_article_table(conn: Connection):
    """
    Builds the Article table.

    Schema:
        id:             VARCHAR(20) PK
        title:          VARCHAR(255)
        created_at:     TIMESTAMP
        updated_at:     TIMESTAMP

    Errors if the table already exists.
    """

    query_str = (
        "CREATE TABLE Article ("
        "   id             VARCHAR(20) PRIMARY KEY,"
        "   title          VARCHAR(255),"
        "   created_at     TIMESTAMP,"
        "   updated_at     TIMESTAMP"
        ");"
    )

    conn.run(query_str)


def insert_article(conn: Connection, article: Article):
    """
    Inserts an Article object into the Article table.
    """

    query_str = (
        "INSERT INTO Article (id, title, created_at, updated_at) "
        "VALUES (:id, :title, :created_at, :updated_at)"
    )

    param_kwargs = {
        "id": article.id,
        "title": article.title,
        "created_at": article.created_at.strftime(PG_TIME_FMT),
        "updated_at": article.updated_at.strftime(PG_TIME_FMT),
    }

    conn.run(query_str, **param_kwargs)


def select_article(conn: Connection, id_: str) -> Article | None:
    """
    Selects a row from the Article table by its ID.
    """

    query_str = "SELECT id, title, created_at, updated_at FROM Article WHERE id=:id"

    res = conn.run(query_str, id=id_)

    if len(res) > 0:
        return Article(
            id_=res[0][0],
            title=res[0][1],
            created_at=res[0][2],
            updated_at=res[0][3],
        )
    else:
        return None


def select_most_recent_updated_at(conn: Connection) -> datetime | None:
    """
    Retrieves the most recent value of update_at from the Article table.
    """

    query_str = "SELECT MAX(updated_at) FROM Article"

    res = conn.run(query_str)

    return res[0][0] if len(res) > 0 else None


def update_article(
    conn: Connection,
    id_: str,
    title: str = None,
    created_at: datetime = None,
    updated_at: datetime = None,
):
    """
    Updates a row in the Article table with a new set of parameters.
    """

    # make sure article exists before editing
    article = select_article(conn, id_)
    if article is None:
        raise ValueError(f"cannot update article with id {id_}: does not exist")

    if title is None:
        title = article.title
    if created_at is None:
        created_at = article.created_at
    if updated_at is None:
        updated_at = article.updated_at

    query_str = (
        "UPDATE Article SET title=:title, created_at=:created_at, updated_at=:updated_at "
        "WHERE id=:id"
    )
    conn.run(
        query_str,
        id=id_,
        title=title,
        created_at=created_at,
        updated_at=updated_at,
    )


def create_category_table(conn: Connection):
    """
    Builds the Category reference table.

    Schema:
        id:             INTEGER PK
        code:           VARCHAR(20)
        name:           VARCHAR(50)

    Fails silently if the table already exists.
    """

    query_str = (
        "CREATE TABLE IF NOT EXISTS Category ("
        "   id             INTEGER PRIMARY KEY,"
        "   code           VARCHAR(20) UNIQUE,"
        "   name           VARCHAR(50)"
        ");"
    )

    conn.run(query_str)


def insert_categories(conn: Connection, categories: list[dict]):
    """
    Inserts a list of categories as records into the Category table.
    Input must be provided as a list of dicts, with keys 'id', 'code', and 'name'.
    """

    query_str = "INSERT INTO Category (id, code, name) VALUES (:id, :code, :name);"

    for cat in categories:
        conn.run(query_str, id=cat["id"], code=cat["code"], name=cat["name"])


def create_article_category_table(conn: Connection):
    """
    Builds the join table between Article and Category

    Fails silently if the table already exists.
    """

    query_str = (
        "CREATE TABLE IF NOT EXISTS Article_Category ("
        "   article_id     VARCHAR(20),"
        "   category_id    INTEGER,"
        ""
        "   FOREIGN KEY (article_id) REFERENCES Article (id),"
        "   FOREIGN KEY (category_id) REFERENCES Category (id)"
        ");"
    )

    conn.run(query_str)


def insert_article_category(conn: Connection, article_id: str, category_id: int):
    """
    Inserts a join entry between an article (id) and category (id)
    """

    query_str = (
        "INSERT INTO Article_Category (article_id, category_id) "
        "VALUES (:article_id, :category_id);"
    )

    conn.run(query_str, article_id=article_id, category_id=category_id)


def delete_article_category_for_article(conn: Connection, article_id: str):
    """
    Deletes all category join entries for a given article by article_id.
    """

    query_str = "DELETE FROM Article_Category WHERE article_id=:article_id;"

    conn.run(query_str, article_id=article_id)


def create_keyword_table(conn: Connection):
    """
    Creates the keyword reference table.

    Fails silently if the table already exists.
    """

    query_str = (
        "CREATE TABLE IF NOT EXISTS Keyword ("
        "   id             INTEGER PRIMARY KEY,"
        "   name           VARCHAR(40)"
        ");"
    )

    conn.run(query_str)


def insert_keywords(conn: Connection, keywords: list[dict]):
    """
    Inserts a list of keywords as records into the Keyword table.

    Input is a list of dicts, with keys 'id' and 'name'.
    """

    query_str = "INSERT INTO Keyword (id, name) VALUES (:id, :name);"

    for kw in keywords:
        conn.run(query_str, id=kw["id"], name=kw["name"])


def create_keyword_occurrence_table(conn: Connection):
    """
    Builds the occurrence table tracking keyword usage in articles.

    Schema:
        article_id:     VARCHAR(20)
        keyword_id:     INTEGER
        total:          INTEGER

    Fails silently if the table already exists.
    """

    query_str = (
        "CREATE TABLE IF NOT EXISTS KeywordOccurrence ("
        "   article_id     VARCHAR(20),"
        "   keyword_id     INTEGER,"
        "   total          INTEGER,"
        ""
        "   FOREIGN KEY (article_id) REFERENCES Article (id),"
        "   FOREIGN KEY (keyword_id) REFERENCES Keyword (id)"
        ");"
    )

    conn.run(query_str)


def insert_keyword_occurrence(
    conn: Connection,
    article_id: str,
    keyword_id: int,
    total: int,
):
    """
    Inserts an occurrence entry for a specific article/keyword.
    """

    query_str = (
        "INSERT INTO KeywordOccurrence (article_id, keyword_id, total) "
        "VALUES (:article_id, :keyword_id, :total);"
    )

    conn.run(
        query_str,
        article_id=article_id,
        keyword_id=keyword_id,
        total=total,
    )


def delete_keyword_occurrences_for_article(conn: Connection, article_id: str):
    """
    Deletes all occurrences entries for a given keyword by article_id.
    """

    query_str = "DELETE FROM KeywordOccurrence WHERE article_id=:article_id;"

    conn.run(query_str, article_id=article_id)
