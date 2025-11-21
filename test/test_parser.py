from parser import parse_arxiv_url_to_id


def test_parse_arxiv_url_to_id():
    URL = "http://arxiv.org/abs/sample-category/33333v1"
    EXPECTED_ID = "33333"

    actual_id = parse_arxiv_url_to_id(URL)

    assert EXPECTED_ID == actual_id
