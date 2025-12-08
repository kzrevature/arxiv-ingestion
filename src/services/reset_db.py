from db.connection import Connection
from db.queries import (
    create_article_category_table,
    create_article_table,
    create_category_table,
    drop_article_table,
)


# drops and recreates the Article table
# useful for development
def reset_db(conn: Connection):
    """Drops and recreates the entire Article table. Use with caution."""
    drop_article_table(conn)
    create_article_table(conn)
    create_category_table(conn)
    create_article_category_table(conn)
