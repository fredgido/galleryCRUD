import pytest
import requests
#from ..run import *


def pytest_report_header(config):
    #if config.option.verbose > 0:
    return ["running instance online test", "doing..."]


def test_online():
    assert requests.get("http://127.0.0.1:5000/").status_code == 200


def test_should_pass():
    pass

#def test_should_fail():
#    raise Exception("errir")


img = "https://flask.palletsprojects.com/en/1.1.x/_images/flask-logo.png"
text = "texet"


def test_create_post():
    link = 'http://127.0.0.1:5000/api/post?text={}&file={}'.format(text, img)
    response = requests.post(link)
    post_id = dict(response.json())["id"]
    assert isinstance(post_id, int) and post_id >= 0


@pytest.fixture
def post():
    link = 'http://127.0.0.1:5000/api/post'
    response = requests.get(link)
    post = dict(response.json())["posts"][0]
    return post


def test_read_post(test_getpost):
    post_id = test_getpost["id"]
    print(post_id)
    link = 'http://127.0.0.1:5000/api/post?id={}'.format(post_id)
    response = requests.get(link)
    assert text == response.json()["text"]
    return dict(response.json())


def test_read_image(test_getpost):
    filename = test_getpost["file"]
    link = 'http://127.0.0.1:5000/static/orig/{}'.format(filename)
    response_server = requests.get(link)
    response_original = requests.get(img)
    assert response_server.content == response_original.content

