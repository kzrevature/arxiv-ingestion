from db.connection import Connection
from db.queries import (
    create_article_category_table,
    create_article_table,
    create_category_table,
    create_keyword_occurrence_table,
    create_keyword_table,
    drop_article_table,
    drop_category_table,
    drop_keyword_table,
)
from services.populate_reference_tables import (
    populate_category_table,
    populate_keyword_table,
)


# drops and recreates the Article table
# useful for development
def reset_db(conn: Connection):
    """Drops and recreates the entire Article table. Use with caution."""
    drop_article_table(conn)
    drop_category_table(conn)
    drop_keyword_table(conn)
    create_article_table(conn)
    create_category_table(conn)
    create_article_category_table(conn)
    create_keyword_table(conn)
    create_keyword_occurrence_table(conn)
    populate_category_table(conn)
    populate_keyword_table(conn)
