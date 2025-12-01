import logging
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from arxiv.request import build_arxiv_query_url, fetch_articles_from_arxiv_api


@pytest.fixture
def build_query_mock():
    with patch("arxiv.request.build_arxiv_query_url") as mock:
        yield mock


@pytest.fixture
def http_get_mock():
    with patch("arxiv.request.requests.get") as mock:
        yield mock


@pytest.fixture
def etree_fromstring_mock():
    with patch("arxiv.request.ET.fromstring") as mock:
        yield mock


def test_build_arxiv_query_url_builds_correct_url():
    start_time = datetime(2025, 1, 1)
    end_time = datetime(2025, 2, 1, 22, 33)

    expected = (
        "http://export.arxiv.org/api/query?search_query=lastUpdatedDate:"
        "[202501010000+TO+202502012233]&max_results=1000&sortBy=submittedDate&sortOrder=ascending"
    )

    actual = build_arxiv_query_url(start_time, end_time)

    assert expected == actual


def test_build_arxiv_query_url_rejects_invalid_time_range(caplog):
    start_time = datetime(2020, 1, 1)
    end_time = datetime(2019, 1, 1)

    with pytest.raises(ValueError):
        build_arxiv_query_url(start_time, end_time)

    assert len(caplog.records) == 1
    assert caplog.records[0].levelno == logging.WARNING


def test_fetch_articles_from_arxiv_api_builds_query_with_correct_args(
    build_query_mock, http_get_mock, etree_fromstring_mock
):
    input_date_1 = datetime(2000, 1, 2)
    input_date_2 = datetime(2000, 3, 4)
    fetch_articles_from_arxiv_api(input_date_1, input_date_2)
    build_query_mock.assert_called_once_with(input_date_1, input_date_2)


def test_fetch_articles_from_arxiv_api_makes_request_with_correct_url(
    build_query_mock, http_get_mock, etree_fromstring_mock
):
    sample_url = "sample-query-url.com"
    build_query_mock.return_value = sample_url

    fetch_articles_from_arxiv_api(None, None)

    http_get_mock.assert_called_once_with(sample_url)


def test_fetch_articles_from_arxiv_api_parses_http_response_to_xml_string(
    build_query_mock, http_get_mock, etree_fromstring_mock
):
    sample_xml = "<xml>sample xml</xml>"
    sample_response = Mock()
    sample_response.text = sample_xml
    http_get_mock.return_value = sample_response
    fetch_articles_from_arxiv_api(None, None)

    etree_fromstring_mock.assert_called_once_with(sample_xml)
