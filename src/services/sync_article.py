from article import Article
from db.connection import Connection
from db.queries import insert_article, select_article, update_article


def sync_article(conn: Connection, article: Article):
    """
    Loads novel article data into the database. Will insert if the article doesn't yet
    exist, update if the article does exist, and error if the changes are not allowed.
    """
    persisted_article = select_article(conn, article.id)
    if persisted_article:
        # creation date should never change
        if persisted_article.created_at != article.created_at:
            raise ValueError(
                "error: attempted to modify the publish date of an existing article"
            )
        # last updated date should be newer than the most recent timestamp
        elif persisted_article.updated_at >= article.updated_at:
            raise ValueError(
                "error: attempted to modify the last updated date of an existing "
                "article earlier than the most recent update"
            )

        # persist the update
        update_article(
            conn, id_=article.id, title=article.title, updated_at=article.updated_at
        )

    else:
        insert_article(conn, article)
