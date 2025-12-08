import logging
import re
from datetime import datetime
from typing import NamedTuple
from xml.etree import ElementTree as ET

from article import Article

LOG = logging.getLogger()

# namespace which prefixes every element in the xml file
XML_NS = "{http://www.w3.org/2005/Atom}"
XML_TIME_FMT = "%Y-%m-%dT%H:%M:%SZ"

# tuple representing the possible outcomes when parsing xml to an articles
# val will be None on an unsuccessful parse (ok=False)
ArticleParseResult = NamedTuple(
    "ArticleParseResult",
    [
        ("ok", bool),
        ("val", Article | None),
        ("url", str),
    ],
)


def extract_article_entries(xml_response: ET.Element) -> list[ET.Element]:
    """
    Takes as input the root XML element of an arXiv API response and returns
    a list of children which represent arXiv articles.
    """
    return xml_response.findall(f"{XML_NS}entry")


def extract_total_results(xml_response: ET.Element) -> int:
    """
    Takes as input the root XML element of an arXiv API response and returns
    the total number of matching articles matched
    """
    for child in xml_response:
        if child.tag.endswith("totalResults"):
            return int(child.text)


def parse_entry_to_article(node: ET.Element) -> ArticleParseResult:
    """
    Takes as input an XML <entry> element representing an arXiv article, and extracts
    the relevant fields into an Article object.
    """
    categories = []
    for child in node:
        if child.tag.endswith("id"):
            url = child.text
            try:
                id_ = parse_arxiv_url_to_id(url)
            except ValueError:
                LOG.warning(f"failed to parse arXiv entry at url: {url}")
                return ArticleParseResult(False, None, url)
        elif child.tag.endswith("title"):
            title = child.text
        elif child.tag.endswith("published"):
            created_at = datetime.strptime(child.text, XML_TIME_FMT)
        elif child.tag.endswith("updated"):
            updated_at = datetime.strptime(child.text, XML_TIME_FMT)
        elif child.tag.endswith("category"):
            categories.append(child.get("term"))
        elif child.tag.endswith("summary"):
            abstract = child.text

    if created_at > updated_at:
        LOG.warning(
            f"arXiv entry has invalid timestamps: published > updated for id {id_}"
        )
        return ArticleParseResult(False, None, url)

    return ArticleParseResult(
        True,
        Article(
            id_,
            title,
            created_at,
            updated_at,
            categories,
            abstract,
        ),
        url,
    )


def validate_arxiv_id_old_fmt(id_: str) -> bool:
    """
    Check if an string matches the pre-2007 arXiv format for article IDs.

    [cat]/YYMMXXX
    """
    id_sections = id_.split("/")
    if len(id_sections) != 2:
        return False
    # the second part of the id is given in YYMMXXX format
    elif not id_sections[1].isdigit():
        return False
    elif len(id_sections[1]) != 7:
        return False
    return True


def validate_arxiv_id_new_fmt(id_: str) -> bool:
    """
    Check if an string matches the post-2007 arXiv format for article IDs.

    YYMM.XXXX
    YYMM.XXXXX
    """
    id_sections = id_.split(".")
    if len(id_sections) != 2:
        return False
    # the first part of the id is in YYMM format
    elif not id_sections[0].isdigit():
        return False
    elif len(id_sections[0]) != 4:
        return False
    # the second section is a string of 4 or 5 digits
    elif not id_sections[1].isdigit():
        return False
    elif len(id_sections[1]) not in (4, 5):
        return False
    return True


def parse_arxiv_url_to_id(article_url):
    """
    Extracts the unique arXiv identifier for an article based on its abstract url.
    Raises a ValueError if the request is malformed.

    Refer to https://info.arxiv.org/help/arxiv_identifier_for_services.html for more details.
    """

    arxiv_url_prefix = "http://arxiv.org/abs/"

    # check prefix
    if not article_url.startswith(arxiv_url_prefix):
        error_message = f"arXiv url is malformed (bad prefix): {article_url}"
        LOG.warning(error_message)
        raise ValueError(error_message)
    article_id = article_url[len(arxiv_url_prefix) :]

    # check version suffix
    suffix_re = "v\\d+$"
    suffix_re_match = re.search(suffix_re, article_id)
    if suffix_re_match:
        article_id = article_id[: suffix_re_match.start()]

    if validate_arxiv_id_new_fmt(article_id) or validate_arxiv_id_old_fmt(article_id):
        return article_id
    else:
        error_message = f"arXiv url is malformed (bad id): {article_id}"
        LOG.warning(error_message)
        raise ValueError(error_message)
