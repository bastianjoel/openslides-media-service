import pytest
import requests

from tests.base import reset_db

DUPLICATE_URL = "http://media:9006/internal/media/duplicate_mediafile/"
GET_URL = "http://media:9006/system/media/get/"


@pytest.fixture(autouse=True)
def reset_db_in_duplicate_mediafile():
    reset_db()


def check_response(response, status_code):
    assert response.status_code == status_code
    assert "message" in response.json()


def check_saved_content(id_, content, mimetype):
    get_response = requests.get(GET_URL + str(id_))
    assert get_response.status_code == 200
    assert get_response.content == content
    assert mimetype in get_response.headers.get("Content-Type")


def test_good():
    payload = {
        "source_id": 2,
        "target_id": 5,
    }
    response = requests.post(DUPLICATE_URL, json=payload)
    assert response.status_code == 200
    assert response.text == ""
    check_saved_content(5, b"a2", "text/plain")


def test_broken_source():
    payload = {
        "source_id": 4,
        "target_id": 5,
    }
    response = requests.post(DUPLICATE_URL, json=payload)
    check_response(response, 404)


def test_broken_target():
    payload = {
        "source_id": 2,
        "target_id": 3,
    }
    response = requests.post(DUPLICATE_URL, json=payload)
    check_response(response, 500)


def test_empty():
    payload = {}
    response = requests.post(DUPLICATE_URL, json=payload)
    check_response(response, 400)
