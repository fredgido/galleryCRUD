import os
import tempfile
import pytest
import hashlib
import requests
#from ..run import *


def pytest_report_header(config):
    #if config.option.verbose > 0:
    return ["running instance online test", "doing..."]


#@pytest.fixture

def test_online():
    assert requests.get("http://127.0.0.1:5000/").status_code == 200


def test_should_pass():
    pass

#def test_should_fail():
#    raise Exception("errir")


global post_id
post_id = 0
global text
text = "testtext"
img = 'https://danbooru.donmai.us/data/sample/' \
       'sample-74c3adb4c381551e88e882d263b79a6b.jpg'
global filename

def test_create_post():
    link = 'http://127.0.0.1:5000/api/post?text={}&file={}'.format(text,img)
    response = requests.post(link)
    global post_id
    post_id = response.json()["id"]
    print(response.text)


def test_read_post():
    print(post_id)
    link = 'http://127.0.0.1:5000/api/post?id={}'.format(post_id)
    response = requests.get(link)
    assert text == response.json()["text"]
    print(response.json())
    global filename
    filename = response.json()["file"]

def test_read_image():
    print(post_id)
    link = 'http://127.0.0.1:5000//static/orig/{}'.format(filename)
    response_server = requests.get(link)
    response_original = requests.get(img)
    assert response_server.content == response_original.content
