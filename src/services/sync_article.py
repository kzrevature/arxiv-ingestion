from article import Article
from db.connection import Connection
from db.queries import (
    delete_article_category_for_article,
    delete_keyword_occurrences_for_article,
    insert_article,
    insert_article_category,
    insert_keyword_occurrence,
    select_article,
    update_article,
)
from utils.categories import build_category_id_reference_dict
from utils.keywords import count_keyword_occurrences

CATEGORY_CODE_TO_ID = build_category_id_reference_dict()


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

    # handle category updates
    delete_article_category_for_article(conn, article.id)
    for category in article.categories:
        insert_article_category(conn, article.id, CATEGORY_CODE_TO_ID[category])

    # handle keyword updates
    delete_keyword_occurrences_for_article(conn, article.id)
    keyword_occurences = count_keyword_occurrences(article.abstract)
    for kw_id, total in keyword_occurences.items():
        insert_keyword_occurrence(conn, article.id, kw_id, total)
