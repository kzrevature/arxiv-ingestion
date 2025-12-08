from db.connection import Pg8000Connection
from db.queries import create_category_table, insert_categories
from utils.categories import load_categories


def populate_category_table():
    """
    Loads article categories from the YAML file and uses them to populate the Category
    table, creating the table if it doesn't yet exist.
    """
    conn = Pg8000Connection()
    categories = load_categories()
    create_category_table(conn)
    insert_categories(conn, categories)
    conn.close()
