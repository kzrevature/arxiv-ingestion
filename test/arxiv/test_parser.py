import logging
import xml.etree.ElementTree as ET
from logging import WARN

import pytest

from arxiv.parser import (extract_article_entries, parse_arxiv_url_to_id,
                          validate_arxiv_id_new_fmt, validate_arxiv_id_old_fmt)


@pytest.fixture()
def sample_arxiv_xml_root():
    return ET.parse("test/fixtures/sample.xml").getroot()


def test_validate_arxiv_id_old_fmt_accepts_good_id():
    good_id = "math/1122334"
    expected = True

    actual = validate_arxiv_id_old_fmt(good_id)

    assert expected == actual


def test_validate_arxiv_id_old_fmt_rejects_no_slash():
    bad_id = "math.1122334"
    expected = False

    actual = validate_arxiv_id_old_fmt(bad_id)

    assert expected == actual


def test_validate_arxiv_id_old_fmt_rejects_multiple_slash():
    bad_id = "math/1122/334"
    expected = False

    actual = validate_arxiv_id_old_fmt(bad_id)

    assert expected == actual


def test_validate_arxiv_id_old_fmt_rejects_nonnumeric_second_section():
    bad_id = "math/1122abc"
    expected = False

    actual = validate_arxiv_id_old_fmt(bad_id)

    assert expected == actual


def test_validate_arxiv_id_old_fmt_rejects_bad_length():
    bad_id = "math/11223344"
    expected = False

    actual = validate_arxiv_id_old_fmt(bad_id)

    assert expected == actual


def test_validate_arxiv_id_new_fmt_accepts_good_id():
    good_id = "1122.4567"
    expected = True

    actual = validate_arxiv_id_new_fmt(good_id)

    assert expected == actual


def test_validate_arxiv_id_new_fmt_rejects_no_period():
    bad_id = "11224567"
    expected = False

    actual = validate_arxiv_id_new_fmt(bad_id)

    assert expected == actual


def test_validate_arxiv_id_new_fmt_rejects_multiple_period():
    bad_id = "11.22.4567"
    expected = False

    actual = validate_arxiv_id_new_fmt(bad_id)

    assert expected == actual


def test_validate_arxiv_id_new_fmt_rejects_incorrect_length_for_date_section():
    bad_id = "111.4567"
    expected = False

    actual = validate_arxiv_id_new_fmt(bad_id)

    assert expected == actual


def test_validate_arxiv_id_new_fmt_rejects_nonnumeric_date_section():
    bad_id = "DEC9.4567"
    expected = False

    actual = validate_arxiv_id_new_fmt(bad_id)

    assert expected == actual


def test_validate_arxiv_id_new_fmt_rejects_incorrect_length_for_numbering_section():
    bad_id = "1122.456789"
    expected = False

    actual = validate_arxiv_id_new_fmt(bad_id)

    assert expected == actual


def test_validate_arxiv_id_new_fmt_rejects_nonnumeric_numbering_section():
    bad_id = "1122.45FF"
    expected = False

    actual = validate_arxiv_id_new_fmt(bad_id)

    assert expected == actual


def test_parse_arxiv_url_to_id_extracts_valid_url_old_fmt():
    good_url = "http://arxiv.org/abs/cat/1123999"
    expected = "cat/1123999"

    actual = parse_arxiv_url_to_id(good_url)

    assert expected == actual


def test_parse_arxiv_url_to_id_extracts_valid_url_new_fmt():
    good_url = "http://arxiv.org/abs/1122.3344"
    expected = "1122.3344"

    actual = parse_arxiv_url_to_id(good_url)

    assert expected == actual


def test_parse_arxiv_url_to_id_accepts_extracts_url_stripping_version_number():
    good_url = "http://arxiv.org/abs/1122.3344v55"
    expected = "1122.3344"
    parse_arxiv_url_to_id(good_url)

    actual = parse_arxiv_url_to_id(good_url)
    assert expected == actual


def test_parse_arxiv_url_to_id_rejects_bad_prefix(caplog):
    bad_url = "http://NOT-arxiv.org/abs/1122.3344v1"

    with pytest.raises(ValueError):
        parse_arxiv_url_to_id(bad_url)

    assert len(caplog.records) == 1
    assert caplog.records[0].levelno == logging.WARN


def test_parse_arxiv_url_to_id_rejects_bad_id(caplog):
    bad_url = "http://arxiv.org/abs/112233.445566v7"

    with pytest.raises(ValueError):
        parse_arxiv_url_to_id(bad_url)

    assert len(caplog.records) == 1
    assert caplog.records[0].levelno == logging.WARN


def test_extract_article_entries(sample_arxiv_xml_root):
    filter_res = extract_article_entries(sample_arxiv_xml_root)
    assert all(el.tag.endswith("entry") for el in filter_res)
