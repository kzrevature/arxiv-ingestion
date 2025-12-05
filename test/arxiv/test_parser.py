import logging
import xml.etree.ElementTree as ET

import pytest

from arxiv.parser import (
    XML_NS,
    XML_TIME_FMT,
    extract_article_entries,
    extract_total_results,
    parse_arxiv_url_to_id,
    parse_entry_to_article,
    validate_arxiv_id_new_fmt,
    validate_arxiv_id_old_fmt,
)


# this fixture is linked to the contents of test/fixtures/sample.xml
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


def test_extract_total_results(sample_arxiv_xml_root):
    total = extract_total_results(sample_arxiv_xml_root)
    assert any(
        el.text == str(total) and el.tag.endswith("totalResults")
        for el in sample_arxiv_xml_root
    )


def test_extract_article_entries(sample_arxiv_xml_root):
    filter_res = extract_article_entries(sample_arxiv_xml_root)
    assert all(el.tag.endswith("entry") for el in filter_res)


def test_parse_entry_to_article_success(sample_arxiv_xml_root):
    sample_arxiv_xml_entry = sample_arxiv_xml_root.find(f"{XML_NS}entry")
    article = parse_entry_to_article(sample_arxiv_xml_entry).val

    assert any(
        article.id == parse_arxiv_url_to_id(el.text) and el.tag.endswith("id")
        for el in sample_arxiv_xml_entry
    )
    assert any(
        article.title == el.text and el.tag.endswith("title")
        for el in sample_arxiv_xml_entry
    )
    assert any(
        article.created_at.strftime(XML_TIME_FMT) == el.text
        and el.tag.endswith("published")
        for el in sample_arxiv_xml_entry
    )
    assert any(
        article.updated_at.strftime(XML_TIME_FMT) == el.text
        and el.tag.endswith("updated")
        for el in sample_arxiv_xml_entry
    )


# TODO: write these tests, they need a corrupted XML
def test_parse_entry_to_article_rejects_invalid_timestamps():
    pass


def test_parse_entry_to_article_rejects_invalid_id():
    pass
