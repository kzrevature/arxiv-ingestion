import traceback
import xml.etree.ElementTree as ET
from datetime import datetime
from uuid import uuid4

from pg8000 import DatabaseError

from arxiv.parser import parse_entry_to_article
from db.connection import Pg8000Connection
from db.queries import select_most_recent_updated_at
from services.extractors import fetch_article_entries
from services.sync_article import sync_article
from utils.logger import LOG

# the first arXiv articles were last updated in 1986
DEFAULT_BACKFILL_START_DATE = datetime(1986, 1, 1)
LOG_REJECTED_DIR = "log/rejected"


def etl_backfill(backfill_start: datetime, backfill_end: datetime):
    """
    Runs a backfill ETL process which ingests all arXiv articles between two dates and
    loads them into the Article table.

    Makes many HTTP requests so it may take some time to complete.
    """

    conn = Pg8000Connection()

    # extraction loop
    for entry in fetch_article_entries(backfill_start, backfill_end):
        # parse and validate
        try:
            article = parse_entry_to_article(entry)
        except ValueError:
            reject_filepath = f"{LOG_REJECTED_DIR}/{str(uuid4())}"
            LOG.error(
                f"ERR: Failed to parse record, storing failed xml in {reject_filepath}\n"
                f"Full trace: {traceback.format_exc()}"
            )
            with open(reject_filepath, "w", encoding="utf-8") as f:
                f.write(ET.tostring(entry, encoding="unicode"))
            continue

        # transform and persist
        try:
            sync_article(conn, article)
        except (DatabaseError, ValueError):
            conn.run("ROLLBACK;")
            reject_filepath = f"{LOG_REJECTED_DIR}/{str(uuid4())}"
            LOG.error(
                f"ERR: Failed to persist record, storing failed xml in {reject_filepath}\n"
                f"Article id: {article.id}\n"
                f"Full trace: {traceback.format_exc()}"
            )
            with open(reject_filepath, "w", encoding="utf-8") as f:
                f.write(ET.tostring(entry, encoding="unicode"))

    conn.close()


def etl_backfill_auto():
    """
    Runs the ETL backfill process. Automatically selects start and end dates by the
    following rules:
      - Start date is the most recent (by updated_at) article in the Article table, or
        Jan 1, 1986 if the table is empty.
      - End date is datetime.now().
    """

    conn = Pg8000Connection()
    backfill_start = select_most_recent_updated_at(conn)
    conn.close()
    if backfill_start is None:
        backfill_start = DEFAULT_BACKFILL_START_DATE

    backfill_end = datetime.now()

    etl_backfill(backfill_start, backfill_end)
