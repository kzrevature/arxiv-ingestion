import time
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Generator

from arxiv.parser import (
    extract_article_entries,
    extract_total_results,
    extract_updated_at_from_entry,
)
from arxiv.request import fetch_articles_from_arxiv_api
from utils.logger import LOG


def fetch_article_entries(
    start_time: datetime, end_time: datetime
) -> Generator[ET.Element]:
    """
    Fetch all arXiv article entries from the given time range. Results are yielded as a
    a generator of XML Elements.

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
        # fetch a page from the api
        try:
            xml_page = fetch_articles_from_arxiv_api(start_time, end_time)
        except ET.ParseError:
            LOG.error("arXiv API is malfunctioning")
            break
        total_matches = extract_total_results(xml_page)
        page_entries = extract_article_entries(xml_page)

        # iterate through and yield articles in the page
        for entry in page_entries:
            yield entry

        # break out when current page contains all remaining results
        if len(page_entries) == total_matches:
            has_more_articles = False

        # slide up start_time to exclude current page
        try:
            start_time = next(
                filter(
                    lambda x: x is not None,
                    map(extract_updated_at_from_entry, reversed(page_entries)),
                )
            )
        except StopIteration:
            LOG.error("ERR: couldn't find next pagination window, stopping iteration")
            has_more_articles = False

        # block to respect the rate limit
        time.sleep(api_rate_limit_seconds)
