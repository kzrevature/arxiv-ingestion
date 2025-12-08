from db.connection import Connection
from db.queries import (
    create_category_table,
    create_keyword_table,
    insert_categories,
    insert_keywords,
)
from utils.categories import load_categories
from utils.keywords import KEYWORD_LIST


def populate_category_table(conn: Connection):
    """
    Loads article categories from the YAML file and uses them to populate the Category
    table, creating the table if it doesn't yet exist.
    """
    categories = load_categories()
    create_category_table(conn)
    insert_categories(conn, categories)


def populate_keyword_table(conn: Connection):
    """
    Loads hardcoded keywords to populate the Keyword table, creating said table if it
    doesn't yet exist
    """
    create_keyword_table(conn)
    keywords = [
        {"id": idx, "name": kw[0] if isinstance(kw, list) else kw}
        for idx, kw in enumerate(KEYWORD_LIST)
    ]
    insert_keywords(conn, keywords)
