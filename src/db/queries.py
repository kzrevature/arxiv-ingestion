from pg8000.native import Connection

from article import Article

PG_TIME_FMT = "%Y-%m-%d %H:%M:%S"


# drops Article table
def drop_article_table(conn: Connection):
    """
    Drops the Article table.

    Fails silently (no-op) if the table does not exist.
    """
    query_str = "DROP TABLE IF EXISTS Article;"
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


def insert_article(conn: Connection, article: Article) -> list:
    """
    Inserts an Article object into the Article table on a given Postgres connection.
    """
    query_str = (
        "INSERT INTO Article (id, title, created_at, updated_at)"
        "VALUES (:id, :title, :created_at, :updated_at)"
    )

    param_kwargs = {
        "id": article.id,
        "title": article.title,
        "created_at": article.created_at.strftime(PG_TIME_FMT),
        "updated_at": article.updated_at.strftime(PG_TIME_FMT),
    }

    conn.run(query_str, **param_kwargs)
