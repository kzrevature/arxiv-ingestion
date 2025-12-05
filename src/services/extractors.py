import logging
import time
from datetime import datetime
from typing import Generator

from article import Article
from arxiv.parser import (
    extract_article_entries,
    extract_total_results,
    parse_entry_to_article,
)
from arxiv.request import fetch_articles_from_arxiv_api

LOG = logging.getLogger()


def fetch_articles(start_time: datetime, end_time: datetime) -> Generator[Article]:
    """
    Fetch all arXiv article entries from the given time range. Results are yielded as a
    a generator of Article objects.

    Makes a series of API calls while respecting the rate limit of once per 3 seconds,
    so this function may take some time to run for larger time ranges.
    """

    api_rate_limit_seconds = 3

    # Use date-based 'pagination' where articles are retrieved 1000 at a time with a
    # sliding date window. The API result provides a number for all (remaining) matches
    # so iteration stops once this number equals the amount of articles in the actual response
    has_more_articles = True
    while has_more_articles:
        LOG.info(f"ingesting articles from {start_time}...")
        # grab a 'page' from the api
        xml_page = fetch_articles_from_arxiv_api(start_time, end_time)
        total_matches = extract_total_results(xml_page)
        page_entries = extract_article_entries(xml_page)

        # iterate through articles in the page
        for entry in page_entries:
            result = parse_entry_to_article(entry)
            if result.ok:
                yield result.val
            else:
                # TODO: emit helpful logs
                pass

        # break out when current page contains all remaining results
        if len(page_entries) == total_matches:
            has_more_articles = False

        # else, push up start_time and continue querying
        else:
            # TODO: add logic to prevent duplication at page boundary
            start_time = result.val.updated_at
            # block to respect the rate limit
            time.sleep(api_rate_limit_seconds)
