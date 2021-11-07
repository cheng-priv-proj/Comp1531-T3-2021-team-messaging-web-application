import pytest
import requests
import json
import flask
from src import config 

from src.other import clear_v1
from src.config import url

@pytest.fixture
def clear_server():
    requests.delete(config.url + "clear/v1")

# Generates new user
@pytest.fixture
def get_valid_token():
    response = requests.post(config.url + 'auth/register/v2', json={
        'email': 'example@email.com', 
        'password': 'potato', 
        'name_first': 'John', 
        'name_last' : 'smith'
    })
    return response.json()

@pytest.fixture
def upload_photo_factory():
    def user_profile_upload_photo(token, img_url, x_start, y_start, x_end, y_end):
        response = requests.post(url + 'user/profile/uploadphoto/v1', params = {
        'token': token,
        'img_url': img_url,
        'x_start': x_start,
        'y_start': y_start,
        'x_end': x_end,
        'y_end': y_end
        })
        return response
    return user_profile_upload_photo


def test_user_profile_upload_photo_v1_invalid_token(clear_server, get_valid_token, upload_photo_factory):
    # generates a filler 300x300 jpeg
    img_url = 'http://dummyimage.com/300.jpeg/09f/fff'
    response = upload_photo_factory(-1, img_url, 0, 0, 200, 200)

    assert response == 403

def test_user_profile_upload_photo_v1_invalid_img_url(clear_server, get_valid_token, upload_photo_factory):
    token = get_valid_token['token']
    img_url = ''
    response = upload_photo_factory(token, img_url, 0, 0, 200, 200)

    assert response == 400

def test_user_profile_upload_photo_v1_invalid_dimensions(clear_server, get_valid_token, upload_photo_factory):
    token = get_valid_token['token']
    img_url = 'http://dummyimage.com/300.jpeg/09f/fff'
    response = upload_photo_factory(token, img_url, 400, 400, 600, 500)

    assert response == 400

def test_user_profile_upload_photo_v1_invalid_end_dimensions(clear_server, get_valid_token, upload_photo_factory):
    token = get_valid_token['token']
    img_url = 'http://dummyimage.com/300.jpeg/09f/fff'
    response = upload_photo_factory(token, img_url, 200, 200, 700, 700)

    assert response == 400

def test_user_profile_upload_photo_v1_photo_not_jpeg(clear_server, get_valid_token, upload_photo_factory):
    token = get_valid_token['token']
    img_url = 'http://dummyimage.com/300.png/09f/fff'
    response = upload_photo_factory(token, img_url, 0, 0, 200, 200)

    assert response == 400
